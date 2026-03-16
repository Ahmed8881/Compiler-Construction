# ──────────────────────────────────────────────────────────────
# approach3_transition_table.py  —  Table-driven DFA
# ──────────────────────────────────────────────────────────────
# Idea: store ALL transitions in a 2-D table.
#   table[current_state][char_class] = next_state
# The driver loop just reads a character, looks up the table,
# and moves to the next state — NO if/elif logic inside loop.
#
# BONUS: CompressedTable_Lexer keeps only the non-error cells
#        in a dictionary — same result but uses less memory.
# ──────────────────────────────────────────────────────────────

from common import *

# ── Step 1: give every character a class number ───────────────
#    (this replaces a big if/elif chain inside the loop)

CC = {ch: i for i, ch in enumerate('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdfghjklmnopqrstuvwxyz_', 0)}
# Simpler approach: classify on-the-fly with a function

def cc(ch):
    """Map one character to a small integer (character class)."""
    if ch == '':          return 0   # EOF
    if ch in ('E','e'):   return 1   # exponent letter (also a letter)
    if ch.isalpha() or ch == '_': return 2   # letter
    if ch.isdigit():      return 3   # digit
    return {
        '+':4,  '-':5,  '*':6,  '/':7,  '=':8,
        '<':9,  '>':10, ':':11, '.':12,
        '(':13, ')':14, '[':15, ']':16,
        ';':17, ',':18,
        '{':19, '}':20,
    }.get(ch, 21)          # 21 = unknown

# Number of character classes
N = 22

# ── Step 2: name the DFA states ───────────────────────────────

# Non-accepting (working) states
(S,   ID,  INT,  FRAC,
 EXPS, EXPSN, EXP,
 CMT, COL, LT,  GT,  DOT) = range(12)

# Accepting states (≥ 100  →  stop the loop and return a token)
(A_ID,  A_INT, A_REAL,
 A_ASSIGN, A_COLON,
 A_EQ,  A_LT,  A_LE,  A_NE,  A_GT,  A_GE,
 A_PLUS, A_MINUS, A_STAR, A_SLASH,
 A_LPAR, A_RPAR, A_LBRK, A_RBRK,
 A_SEMI, A_COMMA,
 A_DOT,  A_DOTDOT, A_EOF) = range(100, 124)

ERR = 200   # error state

# ── Step 3: build the transition table ────────────────────────

T = [[ERR]*N for _ in range(12)]   # T[state][char_class] = next_state

#          EOF  E    LTR  DIG  +       -       *       /
T[S]    = [A_EOF,A_EOF,ERR,ERR,A_PLUS,A_MINUS,A_STAR,A_SLASH,
#          =     <    >     :    .
           A_EQ, LT,  GT,  COL, DOT,
#          (       )       [       ]       ;       ,       {    }    ?
           A_LPAR,A_RPAR,A_LBRK,A_RBRK,A_SEMI,A_COMMA,CMT, ERR, ERR]
T[S][1] = ERR   # 'E'/'e' at start is a letter
T[S][2] = ID    # letter → start identifier
T[S][1] = ID    # E/e   → start identifier too
T[S][3] = INT   # digit → start number

# ID: letters and digits stay in ID state
for cls in (1, 2, 3):   T[ID][cls] = ID

# INT: digits stay; '.' may start fraction; E starts exponent
T[INT][3]  = INT   # more digits
T[INT][12] = FRAC  # '.' → fraction
T[INT][1]  = EXPS  # E/e → exponent

# FRAC: digits stay; E starts exponent
T[FRAC][3] = FRAC
T[FRAC][1] = EXPS

# EXP_START: '+' or '-' → sign state;  digit → exponent digits
T[EXPS][4]  = EXPSN   # '+'
T[EXPS][5]  = EXPSN   # '-'
T[EXPS][3]  = EXP

# EXP_SIGN: only a digit is valid
T[EXPSN][3] = EXP

# EXP: more digits
T[EXP][3] = EXP

# COMMENT: everything stays in comment except '}' (close) and '{' (error)
for cls in range(N):   T[CMT][cls] = CMT
T[CMT][20] = S      # '}' closes the comment → back to START
T[CMT][19] = ERR    # '{' inside comment is illegal
T[CMT][0]  = ERR    # EOF inside comment is illegal

# COL: '=' makes ':=',  anything else → plain ':'
T[COL][8] = A_ASSIGN

# LT: '=' → '<=',  '>' → '<>'
T[LT][8]  = A_LE
T[LT][10] = A_NE

# GT: '=' → '>='
T[GT][8] = A_GE

# DOT: '.' → '..'
T[DOT][12] = A_DOTDOT

# States that retract (put the current char back) when table says ERR
RETRACT = {ID:A_ID, INT:A_INT, FRAC:A_REAL, EXP:A_REAL,
           COL:A_COLON, LT:A_LT, GT:A_GT, DOT:A_DOT}

# Map accepting state → Token
def _make_token(ac, lexeme, line):
    if ac == A_ID:   return BaseLexer.scan_word(None, lexeme, 0)   # placeholder
    # we call scan_word differently below; keep it simple:
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


# ── Step 4: the driver loop (shared by both classes below) ────

def _drive(lexer, lookup):
    """
    lookup(state, char_class) → next_state
    This same function drives both the full-table and compressed-table lexers.
    """
    lexer.skip()                    # drop whitespace / comments
    state  = S
    lexeme = ''
    line   = lexer.line

    while True:
        ch  = lexer._peek()

        # special case: '1..10' — don't consume '.' as decimal point
        if state == INT and ch == '.' and lexer._peek(1) == '.':
            return Token(TT_NUM, lexeme, int(lexeme), line)

        cls = cc(ch)
        ns  = lookup(state, cls)

        if ns == ERR:
            # if current state can retract, accept without consuming ch
            if state in RETRACT:
                ac = RETRACT[state]
                if ac == A_ID:
                    return BaseLexer.scan_word(lexer, lexeme, line)
                return _make_token(ac, lexeme, line)
            raise LexicalError(
                f"Line {line}: unexpected '{ch}' (state={state}, so far='{lexeme}')")

        # consume character (but not inside a comment — don't add to lexeme)
        if ch != '':
            lexer._advance()
            if state != CMT:
                lexeme += ch

        prev_state = state
        state = ns

        # accepting state → return token
        if state >= 100:
            if state == A_ID:
                return BaseLexer.scan_word(lexer, lexeme, line)
            return _make_token(state, lexeme, line)

        # comment just closed (CMT → S): reset lexeme, re-skip whitespace
        if prev_state == CMT and state == S:
            lexeme = ''
            lexer.skip()
            line = lexer.line


# ── Approach 3a: Full transition table ────────────────────────
class TransitionTable_Lexer(BaseLexer):
    def next_token(self):
        return _drive(self, lambda s, c: T[s][c])


# ── Approach 3b: Compressed table (Bonus) ─────────────────────
class CompressedTable_Lexer(BaseLexer):
    # Store only the non-error entries in a dict (saves memory)
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


# ── demo ──────────────────────────────────────────────────────
if __name__ == '__main__':
    src = "program test; var x:integer; begin x := 3 + 4 end."
    print_tokens(TransitionTable_Lexer(src).tokenize_all(), "Approach 3 — Transition Table")
    print("── Bonus: Compressed Table ──")
    CompressedTable_Lexer.stats()
    print_tokens(CompressedTable_Lexer(src).tokenize_all(), "Bonus — Compressed Table")