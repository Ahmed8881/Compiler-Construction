# ──────────────────────────────────────────────────────────────
# approach2_stateless.py  —  Stateless (one function per token)
# ──────────────────────────────────────────────────────────────
# Idea: NO state variable at all.
# next_token() peeks at the first character and immediately
# calls the right helper function for that token type.
# Each helper only deals with one kind of token.
# ──────────────────────────────────────────────────────────────

from common import *

class Stateless_Lexer(BaseLexer):

    def next_token(self):
        self.skip()                         # drop whitespace / comments
        line = self.line
        ch   = self._peek()

        # EOF
        if ch == '':
            return Token(TT_EOF, 'EOF', line=line)

        # identifier or keyword  →  call scan_word from BaseLexer
        if ch.isalpha() or ch == '_':
            return self.scan_word(self._advance(), line)

        # number  →  call scan_num from BaseLexer
        if ch.isdigit():
            return self.scan_num(self._advance(), line)

        # ':' or ':='
        if ch == ':':
            self._advance()
            if self._peek() == '=':
                self._advance(); return Token(TT_ASSIGNOP, ':=', line=line)
            return Token(TT_COLON, ':', line=line)

        # '<'  '<='  '<>'
        if ch == '<':
            self._advance()
            if self._peek() == '=': self._advance(); return Token(TT_RELOP, '<=', line=line)
            if self._peek() == '>': self._advance(); return Token(TT_RELOP, '<>', line=line)
            return Token(TT_RELOP, '<', line=line)

        # '>'  '>='
        if ch == '>':
            self._advance()
            if self._peek() == '=': self._advance(); return Token(TT_RELOP, '>=', line=line)
            return Token(TT_RELOP, '>', line=line)

        # '.'  '..'
        if ch == '.':
            self._advance()
            if self._peek() == '.': self._advance(); return Token(TT_DOTDOT, '..', line=line)
            return Token(TT_DOT, '.', line=line)

        # any single-character token  (+ - * / = ( ) [ ] ; ,)
        if ch in SINGLE_CHAR:
            self._advance()
            return Token(SINGLE_CHAR[ch], ch, line=line)

        raise LexicalError(f"Line {line}: unknown character '{ch}'")


# ── demo ──────────────────────────────────────────────────────
if __name__ == '__main__':
    src = "program test; var x:integer; begin x := 3 + 4 end."
    print_tokens(Stateless_Lexer(src).tokenize_all(), "Approach 2 — Stateless")