"""Main transpiler orchestrator"""
from parsers.python_parser import PythonParser
from parsers.c_parser import CParser
from parsers.cpp_parser import CppParser
from parsers.java_parser import JavaParser
from generators.python_generator import PythonGenerator
from generators.c_generator import CGenerator
from generators.cpp_generator import CppGenerator
from generators.java_generator import JavaGenerator

class Transpiler:
    """Main transpiler class - orchestrates parsing and code generation"""
    
    def __init__(self):
        # Initialize parsers
        self.parsers = {
            'python': PythonParser(),
            'c': CParser(),
            'cpp': CppParser(),
            'java': JavaParser()
        }
        
        # Initialize generators
        self.generators = {
            'python': PythonGenerator(),
            'c': CGenerator(),
            'cpp': CppGenerator(),
            'java': JavaGenerator()
        }
    
    def transpile(self, source_code: str, source_language: str, target_language: str) -> str:
        """
        Transpile code from source language to target language
        
        Args:
            source_code: Source code to transpile
            source_language: Language of source code (python, c, cpp, java)
            target_language: Target language (python, c, cpp, java)
        
        Returns:
            Transpiled code as string
        """
        
        source_language = source_language.lower()
        target_language = target_language.lower()
        
        # Validate languages
        if source_language not in self.parsers:
            raise ValueError(f"Unsupported source language: {source_language}")
        
        if target_language not in self.generators:
            raise ValueError(f"Unsupported target language: {target_language}")
        
        # Parse source code to IR
        parser = self.parsers[source_language]
        ir_program = parser.parse(source_code)
        
        # Check for parse errors
        if parser.errors:
            error_msg = "; ".join(parser.errors)
            raise Exception(f"Parse error: {error_msg}")
        
        # Generate target code from IR
        generator = self.generators[target_language]
        target_code = generator.generate(ir_program)
        
        return target_code
    
    def get_supported_languages(self) -> dict:
        """Get list of supported languages"""
        return {
            'parse': list(self.parsers.keys()),
            'generate': list(self.generators.keys())
        }
