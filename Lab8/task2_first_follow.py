from ll1_grammar import EPSILON

ENDMARKER = "$"


def first_of_sequence(sequence, first_sets, nonterminals):
    result = set()
    nullable_prefix = True

    for symbol in sequence:
        if symbol == EPSILON:
            result.add(EPSILON)
            nullable_prefix = False
            break

        if symbol not in nonterminals:
            result.add(symbol)
            nullable_prefix = False
            break

        result.update(first_sets[symbol] - {EPSILON})
        if EPSILON not in first_sets[symbol]:
            nullable_prefix = False
            break

    if nullable_prefix:
        result.add(EPSILON)

    return result


def compute_first_sets(grammar, nonterminals):
    first = {nt: set() for nt in nonterminals}
    changed = True

    while changed:
        changed = False
        for nt in nonterminals:
            before = len(first[nt])
            for production in grammar[nt]:
                first[nt].update(first_of_sequence(production, first, nonterminals))
            if len(first[nt]) > before:
                changed = True

    return first


def compute_follow_sets(grammar, nonterminals, start_symbol, first_sets):
    follow = {nt: set() for nt in nonterminals}
    follow[start_symbol].add(ENDMARKER)
    changed = True

    while changed:
        changed = False
        for lhs in nonterminals:
            for production in grammar[lhs]:
                for i, symbol in enumerate(production):
                    if symbol not in nonterminals:
                        continue

                    beta = production[i + 1 :]
                    beta_first = first_of_sequence(beta, first_sets, nonterminals) if beta else {EPSILON}

                    before = len(follow[symbol])
                    follow[symbol].update(beta_first - {EPSILON})
                    if EPSILON in beta_first:
                        follow[symbol].update(follow[lhs])
                    if len(follow[symbol]) > before:
                        changed = True

    return follow


def pretty_print_sets(name, sets_map, order):
    print(f"\n{name}:")
    for symbol in order:
        items = ", ".join(sorted(sets_map[symbol]))
        print(f"{symbol} = {{ {items} }}")
