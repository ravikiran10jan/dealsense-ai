from retrieval.semantic_search import semantic_search
from retrieval.web_search import web_search
from llm.answer_llm import answer_with_llm

SIMILARITY_THRESHOLD = 0.3   # tune if needed

def answer_query(query):
    results = semantic_search(query, k=3)

    # If local results found
    if results:
        context = "\n".join([doc.page_content for doc in results])
        return answer_with_llm(context, query)

    # Fallback to internet
    web_context = web_search(query)
    return answer_with_llm(web_context, query)
