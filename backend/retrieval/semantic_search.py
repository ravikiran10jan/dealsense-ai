from langchain_community.vectorstores import FAISS
from ingestion.vector_store import TfidfEmbeddings
import os
import pickle

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_DB_PATH = os.path.join(BASE_DIR, "vector_store", "dealsense_faiss")

def load_vector_store():
    # 🔑 Load fitted vectorizer
    with open(os.path.join(VECTOR_DB_PATH, "tfidf.pkl"), "rb") as f:
        vectorizer = pickle.load(f)

    embeddings = TfidfEmbeddings(vectorizer)

    return FAISS.load_local(
        VECTOR_DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

def semantic_search(query, k=3):
    vector_db = load_vector_store()
    return vector_db.similarity_search(query, k=k)

def semantic_search_with_scores(query, k=3):
    """Returns list of (document, score) tuples. Lower score = more similar."""
    vector_db = load_vector_store()
    return vector_db.similarity_search_with_score(query, k=k)
