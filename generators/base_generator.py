"""Abstract base generator class - FIXED with indent tracking"""

class BaseGenerator:
    """Base generator class - all generators inherit from this."""
    
    def __init__(self, indent_size: int = 2):
        self.indent_level: int = 0
        self.indent_size: int = indent_size
    
    def generate(self, ir_program) -> str:
        """Generate code from IR. Override in subclass."""
        raise NotImplementedError("Subclass must implement generate()")
    
    def _increase_indent(self):
        """Increase indentation level."""
        self.indent_level += 1
    
    def _decrease_indent(self):
        """Decrease indentation level."""
        if self.indent_level > 0:
            self.indent_level -= 1
    
    def _indent(self) -> str:
        """Get current indentation string."""
        return " " * (self.indent_level * self.indent_size)
