"""
Call Repository for CRUD operations on calls, transcripts, summaries, and action items.
Uses JSON file storage for simplicity (can be upgraded to PostgreSQL).
"""
import os
import json
import logging
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

from models.call import (
    Call,
    CallCreate,
    CallStatus,
    TranscriptChunk,
    TranscriptChunkCreate,
    CallSummary,
    CallSummaryCreate,
    ActionItem,
    ActionItemCreate,
    ActionItemUpdate,
    ActionItemStatus,
    ActionItemPriority,
)

logger = logging.getLogger(__name__)

# Storage paths
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CALLS_FILE = os.path.join(DATA_DIR, "calls.json")
TRANSCRIPTS_FILE = os.path.join(DATA_DIR, "transcripts.json")
SUMMARIES_FILE = os.path.join(DATA_DIR, "call_summaries.json")
ACTION_ITEMS_FILE = os.path.join(DATA_DIR, "action_items.json")


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for UUID, datetime, date"""
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)


def _ensure_data_dir():
    """Ensure data directory exists"""
    os.makedirs(DATA_DIR, exist_ok=True)


def _load_json(filepath: str) -> List[Dict]:
    """Load data from JSON file"""
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return []


def _save_json(filepath: str, data: List[Dict]) -> None:
    """Save data to JSON file"""
    _ensure_data_dir()
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, cls=JSONEncoder)


class CallRepository:
    """
    Repository for managing calls, transcripts, summaries, and action items.
    Uses JSON file storage with in-memory caching.
    """
    
    def __init__(self):
        self._calls_cache: Optional[List[Dict]] = None
        self._transcripts_cache: Optional[List[Dict]] = None
        self._summaries_cache: Optional[List[Dict]] = None
        self._action_items_cache: Optional[List[Dict]] = None
    
    # ---------------------
    # Call Operations
    # ---------------------
    
    def _get_calls(self) -> List[Dict]:
        """Get calls with caching"""
        if self._calls_cache is None:
            self._calls_cache = _load_json(CALLS_FILE)
        return self._calls_cache
    
    def _save_calls(self) -> None:
        """Save calls to file"""
        if self._calls_cache is not None:
            _save_json(CALLS_FILE, self._calls_cache)
    
    def create_call(self, call_create: CallCreate) -> Call:
        """Create a new call record"""
        calls = self._get_calls()
        
        call = Call(
            id=uuid4(),
            deal_id=call_create.deal_id,
            account_name=call_create.account_name,
            contact_name=call_create.contact_name,
            started_at=datetime.utcnow(),
            status=CallStatus.IN_PROGRESS,
        )
        
        calls.append(call.dict())
        self._calls_cache = calls
        self._save_calls()
        
        logger.info(f"Created call {call.id} for deal {call.deal_id}")
        return call
    
    def get_call(self, call_id: UUID) -> Optional[Call]:
        """Get a call by ID"""
        calls = self._get_calls()
        for call_data in calls:
            if str(call_data.get("id")) == str(call_id):
                return Call(**call_data)
        return None
    
    def get_calls_by_deal(self, deal_id: int) -> List[Call]:
        """Get all calls for a deal"""
        calls = self._get_calls()
        return [
            Call(**c) for c in calls
            if c.get("deal_id") == deal_id
        ]
    
    def update_call(self, call_id: UUID, updates: Dict[str, Any]) -> Optional[Call]:
        """Update a call record"""
        calls = self._get_calls()
        
        for i, call_data in enumerate(calls):
            if str(call_data.get("id")) == str(call_id):
                call_data.update(updates)
                call_data["updated_at"] = datetime.utcnow().isoformat()
                calls[i] = call_data
                self._calls_cache = calls
                self._save_calls()
                return Call(**call_data)
        
        return None
    
    def end_call(self, call_id: UUID) -> Optional[Call]:
        """Mark a call as ended and calculate duration"""
        call = self.get_call(call_id)
        if not call:
            return None
        
        ended_at = datetime.utcnow()
        duration_seconds = int((ended_at - call.started_at).total_seconds())
        
        return self.update_call(call_id, {
            "ended_at": ended_at,
            "duration_seconds": duration_seconds,
            "status": CallStatus.ENDED.value,
        })
    
    def set_call_summarized(self, call_id: UUID) -> Optional[Call]:
        """Mark a call as summarized"""
        return self.update_call(call_id, {
            "status": CallStatus.SUMMARIZED.value,
        })
    
    def delete_call(self, call_id: UUID) -> bool:
        """Delete a call and all related data"""
        calls = self._get_calls()
        original_length = len(calls)
        
        self._calls_cache = [c for c in calls if str(c.get("id")) != str(call_id)]
        
        if len(self._calls_cache) < original_length:
            self._save_calls()
            # Also delete related transcripts, summaries, action items
            self._delete_transcripts_for_call(call_id)
            self._delete_summary_for_call(call_id)
            self._delete_action_items_for_call(call_id)
            return True
        
        return False
    
    # ---------------------
    # Transcript Operations
    # ---------------------
    
    def _get_transcripts(self) -> List[Dict]:
        """Get transcripts with caching"""
        if self._transcripts_cache is None:
            self._transcripts_cache = _load_json(TRANSCRIPTS_FILE)
        return self._transcripts_cache
    
    def _save_transcripts(self) -> None:
        """Save transcripts to file"""
        if self._transcripts_cache is not None:
            _save_json(TRANSCRIPTS_FILE, self._transcripts_cache)
    
    def add_transcript_chunk(self, chunk_create: TranscriptChunkCreate) -> TranscriptChunk:
        """Add a transcript chunk"""
        transcripts = self._get_transcripts()
        
        chunk = TranscriptChunk(
            id=uuid4(),
            call_id=chunk_create.call_id,
            speaker=chunk_create.speaker,
            text=chunk_create.text,
            start_time=chunk_create.start_time,
            end_time=chunk_create.end_time,
            confidence=chunk_create.confidence,
            is_final=chunk_create.is_final,
        )
        
        transcripts.append(chunk.dict())
        self._transcripts_cache = transcripts
        self._save_transcripts()
        
        return chunk
    
    def get_transcript(
        self,
        call_id: UUID,
        start_time: float = None,
        end_time: float = None
    ) -> List[TranscriptChunk]:
        """Get transcript chunks for a call, optionally filtered by time"""
        transcripts = self._get_transcripts()
        
        chunks = [
            TranscriptChunk(**t) for t in transcripts
            if str(t.get("call_id")) == str(call_id)
        ]
        
        # Filter by time range if specified
        if start_time is not None:
            chunks = [c for c in chunks if c.start_time >= start_time]
        if end_time is not None:
            chunks = [c for c in chunks if c.end_time <= end_time]
        
        # Sort by start time
        chunks.sort(key=lambda c: c.start_time)
        
        return chunks
    
    def get_full_transcript_text(self, call_id: UUID) -> str:
        """Get full transcript as concatenated text with speaker labels"""
        chunks = self.get_transcript(call_id)
        
        lines = []
        for chunk in chunks:
            lines.append(f"{chunk.speaker}: {chunk.text}")
        
        return "\n".join(lines)
    
    def _delete_transcripts_for_call(self, call_id: UUID) -> None:
        """Delete all transcripts for a call"""
        transcripts = self._get_transcripts()
        self._transcripts_cache = [
            t for t in transcripts
            if str(t.get("call_id")) != str(call_id)
        ]
        self._save_transcripts()
    
    # ---------------------
    # Summary Operations
    # ---------------------
    
    def _get_summaries(self) -> List[Dict]:
        """Get summaries with caching"""
        if self._summaries_cache is None:
            self._summaries_cache = _load_json(SUMMARIES_FILE)
        return self._summaries_cache
    
    def _save_summaries(self) -> None:
        """Save summaries to file"""
        if self._summaries_cache is not None:
            _save_json(SUMMARIES_FILE, self._summaries_cache)
    
    def create_summary(self, summary_create: CallSummaryCreate) -> CallSummary:
        """Create a call summary"""
        summaries = self._get_summaries()
        
        # Check if summary already exists for this call
        existing = self.get_summary(summary_create.call_id)
        if existing:
            # Update existing summary
            return self.update_summary(summary_create.call_id, summary_create.dict())
        
        summary = CallSummary(
            id=uuid4(),
            call_id=summary_create.call_id,
            executive_summary=summary_create.executive_summary,
            key_points=summary_create.key_points,
            pain_points=summary_create.pain_points,
            objections=summary_create.objections,
            next_steps=summary_create.next_steps,
            deal_health_score=summary_create.deal_health_score,
            deal_health_reason=summary_create.deal_health_reason,
        )
        
        summaries.append(summary.dict())
        self._summaries_cache = summaries
        self._save_summaries()
        
        logger.info(f"Created summary for call {summary.call_id}")
        return summary
    
    def get_summary(self, call_id: UUID) -> Optional[CallSummary]:
        """Get summary for a call"""
        summaries = self._get_summaries()
        
        for summary_data in summaries:
            if str(summary_data.get("call_id")) == str(call_id):
                return CallSummary(**summary_data)
        
        return None
    
    def update_summary(self, call_id: UUID, updates: Dict[str, Any]) -> Optional[CallSummary]:
        """Update a call summary"""
        summaries = self._get_summaries()
        
        for i, summary_data in enumerate(summaries):
            if str(summary_data.get("call_id")) == str(call_id):
                # Don't overwrite id or call_id
                updates.pop("id", None)
                updates.pop("call_id", None)
                summary_data.update(updates)
                summaries[i] = summary_data
                self._summaries_cache = summaries
                self._save_summaries()
                return CallSummary(**summary_data)
        
        return None
    
    def _delete_summary_for_call(self, call_id: UUID) -> None:
        """Delete summary for a call"""
        summaries = self._get_summaries()
        self._summaries_cache = [
            s for s in summaries
            if str(s.get("call_id")) != str(call_id)
        ]
        self._save_summaries()
    
    # ---------------------
    # Action Item Operations
    # ---------------------
    
    def _get_action_items(self) -> List[Dict]:
        """Get action items with caching"""
        if self._action_items_cache is None:
            self._action_items_cache = _load_json(ACTION_ITEMS_FILE)
        return self._action_items_cache
    
    def _save_action_items(self) -> None:
        """Save action items to file"""
        if self._action_items_cache is not None:
            _save_json(ACTION_ITEMS_FILE, self._action_items_cache)
    
    def create_action_item(self, item_create: ActionItemCreate) -> ActionItem:
        """Create an action item"""
        items = self._get_action_items()
        
        # Default due date to +7 days if not specified
        due_date = item_create.due_date
        if due_date is None:
            due_date = (datetime.utcnow() + timedelta(days=7)).date()
        
        item = ActionItem(
            id=uuid4(),
            call_id=item_create.call_id,
            task=item_create.task,
            owner=item_create.owner,
            due_date=due_date,
            priority=item_create.priority,
            status=ActionItemStatus.PENDING,
        )
        
        items.append(item.dict())
        self._action_items_cache = items
        self._save_action_items()
        
        return item
    
    def get_action_items(self, call_id: UUID) -> List[ActionItem]:
        """Get action items for a call"""
        items = self._get_action_items()
        return [
            ActionItem(**i) for i in items
            if str(i.get("call_id")) == str(call_id)
        ]
    
    def get_action_item(self, item_id: UUID) -> Optional[ActionItem]:
        """Get a specific action item"""
        items = self._get_action_items()
        
        for item_data in items:
            if str(item_data.get("id")) == str(item_id):
                return ActionItem(**item_data)
        
        return None
    
    def update_action_item(
        self,
        item_id: UUID,
        updates: ActionItemUpdate
    ) -> Optional[ActionItem]:
        """Update an action item"""
        items = self._get_action_items()
        
        for i, item_data in enumerate(items):
            if str(item_data.get("id")) == str(item_id):
                # Apply updates
                update_dict = updates.dict(exclude_none=True)
                item_data.update(update_dict)
                item_data["updated_at"] = datetime.utcnow().isoformat()
                items[i] = item_data
                self._action_items_cache = items
                self._save_action_items()
                return ActionItem(**item_data)
        
        return None
    
    def delete_action_item(self, item_id: UUID) -> bool:
        """Delete an action item"""
        items = self._get_action_items()
        original_length = len(items)
        
        self._action_items_cache = [
            i for i in items
            if str(i.get("id")) != str(item_id)
        ]
        
        if len(self._action_items_cache) < original_length:
            self._save_action_items()
            return True
        
        return False
    
    def _delete_action_items_for_call(self, call_id: UUID) -> None:
        """Delete all action items for a call"""
        items = self._get_action_items()
        self._action_items_cache = [
            i for i in items
            if str(i.get("call_id")) != str(call_id)
        ]
        self._save_action_items()
    
    def create_action_items_batch(
        self,
        call_id: UUID,
        items: List[Dict[str, Any]]
    ) -> List[ActionItem]:
        """Create multiple action items at once"""
        created_items = []
        
        for item_data in items:
            item_create = ActionItemCreate(
                call_id=call_id,
                task=item_data.get("task", ""),
                owner=item_data.get("owner", "Seller"),
                due_date=item_data.get("due_date"),
                priority=ActionItemPriority(item_data.get("priority", "medium")),
            )
            created_items.append(self.create_action_item(item_create))
        
        return created_items
    
    # ---------------------
    # Cache Management
    # ---------------------
    
    def clear_cache(self) -> None:
        """Clear all caches to force reload from files"""
        self._calls_cache = None
        self._transcripts_cache = None
        self._summaries_cache = None
        self._action_items_cache = None


# Singleton instance
_call_repository: Optional[CallRepository] = None


def get_call_repository() -> CallRepository:
    """Get or create CallRepository singleton"""
    global _call_repository
    if _call_repository is None:
        _call_repository = CallRepository()
    return _call_repository
