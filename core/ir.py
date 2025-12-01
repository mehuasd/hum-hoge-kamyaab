"""Intermediate Representation (IR) classes for code transpiler"""
from dataclasses import dataclass, field
from typing import List, Optional, Any

@dataclass
class IRNode:
    """Base class for all IR nodes"""
    node_type: str = ""

@dataclass
class IRProgram(IRNode):
    """Root node representing entire program"""
    statements: List[IRNode] = field(default_factory=list)

@dataclass
class IRVariable(IRNode):
    """Variable declaration or reference"""
    name: str = ""
    var_type: str = "auto"
    value: Any = None

@dataclass
class IRAssignment(IRNode):
    """Variable assignment"""
    target: str = ""
    value: Any = None

@dataclass
class IRPrintStatement(IRNode):
    """Print/output statement"""
    arguments: List[Any] = field(default_factory=list)
    format_string: Optional[str] = None

@dataclass
class IRInputStatement(IRNode):
    """Input/read statement"""
    prompt: Optional[str] = None
    var_name: Optional[str] = None
    expected_type: str = "string"

@dataclass
class IRBinaryOp(IRNode):
    """Binary operation (a + b, a < b, etc)"""
    operator: str = ""
    left: Any = None
    right: Any = None

@dataclass
class IRUnaryOp(IRNode):
    """Unary operation (!a, -a, etc)"""
    operator: str = ""
    operand: Any = None

@dataclass
class IRIfStatement(IRNode):
    """If/else conditional"""
    condition: Any = None
    then_body: List[IRNode] = field(default_factory=list)
    elif_parts: List[tuple] = field(default_factory=list)
    else_body: List[IRNode] = field(default_factory=list)

@dataclass
class IRForLoop(IRNode):
    """For loop"""
    var_name: str = ""
    init_value: Any = 0
    condition: Any = None
    update: Any = None
    range_start: int = 0
    range_end: Any = None
    range_step: int = 1
    body: List[IRNode] = field(default_factory=list)
    is_range_loop: bool = False

@dataclass
class IRWhileLoop(IRNode):
    """While loop"""
    condition: Any = None
    body: List[IRNode] = field(default_factory=list)

@dataclass
class IRFunction(IRNode):
    """Function definition"""
    name: str = ""
    parameters: List[IRVariable] = field(default_factory=list)
    return_type: str = "auto"
    body: List[IRNode] = field(default_factory=list)

@dataclass
class IRReturn(IRNode):
    """Return statement"""
    value: Any = None

@dataclass
class IRClass(IRNode):
    """Class definition"""
    name: str = ""
    methods: List[IRFunction] = field(default_factory=list)

@dataclass
class IRFunctionCall(IRNode):
    """Function call"""
    name: str = ""
    arguments: List[Any] = field(default_factory=list)
