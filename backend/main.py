import os
from ingestion.pptx_loader import load_pptx_folder
from ingestion.text_chunker import chunk_documents
from ingestion.vector_store import create_vector_store
from retrieval.semantic_search import load_vector_store, semantic_search

VECTOR_DB_PATH = "vector_store/dealsense_faiss"

from orchestration.hybrid_answer import answer_query


def vector_store_exists():
    """Check if vector store already exists."""
    faiss_index = os.path.join(VECTOR_DB_PATH, "index.faiss")
    return os.path.exists(faiss_index)



def chat():
    while True:
        query = input("\nAsk a question (type 'exit' or 'quit' to quit): ").strip()

        if query.lower() in ["exit", "quit"]:
            print("👋 Exiting. Bye!")
            break   # ⬅️ exits immediately

        answer = answer_query(query)
        print("\n" + answer)


def ingest():
    print("📥 Loading PPTX files...")

    case_docs = load_pptx_folder(
        folder_path="data/case_studies",
        document_type="case_study"
    )

    offering_docs = load_pptx_folder(
        folder_path="data/offerings",
        document_type="offering"
    )

    all_docs = case_docs + offering_docs

    print(f"✅ Loaded {len(all_docs)} slides")

    print("✂️ Chunking documents...")
    chunks = chunk_documents(all_docs)
    print(f"✅ Created {len(chunks)} chunks")

    print("🧠 Creating vector store...")
    create_vector_store(chunks, VECTOR_DB_PATH)

    print("🎉 Vector store created successfully!")
'''
def test_search():
    print("🔍 Testing semantic search...")
    vector_db = load_vector_store()

    query = "when DXC integrated with Luxoft"
    results = semantic_search(query)

    for r in results:
        print("\n---")
        print("Source:", r.metadata["source"])
        print("Slide:", r.metadata["slide"])
        print(r.page_content[:300])'''

if __name__ == "__main__":
    if vector_store_exists():
        print("✅ Vector store already exists, skipping ingestion...")
    else:
        ingest()
    chat()
