from ll1_grammar import grammar_path, load_grammar
from task2_first_follow import compute_first_sets, compute_follow_sets
from task3_parsing_table import compute_parsing_table
from task4_algorithm_4_34 import table_driven_predictive_parse, tokenize_input


class LL1Parser:
    def __init__(self, grammar_file=None):
        self.grammar_file = grammar_file or grammar_path()
        self.grammar = load_grammar(self.grammar_file)
        self.nonterminals = list(self.grammar.keys())
        self.start_symbol = self.nonterminals[0]

        self.first_sets = compute_first_sets(self.grammar, self.nonterminals)
        self.follow_sets = compute_follow_sets(
            self.grammar, self.nonterminals, self.start_symbol, self.first_sets
        )
        self.parse_table, conflicts = compute_parsing_table(
            self.grammar, self.nonterminals, self.first_sets, self.follow_sets
        )

        if conflicts:
            raise ValueError(
                "Grammar is not LL(1). Resolve parse-table conflicts before parsing."
            )

    def parse_string(self, source, trace=False):
        tokens = tokenize_input(source)
        return table_driven_predictive_parse(
            tokens=tokens,
            start_symbol=self.start_symbol,
            parse_table=self.parse_table,
            nonterminals=set(self.nonterminals),
            trace=trace,
        )
