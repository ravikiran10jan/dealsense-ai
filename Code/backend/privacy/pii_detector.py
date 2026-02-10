"""
PII Detection Module
Regex-based detection of Personally Identifiable Information (PII).
"""

import re
from typing import List, Tuple, Dict
from dataclasses import dataclass


# PII type identifiers
PII_TYPES = {
    'EMAIL': 'EMAIL',
    'PHONE': 'PHONE',
    'SSN': 'SSN',
    'CREDIT_CARD': 'CREDIT_CARD',
    'IP_ADDRESS': 'IP_ADDRESS',
}


@dataclass
class PIIMatch:
    """Represents a detected PII match in text."""
    pii_type: str
    start: int
    end: int
    value: str
    
    def __repr__(self):
        masked = self.value[:2] + "***" + self.value[-2:] if len(self.value) > 4 else "***"
        return f"PIIMatch(type={self.pii_type}, value={masked})"


# Regex patterns for PII detection
# Order matters: more specific patterns should come first
PII_PATTERNS: Dict[str, re.Pattern] = {
    # Social Security Number (US format: XXX-XX-XXXX)
    'SSN': re.compile(
        r'\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b'
    ),
    
    # Credit Card Numbers (13-19 digits, with optional separators)
    # Covers Visa, MasterCard, Amex, Discover, etc.
    'CREDIT_CARD': re.compile(
        r'\b(?:4[0-9]{12}(?:[0-9]{3})?|'  # Visa
        r'5[1-5][0-9]{14}|'  # MasterCard
        r'3[47][0-9]{13}|'  # Amex
        r'6(?:011|5[0-9]{2})[0-9]{12}|'  # Discover
        r'(?:[0-9]{4}[-\s]?){3}[0-9]{4})\b'  # Generic 16-digit with separators
    ),
    
    # Email addresses (RFC 5322 simplified)
    'EMAIL': re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        re.IGNORECASE
    ),
    
    # Phone numbers (US and international formats)
    'PHONE': re.compile(
        r'\b(?:'
        r'(?:\+?1[-.\s]?)?'  # Optional US country code
        r'(?:\(?[0-9]{3}\)?[-.\s]?)'  # Area code
        r'[0-9]{3}[-.\s]?'  # Exchange
        r'[0-9]{4}'  # Subscriber
        r')\b'
    ),
    
    # IP Addresses (IPv4)
    'IP_ADDRESS': re.compile(
        r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    ),
}


def luhn_checksum(card_number: str) -> bool:
    """
    Validate credit card number using Luhn algorithm.
    
    Args:
        card_number: Credit card number (digits only)
        
    Returns:
        True if valid according to Luhn algorithm
    """
    digits = [int(d) for d in card_number if d.isdigit()]
    if len(digits) < 13 or len(digits) > 19:
        return False
    
    # Luhn algorithm
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    
    total = sum(odd_digits)
    for digit in even_digits:
        doubled = digit * 2
        total += doubled if doubled < 10 else doubled - 9
    
    return total % 10 == 0


def detect_pii(text: str, pii_types: List[str] = None) -> List[PIIMatch]:
    """
    Detect PII in the given text using regex patterns.
    
    Args:
        text: The text to scan for PII
        pii_types: Optional list of PII types to detect. 
                   If None, detects all types.
                   
    Returns:
        List of PIIMatch objects representing detected PII
    """
    if not text:
        return []
    
    matches: List[PIIMatch] = []
    types_to_check = pii_types or list(PII_PATTERNS.keys())
    
    for pii_type in types_to_check:
        if pii_type not in PII_PATTERNS:
            continue
            
        pattern = PII_PATTERNS[pii_type]
        
        for match in pattern.finditer(text):
            value = match.group()
            
            # Additional validation for credit cards (Luhn check)
            if pii_type == 'CREDIT_CARD':
                clean_value = re.sub(r'[-\s]', '', value)
                if not luhn_checksum(clean_value):
                    continue
            
            # Skip common false positives
            if pii_type == 'PHONE':
                # Skip if it looks like a date or year
                if re.match(r'^(?:19|20)\d{2}$', value.replace('-', '').replace('.', '')):
                    continue
            
            pii_match = PIIMatch(
                pii_type=pii_type,
                start=match.start(),
                end=match.end(),
                value=value
            )
            matches.append(pii_match)
    
    # Sort by position and remove overlapping matches (keep first/most specific)
    matches.sort(key=lambda m: (m.start, -len(m.value)))
    
    filtered_matches = []
    last_end = -1
    for match in matches:
        if match.start >= last_end:
            filtered_matches.append(match)
            last_end = match.end
    
    return filtered_matches


def contains_pii(text: str) -> bool:
    """
    Quick check if text contains any PII.
    
    Args:
        text: The text to check
        
    Returns:
        True if any PII is detected
    """
    return len(detect_pii(text)) > 0


def get_pii_summary(text: str) -> Dict[str, int]:
    """
    Get a summary count of PII types found in text.
    
    Args:
        text: The text to analyze
        
    Returns:
        Dictionary mapping PII types to their count
    """
    matches = detect_pii(text)
    summary = {}
    for match in matches:
        summary[match.pii_type] = summary.get(match.pii_type, 0) + 1
    return summary
