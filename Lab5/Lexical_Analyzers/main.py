import sys, time
from common import print_tokens
from approach1_state_based      import StateBased_Lexer
from approach2_stateless        import Stateless_Lexer
from approach3_transition_table import TransitionTable_Lexer, CompressedTable_Lexer

GCD_SAMPLE = """\
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

def run(src):
    approaches = [
        ("Approach 1 — State-Based DFA",  StateBased_Lexer),
        ("Approach 2 — Stateless",        Stateless_Lexer),
        ("Approach 3 — Transition Table", TransitionTable_Lexer),
        ("Bonus     — Compressed Table",  CompressedTable_Lexer),
    ]

    print(f"\n{'█'*56}")
    print("  PASCAL SUBSET LEXER — ALL APPROACHES")
    print(f"{'█'*56}\nSource:\n{src.strip()}\n")

    results = {}
    for title, Cls in approaches:
        t0   = time.perf_counter()
        toks = Cls(src).tokenize_all()
        ms   = (time.perf_counter() - t0) * 1000
        print_tokens(toks, title)
        results[title] = (toks, ms)

    print("── Compressed Table Stats ────────────────────────────")
    CompressedTable_Lexer.stats()

    print("── Consistency ───────────────────────────────────────")
    base = [t.lexeme for t in results["Approach 1 — State-Based DFA"][0]]
    ok   = True
    for title, (toks, _) in results.items():
        match = [t.lexeme for t in toks] == base
        sym   = "\033[32mOK\033[0m" if match else "\033[31mMISMATCH\033[0m"
        print(f"  {sym}  {title}")
        if not match: ok = False
    if ok:
        print("  \033[32mAll four produce identical token streams ✓\033[0m\n")

    print("── Speed ─────────────────────────────────────────────")
    for title, (_, ms) in results.items():
        print(f"  {ms:.4f} ms  {title}")
    print()


if __name__ == '__main__':
    src = open(sys.argv[1]).read() if len(sys.argv) > 1 else GCD_SAMPLE
    run(src)