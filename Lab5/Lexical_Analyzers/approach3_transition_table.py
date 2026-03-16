from common import *
CC = {ch: i for i, ch in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdfghjklmnopqrstuvwxyz_', 0)}
def cc(ch):
    if ch == '':          return 0   
    if ch in ('E','e'):   return 1   
    if ch.isalpha() or ch == '_': return 2  
    if ch.isdigit():      return 3  
    return {
        '+':4,  '-':5,  '*':6,  '/':7,  '=':8,
        '<':9,  '>':10, ':':11, '.':12,
        '(':13, ')':14, '[':15, ']':16,
        ';':17, ',':18,
        '{':19, '}':20,
    }.get(ch, 21)          

N = 22
(S,   ID,  INT,  FRAC,
 EXPS, EXPSN, EXP,
 CMT, COL, LT,  GT,  DOT) = range(12)
(A_ID,  A_INT, A_REAL,
 A_ASSIGN, A_COLON,
 A_EQ,  A_LT,  A_LE,  A_NE,  A_GT,  A_GE,
 A_PLUS, A_MINUS, A_STAR, A_SLASH,
 A_LPAR, A_RPAR, A_LBRK, A_RBRK,
 A_SEMI, A_COMMA,
 A_DOT,  A_DOTDOT, A_EOF) = range(100, 124)
ERR = 200  

T = [[ERR]*N for _ in range(12)]  

T[S]    = [A_EOF,A_EOF,ERR,ERR,A_PLUS,A_MINUS,A_STAR,A_SLASH,
           A_EQ, LT,  GT,  COL, DOT,
           A_LPAR,A_RPAR,A_LBRK,A_RBRK,A_SEMI,A_COMMA,CMT, ERR, ERR]
T[S][1] = ERR  
T[S][2] = ID    
T[S][1] = ID   
T[S][3] = INT   

for cls in (1, 2, 3):   T[ID][cls] = ID

T[INT][3]  = INT   
T[INT][12] = FRAC  
T[INT][1]  = EXPS 

T[FRAC][3] = FRAC
T[FRAC][1] = EXPS

T[EXPS][4]  = EXPSN 
T[EXPS][5]  = EXPSN   
T[EXPS][3]  = EXP

T[EXPSN][3] = EXP

T[EXP][3] = EXP

for cls in range(N):   T[CMT][cls] = CMT
T[CMT][20] = S   
T[CMT][19] = ERR    
T[CMT][0]  = ERR   

T[COL][8] = A_ASSIGN

T[LT][8]  = A_LE
T[LT][10] = A_NE

T[GT][8] = A_GE

T[DOT][12] = A_DOTDOT

RETRACT = {ID:A_ID, INT:A_INT, FRAC:A_REAL, EXP:A_REAL,
           COL:A_COLON, LT:A_LT, GT:A_GT, DOT:A_DOT}

def _make_token(ac, lexeme, line):
    if ac == A_ID:   return BaseLexer.scan_word(None, lexeme, 0)  
    if ac == A_INT:  return Token(TT_NUM, lexeme, int(lexeme),   line)
    if ac == A_REAL: return Token(TT_NUM, lexeme, float(lexeme), line)
    table = {
        A_ASSIGN:(':=',TT_ASSIGNOP), A_COLON:(':',TT_COLON),
        A_EQ:    ('=', TT_RELOP),   A_LT:   ('<', TT_RELOP),
        A_LE:    ('<=',TT_RELOP),   A_NE:   ('<>',TT_RELOP),
        A_GT:    ('>',TT_RELOP),    A_GE:   ('>=',TT_RELOP),
        A_PLUS:  ('+', TT_ADDOP),   A_MINUS:('-', TT_ADDOP),
        A_STAR:  ('*', TT_MULOP),   A_SLASH:('/', TT_MULOP),
        A_LPAR:  ('(', TT_LPAREN),  A_RPAR: (')', TT_RPAREN),
        A_LBRK:  ('[', TT_LBRACKET),A_RBRK:(']', TT_RBRACKET),
        A_SEMI:  (';', TT_SEMICOLON),A_COMMA:(',',TT_COMMA),
        A_DOT:   ('.', TT_DOT),     A_DOTDOT:('..',TT_DOTDOT),
        A_EOF:   ('EOF',TT_EOF),
    }
    lex, tt = table[ac]
    return Token(tt, lex, line=line)



def _drive(lexer, lookup):
    """
    lookup(state, char_class) → next_state
    This same function drives both the full-table and compressed-table lexers.
    """
    lexer.skip()                  
    state  = S
    lexeme = ''
    line   = lexer.line

    while True:
        ch  = lexer._peek()
        if state == INT and ch == '.' and lexer._peek(1) == '.':
            return Token(TT_NUM, lexeme, int(lexeme), line)

        cls = cc(ch)
        ns  = lookup(state, cls)

        if ns == ERR:
            if state in RETRACT:
                ac = RETRACT[state]
                if ac == A_ID:
                    return BaseLexer.scan_word(lexer, lexeme, line)
                return _make_token(ac, lexeme, line)
            raise LexicalError(
                f"Line {line}: unexpected '{ch}' (state={state}, so far='{lexeme}')")

        if ch != '':
            lexer._advance()
            if state != CMT:
                lexeme += ch

        prev_state = state
        state = ns

        if state >= 100:
            if state == A_ID:
                return BaseLexer.scan_word(lexer, lexeme, line)
            return _make_token(state, lexeme, line)

        if prev_state == CMT and state == S:
            lexeme = ''
            lexer.skip()
            line = lexer.line


class TransitionTable_Lexer(BaseLexer):
    def next_token(self):
        return _drive(self, lambda s, c: T[s][c])


class CompressedTable_Lexer(BaseLexer):
    _sparse = {(s, c): T[s][c]
               for s in range(12) for c in range(N)
               if T[s][c] != ERR}

    def next_token(self):
        return _drive(self, lambda s, c: self._sparse.get((s, c), ERR))

    @classmethod
    def stats(cls):
        total  = 12 * N
        stored = len(cls._sparse)
        print(f"  Full table : {total} cells  |  "
              f"Stored: {stored}  |  "
              f"Saved: {(1-stored/total)*100:.0f}%\n")


if __name__ == '__main__':
    src = "program test; var x:integer; begin x := 3 + 4 end."
    print_tokens(TransitionTable_Lexer(src).tokenize_all(), "Approach 3 — Transition Table")
    print("── Bonus: Compressed Table ──")
    CompressedTable_Lexer.stats()
    print_tokens(CompressedTable_Lexer(src).tokenize_all(), "Bonus — Compressed Table")