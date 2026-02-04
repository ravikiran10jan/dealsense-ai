"""
Action Items Extractor for Live Call Assistant.
Uses LLM to extract actionable tasks from call transcripts.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from .prompt_templates import ACTION_ITEMS_PROMPT_TEMPLATE

load_dotenv()

logger = logging.getLogger(__name__)

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)


async def extract_action_items(
    transcript: str,
    account_name: str = "Customer",
    seller_name: str = "Seller",
    call_date: str = None
) -> List[Dict[str, Any]]:
    """
    Extract action items from a call transcript.
    
    Args:
        transcript: Full call transcript with speaker labels
        account_name: Customer account name
        seller_name: Name of the seller
        call_date: Date of the call (ISO format)
    
    Returns:
        List of action items, each containing:
        - task: Task description
        - owner: Who is responsible
        - due_date: When it's due (YYYY-MM-DD or None)
        - priority: high/medium/low
    """
    if not transcript or len(transcript.strip()) < 50:
        logger.warning("Transcript too short for action items extraction")
        return _generate_default_action_item(account_name)
    
    # Use current date if not provided
    if not call_date:
        call_date = datetime.utcnow().strftime("%Y-%m-%d")
    
    # Build the prompt
    prompt = ACTION_ITEMS_PROMPT_TEMPLATE.format(
        account_name=account_name,
        seller_name=seller_name,
        call_date=call_date,
        transcript=transcript[:10000],  # Limit transcript length
    )
    
    try:
        # Generate action items
        response = llm.invoke(prompt)
        response_text = response.content.strip()
        
        # Parse JSON response
        action_items = _parse_action_items_response(response_text, call_date)
        
        # Ensure we have at least one action item
        if not action_items:
            action_items = _generate_default_action_item(account_name)
        
        # Limit to 10 action items
        action_items = action_items[:10]
        
        logger.info(f"Extracted {len(action_items)} action items")
        return action_items
        
    except Exception as e:
        logger.error(f"Error extracting action items: {e}", exc_info=True)
        return _generate_default_action_item(account_name)


def _parse_action_items_response(response_text: str, call_date: str) -> List[Dict[str, Any]]:
    """
    Parse LLM response into action items list.
    Handles JSON extraction from potentially noisy output.
    """
    try:
        # Handle markdown code blocks
        if "```json" in response_text:
            json_start = response_text.index("```json") + 7
            json_end = response_text.index("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.index("```") + 3
            json_end = response_text.index("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        
        # Find JSON object bounds
        if "{" in response_text:
            start = response_text.index("{")
            depth = 0
            end = start
            for i, char in enumerate(response_text[start:], start):
                if char == "{":
                    depth += 1
                elif char == "}":
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            response_text = response_text[start:end]
        
        data = json.loads(response_text)
        raw_items = data.get("action_items", [])
        
        # Normalize and validate action items
        action_items = []
        for item in raw_items:
            normalized = _normalize_action_item(item, call_date)
            if normalized:
                action_items.append(normalized)
        
        return action_items
        
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse action items JSON: {e}")
        return _extract_action_items_from_text(response_text, call_date)


def _normalize_action_item(item: Dict, call_date: str) -> Optional[Dict[str, Any]]:
    """
    Normalize an action item to consistent format.
    """
    if isinstance(item, str):
        return {
            "task": item,
            "owner": "Seller",
            "due_date": _calculate_default_due_date(call_date),
            "priority": "medium"
        }
    
    if not isinstance(item, dict):
        return None
    
    task = item.get("task", "").strip()
    if not task:
        return None
    
    # Normalize owner
    owner = item.get("owner", "Seller").strip()
    if owner.lower() in ["me", "i", "we", "us", "our team"]:
        owner = "Seller"
    
    # Normalize due date
    due_date = item.get("due_date")
    if due_date:
        due_date = _parse_due_date(due_date, call_date)
    else:
        due_date = None  # Don't assign default, let caller decide
    
    # Normalize priority
    priority = item.get("priority", "medium").lower()
    if priority not in ["high", "medium", "low"]:
        priority = "medium"
    
    return {
        "task": task,
        "owner": owner,
        "due_date": due_date,
        "priority": priority
    }


def _parse_due_date(due_date: Any, call_date: str) -> Optional[str]:
    """
    Parse due date from various formats.
    """
    if due_date is None:
        return None
    
    due_date_str = str(due_date).lower().strip()
    
    # Handle null/none values
    if due_date_str in ["null", "none", "n/a", ""]:
        return None
    
    # Try to parse as ISO date
    try:
        datetime.strptime(due_date_str, "%Y-%m-%d")
        return due_date_str
    except ValueError:
        pass
    
    # Handle relative dates
    try:
        base_date = datetime.strptime(call_date, "%Y-%m-%d")
    except ValueError:
        base_date = datetime.utcnow()
    
    if "today" in due_date_str:
        return base_date.strftime("%Y-%m-%d")
    elif "tomorrow" in due_date_str:
        return (base_date + timedelta(days=1)).strftime("%Y-%m-%d")
    elif "next week" in due_date_str:
        return (base_date + timedelta(days=7)).strftime("%Y-%m-%d")
    elif "next month" in due_date_str:
        return (base_date + timedelta(days=30)).strftime("%Y-%m-%d")
    elif "friday" in due_date_str:
        days_until_friday = (4 - base_date.weekday()) % 7
        if days_until_friday == 0:
            days_until_friday = 7
        return (base_date + timedelta(days=days_until_friday)).strftime("%Y-%m-%d")
    elif "monday" in due_date_str:
        days_until_monday = (0 - base_date.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        return (base_date + timedelta(days=days_until_monday)).strftime("%Y-%m-%d")
    
    # Try to extract days
    import re
    match = re.search(r'(\d+)\s*day', due_date_str)
    if match:
        days = int(match.group(1))
        return (base_date + timedelta(days=days)).strftime("%Y-%m-%d")
    
    return None


def _calculate_default_due_date(call_date: str) -> str:
    """
    Calculate default due date (+7 days from call).
    """
    try:
        base_date = datetime.strptime(call_date, "%Y-%m-%d")
    except ValueError:
        base_date = datetime.utcnow()
    
    return (base_date + timedelta(days=7)).strftime("%Y-%m-%d")


def _extract_action_items_from_text(text: str, call_date: str) -> List[Dict[str, Any]]:
    """
    Fallback extractor when JSON parsing fails.
    Uses simple text analysis to find action items.
    """
    action_items = []
    
    # Common action item indicators
    indicators = [
        "will send",
        "will provide",
        "follow up",
        "schedule",
        "send you",
        "get back to",
        "prepare",
        "create",
        "draft",
        "review",
        "action item",
        "next step",
        "to do",
        "need to",
    ]
    
    lines = text.split("\n")
    for line in lines:
        line_lower = line.lower()
        
        for indicator in indicators:
            if indicator in line_lower:
                # Clean up the line
                task = line.strip()
                if task.startswith("-") or task.startswith("•"):
                    task = task[1:].strip()
                if task.startswith("*"):
                    task = task[1:].strip()
                
                if len(task) > 10:  # Minimum task length
                    action_items.append({
                        "task": task[:200],  # Limit length
                        "owner": "Seller",
                        "due_date": _calculate_default_due_date(call_date),
                        "priority": "medium"
                    })
                break
    
    # Deduplicate
    seen = set()
    unique_items = []
    for item in action_items:
        task_key = item["task"].lower()[:50]
        if task_key not in seen:
            seen.add(task_key)
            unique_items.append(item)
    
    return unique_items[:10]


def _generate_default_action_item(account_name: str) -> List[Dict[str, Any]]:
    """
    Generate a default action item when extraction fails.
    """
    return [{
        "task": f"Follow up with {account_name} regarding next steps",
        "owner": "Seller",
        "due_date": (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "priority": "medium"
    }]
