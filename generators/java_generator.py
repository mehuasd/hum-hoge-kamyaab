"""Java code generator - FULLY FIXED"""
from core.ir import *
from generators.base_generator import BaseGenerator

class JavaGenerator(BaseGenerator):
    """Generate Java code from IR - FULLY FIXED."""
    
    def __init__(self):
        super().__init__(indent_size=4)
    
    def generate(self, ir_program: IRProgram) -> str:
        """Generate Java code."""
        lines = []
        
        lines.append("import java.util.Scanner;")
        lines.append("")
        lines.append("public class Main {")
        self._increase_indent()
        
        lines.append(f"{self._indent()}public static void main(String[] args) {{")
        self._increase_indent()
        
        for stmt in ir_program.statements:
            generated = self._generate_statement(stmt)
            if generated:
                lines.append(generated)
        
        self._decrease_indent()
        lines.append(f"{self._indent()}}}")
        
        self._decrease_indent()
        lines.append("}")
        
        return "\n".join(lines)
    
    def _generate_statement(self, node: IRNode) -> str:
        """Generate statement."""
        
        if isinstance(node, IRPrintStatement):
            return self._generate_println(node)
        elif isinstance(node, IRVariable):  # ⭐ FIX: Handle IRVariable!
            return self._generate_variable(node)
        elif isinstance(node, IRAssignment):
            return self._generate_assignment(node)
        elif isinstance(node, IRIfStatement):
            return self._generate_if(node)
        elif isinstance(node, IRForLoop):
            return self._generate_for(node)
        elif isinstance(node, IRWhileLoop):
            return self._generate_while(node)
        
        return ""
    
    def _generate_println(self, node: IRPrintStatement) -> str:
        """Generate println - ⭐ SMART TYPE DETECTION."""
        
        if not node.arguments:
            return f"{self._indent()}System.out.println();"
        
        args_list = []
        
        for arg in node.arguments:
            arg_str, arg_type = self._get_arg_string_and_type(arg)
            args_list.append(arg_str)
        
        args_str = ", ".join(args_list)
        return f"{self._indent()}System.out.println({args_str});"
    
    def _get_arg_string_and_type(self, arg: Any) -> tuple:
        """⭐ NEW: Determine argument string and type."""
        
        # String literal
        if isinstance(arg, str):
            if arg.startswith('"'):
                return (arg, "string")
            else:
                return (f'"{arg}"', "string")
        
        # Integer
        if isinstance(arg, int):
            return (str(arg), "int")
        
        # Float
        if isinstance(arg, float):
            return (str(arg), "float")
        
        # Variable reference
        if isinstance(arg, IRVariable):
            return (arg.name, "variable")
        
        # Binary operation
        if isinstance(arg, IRBinaryOp):
            return (self._expr_to_string(arg), "expression")
        
        # Fallback
        return (str(arg), "unknown")
    
    def _generate_variable(self, node: IRVariable) -> str:
        """Generate variable declaration."""
        
        if node.value is not None:
            value = self._expr_to_string(node.value)
            return f"{self._indent()}{node.var_type} {node.name} = {value};"
        
        return f"{self._indent()}{node.var_type} {node.name};"
    
    def _generate_assignment(self, node: IRAssignment) -> str:
        """Generate assignment."""
        
        value = self._expr_to_string(node.value)
        return f"{self._indent()}{node.target} = {value};"
    
    def _generate_if(self, node: IRIfStatement) -> str:
        """Generate if - FIXED."""
        lines = []
        
        cond = self._expr_to_string(node.condition)
        lines.append(f'{self._indent()}if ({cond}) {{')
        
        self._increase_indent()
        for stmt in node.then_body:
            generated = self._generate_statement(stmt)
            if generated:
                lines.append(generated)
        self._decrease_indent()
        
        for elif_cond, elif_body in node.elif_parts or []:
            elif_str = self._expr_to_string(elif_cond)
            lines.append(f'{self._indent()}}} else if ({elif_str}) {{')
            self._increase_indent()
            for stmt in elif_body:
                generated = self._generate_statement(stmt)
                if generated:
                    lines.append(generated)
            self._decrease_indent()
        
        if node.else_body:
            lines.append(f'{self._indent()}}} else {{')
            self._increase_indent()
            for stmt in node.else_body:
                generated = self._generate_statement(stmt)
                if generated:
                    lines.append(generated)
            self._decrease_indent()
        
        lines.append(f'{self._indent()}}}')
        
        return "\n".join(lines)
    
    def _generate_for(self, node: IRForLoop) -> str:
        """Generate for - FIXED."""
        lines = []
        
        if node.is_range_loop:
            cond = f"{node.var_name} < {self._expr_to_string(node.range_end)}"
            lines.append(f'{self._indent()}for(int {node.var_name} = {self._expr_to_string(node.range_start)}; {cond}; {node.var_name}++) {{')
        else:
            init = f"int {node.var_name} = {self._expr_to_string(node.init_value)}"
            cond = self._expr_to_string(node.condition)
            update = self._expr_to_string(node.update)
            lines.append(f'{self._indent()}for({init}; {cond}; {update}) {{')
        
        self._increase_indent()
        for stmt in node.body:
            generated = self._generate_statement(stmt)
            if generated:
                lines.append(generated)
        self._decrease_indent()
        
        lines.append(f'{self._indent()}}}')
        
        return "\n".join(lines)
    
    def _generate_while(self, node: IRWhileLoop) -> str:
        """Generate while - FIXED."""
        lines = []
        
        cond = self._expr_to_string(node.condition)
        lines.append(f'{self._indent()}while({cond}) {{')
        
        self._increase_indent()
        for stmt in node.body:
            generated = self._generate_statement(stmt)
            if generated:
                lines.append(generated)
        self._decrease_indent()
        
        lines.append(f'{self._indent()}}}')
        
        return "\n".join(lines)
    
    def _expr_to_string(self, expr: Any) -> str:
        """Convert expression to string."""
        
        if expr is None:
            return "0"
        if isinstance(expr, (int, float)):
            return str(expr)
        if isinstance(expr, str):
            if expr.startswith('"'):
                return expr
            return f'"{expr}"'
        if isinstance(expr, IRVariable):
            return expr.name
        if isinstance(expr, IRBinaryOp):
            left = self._expr_to_string(expr.left)
            right = self._expr_to_string(expr.right)
            return f"({left} {expr.operator} {right})"
        
        return str(expr)
