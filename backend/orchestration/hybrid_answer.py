from retrieval.semantic_search import semantic_search, semantic_search_with_scores
from retrieval.web_search import web_search
from llm.answer_llm import answer_with_llm

# TF-IDF FAISS uses L2 distance - lower is better
# Typical threshold: scores > 1.0 are usually not very relevant
SIMILARITY_THRESHOLD = 1.0

def answer_query(query):
    """
    Hybrid RAG + Web Search + LLM orchestration:
    1. Search vector DB for relevant context
    2. If RAG results are relevant (low distance score), use them
    3. If RAG results are NOT relevant, fall back to web search
    4. Send context to LLM for final answer
    
    Returns: dict with 'answer', 'sources', 'source_type'
    """
    # Get RAG results with similarity scores
    results_with_scores = semantic_search_with_scores(query, k=3)
    
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
