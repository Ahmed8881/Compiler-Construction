from common import *
class StateBased_Lexer(BaseLexer):

    def next_token(self):
        state  = 'START'
        lexeme = ''
        line   = self.line     

        while True:
            if state == 'START':
                self.skip()                    
                if self._peek() == '':
                    return Token(TT_EOF, 'EOF', line=self.line)
                line = self.line
                ch   = self._advance()         

                if ch in SINGLE_CHAR:           return Token(SINGLE_CHAR[ch], ch, line=line)
                if ch.isalpha() or ch == '_':   lexeme = ch; state = 'ID';    continue
                if ch.isdigit():                lexeme = ch; state = 'INT';   continue
                if ch == ':':                   lexeme = ch; state = 'COLON'; continue
                if ch == '<':                   lexeme = ch; state = 'LT';    continue
                if ch == '>':                   lexeme = ch; state = 'GT';    continue
                if ch == '.':                   lexeme = ch; state = 'DOT';   continue
                raise LexicalError(f"Line {line}: unknown character '{ch}'")

            elif state == 'ID':
                if self._peek() != '' and (self._peek().isalnum() or self._peek() == '_'):
                    lexeme += self._advance()
                else:
                    return self.scan_word(lexeme, line)   

            elif state == 'INT':
                if self._peek().isdigit():
                    lexeme += self._advance()
                else:
                    return self.scan_num(lexeme, line)

            elif state == 'COLON':
                if self._peek() == '=':
                    self._advance(); return Token(TT_ASSIGNOP, ':=', line=line)
                return Token(TT_COLON, ':', line=line)

            elif state == 'LT':
                if self._peek() == '=': self._advance(); return Token(TT_RELOP, '<=', line=line)
                if self._peek() == '>': self._advance(); return Token(TT_RELOP, '<>', line=line)
                return Token(TT_RELOP, '<', line=line)

            elif state == 'GT':
                if self._peek() == '=': self._advance(); return Token(TT_RELOP, '>=', line=line)
                return Token(TT_RELOP, '>', line=line)

            elif state == 'DOT':
                if self._peek() == '.': self._advance(); return Token(TT_DOTDOT, '..', line=line)
                return Token(TT_DOT, '.', line=line)


if __name__ == '__main__':
    src = "program test; var x:integer; begin x := 3 + 4 end."
    print_tokens(StateBased_Lexer(src).tokenize_all(), "Approach 1 — State-Based DFA")