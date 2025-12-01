"""Python language parser - FULLY FIXED"""
import ast
from typing import Any, List, Optional
from core.ir import *
class PythonParser:
    """Parse Python source code to IR - FIXED."""
    
    def __init__(self):
        self.errors: List[str] = []
        self.variables = {}  # Track: var_name -> type
    
    def parse(self, source_code: str):
        """Parse Python code."""
        self.errors = []
        self.variables = {}
        
        try:
            tree = ast.parse(source_code)
            from core.ir import IRProgram
            
            statements = []
            for node in tree.body:
                stmt = self._convert_node(node)
                if stmt:
                    statements.append(stmt)
            
            return IRProgram(node_type="program", statements=statements)
        
        except SyntaxError as e:
            self.error(f"Syntax error: {str(e)}")
            from core.ir import IRProgram
            return IRProgram(node_type="program", statements=[])
    
    def _convert_node(self, node: ast.AST):
        """Convert Python AST node to IR."""
        
        # Expression statements
        if isinstance(node, ast.Expr):
            expr = self._convert_expr(node.value)
            if isinstance(expr, IRPrintStatement):
                return expr
            return None
        
        # Assignments - ⭐ CRITICAL FIX: Create IRVariable, not IRAssignment
        elif isinstance(node, ast.Assign):
            targets = node.targets
            if targets and isinstance(targets, ast.Name):
                var_name = targets.id
                value = self._ast_to_value(node.value)
                
                # ⭐ INFER TYPE
                var_type = self._infer_type(node.value)
                self.variables[var_name] = var_type
                
                # ⭐ RETURN AS IRVariable (NOT IRAssignment!)
                return IRVariable(
                    node_type="variable",
                    name=var_name,
                    var_type=var_type,
                    value=value
                )
        
        # If statements
        elif isinstance(node, ast.If):
            condition = self._convert_expr(node.test)
            
            then_body = []
            for stmt in node.body:
                converted = self._convert_node(stmt)
                if converted:
                    then_body.append(converted)
            
            elif_parts = []
            else_body = []
            
            if node.orelse:
                if len(node.orelse) == 1 and isinstance(node.orelse, ast.If):
                    elif_if = node.orelse
                    elif_cond = self._convert_expr(elif_if.test)
                    elif_body_stmts = []
                    for stmt in elif_if.body:
                        converted = self._convert_node(stmt)
                        if converted:
                            elif_body_stmts.append(converted)
                    elif_parts.append((elif_cond, elif_body_stmts))
                else:
                    for stmt in node.orelse:
                        converted = self._convert_node(stmt)
                        if converted:
                            else_body.append(converted)
            
            return IRIfStatement(
                node_type="if",
                condition=condition,
                then_body=then_body,
                elif_parts=elif_parts,
                else_body=else_body
            )
        
        # For loops - ⭐ CRITICAL: Use _ast_to_value for range args!
        elif isinstance(node, ast.For):
            var_name = node.target.id if isinstance(node.target, ast.Name) else "i"
            
            body = []
            for stmt in node.body:
                converted = self._convert_node(stmt)
                if converted:
                    body.append(converted)
            
            if isinstance(node.iter, ast.Call):
                if isinstance(node.iter.func, ast.Name) and node.iter.func.id == "range":
                    args = node.iter.args
                    
                    # ⭐ FIX: Convert AST to actual values!
                    if len(args) == 1:
                        range_end = self._ast_to_value(args)
                        return IRForLoop(
                            node_type="for",
                            var_name=var_name,
                            range_start=0,
                            range_end=range_end,
                            range_step=1,
                            body=body,
                            is_range_loop=True
                        )
                    elif len(args) >= 2:
                        range_start = self._ast_to_value(args)
                        range_end = self._ast_to_value(args)
                        range_step = self._ast_to_value(args) if len(args) > 2 else 1
                        return IRForLoop(
                            node_type="for",
                            var_name=var_name,
                            range_start=range_start,
                            range_end=range_end,
                            range_step=range_step,
                            body=body,
                            is_range_loop=True
                        )
            
            return IRForLoop(
                node_type="for",
                var_name=var_name,
                body=body,
                is_range_loop=False
            )
        
        # While loops
        elif isinstance(node, ast.While):
            condition = self._convert_expr(node.test)
            body = []
            for stmt in node.body:
                converted = self._convert_node(stmt)
                if converted:
                    body.append(converted)
            return IRWhileLoop(node_type="while", condition=condition, body=body)
        
        # Return
        elif isinstance(node, ast.Return):
            value = self._convert_expr(node.value) if node.value else None
            return IRReturn(node_type="return", value=value)
        
        # Function definition
        elif isinstance(node, ast.FunctionDef):
            from core.ir import IRFunction
            params = []
            for arg in node.args.args:
                params.append(IRVariable(node_type="variable", name=arg.arg, var_type="auto"))
            
            body = []
            for stmt in node.body:
                converted = self._convert_node(stmt)
                if converted:
                    body.append(converted)
            
            return IRFunction(
                node_type="function",
                name=node.name,
                parameters=params,
                return_type="auto",
                body=body
            )
        
        return None
    
    def _ast_to_value(self, ast_node: ast.AST) -> Any:
        """⭐ CRITICAL: Convert AST node to actual value."""
        if ast_node is None:
            return None
        
        if isinstance(ast_node, ast.Constant):
            return ast_node.value
        
        if isinstance(ast_node, ast.Num):
            return ast_node.n
        
        if isinstance(ast_node, ast.Str):
            return ast_node.s
        
        if isinstance(ast_node, ast.Name):
            return ast_node.id
        
        if isinstance(ast_node, ast.BinOp):
            left = self._ast_to_value(ast_node.left)
            right = self._ast_to_value(ast_node.right)
            op = self._get_op_string(ast_node.op)
            
            from core.ir import IRBinaryOp
            return IRBinaryOp(operator=op, left=left, right=right)
        
        if isinstance(ast_node, ast.UnaryOp):
            op = self._get_op_string(ast_node.op)
            operand = self._ast_to_value(ast_node.operand)
            
            from core.ir import IRUnaryOp
            return IRUnaryOp(operator=op, operand=operand)
        
        return str(ast_node)
    
    def _convert_expr(self, node: Any) -> Any:
        """Convert expression to IR."""
        
        if node is None:
            return None
        
        if isinstance(node, ast.Constant):
            return node.value
        
        if isinstance(node, ast.Name):
            # ⭐ FIX: Create as IRVariable so generators recognize it
            var_type = self.variables.get(node.id, "auto")
            return IRVariable(node_type="variable", name=node.id, var_type=var_type)
        
        if isinstance(node, ast.BinOp):
            op = self._get_op_string(node.op)
            left = self._convert_expr(node.left)
            right = self._convert_expr(node.right)
            return IRBinaryOp(operator=op, left=left, right=right)
        
        if isinstance(node, ast.Compare):
            left = self._convert_expr(node.left)
            if node.ops and node.comparators:
                op = self._get_op_string(node.ops)
                right = self._convert_expr(node.comparators)
                return IRBinaryOp(operator=op, left=left, right=right)
        
        if isinstance(node, ast.UnaryOp):
            op = self._get_op_string(node.op)
            operand = self._convert_expr(node.operand)
            return IRUnaryOp(operator=op, operand=operand)
        
        if isinstance(node, ast.Call):
            func_name = node.func.id if isinstance(node.func, ast.Name) else "call"
            
            if func_name == "print":
                # ⭐ FIX: Use _ast_to_value to get actual values
                args = [self._ast_to_value(arg) for arg in node.args]
                return IRPrintStatement(node_type="print", arguments=args)
            
            elif func_name == "input":
                prompt = self._ast_to_value(node.args) if node.args else None
                return IRInputStatement(node_type="input", prompt=prompt, expected_type="string")
            
            else:
                args = [self._ast_to_value(arg) for arg in node.args]
                return IRFunctionCall(node_type="call", name=func_name, arguments=args)
        
        return node
    
    def _infer_type(self, ast_node: ast.AST) -> str:
        """⭐ NEW: Infer variable type from AST node."""
        if isinstance(ast_node, ast.Constant):
            if isinstance(ast_node.value, int):
                return "int"
            elif isinstance(ast_node.value, float):
                return "float"
            elif isinstance(ast_node.value, str):
                return "str"
            elif isinstance(ast_node.value, bool):
                return "bool"
        
        if isinstance(ast_node, ast.Num):
            if isinstance(ast_node.n, int):
                return "int"
            else:
                return "float"
        
        if isinstance(ast_node, ast.Str):
            return "str"
        
        if isinstance(ast_node, (ast.BinOp, ast.UnaryOp)):
            return "int"  # Default for operations
        
        return "auto"
    
    def _get_op_string(self, op: Any) -> str:
        """Convert Python operator to string."""
        ops = {
            ast.Add: "+", ast.Sub: "-", ast.Mult: "*", ast.Div: "/",
            ast.Mod: "%", ast.Pow: "**", ast.FloorDiv: "//",
            ast.Lt: "<", ast.Gt: ">", ast.LtE: "<=", ast.GtE: ">=",
            ast.Eq: "==", ast.NotEq: "!=",
            ast.And: "&&", ast.Or: "||", ast.Not: "!",
            ast.Invert: "~", ast.UAdd: "+", ast.USub: "-",
        }
        return ops.get(type(op), str(op))
    
    def error(self, message: str):
        """Record a parse error."""
        self.errors.append(message)
