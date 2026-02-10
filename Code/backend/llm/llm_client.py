def generate_answer(query, context, source):
    """
    Later this will call Azure OpenAI / OpenAI / Ollama.
    For now, just format the response.
    """
    return f"Answering the query: '{query}'\n\nBased on the context:\n{context}\n\n(Source: {source})"