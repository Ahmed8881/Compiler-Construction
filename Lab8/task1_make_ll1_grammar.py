from ll1_grammar import grammar_path, load_grammar
from task2_first_follow import compute_first_sets, compute_follow_sets
from task3_parsing_table import compute_parsing_table, pretty_print_conflicts


def validate_and_report_ll1_grammar():
    grammar = load_grammar(grammar_path())
    nonterminals = list(grammar.keys())
    start_symbol = nonterminals[0]

    first_sets = compute_first_sets(grammar, nonterminals)
    follow_sets = compute_follow_sets(grammar, nonterminals, start_symbol, first_sets)
    _, conflicts = compute_parsing_table(grammar, nonterminals, first_sets, follow_sets)

    print("Checking if language grammar is LL(1)...")
    pretty_print_conflicts(conflicts)


if __name__ == "__main__":
    validate_and_report_ll1_grammar()
