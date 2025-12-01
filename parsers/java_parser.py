"""Java language parser - FIXED for nested structures"""
import re
from typing import List, Optional

class JavaParser:
    """Parse Java source code - FIXED with recursive block parsing."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.tokens: List[str] = []
        self.pos: int = 0
    
    def parse(self, source_code: str):
        """Parse Java code."""
        self.errors = []
        self.tokens = self._tokenize(source_code)
        self.pos = 0
        
        from core.ir import IRProgram
        statements = []
        while self.pos < len(self.tokens):
            token = self._current_token()
            if token == "public" or token == "private" or token == "class":
                stmt = self._parse_class_or_method()
                if stmt:
                    statements.append(stmt)
            else:
                stmt = self._parse_statement()
                if stmt:
                    statements.append(stmt)
        
        return IRProgram(node_type="program", statements=statements)
    
    def _tokenize(self, code: str) -> List[str]:
        """Tokenize Java code."""
        code = re.sub(r'//.*?$', '', code, flags=re.MULTILINE)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        token_pattern = r'(\b\w+\b|[{}()\[\];,=+\-*/%!<>|&^~?:]|"[^"]*"|\d+\.\d+|\d+)'
        tokens = re.findall(token_pattern, code)
        return [t for t in tokens if t.strip()]
    
    def _current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    
    def _consume(self, expected=None):
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
        
        if token == "System":
            return self._parse_println()
        elif token == "if":
            return self._parse_if()
        elif token == "for":
            return self._parse_for()
        elif token == "while":
            return self._parse_while()
        elif token in ["int", "float", "double", "String", "boolean"]:
            return self._parse_declaration()
        elif token == "return":
            return self._parse_return()
        else:
            return self._parse_assignment()
    
    def _parse_if(self):
        """Parse if - FIXED for nested."""
        from core.ir import IRIfStatement
        
        self._consume("if")
        self._consume("(")
        condition = self._parse_expression()
        self._consume(")")
        then_body = self._parse_block()
        else_body = []
        if self._current_token() == "else":
            self._consume("else")
            else_body = self._parse_block()
        return IRIfStatement(
            node_type="if",
            condition=condition,
            then_body=then_body,
            else_body=else_body
        )
    
    def _parse_for(self):
        """Parse for - FIXED for nested."""
        from core.ir import IRForLoop
        
        self._consume("for")
        self._consume("(")
        var_type = self._consume()
        var_name = self._consume()
        self._consume("=")
        init = self._parse_expression()
        self._consume(";")
        condition = self._parse_expression()
        self._consume(";")
        update = self._parse_expression()
        self._consume(")")
        body = self._parse_block()
        return IRForLoop(
            node_type="for",
            var_name=var_name,
            init_value=init,
            condition=condition,
            update=update,
            body=body
        )
    
    def _parse_while(self):
        """Parse while - FIXED for nested."""
        from core.ir import IRWhileLoop
        
        self._consume("while")
        self._consume("(")
        condition = self._parse_expression()
        self._consume(")")
        body = self._parse_block()
        return IRWhileLoop(node_type="while", condition=condition, body=body)
    
    def _parse_block(self) -> List:
        """
        Parse block - FIXED recursive!
        """
        statements = []
        if self._current_token() == "{":
            self._consume("{")
            while self._current_token() and self._current_token() != "}":
                stmt = self._parse_statement()
                if stmt:
                    statements.append(stmt)
            self._consume("}")
        else:
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)
        return statements
    
    def _parse_println(self):
        """Parse System.out.println."""
        from core.ir import IRPrintStatement
        
        self._consume("System")
        self._consume(".")
        self._consume("out")
        self._consume(".")
        self._consume("println")
        self._consume("(")
        args = []
        if self._current_token() != ")":
            args.append(self._parse_expression())
        self._consume(")")
        self._consume(";")
        return IRPrintStatement(node_type="print", arguments=args)
    
    def _parse_declaration(self):
        """Parse declaration."""
        from core.ir import IRVariable
        
        var_type = self._consume()
        name = self._consume()
        if self._current_token() == "=":
            self._consume("=")
            value = self._parse_expression()
            self._consume(";")
            return IRVariable(node_type="variable", name=name, var_type=var_type, value=value)
        else:
            self._consume(";")
            return IRVariable(node_type="variable", name=name, var_type=var_type)
    
    def _parse_return(self):
        """Parse return."""
        from core.ir import IRReturn
        
        self._consume("return")
        value = self._parse_expression() if self._current_token() != ";" else None
        self._consume(";")
        return IRReturn(node_type="return", value=value)
    
    def _parse_assignment(self):
        """Parse assignment."""
        from core.ir import IRAssignment
        
        name = self._current_token()
        if name and name.isidentifier():
            self._consume()
            if self._current_token() == "=":
                self._consume("=")
                value = self._parse_expression()
                self._consume(";")
                return IRAssignment(node_type="assignment", target=name, value=value)
        return None
    
    def _parse_class_or_method(self):
        """Parse class or method - simplified."""
        while self._current_token() in ["public", "private", "static"]:
            self._consume()
        if self._current_token() == "class":
            self._consume("class")
            name = self._consume()
            self._consume("{")
            while self._current_token() and self._current_token() != "}":
                self._consume()
            self._consume("}")
            return None
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
