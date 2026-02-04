"""
Transcription Service for Live Call Assistant.
Supports AssemblyAI real-time transcription with mock mode fallback.
"""
import os
import base64
import logging
import asyncio
from typing import Callable, Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Configuration
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY", "")
AZURE_SPEECH_KEY = os.getenv("AZURE_SPEECH_KEY", "")
AZURE_SPEECH_REGION = os.getenv("AZURE_SPEECH_REGION", "eastus")

# Use mock mode if no API keys configured
USE_MOCK_MODE = not ASSEMBLYAI_API_KEY and not AZURE_SPEECH_KEY


class TranscriptionService:
    """
    Transcription service that handles real-time speech-to-text.
    
    Features:
    - AssemblyAI real-time streaming (primary)
    - Azure Speech Services (fallback)
    - Mock mode for development/testing
    - Speaker diarization support
    - Callback-based chunk delivery
    """
    
    def __init__(self, use_mock: bool = USE_MOCK_MODE):
        self.use_mock = use_mock
        self._active_sessions: Dict[str, Any] = {}
        self._sequence_trackers: Dict[str, int] = {}
        self._time_trackers: Dict[str, float] = {}
        
        if self.use_mock:
            logger.info("Transcription service running in MOCK mode")
        elif ASSEMBLYAI_API_KEY:
            logger.info("Transcription service using AssemblyAI")
        else:
            logger.info("Transcription service using Azure Speech")
    
    async def process_audio_chunk(
        self,
        call_id: UUID,
        audio_data: str,
        sequence: int,
        callback: Callable
    ) -> None:
        """
        Process an audio chunk and call back with transcript chunks.
        
        Args:
            call_id: UUID of the call
            audio_data: Base64 encoded audio data
            sequence: Chunk sequence number
            callback: Async function to call with transcript chunks
                      signature: (call_id, speaker, text, start_time, end_time, is_final)
        """
        call_id_str = str(call_id)
        
        # Initialize tracking for new calls
        if call_id_str not in self._time_trackers:
            self._time_trackers[call_id_str] = 0.0
            self._sequence_trackers[call_id_str] = 0
        
        if self.use_mock:
            await self._process_mock(call_id, callback)
        elif ASSEMBLYAI_API_KEY:
            await self._process_assemblyai(call_id, audio_data, sequence, callback)
        else:
            await self._process_azure(call_id, audio_data, sequence, callback)
    
    async def _process_mock(
        self,
        call_id: UUID,
        callback: Callable
    ) -> None:
        """
        Mock transcription for development.
        Generates realistic-looking transcript chunks.
        """
        call_id_str = str(call_id)
        
        # Simulate some processing delay
        await asyncio.sleep(0.1)
        
        # Get current time
        current_time = self._time_trackers.get(call_id_str, 0.0)
        
        # Mock transcripts that simulate a sales call
        mock_phrases = [
            ("Customer", "So tell me more about your trade finance solution."),
            ("Seller", "Our platform provides end-to-end trade finance automation."),
            ("Customer", "What about integration with existing systems?"),
            ("Seller", "We support APIs for all major banking systems."),
            ("Customer", "How long does implementation typically take?"),
            ("Seller", "Usually 12 to 18 months depending on complexity."),
            ("Customer", "What was the team size for your last major project?"),
            ("Seller", "For CBA we had a 45-person team over 18 months."),
            ("Customer", "That sounds reasonable. What about data privacy?"),
            ("Seller", "We follow strict regional data compliance requirements."),
        ]
        
        # Pick a phrase based on sequence
        seq = self._sequence_trackers.get(call_id_str, 0)
        if seq < len(mock_phrases):
            speaker, text = mock_phrases[seq]
            
            # Calculate timing
            duration = len(text.split()) / 2.5  # ~150 words per minute
            start_time = current_time
            end_time = current_time + duration
            
            # Update trackers
            self._time_trackers[call_id_str] = end_time + 0.5  # Small gap
            self._sequence_trackers[call_id_str] = seq + 1
            
            # Call back with transcript
            await callback(
                call_id=call_id,
                speaker=speaker,
                text=text,
                start_time=start_time,
                end_time=end_time,
                is_final=True
            )
    
    async def _process_assemblyai(
        self,
        call_id: UUID,
        audio_data: str,
        sequence: int,
        callback: Callable
    ) -> None:
        """
        Process audio using AssemblyAI real-time transcription.
        
        Note: Full implementation requires AssemblyAI WebSocket connection.
        This is a simplified version that uses the batch API.
        """
        try:
            import assemblyai as aai
            
            aai.settings.api_key = ASSEMBLYAI_API_KEY
            
            # Decode audio
            audio_bytes = base64.b64decode(audio_data)
            
            # For real-time, you would use aai.RealtimeTranscriber
            # This simplified version uses the batch API
            # In production, maintain a WebSocket connection per call
            
            # Store audio chunks and process in batches
            # This is a placeholder - real implementation needs streaming
            
            call_id_str = str(call_id)
            if call_id_str not in self._active_sessions:
                self._active_sessions[call_id_str] = {
                    "audio_buffer": bytearray(),
                    "last_process_time": datetime.utcnow(),
                }
            
            # Add to buffer
            self._active_sessions[call_id_str]["audio_buffer"].extend(audio_bytes)
            
            # Process every 5 seconds of audio (approximate)
            buffer_size = len(self._active_sessions[call_id_str]["audio_buffer"])
            if buffer_size > 80000:  # ~5 seconds at 16kHz
                await self._transcribe_buffer_assemblyai(call_id, callback)
            
        except ImportError:
            logger.warning("AssemblyAI SDK not installed, falling back to mock")
            await self._process_mock(call_id, callback)
        except Exception as e:
            logger.error(f"AssemblyAI error: {e}")
            raise
    
    async def _transcribe_buffer_assemblyai(
        self,
        call_id: UUID,
        callback: Callable
    ) -> None:
        """Transcribe buffered audio using AssemblyAI"""
        import assemblyai as aai
        import tempfile
        
        call_id_str = str(call_id)
        session = self._active_sessions.get(call_id_str)
        
        if not session or not session["audio_buffer"]:
            return
        
        # Write buffer to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(bytes(session["audio_buffer"]))
            temp_path = f.name
        
        try:
            # Transcribe
            transcriber = aai.Transcriber()
            config = aai.TranscriptionConfig(
                speaker_labels=True,
            )
            transcript = transcriber.transcribe(temp_path, config)
            
            if transcript.status == aai.TranscriptStatus.completed:
                current_time = self._time_trackers.get(call_id_str, 0.0)
                
                # Process utterances
                for utterance in transcript.utterances or []:
                    speaker = f"Speaker {utterance.speaker}"
                    text = utterance.text
                    start_time = current_time + (utterance.start / 1000)
                    end_time = current_time + (utterance.end / 1000)
                    
                    await callback(
                        call_id=call_id,
                        speaker=speaker,
                        text=text,
                        start_time=start_time,
                        end_time=end_time,
                        is_final=True
                    )
                
                # Update time tracker
                if transcript.utterances:
                    last_utterance = transcript.utterances[-1]
                    self._time_trackers[call_id_str] = current_time + (last_utterance.end / 1000)
            
            # Clear buffer
            session["audio_buffer"] = bytearray()
            
        finally:
            # Clean up temp file
            import os
            try:
                os.unlink(temp_path)
            except:
                pass
    
    async def _process_azure(
        self,
        call_id: UUID,
        audio_data: str,
        sequence: int,
        callback: Callable
    ) -> None:
        """
        Process audio using Azure Speech Services.
        
        Note: Full implementation requires Azure Speech SDK.
        This is a simplified placeholder.
        """
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            # Decode audio
            audio_bytes = base64.b64decode(audio_data)
            
            # Configure Azure Speech
            speech_config = speechsdk.SpeechConfig(
                subscription=AZURE_SPEECH_KEY,
                region=AZURE_SPEECH_REGION
            )
            
            # This is a simplified version
            # Full implementation would use continuous recognition
            # with push audio stream
            
            # For now, fall back to mock
            logger.warning("Azure Speech full implementation pending, using mock")
            await self._process_mock(call_id, callback)
            
        except ImportError:
            logger.warning("Azure Speech SDK not installed, falling back to mock")
            await self._process_mock(call_id, callback)
        except Exception as e:
            logger.error(f"Azure Speech error: {e}")
            raise
    
    def start_session(self, call_id: UUID) -> None:
        """Start a transcription session for a call"""
        call_id_str = str(call_id)
        self._active_sessions[call_id_str] = {
            "started_at": datetime.utcnow(),
            "audio_buffer": bytearray(),
        }
        self._time_trackers[call_id_str] = 0.0
        self._sequence_trackers[call_id_str] = 0
        logger.info(f"Started transcription session for call {call_id}")
    
    def end_session(self, call_id: UUID) -> None:
        """End a transcription session for a call"""
        call_id_str = str(call_id)
        self._active_sessions.pop(call_id_str, None)
        self._time_trackers.pop(call_id_str, None)
        self._sequence_trackers.pop(call_id_str, None)
        logger.info(f"Ended transcription session for call {call_id}")
    
    def is_session_active(self, call_id: UUID) -> bool:
        """Check if a session is active"""
        return str(call_id) in self._active_sessions


# Singleton instance
_transcription_service: Optional[TranscriptionService] = None


def get_transcription_service() -> TranscriptionService:
    """Get or create TranscriptionService singleton"""
    global _transcription_service
    if _transcription_service is None:
        _transcription_service = TranscriptionService()
    return _transcription_service
