"""
Reversible Tokenizer for PII
Replaces PII with tokens and stores encrypted mappings for later retrieval.
"""

import os
import uuid
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from contextlib import contextmanager

from .encryption import encrypt_value, decrypt_value
from .pii_detector import detect_pii, PIIMatch


# Database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "data", "pii_mappings.db")


class Tokenizer:
    """
    Reversible tokenizer that replaces PII with tokens and stores
    encrypted mappings for authorized retrieval.
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize the tokenizer.
        
        Args:
            db_path: Path to SQLite database for token storage.
                     Defaults to backend/data/pii_mappings.db
        """
        self.db_path = db_path or DEFAULT_DB_PATH
        self._init_db()
    
    def _init_db(self):
        """Initialize the SQLite database schema."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS pii_tokens (
                    token_id TEXT PRIMARY KEY,
                    pii_type TEXT NOT NULL,
                    encrypted_value BLOB NOT NULL,
                    source_document TEXT,
                    created_at TEXT NOT NULL,
                    accessed_count INTEGER DEFAULT 0,
                    last_accessed TEXT
                )
            ''')
            
            # Create index for efficient lookups
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_source_document 
                ON pii_tokens(source_document)
            ''')
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get a database connection with proper cleanup."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def _generate_token_id(self) -> str:
        """Generate a short unique token ID."""
        return uuid.uuid4().hex[:8]
    
    def _format_token(self, pii_type: str, token_id: str) -> str:
        """Format a token string for insertion into text."""
        return f"[PII:{pii_type}:{token_id}]"
    
    def tokenize(
        self, 
        text: str, 
        source: str = None
    ) -> Tuple[str, List[str]]:
        """
        Replace PII in text with tokens and store encrypted mappings.
        
        Args:
            text: The text containing PII to tokenize
            source: Source identifier for the document (e.g., "deal_123")
            
        Returns:
            Tuple of (sanitized_text, list of token_ids created)
        """
        if not text:
            return text, []
        
        # Detect PII in the text
        matches = detect_pii(text)
        
        if not matches:
            return text, []
        
        token_ids = []
        
        # Process matches in reverse order to preserve string positions
        result = text
        for match in reversed(matches):
            token_id = self._generate_token_id()
            token_ids.insert(0, token_id)  # Maintain order
            
            # Store encrypted mapping
            self._store_mapping(
                token_id=token_id,
                pii_type=match.pii_type,
                value=match.value,
                source=source
            )
            
            # Replace PII with token in text
            token_str = self._format_token(match.pii_type, token_id)
            result = result[:match.start] + token_str + result[match.end:]
        
        return result, token_ids
    
    def _store_mapping(
        self, 
        token_id: str, 
        pii_type: str, 
        value: str, 
        source: str = None
    ):
        """Store an encrypted PII mapping in the database."""
        encrypted = encrypt_value(value)
        
        with self._get_connection() as conn:
            conn.execute('''
                INSERT OR REPLACE INTO pii_tokens 
                (token_id, pii_type, encrypted_value, source_document, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (token_id, pii_type, encrypted, source, datetime.utcnow().isoformat()))
            conn.commit()
    
    def detokenize(self, text: str, track_access: bool = True) -> str:
        """
        Replace tokens in text with original PII values.
        
        Args:
            text: Text containing PII tokens
            track_access: Whether to increment access counter
            
        Returns:
            Text with tokens replaced by original values
        """
        if not text or '[PII:' not in text:
            return text
        
        import re
        token_pattern = re.compile(r'\[PII:([A-Z_]+):([a-f0-9]+)\]')
        
        def replace_token(match):
            pii_type = match.group(1)
            token_id = match.group(2)
            
            original = self._retrieve_value(token_id, track_access)
            return original if original else match.group(0)
        
        return token_pattern.sub(replace_token, text)
    
    def _retrieve_value(self, token_id: str, track_access: bool = True) -> Optional[str]:
        """Retrieve and decrypt the original value for a token."""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT encrypted_value FROM pii_tokens WHERE token_id = ?
            ''', (token_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            if track_access:
                conn.execute('''
                    UPDATE pii_tokens 
                    SET accessed_count = accessed_count + 1,
                        last_accessed = ?
                    WHERE token_id = ?
                ''', (datetime.utcnow().isoformat(), token_id))
                conn.commit()
            
            return decrypt_value(row[0])
    
    def get_tokens_for_source(self, source: str) -> List[Dict]:
        """
        Get all tokens associated with a source document.
        
        Args:
            source: Source document identifier
            
        Returns:
            List of token metadata (without decrypted values)
        """
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT token_id, pii_type, created_at, accessed_count, last_accessed
                FROM pii_tokens WHERE source_document = ?
            ''', (source,))
            
            return [
                {
                    'token_id': row[0],
                    'pii_type': row[1],
                    'created_at': row[2],
                    'accessed_count': row[3],
                    'last_accessed': row[4],
                }
                for row in cursor.fetchall()
            ]
    
    def delete_tokens_for_source(self, source: str) -> int:
        """
        Delete all tokens associated with a source document.
        Used for data cleanup or GDPR compliance.
        
        Args:
            source: Source document identifier
            
        Returns:
            Number of tokens deleted
        """
        with self._get_connection() as conn:
            cursor = conn.execute('''
                DELETE FROM pii_tokens WHERE source_document = ?
            ''', (source,))
            conn.commit()
            return cursor.rowcount
    
    def get_token_stats(self) -> Dict:
        """Get statistics about stored tokens."""
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT 
                    COUNT(*) as total,
                    COUNT(DISTINCT source_document) as sources,
                    SUM(accessed_count) as total_accesses
                FROM pii_tokens
            ''')
            row = cursor.fetchone()
            
            type_cursor = conn.execute('''
                SELECT pii_type, COUNT(*) FROM pii_tokens GROUP BY pii_type
            ''')
            by_type = {r[0]: r[1] for r in type_cursor.fetchall()}
            
            return {
                'total_tokens': row[0],
                'unique_sources': row[1],
                'total_accesses': row[2] or 0,
                'by_type': by_type,
            }


# Singleton instance
_tokenizer_instance: Optional[Tokenizer] = None


def get_tokenizer() -> Tokenizer:
    """Get or create the global tokenizer instance."""
    global _tokenizer_instance
    if _tokenizer_instance is None:
        _tokenizer_instance = Tokenizer()
    return _tokenizer_instance
