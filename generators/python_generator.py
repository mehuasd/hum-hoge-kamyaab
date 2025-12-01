"""Python code generator - FIXED with proper indentation"""
from core.ir import *
from generators.base_generator import BaseGenerator

class PythonGenerator(BaseGenerator):
    """Generate Python code from IR - FIXED."""
    
    def __init__(self):
        super().__init__(indent_size=4)
    
    def generate(self, ir_program: IRProgram) -> str:
        """Generate Python code."""
        lines = []
        
        for stmt in ir_program.statements:
            generated = self._generate_statement(stmt)
            if generated:
                lines.append(generated)
        
        return "\n".join(lines) if lines else "# Empty program"
    
    def _generate_statement(self, node: IRNode) -> str:
        """Generate statement."""
        
        if isinstance(node, IRPrintStatement):
            return self._generate_print(node)
        elif isinstance(node, IRInputStatement):
            return self._generate_input(node)
        elif isinstance(node, IRAssignment):
            return self._generate_assignment(node)
        elif isinstance(node, IRIfStatement):
            return self._generate_if(node)
        elif isinstance(node, IRForLoop):
            return self._generate_for(node)
        elif isinstance(node, IRWhileLoop):
            return self._generate_while(node)
        elif isinstance(node, IRFunction):
            return self._generate_function(node)
        elif isinstance(node, IRVariable):
            return self._generate_variable(node)
        elif isinstance(node, IRClass):
            return self._generate_class(node)
        
        return ""
    
    def _generate_print(self, node: IRPrintStatement) -> str:
        """Generate print statement."""
        args = ", ".join([self._expr_to_string(arg) for arg in node.arguments])
        return f"{self._indent()}print({args})"
    
    def _generate_input(self, node: IRInputStatement) -> str:
        """Generate input statement."""
        var_name = node.var_name or "x"
        prompt = self._expr_to_string(node.prompt) if node.prompt else '""'
        return f"{self._indent()}{var_name} = input({prompt})"
    
    def _generate_assignment(self, node: IRAssignment) -> str:
        """Generate assignment."""
        value = self._expr_to_string(node.value)
        return f"{self._indent()}{node.target} = {value}"
    
    def _generate_if(self, node: IRIfStatement) -> str:
        """Generate if - FIXED keeps statements inside block."""
        lines = []
        
        cond = self._expr_to_string(node.condition)
        lines.append(f'{self._indent()}if {cond}:')
        
        # KEY FIX: Increase indent BEFORE body
        self._increase_indent()
        for stmt in node.then_body:
            generated = self._generate_statement(stmt)
            if generated:
                lines.append(generated)
        self._decrease_indent()
        
        # Handle elif
        for elif_cond, elif_body in node.elif_parts or []:
            elif_str = self._expr_to_string(elif_cond)
            lines.append(f'{self._indent()}elif {elif_str}:')
            self._increase_indent()
            for stmt in elif_body:
                generated = self._generate_statement(stmt)
                if generated:
                    lines.append(generated)
            self._decrease_indent()
        
        # Handle else
        if node.else_body:
            lines.append(f'{self._indent()}else:')
            self._increase_indent()
            for stmt in node.else_body:
                generated = self._generate_statement(stmt)
                if generated:
                    lines.append(generated)
            self._decrease_indent()
        
        return "\n".join(lines)
    
    def _generate_for(self, node: IRForLoop) -> str:
        """Generate for - FIXED keeps statements inside block."""
        lines = []
        
        if node.is_range_loop:
            range_end = self._expr_to_string(node.range_end)
            lines.append(f'{self._indent()}for {node.var_name} in range({range_end}):')
        else:
            lines.append(f'{self._indent()}for {node.var_name} in ...:')
        
        # KEY FIX: Increase indent BEFORE body
        self._increase_indent()
        for stmt in node.body:
            generated = self._generate_statement(stmt)
            if generated:
                lines.append(generated)
        self._decrease_indent()
        
        return "\n".join(lines)
    
    def _generate_while(self, node: IRWhileLoop) -> str:
        """Generate while - FIXED keeps statements inside block."""
        lines = []
        
        cond = self._expr_to_string(node.condition)
        lines.append(f'{self._indent()}while {cond}:')
        
        # KEY FIX: Increase indent BEFORE body
        self._increase_indent()
        for stmt in node.body:
            generated = self._generate_statement(stmt)
            if generated:
                lines.append(generated)
        self._decrease_indent()
        
        return "\n".join(lines)
    
    def _generate_function(self, node: IRFunction) -> str:
        """Generate function."""
        lines = []
        
        params = ", ".join([p.name for p in node.parameters])
        lines.append(f"def {node.name}({params}):")
        
        self._increase_indent()
        for stmt in node.body:
            generated = self._generate_statement(stmt)
            if generated:
                lines.append(generated)
        self._decrease_indent()
        
        return "\n".join(lines)
    
    def _generate_variable(self, node: IRVariable) -> str:
        """Generate variable declaration."""
        if node.value is not None:
            value = self._expr_to_string(node.value)
            return f"{self._indent()}{node.name} = {value}"
        return ""
    
    def _generate_class(self, node: IRClass) -> str:
        """Generate class."""
        lines = []
        
        lines.append(f"class {node.name}:")
        self._increase_indent()
        
        for method in node.methods:
            generated = self._generate_statement(method)
            if generated:
                lines.append(generated)
        
        self._decrease_indent()
        
        return "\n".join(lines)
    
    def _expr_to_string(self, expr: any) -> str:
        """Convert expression to string."""
        if expr is None:
            return "None"
        if isinstance(expr, (int, float)):
            return str(expr)
        if isinstance(expr, str):
            return f'"{expr}"' if not expr.startswith('"') else expr
        if isinstance(expr, IRVariable):
            return expr.name
        if isinstance(expr, IRBinaryOp):
            left = self._expr_to_string(expr.left)
            right = self._expr_to_string(expr.right)
            return f"({left} {expr.operator} {right})"
        
        return str(expr)
