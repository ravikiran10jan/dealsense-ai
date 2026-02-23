import asyncio
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Optional

from retrieval.semantic_search import semantic_search, semantic_search_with_scores
from retrieval.web_search import web_search
from llm.answer_llm import answer_with_llm

logger = logging.getLogger(__name__)

# TF-IDF FAISS uses L2 distance - lower is better
# Threshold adjusted to allow more relevant results from vector DB
# Typical good matches are < 1.8, less relevant matches are > 2.0
SIMILARITY_THRESHOLD = 1.8

# ---------- Timeout / latency budget constants ----------
# Maximum time (seconds) the entire query pipeline is allowed to take.
# After this, the caller gets whatever partial result is available.
GLOBAL_QUERY_TIMEOUT = 12.0

# Maximum time allocated to the web-search leg alone.
WEB_SEARCH_TIMEOUT = 6.0

# Thread pool for running sync functions (RAG, web search) off the event loop
_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="rag-pool")


def _get_track_decorator():
    """Return opik.track when enabled, identity decorator otherwise."""
    try:
        from observability.opik_config import track_if_enabled
        return track_if_enabled()
    except Exception:
        return lambda fn=None, **kw: fn if fn else (lambda f: f)


# =====================================================================
# Synchronous API (used by /api/query and non-live-call paths)
# =====================================================================

def answer_query(query: str) -> Dict[str, Any]:
    """
    Hybrid RAG + Web Search + LLM orchestration:
    1. Search vector DB for relevant context
    2. If RAG results are relevant (low distance score), use them
    3. If RAG results are NOT relevant, fall back to web search
    4. Send context to LLM for final answer
    
    Returns: dict with 'answer', 'sources', 'source_type'
    """
    _track = _get_track_decorator()

    @_track(name="hybrid_rag_query", tags=["rag", "query"])
    def _run_query(q: str) -> Dict[str, Any]:
        return _answer_query_impl(q)

    try:
        return _run_query(query)
    except Exception:
        # Fallback if tracking wrapper fails
        return _answer_query_impl(query)


def _answer_query_impl(query: str) -> Dict[str, Any]:
    """Core implementation of answer_query (separated for trackability)."""
    # Get RAG results with similarity scores (k=5 to include more relevant docs)
    results_with_scores = semantic_search_with_scores(query, k=5)
    
    # Check if we have relevant RAG results
    # For TF-IDF + FAISS L2 distance: lower score = more similar
    has_relevant_rag = False
    rag_context = ""
    rag_sources = []
    
    if results_with_scores:
        best_score = results_with_scores[0][1]  # (doc, score) tuple
        if best_score < SIMILARITY_THRESHOLD:
            has_relevant_rag = True
            rag_context = "\n".join([doc.page_content for doc, score in results_with_scores])
            rag_sources = list(set([doc.metadata.get("source", "Unknown") for doc, score in results_with_scores]))
    
    # If RAG has relevant context, use it
    if has_relevant_rag:
        answer = answer_with_llm(rag_context, query)
        return {
            "answer": answer,
            "sources": rag_sources,
            "source_type": "RAG"
        }
    
    # Otherwise, fall back to web search for real-time information
    try:
        web_context = web_search(query)
        if web_context and web_context.strip():
            answer = answer_with_llm(f"[Web Search Results]\n{web_context}", query)
            return {
                "answer": answer,
                "sources": ["Web Search"],
                "source_type": "WEB"
            }
    except Exception as e:
        logger.warning(f"Web search failed: {e}")
    
    # Final fallback: just use LLM's knowledge without context
    answer = answer_with_llm("No specific context available from knowledge base or web. Use your general knowledge.", query)
    return {
        "answer": answer,
        "sources": ["LLM Knowledge"],
        "source_type": "LLM"
    }


# =====================================================================
# Async API with timeouts (used by live-call and latency-sensitive paths)
# =====================================================================

async def answer_query_async(
    query: str,
    timeout: float = GLOBAL_QUERY_TIMEOUT,
) -> Dict[str, Any]:
    """
    Async version of answer_query with a hard global timeout.

    Runs the synchronous RAG pipeline in a thread-pool and wraps
    the whole thing with asyncio.wait_for().
    """
    loop = asyncio.get_running_loop()

    try:
        result = await asyncio.wait_for(
            loop.run_in_executor(_executor, _answer_query_impl, query),
            timeout=timeout,
        )
        return result
    except asyncio.TimeoutError:
        logger.warning(f"answer_query_async timed out after {timeout}s for: {query[:60]}")
        return {
            "answer": "I'm taking longer than expected to find a detailed answer. "
                      "Based on my general knowledge, please ask me a more specific "
                      "question and I'll do my best to help.",
            "sources": ["Timeout Fallback"],
            "source_type": "TIMEOUT",
            "timed_out": True,
        }


def answer_query_with_context(
    query: str,
    call_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Enhanced RAG query that incorporates live call context.
    Used for push-to-talk queries during active calls.
    """
    _track = _get_track_decorator()

    @_track(name="hybrid_rag_with_context", tags=["rag", "live-call"])
    def _run(q, ctx):
        return _answer_query_with_context_impl(q, ctx)

    try:
        return _run(query, call_context)
    except Exception:
        return _answer_query_with_context_impl(query, call_context)


async def answer_query_with_context_async(
    query: str,
    call_context: Optional[Dict[str, Any]] = None,
    timeout: float = GLOBAL_QUERY_TIMEOUT,
) -> Dict[str, Any]:
    """
    Async, timeout-protected version of answer_query_with_context.

    Priority queue strategy:
      1. RAG search runs first (fast, ~50-100 ms)
      2. If RAG hits, return immediately — skip web search entirely
      3. If RAG misses, fire web search with its own sub-timeout
      4. Global timeout wraps everything — user never waits > timeout
    """
    loop = asyncio.get_running_loop()
    start = time.monotonic()

    try:
        result = await asyncio.wait_for(
            loop.run_in_executor(
                _executor,
                _answer_query_with_context_impl,
                query,
                call_context,
            ),
            timeout=timeout,
        )
        elapsed = time.monotonic() - start
        logger.info(
            f"Live-call query answered in {elapsed:.2f}s "
            f"(source={result.get('source_type')})"
        )
        return result

    except asyncio.TimeoutError:
        elapsed = time.monotonic() - start
        logger.warning(
            f"Live-call query timed out after {elapsed:.2f}s for: {query[:60]}"
        )
        # Return a graceful degradation response instead of hanging
        return {
            "answer": "I couldn't retrieve a detailed answer in time. "
                      "Let me give you a quick response based on what I know — "
                      "please try rephrasing or asking a more specific question.",
            "sources": ["Timeout Fallback"],
            "source_type": "TIMEOUT",
            "confidence": 0.3,
            "timed_out": True,
        }


def _answer_query_with_context_impl(
    query: str,
    call_context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Core implementation of answer_query_with_context."""
    recent_transcript = ""
    account_name = "Unknown"
    
    if call_context:
        recent_transcript = call_context.get("recent_transcript", "")
        account_name = call_context.get("account_name", "Unknown")
    
    # Build enhanced query for better RAG matching
    enhanced_query = query
    if account_name and account_name != "Unknown":
        enhanced_query = f"In the context of {account_name}: {query}"
    
    # ---- Phase 1: RAG search (fast, priority) ----
    results_with_scores = semantic_search_with_scores(enhanced_query, k=3)
    
    has_relevant_rag = False
    rag_context = ""
    rag_sources = []
    confidence = 0.5  # Default confidence
    
    if results_with_scores:
        best_score = results_with_scores[0][1]
        if best_score < SIMILARITY_THRESHOLD:
            has_relevant_rag = True
            rag_context = "\n".join([doc.page_content for doc, score in results_with_scores])
            rag_sources = list(set([doc.metadata.get("source", "Unknown") for doc, score in results_with_scores]))
            # Convert L2 distance to confidence (lower distance = higher confidence)
            confidence = max(0.5, min(1.0, 1.0 - (best_score / 2)))
    
    # Build the combined context for LLM
    combined_context = ""
    
    # Add recent transcript if available
    if recent_transcript:
        combined_context += f"RECENT CONVERSATION:\n{recent_transcript}\n\n"
    
    # Add RAG context if relevant
    if has_relevant_rag:
        combined_context += f"RELEVANT KNOWLEDGE BASE INFORMATION:\n{rag_context}\n\n"
    
    # If we have either context, use it (skip web search -- priority queue)
    if combined_context:
        # Use special prompt for live call assistance
        prompt = f"""You are assisting a sales representative during a live call with {account_name}.
The representative needs a quick, actionable answer they can use immediately.

{combined_context}
USER QUESTION: {query}

Provide a concise, direct answer (2-3 sentences max). Lead with the most important information.
If you're referencing specific data, include the numbers. Be confident and helpful."""
        
        answer = answer_with_llm(combined_context, prompt)
        
        sources = rag_sources if rag_sources else ["Call Context"]
        source_type = "RAG+CALL" if has_relevant_rag else "CALL"
        
        return {
            "answer": answer,
            "sources": sources,
            "source_type": source_type,
            "confidence": confidence
        }
    
    # ---- Phase 2: Web search fallback (with its own timeout) ----
    try:
        web_context = web_search(query, timeout_seconds=WEB_SEARCH_TIMEOUT)
        if web_context and web_context.strip():
            answer = answer_with_llm(f"[Web Search Results]\n{web_context}", query)
            return {
                "answer": answer,
                "sources": ["Web Search"],
                "source_type": "WEB",
                "confidence": 0.7
            }
    except Exception as e:
        logger.warning(f"Web search failed: {e}")
    
    # ---- Phase 3: LLM-only fallback ----
    answer = answer_with_llm("No specific context available. Use your general knowledge to help.", query)
    return {
        "answer": answer,
        "sources": ["LLM Knowledge"],
        "source_type": "LLM",
        "confidence": 0.5
    }
