from common import (BaseLexer, Token, LexicalError, classify_word,
                    TT_NUM, TT_ASSIGNOP, TT_RELOP, TT_ADDOP, TT_MULOP,
                    TT_LPAREN, TT_RPAREN, TT_LBRACKET, TT_RBRACKET,
                    TT_SEMICOLON, TT_COMMA, TT_COLON,
                    TT_DOT, TT_DOTDOT, TT_EOF, print_tokens)

START      = 'START'
IN_ID      = 'IN_ID'
IN_INT     = 'IN_INT'
IN_FRAC    = 'IN_FRAC'
IN_EXP_S   = 'IN_EXP_S'     
IN_EXP_SN  = 'IN_EXP_SN'    
IN_EXP     = 'IN_EXP'
IN_COMMENT = 'IN_COMMENT'
SAW_COLON  = 'SAW_COLON'
SAW_LT     = 'SAW_LT'
SAW_GT     = 'SAW_GT'
SAW_DOT    = 'SAW_DOT'

SINGLE = {
    '+': TT_ADDOP,    '-': TT_ADDOP,
    '*': TT_MULOP,    '/': TT_MULOP,
    '=': TT_RELOP,
    '(': TT_LPAREN,   ')': TT_RPAREN,
    '[': TT_LBRACKET, ']': TT_RBRACKET,
    ';': TT_SEMICOLON, ',': TT_COMMA,
}


class StateBased_Lexer(BaseLexer):

    def next_token(self):
        state  = START
        lexeme = ''
        sl     = self.line    
        while True:

            if state == START:
                ch = self._peek()
                if ch == '':
                    return Token(TT_EOF, 'EOF', line=self.line)
                if ch in ' \t\r\n':
                    self._advance(); continue   # skip whitespace
                sl = self.line
                self._advance()                 # consume first char

                if ch == '{':
                    state = IN_COMMENT; continue
                if ch.isalpha() or ch == '_':
                    lexeme = ch; state = IN_ID; continue
                if ch.isdigit():
                    lexeme = ch; state = IN_INT; continue
                if ch in SINGLE:
                    return Token(SINGLE[ch], ch, line=sl)
                if ch == ':':  lexeme = ':'; state = SAW_COLON; continue
                if ch == '<':  lexeme = '<'; state = SAW_LT;    continue
                if ch == '>':  lexeme = '>'; state = SAW_GT;    continue
                if ch == '.':  lexeme = '.'; state = SAW_DOT;   continue
                raise LexicalError(f"Line {sl}: unknown character '{ch}'")

            # ── Comment: consume until '}' ────────────────────
            elif state == IN_COMMENT:
                ch = self._peek()
                if ch == '':
                    raise LexicalError("Unterminated comment at end of file")
                if ch == '{':
                    raise LexicalError(f"Line {self.line}: nested '{{' inside comment")
                self._advance()
                if ch == '}':
                    state = START   # comment closed, restart

            # ── Identifier / keyword ──────────────────────────
            elif state == IN_ID:
                ch = self._peek()
                if ch != '' and (ch.isalnum() or ch == '_'):
                    lexeme += self._advance()
                else:
                    return classify_word(lexeme, sl)

            # ── Integer digits ────────────────────────────────
            elif state == IN_INT:
                ch = self._peek()
                if ch.isdigit():
                    lexeme += self._advance()
                elif ch == '.' and self._peek(1) == '.':
                    # upcoming ".." is array-range token, not decimal
                    return Token(TT_NUM, lexeme, int(lexeme), sl)
                elif ch == '.':
                    self._advance()
                    if self._peek().isdigit():
                        lexeme += '.'; state = IN_FRAC
                    else:
                        self._unget('.') 
                        return Token(TT_NUM, lexeme, int(lexeme), sl)
                elif ch in ('E', 'e'):
                    lexeme += self._advance(); state = IN_EXP_S
                else:
                    return Token(TT_NUM, lexeme, int(lexeme), sl)

            # ── Fractional digits ─────────────────────────────
            elif state == IN_FRAC:
                ch = self._peek()
                if ch.isdigit():
                    lexeme += self._advance()
                elif ch in ('E', 'e'):
                    lexeme += self._advance(); state = IN_EXP_S
                else:
                    return Token(TT_NUM, lexeme, float(lexeme), sl)

            # ── After 'E': expect sign or digit ───────────────
            elif state == IN_EXP_S:
                ch = self._peek()
                if ch in ('+', '-'):
                    lexeme += self._advance(); state = IN_EXP_SN
                elif ch.isdigit():
                    lexeme += self._advance(); state = IN_EXP
                else:
                    raise LexicalError(f"Line {sl}: bad exponent in '{lexeme}'")

            # ── After 'E+'/'-': expect digit ──────────────────
            elif state == IN_EXP_SN:
                ch = self._peek()
                if ch.isdigit():
                    lexeme += self._advance(); state = IN_EXP
                else:
                    raise LexicalError(f"Line {sl}: bad exponent in '{lexeme}'")

            # ── Exponent digits ───────────────────────────────
            elif state == IN_EXP:
                ch = self._peek()
                if ch.isdigit():
                    lexeme += self._advance()
                else:
                    return Token(TT_NUM, lexeme, float(lexeme), sl)

            # ── ':' or ':=' ───────────────────────────────────
            elif state == SAW_COLON:
                if self._peek() == '=':
                    self._advance()
                    return Token(TT_ASSIGNOP, ':=', line=sl)
                return Token(TT_COLON, ':', line=sl)

            # ── '<', '<=', '<>' ───────────────────────────────
            elif state == SAW_LT:
                ch = self._peek()
                if ch == '=': self._advance(); return Token(TT_RELOP, '<=', line=sl)
                if ch == '>': self._advance(); return Token(TT_RELOP, '<>', line=sl)
                return Token(TT_RELOP, '<', line=sl)

            # ── '>' or '>=' ───────────────────────────────────
            elif state == SAW_GT:
                if self._peek() == '=':
                    self._advance(); return Token(TT_RELOP, '>=', line=sl)
                return Token(TT_RELOP, '>', line=sl)

            # ── '.' or '..' ───────────────────────────────────
            elif state == SAW_DOT:
                if self._peek() == '.':
                    self._advance(); return Token(TT_DOTDOT, '..', line=sl)
                return Token(TT_DOT, '.', line=sl)


# ── Quick demo ────────────────────────────────────────────────
if __name__ == '__main__':
    src = "program test; var x:integer; begin x := 3 + 4 end."
    print_tokens(StateBased_Lexer(src).tokenize_all(),
                 "Approach 1 — State-Based DFA")