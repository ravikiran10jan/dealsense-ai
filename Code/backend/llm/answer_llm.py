import os
import logging
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)


def _get_feedback_adjustments() -> str:
    """Fetch prompt adjustments derived from user feedback."""
    try:
        from storage.feedback_store import get_feedback_store
        store = get_feedback_store()
        return store.get_prompt_adjustments()
    except Exception as exc:
        logger.debug(f"Could not load feedback adjustments: {exc}")
        return ""


def answer_with_llm(context, query):
    feedback_adjustments = _get_feedback_adjustments()

    prompt = f"""You are a helpful sales assistant for DXC Solutions, specializing in Banking & Financial Services solutions.

INSTRUCTIONS:
1. First, check if the provided context contains information relevant to the question.
2. If the context contains relevant information, use it to answer the question and cite the context.
3. If the context does NOT contain relevant information for this specific question, use your general knowledge to provide a helpful answer.
4. Always provide a complete, helpful answer - never say "I cannot answer" or "the context doesn't contain this information" without then providing what you DO know.
{feedback_adjustments}
CONTEXT FROM KNOWLEDGE BASE:
{context}

USER QUESTION:
{query}

Provide a clear, helpful answer. If you're using general knowledge instead of the provided context, that's fine - just answer the question to the best of your ability."""

    # Attach Opik tracer callback when enabled
    try:
        from observability.opik_config import get_opik_tracer
        tracer = get_opik_tracer()
        if tracer:
            return llm.invoke(prompt, config={"callbacks": [tracer]}).content
    except Exception as exc:
        logger.debug(f"Opik tracer unavailable: {exc}")

    return llm.invoke(prompt).content
