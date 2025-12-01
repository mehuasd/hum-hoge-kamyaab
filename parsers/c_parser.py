"""C language parser - FIXED for nested structures"""
import re
from typing import List, Optional

class CParser:
    """Parse C source code - FIXED with recursive block parsing."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.source: str = ""
        self.tokens: List[str] = []
        self.pos: int = 0
    
    def parse(self, source_code: str):
        """Parse C code."""
        self.source = source_code
        self.errors = []
        self.tokens = self._tokenize(source_code)
        self.pos = 0
        
        from core.ir import IRProgram
        statements = []
        while self.pos < len(self.tokens):
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        return IRProgram(node_type="program", statements=statements)
    
    def _tokenize(self, code: str) -> List[str]:
        """Tokenize C code."""
        code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        token_pattern = r'(\b\w+\b|[{}()\[\];,=+\-*/%!<>|&^~?:]|"[^"]*"|\d+\.\d+|\d+)'
        tokens = re.findall(token_pattern, code)
        return [t for t in tokens if t.strip()]
    
    def _current_token(self):
        """Get current token."""
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    
    def _consume(self, expected=None):
        """Consume token."""
        token = self._current_token()
        if expected and token != expected:
            self.error(f"Expected '{expected}', got '{token}'")
        self.pos += 1
        return token
    
    def _parse_statement(self):
        """Parse statement."""
        token = self._current_token()
        
        if not token:
            return None
        
        if token == "printf":
            return self._parse_printf()
        elif token == "if":
            return self._parse_if()
        elif token == "for":
            return self._parse_for()
        elif token == "while":
            return self._parse_while()
        elif token in ["int", "float", "double", "char", "void"]:
            return self._parse_declaration()
        elif token == "return":
            return self._parse_return()
        else:
            return self._parse_assignment_or_expr()
    
    def _parse_if(self):
        """Parse if - FIXED for nested structures."""
        from core.ir import IRIfStatement
        
        self._consume("if")
        self._consume("(")
        condition = self._parse_expression()
        self._consume(")")
        
        # KEY FIX: Parse entire block recursively
        then_body = self._parse_block()
        
        elif_parts = []
        else_body = []
        
        while self._current_token() == "else":
            self._consume("else")
            if self._current_token() == "if":
                self._consume("if")
                self._consume("(")
                elif_cond = self._parse_expression()
                self._consume(")")
                elif_body_stmts = self._parse_block()
                elif_parts.append((elif_cond, elif_body_stmts))
            else:
                else_body = self._parse_block()
                break
        
        return IRIfStatement(
            node_type="if",
            condition=condition,
            then_body=then_body,
            elif_parts=elif_parts,
            else_body=else_body
        )
    
    def _parse_for(self):
        """Parse for - FIXED for nested structures."""
        from core.ir import IRForLoop
        
        self._consume("for")
        self._consume("(")
        
        var_type = self._consume() if self._current_token() in ["int", "float"] else None
        var_name = self._consume()
        
        init_value = 0
        if self._current_token() == "=":
            self._consume("=")
            init_value = self._parse_expression()
        
        self._consume(";")
        condition = self._parse_expression()
        self._consume(";")
        update = self._parse_expression()
        self._consume(")")
        
        # KEY FIX: Parse entire block recursively
        body = self._parse_block()
        
        return IRForLoop(
            node_type="for",
            var_name=var_name,
            init_value=init_value,
            condition=condition,
            update=update,
            body=body,
            is_range_loop=False
        )
    
    def _parse_while(self):
        """Parse while - FIXED for nested structures."""
        from core.ir import IRWhileLoop
        
        self._consume("while")
        self._consume("(")
        condition = self._parse_expression()
        self._consume(")")
        
        # KEY FIX: Parse entire block recursively
        body = self._parse_block()
        
        return IRWhileLoop(node_type="while", condition=condition, body=body)
    
    def _parse_block(self) -> List:
        """
        Parse a block of statements.
        KEY FIX: This is recursive and handles all statements in a block!
        """
        statements = []
        
        if self._current_token() == "{":
            self._consume("{")
            
            # Parse ALL statements until closing brace
            while self._current_token() and self._current_token() != "}":
                stmt = self._parse_statement()
                if stmt:
                    statements.append(stmt)
            
            self._consume("}")
        else:
            # Single statement
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        
        return statements
    
    def _parse_printf(self):
        """Parse printf."""
        from core.ir import IRPrintStatement
        
        self._consume("printf")
        self._consume("(")
        format_str = self._parse_expression()
        args = []
        while self._current_token() == ",":
            self._consume(",")
            args.append(self._parse_expression())
        self._consume(")")
        self._consume(";")
        return IRPrintStatement(node_type="print", arguments=args, format_string=format_str)
    
    def _parse_declaration(self):
        """Parse declaration."""
        from core.ir import IRVariable
        
        var_type = self._consume()
        name = self._consume()
        
        if self._current_token() == "=":
            self._consume("=")
            value = self._parse_expression()
            if self._current_token() == ";":
                self._consume(";")
            return IRVariable(node_type="variable", name=name, var_type=var_type, value=value)
        else:
            if self._current_token() == ";":
                self._consume(";")
            return IRVariable(node_type="variable", name=name, var_type=var_type)
    
    def _parse_return(self):
        """Parse return."""
        from core.ir import IRReturn
        
        self._consume("return")
        value = None
        if self._current_token() != ";":
            value = self._parse_expression()
        self._consume(";")
        return IRReturn(node_type="return", value=value)
    
    def _parse_assignment_or_expr(self):
        """Parse assignment."""
        from core.ir import IRAssignment
        
        name = self._current_token()
        if name and (name.isidentifier() or name.isdigit()):
            self._consume()
            if self._current_token() == "=":
                self._consume("=")
                value = self._parse_expression()
                if self._current_token() == ";":
                    self._consume(";")
                return IRAssignment(node_type="assignment", target=name, value=value)
        return None
    
    def _parse_expression(self) -> str:
        """Parse expression."""
        expr_tokens = []
        paren_count = 0
        
        while self._current_token():
            token = self._current_token()
            
            if token == "(":
                paren_count += 1
            elif token == ")":
                if paren_count == 0:
                    break
                paren_count -= 1
            elif token == ";" and paren_count == 0:
                break
            elif token == "," and paren_count == 0:
                break
            
            expr_tokens.append(self._consume())
        
        return " ".join(expr_tokens) if expr_tokens else "0"
    
    def error(self, message: str):
        """Record a parse error."""
        self.errors.append(message)
