from ll1_grammar import EPSILON
from task2_first_follow import first_of_sequence


def compute_parsing_table(grammar, nonterminals, first_sets, follow_sets):
    table = {nt: {} for nt in nonterminals}
    conflicts = []

    for lhs in nonterminals:
        for rhs in grammar[lhs]:
            seq_first = first_of_sequence(rhs, first_sets, nonterminals)

            for terminal in (seq_first - {EPSILON}):
                if terminal in table[lhs] and table[lhs][terminal] != rhs:
                    conflicts.append((lhs, terminal, table[lhs][terminal], rhs))
                table[lhs][terminal] = rhs

            if EPSILON in seq_first:
                for terminal in follow_sets[lhs]:
                    if terminal in table[lhs] and table[lhs][terminal] != rhs:
                        conflicts.append((lhs, terminal, table[lhs][terminal], rhs))
                    table[lhs][terminal] = rhs

    return table, conflicts


def is_ll1_grammar(conflicts):
    return len(conflicts) == 0


def pretty_print_table(table, nonterminals):
    print("\nParsing Table (filled entries only):")
    for nt in nonterminals:
        if not table[nt]:
            continue
        print(f"\n{nt}:")
        for lookahead in sorted(table[nt].keys()):
            rhs = " ".join(table[nt][lookahead])
            print(f"M[{nt}, {lookahead}] = {nt} -> {rhs}")


def pretty_print_conflicts(conflicts):
    if not conflicts:
        print("\nNo parsing table conflicts. Grammar is LL(1).")
        return

    print("\nConflicts found (Grammar is NOT LL(1)):")
    for lhs, terminal, old_rhs, new_rhs in conflicts:
        print(f"M[{lhs}, {terminal}] has both: {' '.join(old_rhs)}  and  {' '.join(new_rhs)}")
