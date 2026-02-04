"""
Pydantic models for Live Call Assistant
Includes Call, Transcript, Summary, and ActionItem models
"""
from datetime import datetime, date
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class CallStatus(str, Enum):
    """Status of a call"""
    IN_PROGRESS = "in_progress"
    ENDED = "ended"
    SUMMARIZED = "summarized"
    ERROR = "error"


class ActionItemStatus(str, Enum):
    """Status of an action item"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class ActionItemPriority(str, Enum):
    """Priority level of an action item"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ---------------------
# Call Models
# ---------------------

class CallCreate(BaseModel):
    """Request model for creating a new call"""
    deal_id: int
    account_name: str
    contact_name: Optional[str] = None


class Call(BaseModel):
    """Full call record"""
    id: UUID = Field(default_factory=uuid4)
    deal_id: int
    account_name: str
    contact_name: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    status: CallStatus = CallStatus.IN_PROGRESS
    recording_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }


# ---------------------
# Transcript Models
# ---------------------

class TranscriptChunkCreate(BaseModel):
    """Request model for creating a transcript chunk"""
    call_id: UUID
    speaker: str = "Speaker 1"
    text: str
    start_time: float  # Seconds from call start
    end_time: float
    confidence: float = 1.0
    is_final: bool = True


class TranscriptChunk(BaseModel):
    """Full transcript chunk record"""
    id: UUID = Field(default_factory=uuid4)
    call_id: UUID
    speaker: str = "Speaker 1"
    text: str
    start_time: float
    end_time: float
    confidence: float = 1.0
    is_final: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }


# ---------------------
# Summary Models
# ---------------------

class PainPoint(BaseModel):
    """Customer pain point identified in the call"""
    description: str
    severity: str = "medium"  # low, medium, high
    context: Optional[str] = None


class Objection(BaseModel):
    """Customer objection identified in the call"""
    description: str
    category: str = "general"  # pricing, timeline, features, competition, general
    response_suggested: Optional[str] = None


class CallSummaryCreate(BaseModel):
    """Request model for creating a call summary"""
    call_id: UUID
    executive_summary: str
    key_points: List[str]
    pain_points: List[PainPoint] = []
    objections: List[Objection] = []
    next_steps: str
    deal_health_score: int = Field(ge=1, le=10)
    deal_health_reason: str


class CallSummary(BaseModel):
    """Full call summary record"""
    id: UUID = Field(default_factory=uuid4)
    call_id: UUID
    executive_summary: str
    key_points: List[str]
    pain_points: List[PainPoint] = []
    objections: List[Objection] = []
    next_steps: str
    deal_health_score: int = Field(ge=1, le=10)
    deal_health_reason: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }


# ---------------------
# Action Item Models
# ---------------------

class ActionItemCreate(BaseModel):
    """Request model for creating an action item"""
    call_id: UUID
    task: str
    owner: str = "Seller"
    due_date: Optional[date] = None
    priority: ActionItemPriority = ActionItemPriority.MEDIUM


class ActionItemUpdate(BaseModel):
    """Request model for updating an action item"""
    task: Optional[str] = None
    owner: Optional[str] = None
    due_date: Optional[date] = None
    priority: Optional[ActionItemPriority] = None
    status: Optional[ActionItemStatus] = None


class ActionItem(BaseModel):
    """Full action item record"""
    id: UUID = Field(default_factory=uuid4)
    call_id: UUID
    task: str
    owner: str = "Seller"
    due_date: Optional[date] = None
    priority: ActionItemPriority = ActionItemPriority.MEDIUM
    status: ActionItemStatus = ActionItemStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }


# ---------------------
# WebSocket Message Models
# ---------------------

class WSMessageType(str, Enum):
    """WebSocket message types"""
    # Client -> Server
    START_CALL = "start_call"
    AUDIO_CHUNK = "audio_chunk"
    PUSH_TO_TALK_QUERY = "push_to_talk_query"
    END_CALL = "end_call"
    
    # Server -> Client
    TRANSCRIPT_CHUNK = "transcript_chunk"
    QUERY_RESPONSE = "query_response"
    STATUS_UPDATE = "status_update"
    SUMMARY_READY = "summary_ready"
    ERROR = "error"


class WSMessage(BaseModel):
    """Base WebSocket message"""
    type: WSMessageType
    call_id: Optional[UUID] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }


class WSStartCallMessage(WSMessage):
    """Message to start a call"""
    type: WSMessageType = WSMessageType.START_CALL
    deal_id: int
    account_name: str
    contact_name: Optional[str] = None


class WSAudioChunkMessage(WSMessage):
    """Message containing audio chunk"""
    type: WSMessageType = WSMessageType.AUDIO_CHUNK
    audio_data: str  # Base64 encoded
    chunk_sequence: int


class WSPushToTalkQueryMessage(WSMessage):
    """Message for push-to-talk query"""
    type: WSMessageType = WSMessageType.PUSH_TO_TALK_QUERY
    query: str
    deal_id: Optional[int] = None


class WSEndCallMessage(WSMessage):
    """Message to end a call"""
    type: WSMessageType = WSMessageType.END_CALL


class WSTranscriptChunkMessage(WSMessage):
    """Server message with transcript chunk"""
    type: WSMessageType = WSMessageType.TRANSCRIPT_CHUNK
    speaker: str
    text: str
    start_time: float
    end_time: float
    is_final: bool = True


class WSQueryResponseMessage(WSMessage):
    """Server message with query response"""
    type: WSMessageType = WSMessageType.QUERY_RESPONSE
    answer: str
    sources: List[str] = []
    confidence: float = 1.0


class WSStatusUpdateMessage(WSMessage):
    """Server message with status update"""
    type: WSMessageType = WSMessageType.STATUS_UPDATE
    status: str  # "connecting", "transcribing", "error", "ended"
    message: Optional[str] = None


class WSSummaryReadyMessage(WSMessage):
    """Server message indicating summary is ready"""
    type: WSMessageType = WSMessageType.SUMMARY_READY
    summary_id: UUID


class WSErrorMessage(WSMessage):
    """Server message with error"""
    type: WSMessageType = WSMessageType.ERROR
    error: str
    details: Optional[str] = None
