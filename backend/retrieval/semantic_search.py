from langchain_community.vectorstores import FAISS
from ingestion.vector_store import TfidfEmbeddings
import os
import pickle
import logging

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_DB_PATH = os.path.join(BASE_DIR, "vector_store", "dealsense_faiss")

def load_vector_store():
    # Load fitted vectorizer
    with open(os.path.join(VECTOR_DB_PATH, "tfidf.pkl"), "rb") as f:
        vectorizer = pickle.load(f)

    embeddings = TfidfEmbeddings(vectorizer)

    return FAISS.load_local(
        VECTOR_DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )


def _rag_tracked(fn):
    """Apply @track_rag_query when Opik is enabled, else return fn as-is."""
    try:
        from observability.opik_tracer import track_rag_query
        return track_rag_query(name=fn.__name__)(fn)
    except Exception:
        return fn


def _semantic_search(query, k=3):
    vector_db = load_vector_store()
    return vector_db.similarity_search(query, k=k)


def _semantic_search_with_scores(query, k=3):
    """Returns list of (document, score) tuples. Lower score = more similar."""
    vector_db = load_vector_store()
    return vector_db.similarity_search_with_score(query, k=k)


# Wrap with Opik tracing (no-op when disabled)
semantic_search = _rag_tracked(_semantic_search)
semantic_search_with_scores = _rag_tracked(_semantic_search_with_scores)
