"""
WebSocket Connection Manager for Live Call Assistant.
Manages WebSocket connections per call, handles message routing.
"""
import json
import logging
from typing import Dict, List, Optional, Set
from uuid import UUID
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for live calls.
    
    Features:
    - One connection per call (can be extended to multiple for observers)
    - Message broadcasting to call participants
    - Connection state tracking
    - Automatic cleanup on disconnect
    """
    
    def __init__(self):
        # Map of call_id -> WebSocket connections
        self._active_connections: Dict[str, List[WebSocket]] = {}
        # Map of call_id -> connection metadata
        self._connection_metadata: Dict[str, Dict] = {}
        # Set of all connected WebSockets
        self._all_connections: Set[WebSocket] = set()
    
    async def connect(
        self,
        websocket: WebSocket,
        call_id: UUID,
        metadata: Dict = None
    ) -> None:
        """
        Accept WebSocket connection and register for a call.
        
        Args:
            websocket: The WebSocket connection
            call_id: UUID of the call
            metadata: Optional metadata (user_id, deal_id, etc.)
        """
        await websocket.accept()
        
        call_id_str = str(call_id)
        
        if call_id_str not in self._active_connections:
            self._active_connections[call_id_str] = []
            self._connection_metadata[call_id_str] = metadata or {}
        
        self._active_connections[call_id_str].append(websocket)
        self._all_connections.add(websocket)
        
        logger.info(f"WebSocket connected for call {call_id}")
    
    def disconnect(self, websocket: WebSocket, call_id: UUID) -> None:
        """
        Remove a WebSocket connection from a call.
        
        Args:
            websocket: The WebSocket connection to remove
            call_id: UUID of the call
        """
        call_id_str = str(call_id)
        
        if call_id_str in self._active_connections:
            if websocket in self._active_connections[call_id_str]:
                self._active_connections[call_id_str].remove(websocket)
            
            # Cleanup if no more connections for this call
            if not self._active_connections[call_id_str]:
                del self._active_connections[call_id_str]
                self._connection_metadata.pop(call_id_str, None)
        
        self._all_connections.discard(websocket)
        logger.info(f"WebSocket disconnected from call {call_id}")
    
    async def send_personal_message(
        self,
        message: Dict,
        websocket: WebSocket
    ) -> None:
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def broadcast_to_call(
        self,
        message: Dict,
        call_id: UUID
    ) -> None:
        """
        Broadcast a message to all connections for a call.
        
        Args:
            message: The message to send (will be JSON serialized)
            call_id: UUID of the call
        """
        call_id_str = str(call_id)
        
        if call_id_str not in self._active_connections:
            logger.warning(f"No connections found for call {call_id}")
            return
        
        # Add timestamp if not present
        if "timestamp" not in message:
            message["timestamp"] = datetime.utcnow().isoformat()
        
        # Send to all connections
        disconnected = []
        for connection in self._active_connections[call_id_str]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn, call_id)
    
    async def send_transcript_chunk(
        self,
        call_id: UUID,
        speaker: str,
        text: str,
        start_time: float,
        end_time: float,
        is_final: bool = True
    ) -> None:
        """Send a transcript chunk to all call connections."""
        message = {
            "type": "transcript_chunk",
            "call_id": str(call_id),
            "speaker": speaker,
            "text": text,
            "start_time": start_time,
            "end_time": end_time,
            "is_final": is_final,
        }
        await self.broadcast_to_call(message, call_id)
    
    async def send_query_response(
        self,
        call_id: UUID,
        answer: str,
        sources: List[str] = None,
        confidence: float = 1.0
    ) -> None:
        """Send a RAG query response to all call connections."""
        message = {
            "type": "query_response",
            "call_id": str(call_id),
            "answer": answer,
            "sources": sources or [],
            "confidence": confidence,
        }
        await self.broadcast_to_call(message, call_id)
    
    async def send_status_update(
        self,
        call_id: UUID,
        status: str,
        message_text: str = None
    ) -> None:
        """Send a status update to all call connections."""
        message = {
            "type": "status_update",
            "call_id": str(call_id),
            "status": status,
            "message": message_text,
        }
        await self.broadcast_to_call(message, call_id)
    
    async def send_summary_ready(
        self,
        call_id: UUID,
        summary_id: UUID
    ) -> None:
        """Notify that call summary is ready."""
        message = {
            "type": "summary_ready",
            "call_id": str(call_id),
            "summary_id": str(summary_id),
        }
        await self.broadcast_to_call(message, call_id)
    
    async def send_error(
        self,
        call_id: UUID,
        error: str,
        details: str = None
    ) -> None:
        """Send an error message to all call connections."""
        message = {
            "type": "error",
            "call_id": str(call_id),
            "error": error,
            "details": details,
        }
        await self.broadcast_to_call(message, call_id)
    
    def get_connections_for_call(self, call_id: UUID) -> List[WebSocket]:
        """Get all WebSocket connections for a call."""
        call_id_str = str(call_id)
        return self._active_connections.get(call_id_str, [])
    
    def has_connections(self, call_id: UUID) -> bool:
        """Check if a call has any active connections."""
        call_id_str = str(call_id)
        return bool(self._active_connections.get(call_id_str))
    
    def get_active_calls(self) -> List[str]:
        """Get list of call IDs with active connections."""
        return list(self._active_connections.keys())
    
    def get_connection_count(self, call_id: UUID = None) -> int:
        """Get connection count for a specific call or all calls."""
        if call_id:
            call_id_str = str(call_id)
            return len(self._active_connections.get(call_id_str, []))
        return len(self._all_connections)
    
    def get_metadata(self, call_id: UUID) -> Dict:
        """Get metadata for a call's connections."""
        call_id_str = str(call_id)
        return self._connection_metadata.get(call_id_str, {})
    
    async def close_all_for_call(self, call_id: UUID) -> None:
        """Close all connections for a call."""
        call_id_str = str(call_id)
        
        if call_id_str in self._active_connections:
            for connection in self._active_connections[call_id_str][:]:
                try:
                    await connection.close()
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")
                self.disconnect(connection, call_id)


# Singleton instance
_connection_manager: Optional[ConnectionManager] = None


def get_connection_manager() -> ConnectionManager:
    """Get or create ConnectionManager singleton."""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager
