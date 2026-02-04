import os
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)

def answer_with_llm(context, query):
    prompt = f"""You are a helpful sales assistant for DXC Luxoft, specializing in trade finance solutions.

INSTRUCTIONS:
1. First, check if the provided context contains information relevant to the question.
2. If the context contains relevant information, use it to answer the question and cite the context.
3. If the context does NOT contain relevant information for this specific question, use your general knowledge to provide a helpful answer.
4. Always provide a complete, helpful answer - never say "I cannot answer" or "the context doesn't contain this information" without then providing what you DO know.

CONTEXT FROM KNOWLEDGE BASE:
{context}

USER QUESTION:
{query}

Provide a clear, helpful answer. If you're using general knowledge instead of the provided context, that's fine - just answer the question to the best of your ability."""
    return llm.invoke(prompt).content
