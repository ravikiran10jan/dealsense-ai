"""
Feedback Storage for DealSense AI Learning Loop.

Stores user feedback on agent responses to enable continuous improvement.
Feedback is stored with:
- response_id: Unique identifier for the agent response
- agent_name: Which agent generated the response
- rating: thumbs_up, thumbs_down, or numeric 1-5
- comment: Optional user comment
- context: Original query and response for analysis
"""
import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from uuid import uuid4

logger = logging.getLogger(__name__)

FEEDBACK_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "feedback.json")


@dataclass
class FeedbackEntry:
    """A single feedback entry."""
    id: str
    response_id: str
    agent_name: str
    rating: str  # "thumbs_up", "thumbs_down", or "1"-"5"
    comment: Optional[str]
    query: str
    response_summary: str
    timestamp: str
    user_id: Optional[str] = None
    deal_id: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FeedbackStore:
    """
    Persistent storage for feedback entries.
    
    In production, this would be backed by a database.
    For demo purposes, uses JSON file storage.
    """
    
    def __init__(self, file_path: str = FEEDBACK_FILE):
        self.file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create feedback file if it doesn't exist."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump({"entries": [], "stats": {}}, f)
    
    def _load(self) -> Dict[str, Any]:
        """Load feedback data from file."""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {"entries": [], "stats": {}}
    
    def _save(self, data: Dict[str, Any]):
        """Save feedback data to file."""
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def add_feedback(
        self,
        response_id: str,
        agent_name: str,
        rating: str,
        query: str,
        response_summary: str,
        comment: Optional[str] = None,
        user_id: Optional[str] = None,
        deal_id: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> FeedbackEntry:
        """
        Add a new feedback entry.
        
        Args:
            response_id: Unique ID of the agent response being rated
            agent_name: Name of the agent that generated the response
            rating: "thumbs_up", "thumbs_down", or numeric "1"-"5"
            query: Original user query
            response_summary: Summary of the response (first 500 chars)
            comment: Optional user comment
            user_id: Optional user identifier
            deal_id: Optional deal context
            metadata: Additional context
            
        Returns:
            The created FeedbackEntry
        """
        entry = FeedbackEntry(
            id=str(uuid4()),
            response_id=response_id,
            agent_name=agent_name,
            rating=rating,
            comment=comment,
            query=query,
            response_summary=response_summary[:500] if response_summary else "",
            timestamp=datetime.utcnow().isoformat(),
            user_id=user_id,
            deal_id=deal_id,
            metadata=metadata,
        )
        
        data = self._load()
        data["entries"].append(entry.to_dict())
        
        # Update stats
        self._update_stats(data, agent_name, rating)
        
        self._save(data)
        logger.info(f"Feedback recorded: {entry.id} for {agent_name} - {rating}")
        
        return entry
    
    def _update_stats(self, data: Dict[str, Any], agent_name: str, rating: str):
        """Update aggregate statistics."""
        if "stats" not in data:
            data["stats"] = {}
        
        if agent_name not in data["stats"]:
            data["stats"][agent_name] = {
                "total": 0,
                "thumbs_up": 0,
                "thumbs_down": 0,
                "avg_rating": 0,
                "ratings_sum": 0,
                "ratings_count": 0,
            }
        
        stats = data["stats"][agent_name]
        stats["total"] += 1
        
        if rating == "thumbs_up":
            stats["thumbs_up"] += 1
        elif rating == "thumbs_down":
            stats["thumbs_down"] += 1
        elif rating.isdigit():
            stats["ratings_sum"] += int(rating)
            stats["ratings_count"] += 1
            if stats["ratings_count"] > 0:
                stats["avg_rating"] = stats["ratings_sum"] / stats["ratings_count"]
    
    def get_feedback(
        self,
        agent_name: Optional[str] = None,
        rating: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Get feedback entries with optional filtering.
        
        Args:
            agent_name: Filter by agent name
            rating: Filter by rating type
            limit: Maximum entries to return
            
        Returns:
            List of feedback entries
        """
        data = self._load()
        entries = data.get("entries", [])
        
        # Apply filters
        if agent_name:
            entries = [e for e in entries if e.get("agent_name") == agent_name]
        if rating:
            entries = [e for e in entries if e.get("rating") == rating]
        
        # Sort by timestamp descending and limit
        entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return entries[:limit]
    
    def get_stats(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get aggregate statistics.
        
        Args:
            agent_name: Optional agent to filter by
            
        Returns:
            Statistics dictionary
        """
        data = self._load()
        stats = data.get("stats", {})
        
        if agent_name:
            return stats.get(agent_name, {
                "total": 0,
                "thumbs_up": 0,
                "thumbs_down": 0,
                "avg_rating": 0,
            })
        
        # Aggregate all stats
        total_stats = {
            "total": 0,
            "thumbs_up": 0,
            "thumbs_down": 0,
            "by_agent": stats,
        }
        
        for agent_stats in stats.values():
            total_stats["total"] += agent_stats.get("total", 0)
            total_stats["thumbs_up"] += agent_stats.get("thumbs_up", 0)
            total_stats["thumbs_down"] += agent_stats.get("thumbs_down", 0)
        
        if total_stats["total"] > 0:
            total_stats["satisfaction_rate"] = round(
                total_stats["thumbs_up"] / total_stats["total"] * 100, 1
            )
        else:
            total_stats["satisfaction_rate"] = 0
        
        return total_stats
    
    def get_prompt_adjustments(self, agent_name: Optional[str] = None) -> str:
        """
        Extract formatting and behavioral rules from negative feedback comments.
        
        Scans recent thumbs_down feedback with comments and builds a set of
        prompt-level instructions that can be injected into LLM calls so the
        agents self-correct based on user preferences.
        
        Args:
            agent_name: Optional filter for a specific agent
            
        Returns:
            A string of adjustment instructions to inject into prompts,
            or empty string if no adjustments are needed.
        """
        data = self._load()
        entries = data.get("entries", [])
        
        # Filter to negative feedback with actionable comments
        negative = [
            e for e in entries
            if e.get("rating") == "thumbs_down"
            and e.get("comment")
            and len(e.get("comment", "").strip()) > 0
        ]
        
        if agent_name:
            negative = [e for e in negative if e.get("agent_name") == agent_name]
        
        if not negative:
            return ""
        
        # Sort by timestamp descending, take most recent 20
        negative.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        negative = negative[:20]
        
        # Build the adjustment instructions
        rules = []
        for entry in negative:
            comment = entry["comment"].strip()
            rules.append(f"- {comment}")
        
        if not rules:
            return ""
        
        adjustments = (
            "\n\nIMPORTANT — USER FEEDBACK ADJUSTMENTS:\n"
            "The following are corrections based on real user feedback. "
            "You MUST follow these instructions:\n"
            + "\n".join(rules)
            + "\n"
        )
        
        logger.info(
            f"Injecting {len(rules)} prompt adjustment(s) for agent={agent_name or 'all'}"
        )
        return adjustments

    def get_improvement_insights(self) -> Dict[str, Any]:
        """
        Analyze feedback to generate improvement insights.
        
        Returns insights like:
        - Agents with lowest satisfaction
        - Common complaint patterns
        - Suggested improvements
        """
        data = self._load()
        entries = data.get("entries", [])
        stats = data.get("stats", {})
        
        insights = {
            "agents_needing_improvement": [],
            "recent_negative_feedback": [],
            "improvement_suggestions": [],
            "feedback_trend": "stable",
        }
        
        # Find agents with low satisfaction
        for agent_name, agent_stats in stats.items():
            total = agent_stats.get("total", 0)
            if total >= 5:  # Need minimum feedback
                thumbs_up = agent_stats.get("thumbs_up", 0)
                satisfaction = thumbs_up / total if total > 0 else 0
                if satisfaction < 0.7:  # Less than 70% satisfaction
                    insights["agents_needing_improvement"].append({
                        "agent": agent_name,
                        "satisfaction_rate": round(satisfaction * 100, 1),
                        "total_feedback": total,
                    })
        
        # Get recent negative feedback with comments
        negative = [
            e for e in entries 
            if e.get("rating") == "thumbs_down" and e.get("comment")
        ]
        insights["recent_negative_feedback"] = negative[:5]
        
        # Generate suggestions based on patterns
        if insights["agents_needing_improvement"]:
            insights["improvement_suggestions"].append(
                "Review and retrain agents with low satisfaction scores"
            )
        
        if len(negative) > 10:
            insights["improvement_suggestions"].append(
                "High volume of negative feedback - consider prompt engineering review"
            )
        
        return insights


# Singleton instance
_feedback_store: Optional[FeedbackStore] = None


def get_feedback_store() -> FeedbackStore:
    """Get or create the feedback store singleton."""
    global _feedback_store
    if _feedback_store is None:
        _feedback_store = FeedbackStore()
    return _feedback_store
