
from dataclasses import dataclass
from typing import List, Optional, Tuple

@dataclass
class Expr: pass

@dataclass
class IntLit(Expr): text: str
@dataclass
class FloatLit(Expr): text: str
@dataclass
class StringLit(Expr): value: str
@dataclass
class Name(Expr): id: str
@dataclass
class BinOp(Expr):
    op: str
    left: Expr
    right: Expr
@dataclass
class Call(Expr):
    func: Expr
    args: List[Expr]

@dataclass
class Stmt: pass

@dataclass
class Let(Stmt):
    name: str
    type_name: Optional[str]
    expr: Expr

@dataclass
class Var(Stmt):
    name: str
    type_name: Optional[str]
    expr: Expr

@dataclass
class Assign(Stmt):
    name: str
    expr: Expr

@dataclass
class Return(Stmt):
    expr: Optional[Expr]

@dataclass
class ExprStmt(Stmt):
    expr: Expr

@dataclass
class If(Stmt):
    cond: Expr
    then_body: List[Stmt]
    else_body: List[Stmt]

@dataclass
class While(Stmt):
    cond: Expr
    body: List[Stmt]

@dataclass
class ForRange(Stmt):
    var: str
    start: Expr
    end: Expr
    body: List[Stmt]

@dataclass
class Func:
    name: str
    params: List[Tuple[str, Optional[str]]]
    ret_type: Optional[str]
    body: List[Stmt]

@dataclass
class Package:
    name: str

@dataclass
class Module:
    package: Optional[Package]
    uses: List[str]
    funcs: List[Func]
