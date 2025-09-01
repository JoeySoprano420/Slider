
from enum import Enum, auto
from dataclasses import dataclass

class TokKind(Enum):
    EOF = 0
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()

    IDENT = auto()
    INT = auto()
    FLOAT = auto()
    STRING = auto()

    COLON = auto()
    COMMA = auto()
    LPAREN = auto()
    RPAREN = auto()
    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()
    ASSIGN = auto()
    RANGE = auto()

    KW_PACKAGE = auto()
    KW_USE = auto()
    KW_FN = auto()
    KW_LET = auto()
    KW_VAR = auto()
    KW_RETURN = auto()
    KW_IF = auto()
    KW_ELSE = auto()
    KW_WHILE = auto()
    KW_FOR = auto()
    KW_IN = auto()
    KW_SAY = auto()

@dataclass
class Token:
    kind: TokKind
    value: str
    line: int
    col: int
