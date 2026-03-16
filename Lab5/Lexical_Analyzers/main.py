# ============================================================
# main.py  —  Run all approaches on a Pascal source file
# Usage:
#   python main.py              (uses built-in GCD sample)
#   python main.py myfile.pas   (lex your own file)
# ============================================================

import sys, time
from common import print_tokens
from approach1_state_based      import StateBased_Lexer
from approach2_stateless        import Stateless_Lexer
from approach3_transition_table import TransitionTable_Lexer, CompressedTable_Lexer

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

def run(src):
    approaches = [
        ("Approach 1 — State-Based DFA",    StateBased_Lexer),
        ("Approach 2 — Stateless",          Stateless_Lexer),
        ("Approach 3 — Transition Table",   TransitionTable_Lexer),
        ("Bonus     — Compressed Table",    CompressedTable_Lexer),
    ]

    print(f"\n{'█'*58}")
    print("  PASCAL SUBSET LEXER — ALL APPROACHES")
    print(f"{'█'*58}\nSource:\n{src}")

    results = {}
    for title, Cls in approaches:
        t0  = time.perf_counter()
        toks = Cls(src).tokenize_all()
        ms  = (time.perf_counter() - t0) * 1000
        print_tokens(toks, title)
        results[title] = (toks, ms)

    # Bonus stats
    print("── Compressed Table Memory Stats ─────────────────────")
    CompressedTable_Lexer.stats()

    # Consistency
    print("── Consistency check ─────────────────────────────────")
    base = [t.lexeme for t in results["Approach 1 — State-Based DFA"][0]]
    all_same = True
    for title, (toks, _) in results.items():
        match = [t.lexeme for t in toks] == base
        sym   = "\033[32mOK\033[0m" if match else "\033[31mMISMATCH\033[0m"
        print(f"  {sym}  {title}")
        if not match: all_same = False
    if all_same:
        print("  \033[32mAll four produce identical token streams ✓\033[0m\n")

    # Speed
    print("── Speed ─────────────────────────────────────────────")
    for title, (_, ms) in results.items():
        print(f"  {ms:.4f} ms   {title}")
    print()


if __name__ == '__main__':
    src = open(sys.argv[1]).read() if len(sys.argv) > 1 else GCD
    run(src)