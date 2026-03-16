# ──────────────────────────────────────────────────────────────
# approach1_state_based.py  —  Direct-coded DFA
# ──────────────────────────────────────────────────────────────
# Idea: one loop, one 'state' variable.
# Each character moves us to the next state.
# When a token is finished, return it immediately.
# ──────────────────────────────────────────────────────────────

from common import *

class StateBased_Lexer(BaseLexer):

    def next_token(self):
        state  = 'START'
        lexeme = ''
        line   = self.line      # line where this token begins

        while True:

            # ── waiting for the first character of a new token ─
            if state == 'START':
                self.skip()                     # drop whitespace/comments
                if self._peek() == '':
                    return Token(TT_EOF, 'EOF', line=self.line)
                line = self.line
                ch   = self._advance()          # consume first character

                if ch in SINGLE_CHAR:           return Token(SINGLE_CHAR[ch], ch, line=line)
                if ch.isalpha() or ch == '_':   lexeme = ch; state = 'ID';    continue
                if ch.isdigit():                lexeme = ch; state = 'INT';   continue
                if ch == ':':                   lexeme = ch; state = 'COLON'; continue
                if ch == '<':                   lexeme = ch; state = 'LT';    continue
                if ch == '>':                   lexeme = ch; state = 'GT';    continue
                if ch == '.':                   lexeme = ch; state = 'DOT';   continue
                raise LexicalError(f"Line {line}: unknown character '{ch}'")

            # ── reading an identifier ──────────────────────────
            elif state == 'ID':
                if self._peek() != '' and (self._peek().isalnum() or self._peek() == '_'):
                    lexeme += self._advance()
                else:
                    return self.scan_word(lexeme, line)   # classify & return

            # ── reading digits (integer part) ──────────────────
            elif state == 'INT':
                if self._peek().isdigit():
                    lexeme += self._advance()
                else:
                    # hand off to scan_num — it continues from where we are
                    return self.scan_num(lexeme, line)

            # ── ':' — could be ':=' ────────────────────────────
            elif state == 'COLON':
                if self._peek() == '=':
                    self._advance(); return Token(TT_ASSIGNOP, ':=', line=line)
                return Token(TT_COLON, ':', line=line)

            # ── '<' — could be '<=', '<>' ──────────────────────
            elif state == 'LT':
                if self._peek() == '=': self._advance(); return Token(TT_RELOP, '<=', line=line)
                if self._peek() == '>': self._advance(); return Token(TT_RELOP, '<>', line=line)
                return Token(TT_RELOP, '<', line=line)

            # ── '>' — could be '>=' ────────────────────────────
            elif state == 'GT':
                if self._peek() == '=': self._advance(); return Token(TT_RELOP, '>=', line=line)
                return Token(TT_RELOP, '>', line=line)

            # ── '.' — could be '..' ────────────────────────────
            elif state == 'DOT':
                if self._peek() == '.': self._advance(); return Token(TT_DOTDOT, '..', line=line)
                return Token(TT_DOT, '.', line=line)


# ── demo ──────────────────────────────────────────────────────
if __name__ == '__main__':
    src = "program test; var x:integer; begin x := 3 + 4 end."
    print_tokens(StateBased_Lexer(src).tokenize_all(), "Approach 1 — State-Based DFA")