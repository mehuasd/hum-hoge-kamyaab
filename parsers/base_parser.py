"""Abstract base parser class"""
from typing import List, Optional

class BaseParser:
    """Abstract parser base class - all parsers inherit from this."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.source: str = ""
    
    def parse(self, source_code: str):
        """Parse source code to IR. Override in subclass."""
        raise NotImplementedError("Subclass must implement parse()")
    
    def _parse_block(self) -> List:
        """
        Parse a block of statements. MUST handle both:
        - Single statement (no braces)
        - Multiple statements (with braces)
        
        KEY FIX: This is recursive - handles nested structures
        """
        raise NotImplementedError("Subclass must implement _parse_block()")
    
    def error(self, message: str):
        """Record a parse error."""
        self.errors.append(message)
