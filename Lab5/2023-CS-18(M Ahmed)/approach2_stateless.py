from common import *
class Stateless_Lexer(BaseLexer):

    def next_token(self):
        self.skip()                        
        line = self.line
        ch   = self._peek()

        if ch == '':
            return Token(TT_EOF, 'EOF', line=line)

        if ch.isalpha() or ch == '_':
            return self.scan_word(self._advance(), line)

        if ch.isdigit():
            return self.scan_num(self._advance(), line)

        if ch == ':':
            self._advance()
            if self._peek() == '=':
                self._advance(); return Token(TT_ASSIGNOP, ':=', line=line)
            return Token(TT_COLON, ':', line=line)

        if ch == '<':
            self._advance()
            if self._peek() == '=': self._advance(); return Token(TT_RELOP, '<=', line=line)
            if self._peek() == '>': self._advance(); return Token(TT_RELOP, '<>', line=line)
            return Token(TT_RELOP, '<', line=line)

        if ch == '>':
            self._advance()
            if self._peek() == '=': self._advance(); return Token(TT_RELOP, '>=', line=line)
            return Token(TT_RELOP, '>', line=line)

        if ch == '.':
            self._advance()
            if self._peek() == '.': self._advance(); return Token(TT_DOTDOT, '..', line=line)
            return Token(TT_DOT, '.', line=line)

        if ch in SINGLE_CHAR:
            self._advance()
            return Token(SINGLE_CHAR[ch], ch, line=line)

        raise LexicalError(f"Line {line}: unknown character '{ch}'")


if __name__ == '__main__':
    src = "program test; var x:integer; begin x := 3 + 4 end."
    print_tokens(Stateless_Lexer(src).tokenize_all(), "Approach 2 — Stateless")