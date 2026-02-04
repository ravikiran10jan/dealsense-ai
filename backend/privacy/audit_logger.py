"""
Audit Logging Module
Provides comprehensive audit logging for security and compliance tracking.
"""

import os
import sqlite3
import hashlib
import json
from datetime import datetime
from typing import Optional, Dict, List, Any
from contextlib import contextmanager


# Database path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "data", "audit_logs.db")


# Audit action types
ACTIONS = {
    # API Actions
    'api_request': 'General API request',
    'query': 'RAG query executed',
    'search': 'Semantic search executed',
    
    # Deal Actions
    'deal_create': 'New deal created',
    'deal_read': 'Deal details accessed',
    'deal_update': 'Deal updated',
    'deal_delete': 'Deal deleted',
    
    # PII Actions
    'pii_sanitize': 'PII sanitized from text',
    'pii_detokenize': 'PII tokens revealed (admin)',
    'pii_delete': 'PII tokens deleted',
    
    # Auth Actions
    'auth_success': 'Successful authentication',
    'auth_failure': 'Failed authentication attempt',
    'key_create': 'API key generated',
    'key_revoke': 'API key revoked',
}


class AuditLogger:
    """
    Comprehensive audit logger for tracking data access and modifications.
    Stores audit events without logging actual PII values.
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize the audit logger.
        
        Args:
            db_path: Path to SQLite database for audit logs.
        """
        self.db_path = db_path or DEFAULT_DB_PATH
        self._init_db()
    
    def _init_db(self):
        """Initialize the SQLite database schema."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_id TEXT,
                    user_role TEXT,
                    action TEXT NOT NULL,
                    resource_type TEXT,
                    resource_id TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    status TEXT NOT NULL,
                    pii_accessed INTEGER DEFAULT 0,
                    metadata TEXT
                )
            ''')
            
            # Create indexes for efficient querying
            conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON audit_log(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_user_id ON audit_log(user_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_action ON audit_log(action)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_resource ON audit_log(resource_type, resource_id)')
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
    
    def _hash_query(self, query: str) -> str:
        """
        Hash a query string for storage.
        We store hashes instead of actual queries to prevent PII leakage.
        """
        return hashlib.sha256(query.encode()).hexdigest()[:16]
    
    def log(
        self,
        action: str,
        user_id: str = None,
        user_role: str = None,
        resource_type: str = None,
        resource_id: str = None,
        ip_address: str = None,
        user_agent: str = None,
        status: str = 'success',
        pii_accessed: bool = False,
        metadata: Dict = None
    ) -> int:
        """
        Log an audit event.
        
        Args:
            action: Action type (see ACTIONS dict)
            user_id: User identifier
            user_role: User's role
            resource_type: Type of resource accessed (deal, transcript, etc.)
            resource_id: Specific resource identifier
            ip_address: Client IP address
            user_agent: Client user agent
            status: 'success', 'failure', 'denied'
            pii_accessed: Whether PII was accessed/revealed
            metadata: Additional metadata (will be JSON serialized)
            
        Returns:
            The ID of the created log entry
        """
        # Sanitize metadata to prevent PII in logs
        safe_metadata = None
        if metadata:
            safe_metadata = self._sanitize_metadata(metadata)
        
        with self._get_connection() as conn:
            cursor = conn.execute('''
                INSERT INTO audit_log 
                (timestamp, user_id, user_role, action, resource_type, resource_id,
                 ip_address, user_agent, status, pii_accessed, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.utcnow().isoformat(),
                user_id,
                user_role,
                action,
                resource_type,
                resource_id,
                ip_address,
                user_agent,
                status,
                1 if pii_accessed else 0,
                json.dumps(safe_metadata) if safe_metadata else None
            ))
            conn.commit()
            return cursor.lastrowid
    
    def _sanitize_metadata(self, metadata: Dict) -> Dict:
        """
        Sanitize metadata to prevent PII from being logged.
        Hashes or removes potentially sensitive fields.
        """
        safe = {}
        sensitive_keys = {'query', 'content', 'notes', 'text', 'message'}
        
        for key, value in metadata.items():
            if key.lower() in sensitive_keys:
                # Hash the value instead of storing it
                if isinstance(value, str):
                    safe[f'{key}_hash'] = self._hash_query(value)
                else:
                    safe[key] = '[REDACTED]'
            elif isinstance(value, dict):
                safe[key] = self._sanitize_metadata(value)
            else:
                safe[key] = value
        
        return safe
    
    def log_api_request(
        self,
        endpoint: str,
        method: str,
        auth_info: Dict = None,
        status_code: int = 200
    ) -> int:
        """
        Log an API request.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method
            auth_info: Authentication info dict
            status_code: HTTP response status code
        """
        status = 'success' if status_code < 400 else 'failure'
        
        return self.log(
            action='api_request',
            user_id=auth_info.get('user_id') if auth_info else None,
            user_role=auth_info.get('role') if auth_info else None,
            ip_address=auth_info.get('ip_address') if auth_info else None,
            user_agent=auth_info.get('user_agent') if auth_info else None,
            status=status,
            metadata={'endpoint': endpoint, 'method': method, 'status_code': status_code}
        )
    
    def log_query(
        self,
        query: str,
        auth_info: Dict = None,
        results_count: int = 0
    ) -> int:
        """
        Log a RAG query execution.
        
        Args:
            query: The query string (will be hashed)
            auth_info: Authentication info dict
            results_count: Number of results returned
        """
        return self.log(
            action='query',
            user_id=auth_info.get('user_id') if auth_info else None,
            user_role=auth_info.get('role') if auth_info else None,
            ip_address=auth_info.get('ip_address') if auth_info else None,
            resource_type='rag',
            status='success',
            metadata={'query_hash': self._hash_query(query), 'results_count': results_count}
        )
    
    def log_deal_access(
        self,
        deal_id: int,
        action: str,
        auth_info: Dict = None,
        status: str = 'success'
    ) -> int:
        """
        Log deal-related actions.
        
        Args:
            deal_id: The deal ID
            action: Action type (deal_create, deal_read, deal_update, deal_delete)
            auth_info: Authentication info dict
            status: Action status
        """
        return self.log(
            action=action,
            user_id=auth_info.get('user_id') if auth_info else None,
            user_role=auth_info.get('role') if auth_info else None,
            ip_address=auth_info.get('ip_address') if auth_info else None,
            resource_type='deal',
            resource_id=str(deal_id),
            status=status
        )
    
    def log_pii_access(
        self,
        action: str,
        source: str,
        auth_info: Dict = None,
        token_count: int = 0
    ) -> int:
        """
        Log PII-related actions.
        
        Args:
            action: PII action type (pii_sanitize, pii_detokenize, pii_delete)
            source: Source document identifier
            auth_info: Authentication info dict
            token_count: Number of tokens affected
        """
        return self.log(
            action=action,
            user_id=auth_info.get('user_id') if auth_info else None,
            user_role=auth_info.get('role') if auth_info else None,
            ip_address=auth_info.get('ip_address') if auth_info else None,
            resource_type='pii',
            resource_id=source,
            pii_accessed=(action == 'pii_detokenize'),
            status='success',
            metadata={'token_count': token_count}
        )
    
    def get_logs(
        self,
        user_id: str = None,
        action: str = None,
        resource_type: str = None,
        resource_id: str = None,
        start_date: str = None,
        end_date: str = None,
        pii_only: bool = False,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """
        Query audit logs with filters.
        
        Args:
            user_id: Filter by user
            action: Filter by action type
            resource_type: Filter by resource type
            resource_id: Filter by specific resource
            start_date: Start date (ISO format)
            end_date: End date (ISO format)
            pii_only: Only show PII access events
            limit: Maximum results
            offset: Results offset for pagination
            
        Returns:
            List of audit log entries
        """
        conditions = []
        params = []
        
        if user_id:
            conditions.append("user_id = ?")
            params.append(user_id)
        
        if action:
            conditions.append("action = ?")
            params.append(action)
        
        if resource_type:
            conditions.append("resource_type = ?")
            params.append(resource_type)
        
        if resource_id:
            conditions.append("resource_id = ?")
            params.append(resource_id)
        
        if start_date:
            conditions.append("timestamp >= ?")
            params.append(start_date)
        
        if end_date:
            conditions.append("timestamp <= ?")
            params.append(end_date)
        
        if pii_only:
            conditions.append("pii_accessed = 1")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        params.extend([limit, offset])
        
        with self._get_connection() as conn:
            cursor = conn.execute(f'''
                SELECT * FROM audit_log
                WHERE {where_clause}
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            ''', params)
            
            logs = []
            for row in cursor.fetchall():
                log_entry = dict(row)
                if log_entry.get('metadata'):
                    log_entry['metadata'] = json.loads(log_entry['metadata'])
                logs.append(log_entry)
            
            return logs
    
    def get_stats(self, days: int = 30) -> Dict:
        """
        Get audit statistics for the specified period.
        
        Args:
            days: Number of days to include
            
        Returns:
            Statistics dictionary
        """
        from datetime import timedelta
        start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        with self._get_connection() as conn:
            # Total events
            cursor = conn.execute(
                "SELECT COUNT(*) FROM audit_log WHERE timestamp >= ?",
                (start_date,)
            )
            total = cursor.fetchone()[0]
            
            # Events by action
            cursor = conn.execute('''
                SELECT action, COUNT(*) FROM audit_log
                WHERE timestamp >= ?
                GROUP BY action
            ''', (start_date,))
            by_action = {r[0]: r[1] for r in cursor.fetchall()}
            
            # Unique users
            cursor = conn.execute('''
                SELECT COUNT(DISTINCT user_id) FROM audit_log
                WHERE timestamp >= ? AND user_id IS NOT NULL
            ''', (start_date,))
            unique_users = cursor.fetchone()[0]
            
            # PII access count
            cursor = conn.execute(
                "SELECT COUNT(*) FROM audit_log WHERE timestamp >= ? AND pii_accessed = 1",
                (start_date,)
            )
            pii_accesses = cursor.fetchone()[0]
            
            # Failed auth attempts
            cursor = conn.execute('''
                SELECT COUNT(*) FROM audit_log
                WHERE timestamp >= ? AND action = 'auth_failure'
            ''', (start_date,))
            failed_auth = cursor.fetchone()[0]
            
            return {
                'period_days': days,
                'total_events': total,
                'unique_users': unique_users,
                'pii_accesses': pii_accesses,
                'failed_auth_attempts': failed_auth,
                'by_action': by_action
            }


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get or create the global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def audit_log(
    action: str,
    user_id: str = None,
    resource_type: str = None,
    resource_id: str = None,
    auth_info: Dict = None,
    status: str = 'success',
    pii_accessed: bool = False,
    **kwargs
) -> int:
    """
    Convenience function to log audit events using the global logger.
    
    Args:
        action: Action type
        user_id: User identifier (or extracted from auth_info)
        resource_type: Type of resource
        resource_id: Specific resource ID
        auth_info: Auth info dict (provides user_id, role, ip, user_agent)
        status: Action status
        pii_accessed: Whether PII was accessed
        **kwargs: Additional metadata
        
    Returns:
        The log entry ID
    """
    logger = get_audit_logger()
    
    # Extract info from auth_info if provided
    if auth_info:
        user_id = user_id or auth_info.get('user_id')
        user_role = auth_info.get('role')
        ip_address = auth_info.get('ip_address')
        user_agent = auth_info.get('user_agent')
    else:
        user_role = None
        ip_address = None
        user_agent = None
    
    return logger.log(
        action=action,
        user_id=user_id,
        user_role=user_role,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        user_agent=user_agent,
        status=status,
        pii_accessed=pii_accessed,
        metadata=kwargs if kwargs else None
    )
