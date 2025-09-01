
from typing import List, Optional, Tuple
from .tokens import TokKind, Token
from . import ast as A

class Parser:
    def __init__(self, tokens: List[Token]):
        self.toks = tokens
        self.i = 0

    def cur(self) -> Token: return self.toks[self.i]

    def eat(self, kind: TokKind) -> Token:
        t = self.cur()
        if t.kind != kind:
            raise SyntaxError(f"Expected {kind.name}, got {t.kind.name} at line {t.line}")
        self.i += 1
        return t

    def match(self, kind: TokKind) -> bool:
        if self.cur().kind == kind:
            self.i += 1
            return True
        return False

    def parse(self) -> A.Module:
        package = None; uses = []; funcs = []
        if self.cur().kind == TokKind.KW_PACKAGE:
            self.eat(TokKind.KW_PACKAGE)
            name = self.eat(TokKind.IDENT).value
            self._newline_optional()
            package = A.Package(name)
        while self.cur().kind == TokKind.KW_USE:
            self.eat(TokKind.KW_USE)
            path = self.eat(TokKind.IDENT).value
            uses.append(path); self._newline_required()
        while self.cur().kind != TokKind.EOF:
            funcs.append(self.parse_func())
        return A.Module(package, uses, funcs)

    def parse_func(self) -> A.Func:
        self.eat(TokKind.KW_FN)
        name = self.eat(TokKind.IDENT).value
        self.eat(TokKind.LPAREN)
        params = []
        if self.cur().kind != TokKind.RPAREN:
            while True:
                pname = self.eat(TokKind.IDENT).value
                ptype = None
                if self.match(TokKind.COLON):
                    ptype = self.eat(TokKind.IDENT).value
                params.append((pname, ptype))
                if self.match(TokKind.COMMA): continue
                break
        self.eat(TokKind.RPAREN)
        ret_type = None
        self.eat(TokKind.COLON)
        self._expect_indent()
        body = self.parse_block()
        return A.Func(name, params, ret_type, body)

    def parse_block(self):
        out = []
        while True:
            k = self.cur().kind
            if k == TokKind.DEDENT:
                self.eat(TokKind.DEDENT); break
            out.append(self.parse_stmt())
        return out

    def parse_stmt(self):
        k = self.cur().kind
        if k == TokKind.KW_LET:
            self.eat(TokKind.KW_LET)
            name = self.eat(TokKind.IDENT).value
            typ = None
            if self.match(TokKind.COLON):
                typ = self.eat(TokKind.IDENT).value
            self.eat(TokKind.ASSIGN)
            expr = self.parse_expr()
            self._newline_required()
            return A.Let(name, typ, expr)
        if k == TokKind.KW_VAR:
            self.eat(TokKind.KW_VAR)
            name = self.eat(TokKind.IDENT).value
            typ = None
            if self.match(TokKind.COLON):
                typ = self.eat(TokKind.IDENT).value
            self.eat(TokKind.ASSIGN)
            expr = self.parse_expr()
            self._newline_required()
            return A.Var(name, typ, expr)
        if k == TokKind.KW_RETURN:
            self.eat(TokKind.KW_RETURN)
            expr = None if self.cur().kind in (TokKind.NEWLINE, TokKind.DEDENT) else self.parse_expr()
            self._newline_required()
            return A.Return(expr)
        if k == TokKind.KW_IF:
            self.eat(TokKind.KW_IF); cond = self.parse_expr()
            self.eat(TokKind.COLON); self._expect_indent()
            thenb = self.parse_block(); elseb = []
            if self.cur().kind == TokKind.KW_ELSE:
                self.eat(TokKind.KW_ELSE); self.eat(TokKind.COLON); self._expect_indent()
                elseb = self.parse_block()
            return A.If(cond, thenb, elseb)
        if k == TokKind.KW_WHILE:
            self.eat(TokKind.KW_WHILE); cond = self.parse_expr()
            self.eat(TokKind.COLON); self._expect_indent()
            body = self.parse_block(); return A.While(cond, body)
        if k == TokKind.KW_FOR:
            self.eat(TokKind.KW_FOR); var = self.eat(TokKind.IDENT).value
            self.eat(TokKind.KW_IN); start = self.parse_expr(); self.eat(TokKind.RANGE); end = self.parse_expr()
            self.eat(TokKind.COLON); self._expect_indent(); body = self.parse_block()
            return A.ForRange(var, start, end, body)
        expr = self.parse_expr(); self._newline_required(); return A.ExprStmt(expr)

    def parse_expr(self):
        left = self.parse_term()
        while self.cur().kind in (TokKind.PLUS, TokKind.MINUS):
            op = self.eat(self.cur().kind).value; right = self.parse_term()
            left = A.BinOp(op, left, right)
        return left

    def parse_term(self):
        left = self.parse_factor()
        while self.cur().kind in (TokKind.STAR, TokKind.SLASH):
            op = self.eat(self.cur().kind).value; right = self.parse_factor()
            left = A.BinOp(op, left, right)
        return left

    def parse_factor(self):
        t = self.cur()
        if t.kind == TokKind.INT: self.eat(TokKind.INT); return A.IntLit(t.value)
        if t.kind == TokKind.FLOAT: self.eat(TokKind.FLOAT); return A.FloatLit(t.value)
        if t.kind == TokKind.STRING: self.eat(TokKind.STRING); return A.StringLit(t.value)
        if t.kind == TokKind.IDENT:
            self.eat(TokKind.IDENT); base = A.Name(t.value)
            if self.cur().kind == TokKind.LPAREN:
                self.eat(TokKind.LPAREN); args=[]
                if self.cur().kind != TokKind.RPAREN:
                    while True:
                        args.append(self.parse_expr())
                        if self.match(TokKind.COMMA): continue
                        break
                self.eat(TokKind.RPAREN); return A.Call(base, args)
            return base
        raise SyntaxError(f"Unexpected token {t.kind.name} at line {t.line}")

    def _newline_required(self):
        if self.cur().kind != TokKind.NEWLINE:
            raise SyntaxError(f"Expected NEWLINE at line {self.cur().line}")
        while self.cur().kind == TokKind.NEWLINE:
            self.eat(TokKind.NEWLINE)

    def _newline_optional(self):
        while self.cur().kind == TokKind.NEWLINE:
            self.eat(TokKind.NEWLINE)

    def _expect_indent(self):
        if not self.match(TokKind.INDENT):
            raise SyntaxError(f"Expected INDENT at line {self.cur().line}")
