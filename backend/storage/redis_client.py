"""
Redis client for real-time transcript buffer during live calls.
Stores last 2 minutes of transcript for context-aware queries.
"""
import os
import json
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
import redis
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
TRANSCRIPT_BUFFER_TTL = 3600  # 1 hour after call ends
TRANSCRIPT_WINDOW_SECONDS = 120  # 2 minutes sliding window


class RedisClient:
    """
    Redis client for managing real-time transcript buffers.
    
    Key patterns:
    - call:{call_id}:transcript_buffer - List of transcript chunks (last 2 min)
    - call:{call_id}:status - Current call status
    - call:{call_id}:metadata - Call metadata (deal_id, account, etc.)
    - active_calls:{user_id} - Set of active call IDs for user
    """
    
    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or REDIS_URL
        self._client: Optional[redis.Redis] = None
        self._connected = False
    
    @property
    def client(self) -> redis.Redis:
        """Lazy connection to Redis"""
        if self._client is None:
            try:
                self._client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5
                )
                # Test connection
                self._client.ping()
                self._connected = True
                logger.info(f"Connected to Redis at {self.redis_url}")
            except redis.ConnectionError as e:
                logger.warning(f"Redis not available: {e}. Using in-memory fallback.")
                self._connected = False
                # Use fake redis for local development
                self._client = InMemoryRedis()
        return self._client
    
    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        return self._connected
    
    # ---------------------
    # Transcript Buffer Operations
    # ---------------------
    
    def add_transcript_chunk(
        self,
        call_id: UUID,
        chunk: Dict[str, Any],
        max_chunks: int = 100
    ) -> None:
        """
        Add a transcript chunk to the buffer.
        Maintains a sliding window of recent transcript.
        """
        key = f"call:{call_id}:transcript_buffer"
        chunk_json = json.dumps(chunk, default=str)
        
        # Add to list (right side)
        self.client.rpush(key, chunk_json)
        
        # Trim to keep only last N chunks (approximate 2 min window)
        self.client.ltrim(key, -max_chunks, -1)
        
        # Set TTL
        self.client.expire(key, TRANSCRIPT_BUFFER_TTL)
    
    def get_transcript_buffer(
        self,
        call_id: UUID,
        last_n: int = None
    ) -> List[Dict[str, Any]]:
        """
        Get transcript chunks from buffer.
        Returns last N chunks or all if not specified.
        """
        key = f"call:{call_id}:transcript_buffer"
        
        if last_n:
            chunks = self.client.lrange(key, -last_n, -1)
        else:
            chunks = self.client.lrange(key, 0, -1)
        
        return [json.loads(chunk) for chunk in chunks]
    
    def get_recent_transcript_text(
        self,
        call_id: UUID,
        window_seconds: int = TRANSCRIPT_WINDOW_SECONDS
    ) -> str:
        """
        Get concatenated transcript text from last N seconds.
        Used for building context for RAG queries.
        """
        chunks = self.get_transcript_buffer(call_id)
        
        if not chunks:
            return ""
        
        # Get current time reference (last chunk end time)
        latest_time = max(chunk.get("end_time", 0) for chunk in chunks)
        cutoff_time = latest_time - window_seconds
        
        # Filter chunks within window
        recent_chunks = [
            chunk for chunk in chunks
            if chunk.get("start_time", 0) >= cutoff_time
        ]
        
        # Build transcript text with speaker labels
        lines = []
        for chunk in recent_chunks:
            speaker = chunk.get("speaker", "Unknown")
            text = chunk.get("text", "")
            lines.append(f"{speaker}: {text}")
        
        return "\n".join(lines)
    
    def clear_transcript_buffer(self, call_id: UUID) -> None:
        """Clear transcript buffer for a call"""
        key = f"call:{call_id}:transcript_buffer"
        self.client.delete(key)
    
    # ---------------------
    # Call Status Operations
    # ---------------------
    
    def set_call_status(self, call_id: UUID, status: str) -> None:
        """Set call status"""
        key = f"call:{call_id}:status"
        self.client.set(key, status)
        self.client.expire(key, TRANSCRIPT_BUFFER_TTL)
    
    def get_call_status(self, call_id: UUID) -> Optional[str]:
        """Get call status"""
        key = f"call:{call_id}:status"
        return self.client.get(key)
    
    # ---------------------
    # Call Metadata Operations
    # ---------------------
    
    def set_call_metadata(self, call_id: UUID, metadata: Dict[str, Any]) -> None:
        """Store call metadata"""
        key = f"call:{call_id}:metadata"
        self.client.hset(key, mapping={k: json.dumps(v, default=str) for k, v in metadata.items()})
        self.client.expire(key, TRANSCRIPT_BUFFER_TTL)
    
    def get_call_metadata(self, call_id: UUID) -> Dict[str, Any]:
        """Get call metadata"""
        key = f"call:{call_id}:metadata"
        data = self.client.hgetall(key)
        return {k: json.loads(v) for k, v in data.items()}
    
    # ---------------------
    # Active Calls Management
    # ---------------------
    
    def add_active_call(self, user_id: str, call_id: UUID) -> None:
        """Add call to user's active calls set"""
        key = f"active_calls:{user_id}"
        self.client.sadd(key, str(call_id))
        self.client.expire(key, TRANSCRIPT_BUFFER_TTL)
    
    def remove_active_call(self, user_id: str, call_id: UUID) -> None:
        """Remove call from user's active calls set"""
        key = f"active_calls:{user_id}"
        self.client.srem(key, str(call_id))
    
    def get_active_calls(self, user_id: str) -> List[str]:
        """Get user's active call IDs"""
        key = f"active_calls:{user_id}"
        return list(self.client.smembers(key))
    
    # ---------------------
    # Cleanup
    # ---------------------
    
    def cleanup_call(self, call_id: UUID) -> None:
        """Remove all Redis data for a call"""
        keys = [
            f"call:{call_id}:transcript_buffer",
            f"call:{call_id}:status",
            f"call:{call_id}:metadata"
        ]
        for key in keys:
            self.client.delete(key)


class InMemoryRedis:
    """
    In-memory fallback when Redis is not available.
    Useful for local development without Redis.
    """
    
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._lists: Dict[str, List] = {}
        self._sets: Dict[str, set] = {}
        self._hashes: Dict[str, Dict] = {}
    
    def ping(self) -> bool:
        return True
    
    def set(self, key: str, value: str) -> None:
        self._data[key] = value
    
    def get(self, key: str) -> Optional[str]:
        return self._data.get(key)
    
    def delete(self, key: str) -> None:
        self._data.pop(key, None)
        self._lists.pop(key, None)
        self._sets.pop(key, None)
        self._hashes.pop(key, None)
    
    def expire(self, key: str, ttl: int) -> None:
        pass  # No-op for in-memory
    
    def rpush(self, key: str, value: str) -> int:
        if key not in self._lists:
            self._lists[key] = []
        self._lists[key].append(value)
        return len(self._lists[key])
    
    def lrange(self, key: str, start: int, end: int) -> List[str]:
        if key not in self._lists:
            return []
        lst = self._lists[key]
        if end == -1:
            end = len(lst)
        else:
            end = end + 1
        if start < 0:
            start = max(0, len(lst) + start)
        return lst[start:end]
    
    def ltrim(self, key: str, start: int, end: int) -> None:
        if key not in self._lists:
            return
        lst = self._lists[key]
        if start < 0:
            start = max(0, len(lst) + start)
        if end == -1:
            end = len(lst)
        else:
            end = end + 1
        self._lists[key] = lst[start:end]
    
    def sadd(self, key: str, value: str) -> int:
        if key not in self._sets:
            self._sets[key] = set()
        self._sets[key].add(value)
        return 1
    
    def srem(self, key: str, value: str) -> int:
        if key in self._sets:
            self._sets[key].discard(value)
        return 1
    
    def smembers(self, key: str) -> set:
        return self._sets.get(key, set())
    
    def hset(self, key: str, mapping: Dict = None, **kwargs) -> None:
        if key not in self._hashes:
            self._hashes[key] = {}
        if mapping:
            self._hashes[key].update(mapping)
        self._hashes[key].update(kwargs)
    
    def hgetall(self, key: str) -> Dict:
        return self._hashes.get(key, {})


# Singleton instance
_redis_client: Optional[RedisClient] = None


def get_redis_client() -> RedisClient:
    """Get or create Redis client singleton"""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client
