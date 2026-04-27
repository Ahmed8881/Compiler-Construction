import re
from pathlib import Path

EPSILON = "epsilon"
ENDMARKER = "$"


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
            alternatives = []
            for alt in rhs_text.split("|"):
                symbols = alt.strip().split()
                if not symbols:
                    symbols = [EPSILON]
                alternatives.append(symbols)
            grammar[lhs] = alternatives
    if not grammar:
        raise ValueError("Grammar file is empty or invalid.")
    return grammar


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
                seq_first = first_of_sequence(production, first, nonterminals)
                first[nt].update(seq_first)

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


def build_parse_table(grammar, nonterminals, first_sets, follow_sets):
    table = {nt: {} for nt in nonterminals}

    for lhs in nonterminals:
        for rhs in grammar[lhs]:
            seq_first = first_of_sequence(rhs, first_sets, nonterminals)

            for terminal in (seq_first - {EPSILON}):
                if terminal in table[lhs] and table[lhs][terminal] != rhs:
                    raise ValueError(f"Grammar is not LL(1): conflict at M[{lhs}, {terminal}]")
                table[lhs][terminal] = rhs

            if EPSILON in seq_first:
                for terminal in follow_sets[lhs]:
                    if terminal in table[lhs] and table[lhs][terminal] != rhs:
                        raise ValueError(f"Grammar is not LL(1): conflict at M[{lhs}, {terminal}]")
                    table[lhs][terminal] = rhs

    return table


def normalize_token(raw):
    keywords = {
        "program",
        "var",
        "array",
        "of",
        "integer",
        "real",
        "function",
        "procedure",
        "begin",
        "end",
        "if",
        "then",
        "else",
        "while",
        "do",
        "not",
        "div",
        "mod",
        "and",
        "or",
    }

    relops = {"=", "<>", "<", "<=", ">", ">="}

    if raw in {"(", ")", "[", "]", ";", ",", ":", "..", "+", "-", "*", "/"}:
        return raw
    if raw == ":=":
        return "assignop"
    if raw in relops:
        return "relop"
    if re.fullmatch(r"\d+(\.\d+)?", raw):
        return "num"
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", raw):
        text = raw.lower()
        if text in keywords:
            if text in {"div", "mod", "and"}:
                return text
            if text == "or":
                return text
            return text
        return "id"

    return raw


def tokenize_input(source):
    pattern = re.compile(r":=|\.\.|<=|>=|<>|[(),;:\[\]+\-*/=<>]|\d+(?:\.\d+)?|[A-Za-z_][A-Za-z0-9_]*")
    raw_tokens = pattern.findall(source)
    tokens = [normalize_token(tok) for tok in raw_tokens]
    tokens.append(ENDMARKER)
    return tokens


def parse_non_recursive(tokens, start_symbol, parse_table, nonterminals):
    stack = [ENDMARKER, start_symbol]
    pointer = 0

    while stack:
        top = stack[-1]
        lookahead = tokens[pointer] if pointer < len(tokens) else ENDMARKER

        if top == ENDMARKER and lookahead == ENDMARKER:
            return True, None

        if top not in nonterminals:
            if top == lookahead:
                stack.pop()
                pointer += 1
            else:
                return False, f"Expected '{top}', got '{lookahead}'"
            continue

        production = parse_table.get(top, {}).get(lookahead)
        if production is None:
            return False, f"No rule for M[{top}, {lookahead}]"

        stack.pop()
        if production != [EPSILON]:
            for symbol in reversed(production):
                stack.append(symbol)

    return False, "Stack became empty before acceptance"


def main():
    script_dir = Path(__file__).resolve().parent
    grammar_file = script_dir / "grammar_ll1.txt"

    try:
        grammar = load_grammar(grammar_file)
    except Exception as error:
        print(f"Failed to load grammar: {error}")
        return

    nonterminals = list(grammar.keys())
    start_symbol = nonterminals[0]

    try:
        first_sets = compute_first_sets(grammar, nonterminals)
        follow_sets = compute_follow_sets(grammar, nonterminals, start_symbol, first_sets)
        parse_table = build_parse_table(grammar, nonterminals, first_sets, follow_sets)
    except Exception as error:
        print(f"Failed to build LL(1) parser: {error}")
        return

    print("Enter input string:")
    user_input = input("> ").strip()

    tokens = tokenize_input(user_input)
    is_valid, error_message = parse_non_recursive(tokens, start_symbol, parse_table, set(nonterminals))

    if is_valid:
        print("Valid")
    else:
        print("Invalid")
        print(f"Reason: {error_message}")


if __name__ == "__main__":
    main()
