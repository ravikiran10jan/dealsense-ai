from typing import Dict, Any, Optional
from retrieval.semantic_search import semantic_search, semantic_search_with_scores
from retrieval.web_search import web_search
from llm.answer_llm import answer_with_llm

# TF-IDF FAISS uses L2 distance - lower is better
# Threshold adjusted to allow more relevant results from vector DB
# Typical good matches are < 1.8, less relevant matches are > 2.0
SIMILARITY_THRESHOLD = 1.8


def answer_query(query: str) -> Dict[str, Any]:
    """
    Hybrid RAG + Web Search + LLM orchestration:
    1. Search vector DB for relevant context
    2. If RAG results are relevant (low distance score), use them
    3. If RAG results are NOT relevant, fall back to web search
    4. Send context to LLM for final answer
    
    Returns: dict with 'answer', 'sources', 'source_type'
    """
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
        print(f"Web search failed: {e}")
    
    # Final fallback: just use LLM's knowledge without context
    answer = answer_with_llm("No specific context available from knowledge base or web. Use your general knowledge.", query)
    return {
        "answer": answer,
        "sources": ["LLM Knowledge"],
        "source_type": "LLM"
    }


def answer_query_with_context(
    query: str,
    call_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Enhanced RAG query that incorporates live call context.
    Used for push-to-talk queries during active calls.
    
    Args:
        query: The user's question
        call_context: Optional context from active call containing:
            - recent_transcript: Last 2 minutes of conversation
            - account_name: Customer name
            - deal_id: Associated deal ID
            - industry: Customer industry
    
    Returns:
        dict with 'answer', 'sources', 'source_type', 'confidence'
    """
    recent_transcript = ""
    account_name = "Unknown"
    
    if call_context:
        recent_transcript = call_context.get("recent_transcript", "")
        account_name = call_context.get("account_name", "Unknown")
    
    # Build enhanced query for better RAG matching
    enhanced_query = query
    if account_name and account_name != "Unknown":
        enhanced_query = f"In the context of {account_name}: {query}"
    
    # Get RAG results with similarity scores
    results_with_scores = semantic_search_with_scores(enhanced_query, k=3)
    
    # Check if we have relevant RAG results
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
    
    # If we have either context, use it
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
    
    # Fall back to web search
    try:
        web_context = web_search(query)
        if web_context and web_context.strip():
            answer = answer_with_llm(f"[Web Search Results]\n{web_context}", query)
            return {
                "answer": answer,
                "sources": ["Web Search"],
                "source_type": "WEB",
                "confidence": 0.7
            }
    except Exception as e:
        print(f"Web search failed: {e}")
    
    # Final fallback: LLM knowledge
    answer = answer_with_llm("No specific context available. Use your general knowledge to help.", query)
    return {
        "answer": answer,
        "sources": ["LLM Knowledge"],
        "source_type": "LLM",
        "confidence": 0.5
    }
