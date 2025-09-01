
from .tokens import TokKind, Token

KEYWORDS = {
    "package": TokKind.KW_PACKAGE,
    "use": TokKind.KW_USE,
    "fn": TokKind.KW_FN,
    "let": TokKind.KW_LET,
    "var": TokKind.KW_VAR,
    "return": TokKind.KW_RETURN,
    "if": TokKind.KW_IF,
    "else": TokKind.KW_ELSE,
    "while": TokKind.KW_WHILE,
    "for": TokKind.KW_FOR,
    "in": TokKind.KW_IN,
    "say": TokKind.KW_SAY,
}

class Lexer:
    def __init__(self, src: str):
        self.src = src.replace('\r\n', '\n')
        self.pos = 0
        self.line = 1
        self.col = 1
        self.indent_stack = [0]
        self.tokens = []

    def lex(self):
        lines = self.src.split('\n')
        for i, raw in enumerate(lines, start=1):
            self._lex_line(raw, i)
        while len(self.indent_stack) > 1:
            self.tokens.append(Token(TokKind.DEDENT, "", self.line, self.col))
            self.indent_stack.pop()
        self.tokens.append(Token(TokKind.EOF, "", self.line, self.col))
        return self.tokens

    def _lex_line(self, raw: str, lineno: int):
        if raw.strip().startswith("#"):
            return

        indent = len(raw) - len(raw.lstrip(' '))
        stripped = raw.strip()
        if stripped == "":
            self.line = lineno
            self.col = 1
            return

        if stripped:
            if indent > self.indent_stack[-1]:
                self.indent_stack.append(indent)
                self.tokens.append(Token(TokKind.INDENT, "", lineno, 1))
            while indent < self.indent_stack[-1]:
                self.indent_stack.pop()
                self.tokens.append(Token(TokKind.DEDENT, "", lineno, 1))

        self.line = lineno
        self.col = indent + 1
        s = stripped
        p = 0

        def emit(kind, val=""):
            self.tokens.append(Token(kind, val, lineno, self.col))

        while p < len(s):
            ch = s[p]

            if ch.isalpha() or ch == '_' or ch == '/':
                start = p
                while p < len(s) and (s[p].isalnum() or s[p] in "_/"):
                    p += 1
                lex = s[start:p]
                kind = KEYWORDS.get(lex, TokKind.IDENT)
                emit(kind, lex)
                self.col += (p - start)
                continue

            if ch.isdigit() or ch in "te":
                start = p
                seen_dot = False
                while p < len(s):
                    c = s[p]
                    if c == '.':
                        if p+1 < len(s) and s[p:p+3] == '..':
                            break
                        if seen_dot: break
                        seen_dot = True
                        p += 1
                    elif c.isdigit() or c in "te":
                        p += 1
                    else:
                        break
                lexnum = s[start:p]
                if p+3 <= len(s) and s[p:p+3] == "b12":
                    p += 3
                    emit(TokKind.INT, lexnum + ".b12")
                    self.col += (p - start)
                    continue
                if seen_dot:
                    emit(TokKind.FLOAT, lexnum)
                else:
                    emit(TokKind.INT, lexnum)
                self.col += (p - start)
                continue

            if ch == '"':
                start = p
                p += 1
                buf = []
                while p < len(s) and s[p] != '"':
                    if s[p] == '\\' and p+1 < len(s):
                        esc = s[p+1]
                        mapping = {'n':'\n','t':'\t','"':'"','\\':'\\'}
                        buf.append(mapping.get(esc, esc))
                        p += 2
                    else:
                        buf.append(s[p]); p += 1
                if p >= len(s) or s[p] != '"':
                    raise SyntaxError(f"Unterminated string at line {lineno}")
                p += 1
                emit(TokKind.STRING, ''.join(buf))
                self.col += (p - start)
                continue

            if s.startswith("..", p):
                emit(TokKind.RANGE, ".."); p += 2; self.col += 2; continue
            if ch == ':': emit(TokKind.COLON, ":"); p+=1; self.col+=1; continue
            if ch == ',': emit(TokKind.COMMA, ","); p+=1; self.col+=1; continue
            if ch == '(': emit(TokKind.LPAREN, "("); p+=1; self.col+=1; continue
            if ch == ')': emit(TokKind.RPAREN, ")"); p+=1; self.col+=1; continue
            if ch == '+': emit(TokKind.PLUS, "+"); p+=1; self.col+=1; continue
            if ch == '-': emit(TokKind.MINUS, "-"); p+=1; self.col+=1; continue
            if ch == '*': emit(TokKind.STAR, "*"); p+=1; self.col+=1; continue
            if ch == '/': emit(TokKind.SLASH, "/"); p+=1; self.col+=1; continue
            if ch == '=': emit(TokKind.ASSIGN, "="); p+=1; self.col+=1; continue

            if ch in ' \t':
                p += 1; self.col += 1; continue

            raise SyntaxError(f"Unexpected character '{ch}' at line {lineno}, col {self.col}")

        self.tokens.append(Token(TokKind.NEWLINE, "", lineno, self.col))
