import re

from ll1_grammar import EPSILON

ENDMARKER = "$"


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
        return text if text in keywords else "id"

    return raw


def tokenize_input(source):
    pattern = re.compile(r":=|\.\.|<=|>=|<>|[(),;:\[\]+\-*/=<>]|\d+(?:\.\d+)?|[A-Za-z_][A-Za-z0-9_]*")
    raw_tokens = pattern.findall(source)
    return [normalize_token(tok) for tok in raw_tokens] + [ENDMARKER]


def table_driven_predictive_parse(tokens, start_symbol, parse_table, nonterminals, trace=False):
    stack = [ENDMARKER, start_symbol]
    pointer = 0
    derivation = []

    if trace:
        print("\nAlgorithm 4.34 Trace:")
        print("Stack | Input | Action")

    while stack:
        x = stack[-1]
        a = tokens[pointer] if pointer < len(tokens) else ENDMARKER

        if trace:
            print(f"{' '.join(stack)} | {' '.join(tokens[pointer:])} | ", end="")

        if x == ENDMARKER and a == ENDMARKER:
            if trace:
                print("accept")
            return True, derivation, None

        if x not in nonterminals:
            if x == a:
                stack.pop()
                pointer += 1
                if trace:
                    print(f"match {a}")
            else:
                if trace:
                    print(f"error: expected {x}, got {a}")
                return False, derivation, f"Expected '{x}', got '{a}'"
            continue

        entry = parse_table.get(x, {}).get(a)
        if entry is None:
            if trace:
                print(f"error: no entry M[{x}, {a}]")
            return False, derivation, f"No rule for M[{x}, {a}]"

        derivation.append((x, entry))
        stack.pop()
        if entry != [EPSILON]:
            for symbol in reversed(entry):
                stack.append(symbol)

        if trace:
            print(f"output {x} -> {' '.join(entry)}")

    return False, derivation, "Stack became empty before acceptance"
