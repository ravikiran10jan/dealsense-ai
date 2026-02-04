"""
High-level Sanitization Orchestrator
Provides simple interface for PII sanitization throughout the application.
"""

from typing import Tuple, List, Optional, Dict, Union
from .tokenizer import Tokenizer, get_tokenizer
from .pii_detector import detect_pii, contains_pii, get_pii_summary


class Sanitizer:
    """
    High-level sanitizer that orchestrates PII detection and tokenization.
    Provides a simple interface for sanitizing text throughout the application.
    """
    
    def __init__(self, tokenizer: Tokenizer = None):
        """
        Initialize the sanitizer.
        
        Args:
            tokenizer: Optional tokenizer instance. Uses global instance if not provided.
        """
        self.tokenizer = tokenizer or get_tokenizer()
    
    def sanitize(
        self, 
        text: str, 
        source: str = None,
        return_stats: bool = False
    ) -> Union[Tuple[str, List[str]], Tuple[str, List[str], Dict]]:
        """
        Sanitize text by replacing PII with tokens.
        
        Args:
            text: The text to sanitize
            source: Source identifier for tracking (e.g., "deal_123", "transcript_456")
            return_stats: If True, also return statistics about detected PII
            
        Returns:
            Tuple of (sanitized_text, list of token_ids)
            If return_stats=True: (sanitized_text, token_ids, stats_dict)
        """
        if not text:
            if return_stats:
                return text, [], {}
            return text, []
        
        # Get stats before sanitization if requested
        stats = get_pii_summary(text) if return_stats else None
        
        # Tokenize the text
        sanitized_text, token_ids = self.tokenizer.tokenize(text, source)
        
        if return_stats:
            return sanitized_text, token_ids, stats
        return sanitized_text, token_ids
    
    def desanitize(self, text: str, track_access: bool = True) -> str:
        """
        Restore original PII values in tokenized text.
        Should only be called for authorized users.
        
        Args:
            text: Text containing PII tokens
            track_access: Whether to track this access in the database
            
        Returns:
            Text with original PII values restored
        """
        return self.tokenizer.detokenize(text, track_access)
    
    def is_sanitized(self, text: str) -> bool:
        """
        Check if text contains PII tokens (indicating it has been sanitized).
        
        Args:
            text: The text to check
            
        Returns:
            True if text contains PII tokens
        """
        if not text:
            return True  # Empty text is considered "sanitized"
        return '[PII:' in text
    
    def needs_sanitization(self, text: str) -> bool:
        """
        Check if text contains raw PII that needs sanitization.
        
        Args:
            text: The text to check
            
        Returns:
            True if text contains unsanitized PII
        """
        return contains_pii(text)
    
    def validate_sanitization(self, text: str) -> Tuple[bool, List[str]]:
        """
        Validate that text has been properly sanitized.
        Checks for any remaining raw PII that might have been missed.
        
        Args:
            text: The sanitized text to validate
            
        Returns:
            Tuple of (is_valid, list of detected PII types if any)
        """
        if not text:
            return True, []
        
        matches = detect_pii(text)
        if matches:
            pii_types = list(set(m.pii_type for m in matches))
            return False, pii_types
        return True, []


# Global sanitizer instance
_sanitizer_instance: Optional[Sanitizer] = None


def get_sanitizer() -> Sanitizer:
    """Get or create the global sanitizer instance."""
    global _sanitizer_instance
    if _sanitizer_instance is None:
        _sanitizer_instance = Sanitizer()
    return _sanitizer_instance


def sanitize_text(text: str, source: str = None) -> Tuple[str, List[str]]:
    """
    Convenience function to sanitize text using the global sanitizer.
    
    Args:
        text: The text to sanitize
        source: Source identifier for tracking
        
    Returns:
        Tuple of (sanitized_text, list of token_ids)
    """
    return get_sanitizer().sanitize(text, source)


def desanitize_text(text: str, track_access: bool = True) -> str:
    """
    Convenience function to desanitize text using the global sanitizer.
    
    Args:
        text: Text containing PII tokens
        track_access: Whether to track this access
        
    Returns:
        Text with original PII values restored
    """
    return get_sanitizer().desanitize(text, track_access)
