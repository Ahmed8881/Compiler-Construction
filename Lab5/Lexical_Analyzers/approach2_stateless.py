# ============================================================
# approach2_stateless.py  —  Stateless (one function per token)
# ============================================================
# How it works:
#   No state variable. next_token() peeks at the first char
#   and calls the right scan_* helper directly.
#   Each helper only knows about its own token type.
# ============================================================

from common import (BaseLexer, Token, LexicalError, classify_word,
                    TT_NUM, TT_ASSIGNOP, TT_RELOP, TT_ADDOP, TT_MULOP,
                    TT_LPAREN, TT_RPAREN, TT_LBRACKET, TT_RBRACKET,
                    TT_SEMICOLON, TT_COMMA, TT_COLON,
                    TT_DOT, TT_DOTDOT, TT_EOF, print_tokens)


class Stateless_Lexer(BaseLexer):

    # ── Skip whitespace and { } comments ─────────────────────
    def _skip(self):
        while True:
            ch = self._peek()
            if ch == '':
                return
            if ch in ' \t\r\n':
                self._advance()
            elif ch == '{':
                self._advance()           # consume '{'
                while True:
                    c = self._peek()
                    if c == '':
                        raise LexicalError("Unterminated comment")
                    if c == '{':
                        raise LexicalError(f"Line {self.line}: nested '{{' in comment")
                    self._advance()
                    if c == '}':
                        break             # comment closed
            else:
                break

    # ── Scan an identifier or keyword ────────────────────────
    def _scan_id(self, sl):
        word = ''
        while self._peek() != '' and (self._peek().isalnum() or self._peek() == '_'):
            word += self._advance()
        return classify_word(word, sl)

    # ── Scan a number (integer or real) ──────────────────────
    def _scan_num(self, sl):
        lex = ''
        real = False

        # integer part
        while self._peek().isdigit():
            lex += self._advance()

        # optional fraction  (watch out for ".." array range)
        if self._peek() == '.' and self._peek(1) != '.':
            if self._peek(1).isdigit():
                lex += self._advance()    # consume '.'
                real = True
                while self._peek().isdigit():
                    lex += self._advance()

        # optional exponent
        if self._peek() in ('E', 'e'):
            lex += self._advance(); real = True
            if self._peek() in ('+', '-'):
                lex += self._advance()
            if not self._peek().isdigit():
                raise LexicalError(f"Line {sl}: bad exponent in '{lex}'")
            while self._peek().isdigit():
                lex += self._advance()

        val = float(lex) if real else int(lex)
        return Token(TT_NUM, lex, val, sl)

    # ── Scan :  or := ─────────────────────────────────────────
    def _scan_colon(self, sl):
        self._advance()                   # consume ':'
        if self._peek() == '=':
            self._advance()
            return Token(TT_ASSIGNOP, ':=', line=sl)
        return Token(TT_COLON, ':', line=sl)

    # ── Scan <  <=  <> ────────────────────────────────────────
    def _scan_lt(self, sl):
        self._advance()                   # consume '<'
        if self._peek() == '=': self._advance(); return Token(TT_RELOP, '<=', line=sl)
        if self._peek() == '>': self._advance(); return Token(TT_RELOP, '<>', line=sl)
        return Token(TT_RELOP, '<', line=sl)

    # ── Scan >  >= ────────────────────────────────────────────
    def _scan_gt(self, sl):
        self._advance()                   # consume '>'
        if self._peek() == '=': self._advance(); return Token(TT_RELOP, '>=', line=sl)
        return Token(TT_RELOP, '>', line=sl)

    # ── Scan .  .. ────────────────────────────────────────────
    def _scan_dot(self, sl):
        self._advance()                   # consume first '.'
        if self._peek() == '.': self._advance(); return Token(TT_DOTDOT, '..', line=sl)
        return Token(TT_DOT, '.', line=sl)

    # ── Main dispatch ─────────────────────────────────────────
    def next_token(self):
        self._skip()
        sl = self.line
        ch = self._peek()

        if ch == '':         return Token(TT_EOF, 'EOF', line=sl)
        if ch.isalpha() or ch == '_': return self._scan_id(sl)
        if ch.isdigit():     return self._scan_num(sl)
        if ch == ':':        return self._scan_colon(sl)
        if ch == '<':        return self._scan_lt(sl)
        if ch == '>':        return self._scan_gt(sl)
        if ch == '.':        return self._scan_dot(sl)

        # single-character tokens
        self._advance()
        single = {
            '+': TT_ADDOP,    '-': TT_ADDOP,
            '*': TT_MULOP,    '/': TT_MULOP,
            '=': TT_RELOP,
            '(': TT_LPAREN,   ')': TT_RPAREN,
            '[': TT_LBRACKET, ']': TT_RBRACKET,
            ';': TT_SEMICOLON, ',': TT_COMMA,
        }
        if ch in single:
            return Token(single[ch], ch, line=sl)

        raise LexicalError(f"Line {sl}: unknown character '{ch}'")


# ── Quick demo ────────────────────────────────────────────────
if __name__ == '__main__':
    src = "program test; var x:integer; begin x := 3 + 4 end."
    print_tokens(Stateless_Lexer(src).tokenize_all(),
                 "Approach 2 — Stateless")