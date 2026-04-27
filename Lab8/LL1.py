import re
from collections import defaultdict

EPSILON = "epsilon"
ENDMARKER = "$"


def build_grammar():
	grammar = {
		"program": [["program", "id", "(", "identifier_list", ")", ";", "declarations", "subprogram_declarations", "compound_statement"]],
		"identifier_list": [["id", "identifier_list_tail"]],
		"identifier_list_tail": [[",", "id", "identifier_list_tail"], [EPSILON]],
		"declarations": [["var", "identifier_list", ":", "type", ";", "declarations"], [EPSILON]],
		"type": [["standard_type"], ["array", "[", "num", "..", "num", "]", "of", "standard_type"]],
		"standard_type": [["integer"], ["real"]],
		"subprogram_declarations": [["subprogram_declaration", ";", "subprogram_declarations"], [EPSILON]],
		"subprogram_declaration": [["subprogram_head", "declarations", "compound_statement"]],
		"subprogram_head": [["function", "id", "arguments", ":", "standard_type", ";"], ["procedure", "id", "arguments", ";"]],
		"arguments": [["(", "parameter_list", ")"], [EPSILON]],
		"parameter_list": [["identifier_list", ":", "type", "parameter_list_tail"]],
		"parameter_list_tail": [[";", "identifier_list", ":", "type", "parameter_list_tail"], [EPSILON]],
		"compound_statement": [["begin", "optional_statements", "end"]],
		"optional_statements": [["statement_list"], [EPSILON]],
		"statement_list": [["statement", "statement_list_tail"]],
		"statement_list_tail": [[";", "statement", "statement_list_tail"], [EPSILON]],
		"statement": [
			["id", "statement_id_tail"],
			["compound_statement"],
			["if", "expression", "then", "statement", "else", "statement"],
			["while", "expression", "do", "statement"],
		],
		"statement_id_tail": [["[", "expression", "]", "assignop", "expression"], ["assignop", "expression"], ["(", "expression_list", ")"], [EPSILON]],
		"expression_list": [["expression", "expression_list_tail"]],
		"expression_list_tail": [[",", "expression", "expression_list_tail"], [EPSILON]],
		"expression": [["simple_expression", "expression_tail"]],
		"expression_tail": [["relop", "simple_expression"], [EPSILON]],
		"simple_expression": [["term", "simple_expression_tail"], ["sign", "term", "simple_expression_tail"]],
		"simple_expression_tail": [["addop", "term", "simple_expression_tail"], [EPSILON]],
		"term": [["factor", "term_tail"]],
		"term_tail": [["mulop", "factor", "term_tail"], [EPSILON]],
		"factor": [["id", "factor_tail"], ["num"], ["(", "expression", ")"], ["not", "factor"]],
		"factor_tail": [["(", "expression_list", ")"], [EPSILON]],
		"sign": [["+"], ["-"]],
		"addop": [["+"], ["-"], ["or"]],
		"mulop": [["*"], ["/"], ["div"], ["mod"], ["and"]],
		"relop": [["="], ["<>"], ["<"], ["<="], [">"], [">="]],
	}
	return grammar


def compute_first_sets(grammar, nonterminals):
	first = {nt: set() for nt in nonterminals}
	changed = True

	while changed:
		changed = False
		for nt in nonterminals:
			for production in grammar[nt]:
				old_size = len(first[nt])
				all_nullable = True

				for symbol in production:
					if symbol == EPSILON:
						first[nt].add(EPSILON)
						all_nullable = False
						break

					if symbol not in nonterminals:
						first[nt].add(symbol)
						all_nullable = False
						break

					first[nt].update(first[symbol] - {EPSILON})
					if EPSILON not in first[symbol]:
						all_nullable = False
						break

				if all_nullable:
					first[nt].add(EPSILON)

				if len(first[nt]) != old_size:
					changed = True

	return first


def first_of_sequence(sequence, first_sets, nonterminals):
	result = set()
	all_nullable = True

	for symbol in sequence:
		if symbol == EPSILON:
			result.add(EPSILON)
			all_nullable = False
			break

		if symbol not in nonterminals:
			result.add(symbol)
			all_nullable = False
			break

		result.update(first_sets[symbol] - {EPSILON})
		if EPSILON not in first_sets[symbol]:
			all_nullable = False
			break

	if all_nullable:
		result.add(EPSILON)

	return result


def compute_follow_sets(grammar, nonterminals, start_symbol, first_sets):
	follow = {nt: set() for nt in nonterminals}
	follow[start_symbol].add(ENDMARKER)
	changed = True

	while changed:
		changed = False
		for lhs in nonterminals:
			for production in grammar[lhs]:
				for idx, symbol in enumerate(production):
					if symbol not in nonterminals:
						continue

					beta = production[idx + 1 :]
					first_beta = first_of_sequence(beta, first_sets, nonterminals) if beta else {EPSILON}

					old_size = len(follow[symbol])
					follow[symbol].update(first_beta - {EPSILON})
					if EPSILON in first_beta:
						follow[symbol].update(follow[lhs])

					if len(follow[symbol]) != old_size:
						changed = True

	return follow


def build_production_index(grammar):
	production_list = []
	counter = 1
	for lhs, alternatives in grammar.items():
		for rhs in alternatives:
			production_list.append((counter, lhs, rhs))
			counter += 1
	return production_list


def build_parse_table(grammar, nonterminals, terminals, first_sets, follow_sets, production_index):
	table = {nt: {} for nt in nonterminals}
	production_lookup = {(lhs, tuple(rhs)): number for number, lhs, rhs in production_index}
	conflicts = []

	for lhs in nonterminals:
		for rhs in grammar[lhs]:
			seq_first = first_of_sequence(rhs, first_sets, nonterminals)
			rule_number = production_lookup[(lhs, tuple(rhs))]

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
	addops = {"+", "-", "or"}
	mulops = {"*", "/", "div", "mod", "and"}

	if raw in {"(", ")", "[", "]", ";", ",", ":", ".."}:
		return raw
	if raw == ":=":
		return "assignop"
	if raw in relops:
		return "relop"
	if raw in addops:
		return raw if raw in {"+", "-"} else "or"
	if raw in mulops:
		return raw if raw in {"*", "/"} else raw
	if re.fullmatch(r"\d+(\.\d+)?", raw):
		return "num"
	if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", raw):
		lower = raw.lower()
		if lower in keywords:
			return lower
		return "id"
	return raw


def tokenize_source(source):
	token_pattern = re.compile(r":=|\.\.|<=|>=|<>|[(),;:\[\]+\-*/=<>]|\d+(?:\.\d+)?|[A-Za-z_][A-Za-z0-9_]*")
	raw_tokens = token_pattern.findall(source)
	normalized = [normalize_token(tok) for tok in raw_tokens]
	return normalized


def format_rhs(rhs):
	return " ".join(rhs)


def print_productions(production_index):
	print("\nProduction Rules:")
	for number, lhs, rhs in production_index:
		print(f"{number:>2}. {lhs} -> {format_rhs(rhs)}")


def print_table(table, nonterminals):
	print("\nParsing Table (only filled entries):")
	for nt in nonterminals:
		entries = sorted(table[nt].items(), key=lambda x: x[0])
		if not entries:
			continue
		print(f"\n{nt}:")
		for terminal, rhs in entries:
			print(f"  M[{nt}, {terminal}] = {nt} -> {format_rhs(rhs)}")


def build_production_lookup(production_index):
	return {(lhs, tuple(rhs)): number for number, lhs, rhs in production_index}


def parse_non_recursive(tokens, start_symbol, table, nonterminals, production_numbers):
	stack = [ENDMARKER, start_symbol]
	pointer = 0
	step = 1
	selected_rules = []

	print("\nTrace (Input Buffer, Parse Stack, Action):")

	while stack:
		top = stack[-1]
		lookahead = tokens[pointer] if pointer < len(tokens) else ENDMARKER
		input_buffer = " ".join(tokens[pointer:])
		stack_view = " ".join(stack)

		if top == ENDMARKER and lookahead == ENDMARKER:
			print(f"Step {step:>2}: input=[{input_buffer}] stack=[{stack_view}] action=accept")
			return True, selected_rules

		if top not in nonterminals:
			if top == lookahead:
				print(f"Step {step:>2}: input=[{input_buffer}] stack=[{stack_view}] action=match '{lookahead}'")
				stack.pop()
				pointer += 1
			else:
				print(f"Step {step:>2}: input=[{input_buffer}] stack=[{stack_view}] action=error (expected '{top}', got '{lookahead}')")
				return False, selected_rules
		else:
			entry = table.get(top, {}).get(lookahead)
			if entry is None:
				print(f"Step {step:>2}: input=[{input_buffer}] stack=[{stack_view}] action=error (no table entry M[{top}, {lookahead}])")
				return False, selected_rules

			stack.pop()
			if entry != [EPSILON]:
				for symbol in reversed(entry):
					stack.append(symbol)

			rule_no = production_numbers[(top, tuple(entry))]
			selected_rules.append((rule_no, top, entry))
			print(f"Step {step:>2}: input=[{input_buffer}] stack=[{stack_view}] action=output rule {rule_no}: {top} -> {format_rhs(entry)}")

		step += 1

	return False, selected_rules


def main():
	grammar = build_grammar()
	nonterminals = list(grammar.keys())
	start_symbol = "program"

	all_symbols = set()
	for alternatives in grammar.values():
		for rhs in alternatives:
			all_symbols.update(rhs)

	terminals = sorted(sym for sym in all_symbols if sym not in grammar and sym != EPSILON)

	first_sets = compute_first_sets(grammar, nonterminals)
	follow_sets = compute_follow_sets(grammar, nonterminals, start_symbol, first_sets)
	production_index = build_production_index(grammar)
	table, conflicts = build_parse_table(grammar, nonterminals, terminals, first_sets, follow_sets, production_index)

	print_productions(production_index)

	if conflicts:
		print("\nWarning: Grammar conflicts were found in parse table:")
		for lhs, terminal, old_rhs, new_rhs in conflicts:
			print(f"  Conflict at M[{lhs}, {terminal}] between '{format_rhs(old_rhs)}' and '{format_rhs(new_rhs)}'")
	else:
		print("\nNo LL(1) table conflicts found.")

	print_table(table, nonterminals)

	print("\nEnter input program string (raw Pascal-like source).")
	print("Press Enter for default example.")
	user_input = input("> ").strip()

	if not user_input:
		user_input = "program p ( x ) ; begin end"
		print(f"Using default input: {user_input}")

	token_stream = tokenize_source(user_input)
	token_stream.append(ENDMARKER)

	print(f"\nInput Buffer Tokens: {' '.join(token_stream)}")

	production_numbers = build_production_lookup(production_index)
	accepted, selected_rules = parse_non_recursive(token_stream, start_symbol, table, set(nonterminals), production_numbers)

	print("\nSelected Production Sequence:")
	if selected_rules:
		for number, lhs, rhs in selected_rules:
			print(f"{number:>2}. {lhs} -> {format_rhs(rhs)}")
	else:
		print("None")

	if accepted:
		print("\nResult: Input accepted by non-recursive LL(1) parser.")
	else:
		print("\nResult: Input rejected (syntax error).")


if __name__ == "__main__":
	main()
