"""
Summarization package for Live Call Assistant
"""
from .call_summary import generate_call_summary
from .action_items_extractor import extract_action_items
from .prompt_templates import SUMMARY_PROMPT_TEMPLATE, ACTION_ITEMS_PROMPT_TEMPLATE

__all__ = [
    "generate_call_summary",
    "extract_action_items",
    "SUMMARY_PROMPT_TEMPLATE",
    "ACTION_ITEMS_PROMPT_TEMPLATE",
]
