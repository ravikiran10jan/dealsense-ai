"""
Live Call Handler for processing WebSocket messages during calls.
Handles start, audio chunks, queries, and end call events.
"""
import json
import logging
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from fastapi import WebSocket

from models.call import (
    Call,
    CallCreate,
    CallStatus,
    TranscriptChunkCreate,
    WSMessageType,
)
from storage import get_redis_client, get_call_repository
from websocket.connection_manager import get_connection_manager

logger = logging.getLogger(__name__)


class LiveCallHandler:
    """
    Handles WebSocket message processing for live calls.
    
    Responsibilities:
    - Process incoming WebSocket messages
    - Route to appropriate handlers
    - Coordinate between Redis, Repository, and Transcription services
    - Send responses back to clients
    """
    
    def __init__(self):
        self.redis = get_redis_client()
        self.repository = get_call_repository()
        self.connection_manager = get_connection_manager()
        self._transcription_service = None  # Lazy load
    
    @property
    def transcription_service(self):
        """Lazy load transcription service"""
        if self._transcription_service is None:
            from transcription import get_transcription_service
            self._transcription_service = get_transcription_service()
        return self._transcription_service
    
    async def handle_message(
        self,
        websocket: WebSocket,
        call_id: UUID,
        message: Dict[str, Any]
    ) -> None:
        """
        Main message handler - routes to specific handlers based on message type.
        
        Args:
            websocket: The WebSocket connection
            call_id: UUID of the call
            message: The parsed message dictionary
        """
        message_type = message.get("type")
        
        try:
            if message_type == WSMessageType.START_CALL.value:
                await self._handle_start_call(websocket, call_id, message)
            
            elif message_type == WSMessageType.AUDIO_CHUNK.value:
                await self._handle_audio_chunk(call_id, message)
            
            elif message_type == WSMessageType.PUSH_TO_TALK_QUERY.value:
                await self._handle_push_to_talk_query(call_id, message)
            
            elif message_type == WSMessageType.END_CALL.value:
                await self._handle_end_call(call_id, message)
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
                await self.connection_manager.send_error(
                    call_id,
                    "Unknown message type",
                    f"Received unknown type: {message_type}"
                )
        
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            await self.connection_manager.send_error(
                call_id,
                "Message processing error",
                str(e)
            )
    
    async def _handle_start_call(
        self,
        websocket: WebSocket,
        call_id: UUID,
        message: Dict[str, Any]
    ) -> None:
        """
        Handle start_call message - initialize call record and services.
        """
        deal_id = message.get("deal_id")
        account_name = message.get("account_name", "Unknown")
        contact_name = message.get("contact_name")
        
        logger.info(f"Starting call {call_id} for deal {deal_id}")
        
        # Check if call already exists
        existing_call = self.repository.get_call(call_id)
        if existing_call and existing_call.status == CallStatus.IN_PROGRESS:
            # Call already in progress, just reconnecting
            await self.connection_manager.send_status_update(
                call_id,
                "connected",
                "Reconnected to existing call"
            )
            return
        
        # Create call record
        call_create = CallCreate(
            deal_id=deal_id,
            account_name=account_name,
            contact_name=contact_name,
        )
        
        # Override the auto-generated ID with the provided one
        call = self.repository.create_call(call_create)
        
        # Store call metadata in Redis for quick access
        self.redis.set_call_metadata(call_id, {
            "deal_id": deal_id,
            "account_name": account_name,
            "contact_name": contact_name,
            "started_at": datetime.utcnow().isoformat(),
        })
        self.redis.set_call_status(call_id, CallStatus.IN_PROGRESS.value)
        
        # Notify client
        await self.connection_manager.send_status_update(
            call_id,
            "connected",
            "Call started. Ready to receive audio."
        )
        
        logger.info(f"Call {call_id} started successfully")
    
    async def _handle_audio_chunk(
        self,
        call_id: UUID,
        message: Dict[str, Any]
    ) -> None:
        """
        Handle audio_chunk message - forward to transcription service.
        """
        audio_data = message.get("audio_data")  # Base64 encoded
        chunk_sequence = message.get("chunk_sequence", 0)
        
        if not audio_data:
            logger.warning(f"Empty audio chunk received for call {call_id}")
            return
        
        # Forward to transcription service
        # The transcription service will call back with transcript chunks
        try:
            await self.transcription_service.process_audio_chunk(
                call_id=call_id,
                audio_data=audio_data,
                sequence=chunk_sequence,
                callback=self._on_transcript_chunk
            )
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            # Don't fail the whole call, just log the error
    
    async def _on_transcript_chunk(
        self,
        call_id: UUID,
        speaker: str,
        text: str,
        start_time: float,
        end_time: float,
        is_final: bool
    ) -> None:
        """
        Callback from transcription service when a transcript chunk is ready.
        """
        # Store in Redis buffer for real-time context
        chunk_data = {
            "speaker": speaker,
            "text": text,
            "start_time": start_time,
            "end_time": end_time,
            "is_final": is_final,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self.redis.add_transcript_chunk(call_id, chunk_data)
        
        # Store final chunks in repository for permanent storage
        if is_final:
            chunk_create = TranscriptChunkCreate(
                call_id=call_id,
                speaker=speaker,
                text=text,
                start_time=start_time,
                end_time=end_time,
                is_final=True,
            )
            self.repository.add_transcript_chunk(chunk_create)
        
        # Send to frontend
        await self.connection_manager.send_transcript_chunk(
            call_id=call_id,
            speaker=speaker,
            text=text,
            start_time=start_time,
            end_time=end_time,
            is_final=is_final,
        )
    
    async def _handle_push_to_talk_query(
        self,
        call_id: UUID,
        message: Dict[str, Any]
    ) -> None:
        """
        Handle push_to_talk_query - process RAG query with call context.
        """
        query = message.get("query", "")
        deal_id = message.get("deal_id")
        
        if not query:
            await self.connection_manager.send_error(
                call_id,
                "Empty query",
                "Please provide a question"
            )
            return
        
        logger.info(f"Processing push-to-talk query for call {call_id}: {query[:50]}...")
        
        # Get recent transcript context from Redis
        recent_transcript = self.redis.get_recent_transcript_text(call_id)
        
        # Get call metadata
        metadata = self.redis.get_call_metadata(call_id)
        account_name = metadata.get("account_name", "Unknown")
        
        # Build context-aware query
        try:
            from orchestration.hybrid_answer import answer_query_with_context
            
            result = answer_query_with_context(
                query=query,
                call_context={
                    "recent_transcript": recent_transcript,
                    "account_name": account_name,
                    "deal_id": deal_id,
                }
            )
            
            # Send response
            await self.connection_manager.send_query_response(
                call_id=call_id,
                answer=result.get("answer", "No answer available"),
                sources=result.get("sources", []),
                confidence=result.get("confidence", 1.0),
            )
            
        except ImportError:
            # Fallback to regular query if context-aware not available
            from orchestration.hybrid_answer import answer_query
            
            # Prepend context to query
            enhanced_query = f"In the context of a call with {account_name}: {query}"
            if recent_transcript:
                enhanced_query = f"Recent conversation:\n{recent_transcript}\n\nQuestion: {query}"
            
            result = answer_query(enhanced_query)
            
            await self.connection_manager.send_query_response(
                call_id=call_id,
                answer=result.get("answer", "No answer available"),
                sources=result.get("sources", []),
            )
        
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            await self.connection_manager.send_error(
                call_id,
                "Query processing error",
                str(e)
            )
    
    async def _handle_end_call(
        self,
        call_id: UUID,
        message: Dict[str, Any]
    ) -> None:
        """
        Handle end_call message - finalize call and trigger summary generation.
        """
        logger.info(f"Ending call {call_id}")
        
        # Update call record
        call = self.repository.end_call(call_id)
        if not call:
            logger.warning(f"Call {call_id} not found in repository")
        
        # Update Redis status
        self.redis.set_call_status(call_id, CallStatus.ENDED.value)
        
        # Notify client that call is ending
        await self.connection_manager.send_status_update(
            call_id,
            "ended",
            "Call ended. Generating summary..."
        )
        
        # Trigger summary generation asynchronously
        try:
            await self._generate_summary(call_id)
        except Exception as e:
            logger.error(f"Error generating summary: {e}", exc_info=True)
            await self.connection_manager.send_error(
                call_id,
                "Summary generation failed",
                str(e)
            )
    
    async def _generate_summary(self, call_id: UUID) -> None:
        """
        Generate call summary using LLM.
        """
        # Get full transcript
        transcript_text = self.repository.get_full_transcript_text(call_id)
        
        if not transcript_text:
            logger.warning(f"No transcript found for call {call_id}")
            await self.connection_manager.send_error(
                call_id,
                "No transcript",
                "Cannot generate summary without transcript"
            )
            return
        
        # Get call metadata
        call = self.repository.get_call(call_id)
        metadata = self.redis.get_call_metadata(call_id)
        
        # Generate summary using summarization service
        try:
            from summarization import generate_call_summary
            
            summary_data = await generate_call_summary(
                transcript=transcript_text,
                account_name=metadata.get("account_name", call.account_name if call else "Unknown"),
                deal_id=metadata.get("deal_id", call.deal_id if call else None),
                duration_minutes=(call.duration_seconds // 60) if call and call.duration_seconds else 0,
            )
            
            # Store summary
            from models.call import CallSummaryCreate, ActionItemPriority
            
            summary_create = CallSummaryCreate(
                call_id=call_id,
                executive_summary=summary_data.get("executive_summary", ""),
                key_points=summary_data.get("key_points", []),
                pain_points=summary_data.get("pain_points", []),
                objections=summary_data.get("objections", []),
                next_steps=summary_data.get("next_steps", ""),
                deal_health_score=summary_data.get("deal_health_score", 5),
                deal_health_reason=summary_data.get("deal_health_reason", ""),
            )
            
            summary = self.repository.create_summary(summary_create)
            
            # Store action items
            action_items = summary_data.get("action_items", [])
            if action_items:
                self.repository.create_action_items_batch(call_id, action_items)
            
            # Mark call as summarized
            self.repository.set_call_summarized(call_id)
            
            # Notify client
            await self.connection_manager.send_summary_ready(call_id, summary.id)
            
            logger.info(f"Summary generated for call {call_id}")
            
        except ImportError as e:
            logger.error(f"Summarization module not available: {e}")
            # Create a placeholder summary
            await self.connection_manager.send_status_update(
                call_id,
                "summary_pending",
                "Summary generation module not available"
            )
        
        except Exception as e:
            logger.error(f"Summary generation error: {e}", exc_info=True)
            raise
    
    async def add_mock_transcript_chunk(
        self,
        call_id: UUID,
        speaker: str,
        text: str,
        start_time: float = None,
        end_time: float = None
    ) -> None:
        """
        Add a mock transcript chunk - useful for testing without real audio.
        """
        # Get current time reference from existing chunks
        existing_chunks = self.redis.get_transcript_buffer(call_id)
        
        if existing_chunks:
            last_end_time = max(c.get("end_time", 0) for c in existing_chunks)
        else:
            last_end_time = 0
        
        if start_time is None:
            start_time = last_end_time + 0.5
        if end_time is None:
            # Estimate based on text length (roughly 150 words per minute)
            words = len(text.split())
            duration = max(1.0, words / 2.5)  # At least 1 second
            end_time = start_time + duration
        
        await self._on_transcript_chunk(
            call_id=call_id,
            speaker=speaker,
            text=text,
            start_time=start_time,
            end_time=end_time,
            is_final=True,
        )


# Singleton instance
_live_call_handler: Optional[LiveCallHandler] = None


def get_live_call_handler() -> LiveCallHandler:
    """Get or create LiveCallHandler singleton."""
    global _live_call_handler
    if _live_call_handler is None:
        _live_call_handler = LiveCallHandler()
    return _live_call_handler
