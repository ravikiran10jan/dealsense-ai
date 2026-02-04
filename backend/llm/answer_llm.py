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
    prompt = f"""
You are a helpful assistant.
Answer the question using the context below.

Context:
{context}

Question:
{query}
"""
    return llm.invoke(prompt).content
