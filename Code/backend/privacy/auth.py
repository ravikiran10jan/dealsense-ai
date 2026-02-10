"""
API Authentication Module
Provides API key-based authentication with role-based access control.
"""

import os
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from contextlib import contextmanager
from fastapi import HTTPException, Security, Request
from fastapi.security.api_key import APIKeyHeader


# Database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "data", "api_keys.db")

# API Key header
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# Role definitions
ROLES = {
    'admin': {
        'description': 'Full access including PII management and audit logs',
        'permissions': ['read', 'write', 'delete', 'pii_access', 'audit_access', 'admin']
    },
    'seller': {
        'description': 'Can create deals, query RAG, and manage own deals',
        'permissions': ['read', 'write', 'delete']
    },
    'readonly': {
        'description': 'Can only query RAG and view deals',
        'permissions': ['read']
    }
}


class AuthManager:
    """Manages API key authentication and authorization."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize the auth manager.
        
        Args:
            db_path: Path to SQLite database for API key storage.
        """
        self.db_path = db_path or DEFAULT_DB_PATH
        self._init_db()
    
    def _init_db(self):
        """Initialize the SQLite database schema."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS api_keys (
                    key_hash TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    expires_at TEXT,
                    revoked INTEGER DEFAULT 0,
                    last_used TEXT
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_id ON api_keys(user_id)
            ''')
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get a database connection with proper cleanup."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _hash_key(self, api_key: str) -> str:
        """Hash an API key for secure storage."""
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def generate_api_key(
        self,
        user_id: str,
        role: str,
        description: str = None,
        expires_in_days: int = None
    ) -> str:
        """
        Generate a new API key for a user.
        
        Args:
            user_id: User identifier (email or username)
            role: User role ('admin', 'seller', 'readonly')
            description: Optional description for the key
            expires_in_days: Optional expiration in days (None = never expires)
            
        Returns:
            The generated API key (store securely - only returned once!)
        """
        if role not in ROLES:
            raise ValueError(f"Invalid role. Must be one of: {list(ROLES.keys())}")
        
        # Generate secure random key with prefix
        raw_key = secrets.token_urlsafe(32)
        api_key = f"ds_{raw_key}"
        key_hash = self._hash_key(api_key)
        
        expires_at = None
        if expires_in_days:
            expires_at = (datetime.utcnow() + timedelta(days=expires_in_days)).isoformat()
        
        with self._get_connection() as conn:
            conn.execute('''
                INSERT INTO api_keys 
                (key_hash, user_id, role, description, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (key_hash, user_id, role, description, datetime.utcnow().isoformat(), expires_at))
            conn.commit()
        
        return api_key
    
    def verify_key(self, api_key: str) -> Optional[Dict]:
        """
        Verify an API key and return user info if valid.
        
        Args:
            api_key: The API key to verify
            
        Returns:
            Dict with user_id, role, permissions if valid, None otherwise
        """
        if not api_key:
            return None
        
        key_hash = self._hash_key(api_key)
        
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT user_id, role, revoked, expires_at
                FROM api_keys WHERE key_hash = ?
            ''', (key_hash,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Check if revoked
            if row['revoked']:
                return None
            
            # Check expiration
            if row['expires_at']:
                expires_at = datetime.fromisoformat(row['expires_at'])
                if datetime.utcnow() > expires_at:
                    return None
            
            # Update last used timestamp
            conn.execute('''
                UPDATE api_keys SET last_used = ? WHERE key_hash = ?
            ''', (datetime.utcnow().isoformat(), key_hash))
            conn.commit()
            
            role = row['role']
            return {
                'user_id': row['user_id'],
                'role': role,
                'permissions': ROLES.get(role, {}).get('permissions', [])
            }
    
    def revoke_key(self, api_key: str) -> bool:
        """
        Revoke an API key.
        
        Args:
            api_key: The API key to revoke
            
        Returns:
            True if key was revoked, False if not found
        """
        key_hash = self._hash_key(api_key)
        
        with self._get_connection() as conn:
            cursor = conn.execute('''
                UPDATE api_keys SET revoked = 1 WHERE key_hash = ?
            ''', (key_hash,))
            conn.commit()
            return cursor.rowcount > 0
    
    def revoke_user_keys(self, user_id: str) -> int:
        """
        Revoke all API keys for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Number of keys revoked
        """
        with self._get_connection() as conn:
            cursor = conn.execute('''
                UPDATE api_keys SET revoked = 1 WHERE user_id = ?
            ''', (user_id,))
            conn.commit()
            return cursor.rowcount
    
    def list_keys(self, user_id: str = None) -> List[Dict]:
        """
        List API keys (metadata only, not the actual keys).
        
        Args:
            user_id: Optional filter by user
            
        Returns:
            List of key metadata
        """
        with self._get_connection() as conn:
            if user_id:
                cursor = conn.execute('''
                    SELECT user_id, role, description, created_at, expires_at, revoked, last_used
                    FROM api_keys WHERE user_id = ?
                ''', (user_id,))
            else:
                cursor = conn.execute('''
                    SELECT user_id, role, description, created_at, expires_at, revoked, last_used
                    FROM api_keys
                ''')
            
            return [dict(row) for row in cursor.fetchall()]
    
    def has_permission(self, auth_info: Dict, permission: str) -> bool:
        """
        Check if user has a specific permission.
        
        Args:
            auth_info: Auth info dict from verify_key
            permission: Permission to check
            
        Returns:
            True if user has the permission
        """
        if not auth_info:
            return False
        return permission in auth_info.get('permissions', [])


# Global auth manager instance
_auth_manager: Optional[AuthManager] = None


def get_auth_manager() -> AuthManager:
    """Get or create the global auth manager instance."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager


async def verify_api_key(
    request: Request,
    api_key: str = Security(API_KEY_HEADER)
) -> Dict:
    """
    FastAPI dependency for API key verification.
    
    Args:
        request: FastAPI request object
        api_key: API key from header
        
    Returns:
        Auth info dict with user_id, role, permissions
        
    Raises:
        HTTPException: If authentication fails
    """
    # Check for bypass in development mode
    dev_mode = os.getenv("DEALSENSE_DEV_MODE", "").lower() == "true"
    
    if not api_key:
        if dev_mode:
            # Return default admin auth in dev mode without key
            return {
                'user_id': 'dev_user',
                'role': 'admin',
                'permissions': ROLES['admin']['permissions']
            }
        raise HTTPException(
            status_code=401,
            detail="API key required. Pass via X-API-Key header."
        )
    
    auth_manager = get_auth_manager()
    auth_info = auth_manager.verify_key(api_key)
    
    if not auth_info:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired API key."
        )
    
    # Add request metadata for audit logging
    auth_info['ip_address'] = request.client.host if request.client else 'unknown'
    auth_info['user_agent'] = request.headers.get('user-agent', 'unknown')
    
    return auth_info


def require_permission(permission: str):
    """
    Decorator factory to require a specific permission.
    Use as: @require_permission('admin')
    
    Args:
        permission: Required permission
        
    Returns:
        Dependency function for FastAPI
    """
    async def check_permission(auth: Dict = Security(verify_api_key)):
        if not get_auth_manager().has_permission(auth, permission):
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied. Required: {permission}"
            )
        return auth
    return check_permission


def require_role(role: str):
    """
    Decorator factory to require a specific role.
    
    Args:
        role: Required role
        
    Returns:
        Dependency function for FastAPI
    """
    async def check_role(auth: Dict = Security(verify_api_key)):
        if auth.get('role') != role:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required role: {role}"
            )
        return auth
    return check_role
