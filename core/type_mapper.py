"""Type mapping between different programming languages"""

class TypeMapper:
    """Maps types between different languages"""
    
    # Python type to other languages
    PYTHON_TYPES = {
        'int': {'c': 'int', 'cpp': 'int', 'java': 'int'},
        'float': {'c': 'float', 'cpp': 'float', 'java': 'float'},
        'str': {'c': 'char*', 'cpp': 'string', 'java': 'String'},
        'bool': {'c': 'int', 'cpp': 'bool', 'java': 'boolean'},
        'list': {'c': 'array', 'cpp': 'vector', 'java': 'ArrayList'},
        'dict': {'c': 'struct', 'cpp': 'map', 'java': 'HashMap'},
        'auto': {'c': 'auto', 'cpp': 'auto', 'java': 'var'}
    }
    
    # C type to other languages
    C_TYPES = {
        'int': {'python': 'int', 'cpp': 'int', 'java': 'int'},
        'float': {'python': 'float', 'cpp': 'float', 'java': 'float'},
        'char*': {'python': 'str', 'cpp': 'string', 'java': 'String'},
        'double': {'python': 'float', 'cpp': 'double', 'java': 'double'},
        'void': {'python': 'None', 'cpp': 'void', 'java': 'void'}
    }
    
    @staticmethod
    def map_type(type_name: str, from_lang: str, to_lang: str) -> str:
        """Map a type from one language to another"""
        
        type_name = type_name.strip().lower()
        
        if from_lang == 'python':
            mapping = TypeMapper.PYTHON_TYPES.get(type_name, {})
            return mapping.get(to_lang, 'auto')
        
        elif from_lang == 'c':
            mapping = TypeMapper.C_TYPES.get(type_name, {})
            return mapping.get(to_lang, 'auto')
        
        return 'auto'
    
    @staticmethod
    def get_default_value(type_name: str, language: str) -> str:
        """Get default value for a type in given language"""
        
        type_name = type_name.lower()
        
        if language == 'python':
            defaults = {'int': '0', 'float': '0.0', 'str': '""', 'bool': 'False'}
            return defaults.get(type_name, 'None')
        
        elif language in ['c', 'cpp']:
            defaults = {'int': '0', 'float': '0.0f', 'double': '0.0', 'char*': '""'}
            return defaults.get(type_name, '0')
        
        elif language == 'java':
            defaults = {'int': '0', 'float': '0.0f', 'double': '0.0', 'String': '""', 'boolean': 'false'}
            return defaults.get(type_name, 'null')
        
        return '0'
