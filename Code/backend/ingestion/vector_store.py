from langchain_community.vectorstores import FAISS
from langchain.embeddings.base import Embeddings
from sklearn.feature_extraction.text import TfidfVectorizer
import pickle
import os

class TfidfEmbeddings(Embeddings):
    def __init__(self, vectorizer):
        self.vectorizer = vectorizer

    def embed_documents(self, texts):
        return self.vectorizer.transform(texts).toarray().tolist()

    def embed_query(self, text):
        return self.vectorizer.transform([text]).toarray()[0].tolist()


def create_vector_store(documents, persist_path):
    persist_path = os.path.abspath(persist_path)
    os.makedirs(persist_path, exist_ok=True)

    texts = [doc.page_content for doc in documents]

    # 🔑 Fit ONCE
    vectorizer = TfidfVectorizer()
    vectorizer.fit(texts)

    embeddings = TfidfEmbeddings(vectorizer)

    vector_db = FAISS.from_documents(documents, embeddings)
    vector_db.save_local(persist_path)

    # 🔑 Persist vectorizer
    with open(os.path.join(persist_path, "tfidf.pkl"), "wb") as f:
        pickle.dump(vectorizer, f)

    print(f"📦 Vector store + TF-IDF saved at: {persist_path}")
    return vector_db
