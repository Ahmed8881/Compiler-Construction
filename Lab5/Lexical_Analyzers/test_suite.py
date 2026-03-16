# ============================================================
# test_suite.py  —  Tests for all three lexer approaches
# ============================================================

from common import (TT_KEYWORD, TT_ID, TT_NUM, TT_ASSIGNOP, TT_RELOP,
                    TT_ADDOP, TT_MULOP, TT_LPAREN, TT_RPAREN,
                    TT_LBRACKET, TT_RBRACKET, TT_SEMICOLON, TT_COMMA,
                    TT_COLON, TT_DOT, TT_DOTDOT, TT_EOF, LexicalError)

from approach1_state_based      import StateBased_Lexer
from approach2_stateless        import Stateless_Lexer
from approach3_transition_table import TransitionTable_Lexer, CompressedTable_Lexer

ALL = [StateBased_Lexer, Stateless_Lexer,
       TransitionTable_Lexer, CompressedTable_Lexer]

# ── test runner ───────────────────────────────────────────────
ok = fail = 0

def test(desc, src, expect_types=None, expect_lex=None, error=False):
    global ok, fail
    for Cls in ALL:
        try:
            toks = [t for t in Cls(src).tokenize_all() if t.type != TT_EOF]
        except Exception as e:
            if error:
                ok += 1
                print(f"  \033[32mPASS\033[0m  {Cls.__name__}: {desc}")
            else:
                fail += 1
                print(f"  \033[31mFAIL\033[0m  {Cls.__name__}: {desc} — {e}")
            continue

        if error:
            fail += 1
            print(f"  \033[31mFAIL\033[0m  {Cls.__name__}: {desc} — expected error")
            continue

        got_t = [t.type   for t in toks]
        got_l = [t.lexeme for t in toks]
        passed = True
        if expect_types  is not None and got_t != expect_types:  passed = False
        if expect_lex    is not None and got_l != expect_lex:     passed = False

        if passed:
            ok += 1
            print(f"  \033[32mPASS\033[0m  {Cls.__name__}: {desc}")
        else:
            fail += 1
            print(f"  \033[31mFAIL\033[0m  {Cls.__name__}: {desc}")
            if expect_types: print(f"        types exp: {expect_types}")
            if expect_types: print(f"        types got: {got_t}")


# ── 1. Keywords ───────────────────────────────────────────────
print("\n── Keywords ──────────────────────────────────────────────")
for kw in ['program','var','integer','real','array','of',
           'function','procedure','begin','end',
           'if','then','else','while','do','not']:
    test(f"kw '{kw}'", kw, expect_types=[TT_KEYWORD], expect_lex=[kw])

for kw,tt in [('or',TT_ADDOP),('and',TT_MULOP),('div',TT_MULOP),('mod',TT_MULOP)]:
    test(f"op-kw '{kw}'", kw, expect_types=[tt])

# ── 2. Identifiers ────────────────────────────────────────────
print("\n── Identifiers ───────────────────────────────────────────")
for name in ['x','abc','gcd','myVar','var2','x1y2z3','HelloWorld']:
    test(f"id '{name}'", name, expect_types=[TT_ID], expect_lex=[name])

# ── 3. Numbers ────────────────────────────────────────────────
print("\n── Numbers ───────────────────────────────────────────────")
for n,v in [('0',0),('42',42),('999',999)]:
    test(f"int {n}", n, expect_types=[TT_NUM])
for n in ['3.14','0.0','1.5E10','2.0E+3','9.9E-2']:
    test(f"real {n}", n, expect_types=[TT_NUM])

# ── 4. Operators ──────────────────────────────────────────────
print("\n── Operators ─────────────────────────────────────────────")
for op,tt in [('=',TT_RELOP),('<>',TT_RELOP),('<',TT_RELOP),
              ('<=',TT_RELOP),('>=',TT_RELOP),('>',TT_RELOP)]:
    test(f"relop '{op}'", op, expect_types=[tt], expect_lex=[op])
for op in ['+','-']: test(f"addop '{op}'", op, expect_types=[TT_ADDOP])
for op in ['*','/']: test(f"mulop '{op}'", op, expect_types=[TT_MULOP])
test(":=",   ':=', expect_types=[TT_ASSIGNOP])
test("colon",':',  expect_types=[TT_COLON])

# ── 5. Punctuation ────────────────────────────────────────────
print("\n── Punctuation ───────────────────────────────────────────")
for ch,tt in [('(',TT_LPAREN),(')',TT_RPAREN),
              ('[',TT_LBRACKET),(']',TT_RBRACKET),
              (';',TT_SEMICOLON),(',',TT_COMMA),
              ('.',TT_DOT),('..',TT_DOTDOT)]:
    test(f"'{ch}'", ch, expect_types=[tt])

# ── 6. DOTDOT in array context ────────────────────────────────
print("\n── DOTDOT in array ───────────────────────────────────────")
test("array [1..10] of integer",
     "array [ 1 .. 10 ] of integer",
     expect_types=[TT_KEYWORD,TT_LBRACKET,TT_NUM,TT_DOTDOT,
                   TT_NUM,TT_RBRACKET,TT_KEYWORD,TT_KEYWORD])

# ── 7. Comments ───────────────────────────────────────────────
print("\n── Comments ──────────────────────────────────────────────")
test("inline comment",    "{ hello } x",      expect_types=[TT_ID])
test("between tokens",    "begin { x } end",  expect_types=[TT_KEYWORD,TT_KEYWORD])
test("multi-line comment","x { a\n b } y",    expect_types=[TT_ID,TT_ID])

# ── 8. Full programs ──────────────────────────────────────────
print("\n── Full programs ─────────────────────────────────────────")
GCD = """\
program example(input, output);
var x, y: integer;
function gcd(a, b: integer): integer;
begin
    if b = 0 then gcd := a
    else gcd := gcd(b, a mod b)
end;
begin
    read(x, y);
    write(gcd(x, y))
end.
"""
test("GCD program (Fig A.1)", GCD)
test("array program",
     "program t; var a:array[1..5] of integer; begin a[1]:=9 end.")
test("while program",
     "program t; var i:integer; begin i:=1; while i<=10 do i:=i+1 end.")

# ── 9. Error cases ────────────────────────────────────────────
print("\n── Errors ────────────────────────────────────────────────")
test("nested comment",      "{ outer { inner } }", error=True)
test("unterminated comment","x := 5 { no close",   error=True)
test("bad exponent",        "1.5Eabc",              error=True)
test("unknown char '@'",    "@",                    error=True)

# ── Summary ───────────────────────────────────────────────────
print(f"\n{'='*52}")
print(f"  {ok + fail} tests — {ok} passed, {fail} failed")
if fail == 0:
    print("  \033[32mAll tests passed! ✓\033[0m")
else:
    print(f"  \033[31m{fail} FAILED\033[0m")
print(f"{'='*52}\n")