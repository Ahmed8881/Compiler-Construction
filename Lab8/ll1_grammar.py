from pathlib import Path

EPSILON = "epsilon"


def load_grammar(file_path):
    grammar = {}
    with open(file_path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "->" not in line:
                continue

            lhs, rhs_text = line.split("->", 1)
            lhs = lhs.strip()
            grammar[lhs] = []

            for alt in rhs_text.split("|"):
                symbols = alt.strip().split()
                grammar[lhs].append(symbols if symbols else [EPSILON])

    if not grammar:
        raise ValueError("Grammar file is empty or invalid.")

    return grammar


def grammar_path():
    return Path(__file__).resolve().parent / "grammar_ll1.txt"
