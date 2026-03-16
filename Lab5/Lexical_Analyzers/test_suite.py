from common import *
from approach1_state_based      import StateBased_Lexer
from approach2_stateless        import Stateless_Lexer
from approach3_transition_table import TransitionTable_Lexer, CompressedTable_Lexer

ALL_LEXERS = [StateBased_Lexer, Stateless_Lexer,
              TransitionTable_Lexer, CompressedTable_Lexer]

passed = failed = 0

def test(desc, src, expect_types=None, expect_error=False):
    global passed, failed
    for Cls in ALL_LEXERS:
        try:
            toks = [t for t in Cls(src).tokenize_all() if t.type != TT_EOF]
        except Exception as e:
            if expect_error:
                passed += 1
                print(f"  \033[32mPASS\033[0m  {Cls.__name__:30s} {desc}")
            else:
                failed += 1
                print(f"  \033[31mFAIL\033[0m  {Cls.__name__:30s} {desc}  ← {e}")
            continue

        if expect_error:
            failed += 1
            print(f"  \033[31mFAIL\033[0m  {Cls.__name__:30s} {desc}  ← expected error, got none")
            continue

        got = [t.type for t in toks]
        if expect_types is None or got == expect_types:
            passed += 1
            print(f"  \033[32mPASS\033[0m  {Cls.__name__:30s} {desc}")
        else:
            failed += 1
            print(f"  \033[31mFAIL\033[0m  {Cls.__name__:30s} {desc}")
            print(f"           expected: {expect_types}")
            print(f"           got:      {got}")


print("\n── Keywords ──────────────────────────────────────────────")
for kw in ['program','var','integer','real','array','of',
           'function','procedure','begin','end',
           'if','then','else','while','do','not']:
    test(f"'{kw}'", kw, [TT_KEYWORD])

test("'or'",  'or',  [TT_ADDOP])
test("'and'", 'and', [TT_MULOP])
test("'div'", 'div', [TT_MULOP])
test("'mod'", 'mod', [TT_MULOP])

print("\n── Identifiers ───────────────────────────────────────────")
for name in ['x', 'abc', 'gcd', 'myVar', 'var2', 'HelloWorld']:
    test(f"'{name}'", name, [TT_ID])

print("\n── Numbers ───────────────────────────────────────────────")
for n in ['0', '42', '999']:
    test(f"int {n}", n, [TT_NUM])
for n in ['3.14', '0.0', '1.5E10', '2.0E+3', '9.9E-2']:
    test(f"real {n}", n, [TT_NUM])

print("\n── Operators ─────────────────────────────────────────────")
for op,tt in [('=',TT_RELOP),('<>',TT_RELOP),('<',TT_RELOP),
              ('<=',TT_RELOP),('>=',TT_RELOP),('>',TT_RELOP),
              ('+',TT_ADDOP),('-',TT_ADDOP),
              ('*',TT_MULOP),('/',TT_MULOP),
              (':=',TT_ASSIGNOP),(':',TT_COLON)]:
    test(f"'{op}'", op, [tt])

print("\n── Punctuation ───────────────────────────────────────────")
for ch,tt in [('(',TT_LPAREN),(')',TT_RPAREN),
              ('[',TT_LBRACKET),(']',TT_RBRACKET),
              (';',TT_SEMICOLON),(',',TT_COMMA),
              ('.',TT_DOT),('..',TT_DOTDOT)]:
    test(f"'{ch}'", ch, [tt])

print("\n── DOTDOT ────────────────────────────────────────────────")
test("array [1..10] of integer",
     "array [ 1 .. 10 ] of integer",
     [TT_KEYWORD, TT_LBRACKET, TT_NUM, TT_DOTDOT,
      TT_NUM, TT_RBRACKET, TT_KEYWORD, TT_KEYWORD])

print("\n── Comments ──────────────────────────────────────────────")
test("inline comment",     "{ hello } x",     [TT_ID])
test("comment mid-code",   "begin { x } end", [TT_KEYWORD, TT_KEYWORD])
test("multi-line comment", "x { a\n b } y",   [TT_ID, TT_ID])

print("\n── Full programs ─────────────────────────────────────────")
test("GCD program (Fig A.1)", """\
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
""")

test("array program",
     "program t; var a:array[1..5] of integer; begin a[1]:=9 end.")

test("while program",
     "program t; var i:integer; begin i:=1; while i<=10 do i:=i+1 end.")

# ── 9. Error cases ────────────────────────────────────────────
print("\n── Errors ────────────────────────────────────────────────")
test("nested comment",       "{ outer { inner } }", expect_error=True)
test("unterminated comment", "x := 5 { no close",   expect_error=True)
test("bad exponent",         "1.5Eabc",             expect_error=True)
test("unknown char '@'",     "@",                   expect_error=True)

# ── Summary ───────────────────────────────────────────────────
total = passed + failed
print(f"\n{'='*52}")
print(f"  {total} tests  —  {passed} passed,  {failed} failed")
print("  \033[32mAll passed! ✓\033[0m" if failed == 0 else f"  \033[31m{failed} FAILED\033[0m")
print(f"{'='*52}\n")