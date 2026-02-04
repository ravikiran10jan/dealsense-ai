"""
Call Summary Generator for Live Call Assistant.
Uses LLM to generate structured summaries from call transcripts.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from .prompt_templates import SUMMARY_PROMPT_TEMPLATE
from .action_items_extractor import extract_action_items

load_dotenv()

logger = logging.getLogger(__name__)

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY")
)


async def generate_call_summary(
    transcript: str,
    account_name: str = "Unknown",
    deal_id: int = None,
    duration_minutes: int = 0,
    industry: str = "Unknown",
    deal_stage: str = "Discovery",
    seller_name: str = "Seller"
) -> Dict[str, Any]:
    """
    Generate a structured summary from a call transcript.
    
    Args:
        transcript: Full call transcript with speaker labels
        account_name: Customer account name
        deal_id: Associated deal ID
        duration_minutes: Call duration in minutes
        industry: Customer industry
        deal_stage: Current deal stage
        seller_name: Name of the seller
    
    Returns:
        Dictionary containing:
        - executive_summary: Brief overview
        - key_points: List of main discussion points
        - pain_points: List of customer pain points
        - objections: List of objections raised
        - next_steps: Agreed next steps
        - deal_health_score: 1-10 score
        - deal_health_reason: Explanation of score
        - action_items: List of extracted action items
    """
    if not transcript or len(transcript.strip()) < 50:
        logger.warning("Transcript too short for meaningful summary")
        return _generate_empty_summary(account_name)
    
    # Build the summary prompt
    prompt = SUMMARY_PROMPT_TEMPLATE.format(
        account_name=account_name,
        industry=industry,
        deal_stage=deal_stage,
        duration_minutes=duration_minutes,
        transcript=transcript[:15000],  # Limit transcript length
    )
    
    try:
        # Generate summary
        response = llm.invoke(prompt)
        summary_text = response.content.strip()
        
        # Parse JSON response
        summary = _parse_summary_response(summary_text)
        
        # Extract action items separately for better accuracy
        action_items = await extract_action_items(
            transcript=transcript,
            account_name=account_name,
            seller_name=seller_name,
        )
        
        summary["action_items"] = action_items
        
        logger.info(f"Generated summary for {account_name} with {len(action_items)} action items")
        return summary
        
    except Exception as e:
        logger.error(f"Error generating summary: {e}", exc_info=True)
        return _generate_fallback_summary(transcript, account_name)


def _parse_summary_response(response_text: str) -> Dict[str, Any]:
    """
    Parse LLM response into structured summary.
    Handles JSON extraction from potentially noisy output.
    """
    # Try to extract JSON from response
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
            # Find matching closing brace
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
        
        summary = json.loads(response_text)
        
        # Validate and normalize structure
        return {
            "executive_summary": summary.get("executive_summary", ""),
            "key_points": summary.get("key_points", []),
            "pain_points": _normalize_pain_points(summary.get("pain_points", [])),
            "objections": _normalize_objections(summary.get("objections", [])),
            "next_steps": summary.get("next_steps", ""),
            "deal_health_score": min(10, max(1, int(summary.get("deal_health_score", 5)))),
            "deal_health_reason": summary.get("deal_health_reason", ""),
        }
        
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse JSON: {e}")
        # Try to extract key information from text
        return _parse_text_summary(response_text)


def _normalize_pain_points(pain_points: List) -> List[Dict]:
    """Normalize pain points to consistent format"""
    normalized = []
    for pp in pain_points:
        if isinstance(pp, str):
            normalized.append({
                "description": pp,
                "severity": "medium",
                "context": None
            })
        elif isinstance(pp, dict):
            normalized.append({
                "description": pp.get("description", str(pp)),
                "severity": pp.get("severity", "medium"),
                "context": pp.get("context")
            })
    return normalized


def _normalize_objections(objections: List) -> List[Dict]:
    """Normalize objections to consistent format"""
    normalized = []
    for obj in objections:
        if isinstance(obj, str):
            normalized.append({
                "description": obj,
                "category": "general",
                "response_suggested": None
            })
        elif isinstance(obj, dict):
            normalized.append({
                "description": obj.get("description", str(obj)),
                "category": obj.get("category", "general"),
                "response_suggested": obj.get("response_suggested")
            })
    return normalized


def _parse_text_summary(text: str) -> Dict[str, Any]:
    """
    Fallback parser for non-JSON responses.
    Extracts information from plain text.
    """
    lines = text.strip().split("\n")
    
    summary = {
        "executive_summary": "",
        "key_points": [],
        "pain_points": [],
        "objections": [],
        "next_steps": "",
        "deal_health_score": 5,
        "deal_health_reason": "Unable to parse structured response",
    }
    
    # Try to find key sections
    current_section = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        lower_line = line.lower()
        
        if "executive summary" in lower_line or "summary:" in lower_line:
            current_section = "executive_summary"
        elif "key point" in lower_line or "discussion point" in lower_line:
            current_section = "key_points"
        elif "pain point" in lower_line:
            current_section = "pain_points"
        elif "objection" in lower_line:
            current_section = "objections"
        elif "next step" in lower_line:
            current_section = "next_steps"
        elif "health" in lower_line and "score" in lower_line:
            current_section = "deal_health"
        elif current_section:
            if line.startswith("-") or line.startswith("•") or line.startswith("*"):
                line = line[1:].strip()
            
            if current_section == "executive_summary":
                summary["executive_summary"] = line
            elif current_section == "key_points":
                summary["key_points"].append(line)
            elif current_section == "pain_points":
                summary["pain_points"].append({
                    "description": line,
                    "severity": "medium",
                    "context": None
                })
            elif current_section == "objections":
                summary["objections"].append({
                    "description": line,
                    "category": "general",
                    "response_suggested": None
                })
            elif current_section == "next_steps":
                summary["next_steps"] = line
            elif current_section == "deal_health":
                # Try to extract score
                import re
                numbers = re.findall(r'\d+', line)
                if numbers:
                    score = int(numbers[0])
                    summary["deal_health_score"] = min(10, max(1, score))
                summary["deal_health_reason"] = line
    
    return summary


def _generate_empty_summary(account_name: str) -> Dict[str, Any]:
    """Generate an empty summary structure"""
    return {
        "executive_summary": f"Call with {account_name} - transcript too short for analysis.",
        "key_points": ["Insufficient transcript data for analysis"],
        "pain_points": [],
        "objections": [],
        "next_steps": "Review call recording if available",
        "deal_health_score": 5,
        "deal_health_reason": "Unable to assess - insufficient data",
        "action_items": [],
    }


def _generate_fallback_summary(transcript: str, account_name: str) -> Dict[str, Any]:
    """
    Generate a basic summary when LLM fails.
    Uses simple text analysis.
    """
    # Count speakers
    speakers = set()
    lines = transcript.split("\n")
    for line in lines:
        if ":" in line:
            speaker = line.split(":")[0].strip()
            if speaker and len(speaker) < 30:
                speakers.add(speaker)
    
    # Count words
    word_count = len(transcript.split())
    
    return {
        "executive_summary": f"Call with {account_name} involving {len(speakers)} participants. Approximately {word_count} words exchanged.",
        "key_points": [
            f"Participants: {', '.join(speakers)}",
            f"Transcript length: {word_count} words",
            "Manual review recommended for detailed analysis"
        ],
        "pain_points": [],
        "objections": [],
        "next_steps": "Review transcript manually and extract key insights",
        "deal_health_score": 5,
        "deal_health_reason": "Automated analysis failed - manual review recommended",
        "action_items": [{
            "task": f"Review call transcript with {account_name}",
            "owner": "Seller",
            "due_date": None,
            "priority": "medium"
        }],
    }
