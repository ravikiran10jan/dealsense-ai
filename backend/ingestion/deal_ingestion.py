"""
Deal Ingestion Module
Adds new deal documents to the existing FAISS vector store
With PII sanitization to protect sensitive information.
"""
import os
import pickle
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from ingestion.vector_store import TfidfEmbeddings
from privacy.sanitizer import sanitize_text
from privacy.audit_logger import audit_log

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_DB_PATH = os.path.join(BASE_DIR, "vector_store", "dealsense_faiss")


def load_vector_store_for_update():
    """Load existing vector store and vectorizer for updates"""
    vectorizer_path = os.path.join(VECTOR_DB_PATH, "tfidf.pkl")
    
    if not os.path.exists(vectorizer_path):
        raise FileNotFoundError(f"Vector store not found at {VECTOR_DB_PATH}")
    
    # Load fitted vectorizer
    with open(vectorizer_path, "rb") as f:
        vectorizer = pickle.load(f)
    
    embeddings = TfidfEmbeddings(vectorizer)
    
    vector_db = FAISS.load_local(
        VECTOR_DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
    
    return vector_db, embeddings


def ingest_deal_to_vector_store(
    deal_id: int,
    account_name: str,
    content: str,
    metadata: dict = None
) -> bool:
    """
    Add a new deal document to the FAISS vector store.
    Content is automatically sanitized to remove PII.
    
    Args:
        deal_id: Unique identifier for the deal
        account_name: Name of the account/company
        content: Text content to be indexed (notes, description, etc.)
        metadata: Additional metadata (industry, stage, etc.)
    
    Returns:
        bool: True if successful, False otherwise
    """
    if not content or not content.strip():
        print(f"Warning: No content to ingest for deal {deal_id}")
        return False
    
    try:
        # Load existing vector store
        vector_db, embeddings = load_vector_store_for_update()
        
        # Sanitize content to remove PII before indexing
        source_ref = f"deal_{deal_id}"
        sanitized_content, content_tokens = sanitize_text(content, source=source_ref)
        sanitized_account, account_tokens = sanitize_text(account_name, source=f"{source_ref}_name")
        
        all_tokens = content_tokens + account_tokens
        
        # Create document with metadata
        doc_metadata = {
            "source": source_ref,
            "deal_id": deal_id,
            "account_name": sanitized_account,  # Store sanitized account name
            "type": "deal_notes",
            "pii_tokens": all_tokens,  # Track tokens for potential retrieval
        }
        
        # Merge additional metadata
        if metadata:
            doc_metadata.update(metadata)
        
        # Create document with sanitized content
        document = Document(
            page_content=f"Deal: {sanitized_account}\n\n{sanitized_content}",
            metadata=doc_metadata
        )
        
        # Add to vector store
        vector_db.add_documents([document])
        
        # Save updated vector store
        vector_db.save_local(VECTOR_DB_PATH)
        
        # Audit log the ingestion
        if all_tokens:
            audit_log(
                action='pii_sanitize',
                resource_type='deal',
                resource_id=str(deal_id),
                status='success',
                token_count=len(all_tokens)
            )
        
        print(f"Successfully ingested deal {deal_id} ({sanitized_account}) to vector store")
        return True
        
    except Exception as e:
        print(f"Error ingesting deal to vector store: {e}")
        raise e


def ingest_transcript_to_vector_store(
    deal_id: int,
    account_name: str,
    transcript_content: str,
    call_date: str = None
) -> bool:
    """
    Add a call transcript to the vector store.
    Transcript content is automatically sanitized to remove PII.
    
    Args:
        deal_id: Associated deal ID
        account_name: Name of the account/company
        transcript_content: Full transcript text
        call_date: Date of the call
    
    Returns:
        bool: True if successful
    """
    if not transcript_content or not transcript_content.strip():
        print(f"Warning: No transcript content to ingest for deal {deal_id}")
        return False
    
    try:
        vector_db, embeddings = load_vector_store_for_update()
        
        # Sanitize transcript content to remove PII
        source_ref = f"transcript_deal_{deal_id}"
        sanitized_content, content_tokens = sanitize_text(transcript_content, source=source_ref)
        sanitized_account, account_tokens = sanitize_text(account_name, source=f"{source_ref}_name")
        
        all_tokens = content_tokens + account_tokens
        
        # Create document with transcript metadata
        doc_metadata = {
            "source": source_ref,
            "deal_id": deal_id,
            "account_name": sanitized_account,
            "type": "call_transcript",
            "call_date": call_date or "unknown",
            "pii_tokens": all_tokens,
        }
        
        document = Document(
            page_content=f"Call Transcript - {sanitized_account}\n\n{sanitized_content}",
            metadata=doc_metadata
        )
        
        vector_db.add_documents([document])
        vector_db.save_local(VECTOR_DB_PATH)
        
        # Audit log the ingestion
        if all_tokens:
            audit_log(
                action='pii_sanitize',
                resource_type='transcript',
                resource_id=str(deal_id),
                status='success',
                token_count=len(all_tokens)
            )
        
        print(f"Successfully ingested transcript for deal {deal_id} ({sanitized_account})")
        return True
        
    except Exception as e:
        print(f"Error ingesting transcript to vector store: {e}")
        raise e


def ingest_action_items_to_vector_store(
    deal_id: int,
    account_name: str,
    action_items: list
) -> bool:
    """
    Add action items from a call to the vector store.
    Action items are automatically sanitized to remove PII.
    
    Args:
        deal_id: Associated deal ID
        account_name: Name of the account/company
        action_items: List of action item strings
    
    Returns:
        bool: True if successful
    """
    if not action_items:
        return False
    
    try:
        vector_db, embeddings = load_vector_store_for_update()
        
        # Format action items as text
        action_text = "\n".join([f"- {item}" for item in action_items])
        
        # Sanitize action items content
        source_ref = f"actions_deal_{deal_id}"
        sanitized_content, content_tokens = sanitize_text(action_text, source=source_ref)
        sanitized_account, account_tokens = sanitize_text(account_name, source=f"{source_ref}_name")
        
        all_tokens = content_tokens + account_tokens
        
        doc_metadata = {
            "source": source_ref,
            "deal_id": deal_id,
            "account_name": sanitized_account,
            "type": "action_items",
            "pii_tokens": all_tokens,
        }
        
        document = Document(
            page_content=f"Action Items - {sanitized_account}\n\n{sanitized_content}",
            metadata=doc_metadata
        )
        
        vector_db.add_documents([document])
        vector_db.save_local(VECTOR_DB_PATH)
        
        # Audit log the ingestion
        if all_tokens:
            audit_log(
                action='pii_sanitize',
                resource_type='action_items',
                resource_id=str(deal_id),
                status='success',
                token_count=len(all_tokens)
            )
        
        print(f"Successfully ingested action items for deal {deal_id} ({sanitized_account})")
        return True
        
    except Exception as e:
        print(f"Error ingesting action items to vector store: {e}")
        raise e
