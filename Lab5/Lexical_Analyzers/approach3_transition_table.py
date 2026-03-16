# ============================================================
# approach3_transition_table.py  —  Table-driven DFA
# ============================================================
# How it works:
#   A 2-D table  TABLE[state][char_class] = next_state
#   is built once at import time.  The driver loop just reads
#   characters, classifies them, and does a table lookup.
#   No if/elif logic inside the loop itself.
#
# BONUS: CompressedTable_Lexer stores only the non-error cells
#        in a dict — same result, less memory.
# ============================================================

from common import (BaseLexer, Token, LexicalError, classify_word,
                    TT_NUM, TT_ASSIGNOP, TT_RELOP, TT_ADDOP, TT_MULOP,
                    TT_LPAREN, TT_RPAREN, TT_LBRACKET, TT_RBRACKET,
                    TT_SEMICOLON, TT_COMMA, TT_COLON,
                    TT_DOT, TT_DOTDOT, TT_EOF, print_tokens)

# ── Character classes (columns of the table) ─────────────────
(CC_LETTER, CC_DIGIT, CC_E,
 CC_PLUS, CC_MINUS, CC_STAR, CC_SLASH,
 CC_EQ, CC_LT, CC_GT, CC_COLON, CC_DOT,
 CC_LPAREN, CC_RPAREN, CC_LBRACK, CC_RBRACK,
 CC_SEMI, CC_COMMA,
 CC_LBRACE, CC_RBRACE,
 CC_OTHER, CC_EOF) = range(22)

def char_class(ch):
    if ch == '':          return CC_EOF
    if ch in ('E','e'):   return CC_E       # also a letter, handled first
    if ch.isalpha() or ch == '_': return CC_LETTER
    if ch.isdigit():      return CC_DIGIT
    return {
        '+':CC_PLUS,  '-':CC_MINUS, '*':CC_STAR,   '/':CC_SLASH,
        '=':CC_EQ,    '<':CC_LT,    '>':CC_GT,     ':':CC_COLON,
        '.':CC_DOT,   '(':CC_LPAREN,')':CC_RPAREN,
        '[':CC_LBRACK,']':CC_RBRACK,';':CC_SEMI,   ',':CC_COMMA,
        '{':CC_LBRACE,'}':CC_RBRACE,
    }.get(ch, CC_OTHER)

# ── DFA states ────────────────────────────────────────────────
(ST_START,
 ST_ID, ST_INT, ST_FRAC,
 ST_EXP_S, ST_EXP_SN, ST_EXP,
 ST_COMMENT,
 ST_COLON, ST_LT, ST_GT, ST_DOT) = range(12)

# Accepting states (≥ 100)
(AC_ID, AC_INT, AC_REAL,
 AC_ASSIGN, AC_COLON,
 AC_EQ, AC_LT, AC_LE, AC_NE, AC_GT, AC_GE,
 AC_PLUS, AC_MINUS, AC_STAR, AC_SLASH,
 AC_LPAR, AC_RPAR, AC_LBRK, AC_RBRK,
 AC_SEMI, AC_COMMA,
 AC_DOT, AC_DOTDOT,
 AC_EOF) = range(100, 124)

ERR = 200

def is_accept(s): return 100 <= s < ERR

# ── Build the transition table ────────────────────────────────
T = [[ERR]*22 for _ in range(12)]

def _build():
    # START
    T[ST_START][CC_LETTER]=ST_ID;   T[ST_START][CC_E]=ST_ID
    T[ST_START][CC_DIGIT] =ST_INT
    T[ST_START][CC_PLUS]  =AC_PLUS; T[ST_START][CC_MINUS]=AC_MINUS
    T[ST_START][CC_STAR]  =AC_STAR; T[ST_START][CC_SLASH]=AC_SLASH
    T[ST_START][CC_EQ]    =AC_EQ
    T[ST_START][CC_LT]    =ST_LT;   T[ST_START][CC_GT]  =ST_GT
    T[ST_START][CC_COLON] =ST_COLON;T[ST_START][CC_DOT] =ST_DOT
    T[ST_START][CC_LPAREN]=AC_LPAR; T[ST_START][CC_RPAREN]=AC_RPAR
    T[ST_START][CC_LBRACK]=AC_LBRK; T[ST_START][CC_RBRACK]=AC_RBRK
    T[ST_START][CC_SEMI]  =AC_SEMI; T[ST_START][CC_COMMA]=AC_COMMA
    T[ST_START][CC_LBRACE]=ST_COMMENT
    T[ST_START][CC_EOF]   =AC_EOF

    # ID: letters/digits stay in ID
    T[ST_ID][CC_LETTER]=ST_ID; T[ST_ID][CC_E]=ST_ID; T[ST_ID][CC_DIGIT]=ST_ID

    # INT
    T[ST_INT][CC_DIGIT]=ST_INT; T[ST_INT][CC_DOT]=ST_FRAC; T[ST_INT][CC_E]=ST_EXP_S

    # FRAC
    T[ST_FRAC][CC_DIGIT]=ST_FRAC; T[ST_FRAC][CC_E]=ST_EXP_S

    # EXP
    T[ST_EXP_S][CC_PLUS]=ST_EXP_SN; T[ST_EXP_S][CC_MINUS]=ST_EXP_SN
    T[ST_EXP_S][CC_DIGIT]=ST_EXP
    T[ST_EXP_SN][CC_DIGIT]=ST_EXP
    T[ST_EXP][CC_DIGIT]=ST_EXP

    # COMMENT: everything stays in comment except '}' (close) and '{' (error)
    for cc in range(22):
        T[ST_COMMENT][cc] = ST_COMMENT
    T[ST_COMMENT][CC_RBRACE]=ST_START   # close comment
    T[ST_COMMENT][CC_LBRACE]=ERR        # nested '{'
    T[ST_COMMENT][CC_EOF]   =ERR

    # COLON
    T[ST_COLON][CC_EQ]=AC_ASSIGN

    # LT
    T[ST_LT][CC_EQ]=AC_LE; T[ST_LT][CC_GT]=AC_NE

    # GT
    T[ST_GT][CC_EQ]=AC_GE

    # DOT
    T[ST_DOT][CC_DOT]=AC_DOTDOT

_build()

# States that accept by retracting (put current char back)
RETRACT = {
    ST_ID:ST_ID, ST_INT:ST_INT, ST_FRAC:ST_FRAC, ST_EXP:ST_EXP,
    ST_COLON:ST_COLON, ST_LT:ST_LT, ST_GT:ST_GT, ST_DOT:ST_DOT,
}
RETRACT_AC = {
    ST_ID:AC_ID, ST_INT:AC_INT, ST_FRAC:AC_REAL, ST_EXP:AC_REAL,
    ST_COLON:AC_COLON, ST_LT:AC_LT, ST_GT:AC_GT, ST_DOT:AC_DOT,
}

# Map accepting state → Token
def _make(ac, lexeme, line):
    if ac == AC_ID:
        return classify_word(lexeme, line)
    if ac == AC_INT:
        return Token(TT_NUM, lexeme, int(lexeme), line)
    if ac == AC_REAL:
        return Token(TT_NUM, lexeme, float(lexeme), line)
    simple = {
        AC_ASSIGN:Token(TT_ASSIGNOP,  ':=', line=line),
        AC_COLON: Token(TT_COLON,     ':',  line=line),
        AC_EQ:    Token(TT_RELOP,     '=',  line=line),
        AC_LT:    Token(TT_RELOP,     '<',  line=line),
        AC_LE:    Token(TT_RELOP,     '<=', line=line),
        AC_NE:    Token(TT_RELOP,     '<>', line=line),
        AC_GT:    Token(TT_RELOP,     '>',  line=line),
        AC_GE:    Token(TT_RELOP,     '>=', line=line),
        AC_PLUS:  Token(TT_ADDOP,     '+',  line=line),
        AC_MINUS: Token(TT_ADDOP,     '-',  line=line),
        AC_STAR:  Token(TT_MULOP,     '*',  line=line),
        AC_SLASH: Token(TT_MULOP,     '/',  line=line),
        AC_LPAR:  Token(TT_LPAREN,    '(',  line=line),
        AC_RPAR:  Token(TT_RPAREN,    ')',  line=line),
        AC_LBRK: Token(TT_LBRACKET,   '[',  line=line),
        AC_RBRK: Token(TT_RBRACKET,   ']',  line=line),
        AC_SEMI:  Token(TT_SEMICOLON, ';',  line=line),
        AC_COMMA: Token(TT_COMMA,     ',',  line=line),
        AC_DOT:   Token(TT_DOT,       '.',  line=line),
        AC_DOTDOT:Token(TT_DOTDOT,    '..', line=line),
        AC_EOF:   Token(TT_EOF,       'EOF',line=line),
    }
    return simple[ac]


# ── Driver (shared by both lexer classes) ─────────────────────
def _run(lexer, lookup):
    """
    Core table-driven loop.
    lookup(state, cc) → next_state   (full table or compressed dict)
    """
    # skip whitespace
    while lexer._peek() in (' ','\t','\r','\n'):
        lexer._advance()

    state = ST_START
    lexeme = ''
    sl = lexer.line

    while True:
        ch = lexer._peek()

        # Dot-dot special case: 1..10 — don't consume '.' as decimal point
        if state == ST_INT and ch == '.' and lexer._peek(1) == '.':
            return _make(AC_INT, lexeme, sl)

        cc = char_class(ch)
        ns = lookup(state, cc)

        if ns == ERR:
            if state in RETRACT_AC:
                return _make(RETRACT_AC[state], lexeme, sl)
            raise LexicalError(
                f"Line {sl}: unexpected '{ch}' (state={state}, lexeme='{lexeme}')")

        if ch != '' and state != ST_COMMENT:
            lexeme += ch
        if ch != '':
            lexer._advance()

        prev, state = state, ns

        if is_accept(state):
            return _make(state, lexeme, sl)

        # Comment just closed → reset and skip whitespace
        if prev == ST_COMMENT and state == ST_START:
            lexeme = ''
            while lexer._peek() in (' ','\t','\r','\n'):
                lexer._advance()
            sl = lexer.line


# ── Approach 3a: Full Table ───────────────────────────────────
class TransitionTable_Lexer(BaseLexer):
    def next_token(self):
        return _run(self, lambda s, cc: T[s][cc])


# ── Approach 3b: Compressed Table (Bonus) ─────────────────────
class CompressedTable_Lexer(BaseLexer):
    # Build sparse dict once at class level
    _sparse = {(s, cc): T[s][cc]
               for s in range(12) for cc in range(22)
               if T[s][cc] != ERR}

    def next_token(self):
        return _run(self, lambda s, cc: self._sparse.get((s, cc), ERR))

    @classmethod
    def stats(cls):
        total  = 12 * 22
        stored = len(cls._sparse)
        saved  = (1 - stored/total) * 100
        print(f"  Full table : {total} cells")
        print(f"  Stored     : {stored} non-error cells")
        print(f"  Savings    : {saved:.0f}% memory saved\n")


# ── Quick demo ────────────────────────────────────────────────
if __name__ == '__main__':
    src = "program test; var x:integer; begin x := 3 + 4 end."
    print_tokens(TransitionTable_Lexer(src).tokenize_all(),
                 "Approach 3 — Transition Table")
    print("── Compressed Table Bonus ──")
    CompressedTable_Lexer.stats()
    print_tokens(CompressedTable_Lexer(src).tokenize_all(),
                 "Bonus — Compressed Table")