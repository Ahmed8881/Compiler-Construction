import re
from collections import defaultdict

class OperatorPrecedenceParser:
    def __init__(self):
        self.grammar = defaultdict(list)
        self.non_terminals = set()
        self.terminals = set()
        self.first_set = defaultdict(set)
        self.last_set = defaultdict(set)
        self.precedence_table = defaultdict(dict)
        self.define_grammar()
        self.define_operators()
        self.compute_first_last()
        self.build_precedence_table()

    def define_grammar(self):
        self.grammar['E'] = ['E relop T', 'T']
        self.grammar['T'] = ['T addop F', 'F']
        self.grammar['F'] = ['F mulop P', 'P']
        self.grammar['P'] = ['id', 'num', '( E )', 'not P']

        self.non_terminals = {'E', 'T', 'F', 'P'}
        self.terminals = {'id', 'num', '+', '-', '*', '/', '(', ')',
                          'relop', 'addop', 'mulop', 'not', '$'}

    def define_operators(self):
        self.operators = {
            '+', '-', '*', '/', 'relop', 'addop', 'mulop', 'not',
            '(', ')'
        }

    def get_precedence(self, op):
        precedence = {
            'not': 8,
            'mulop': 7,
            '*': 7,
            '/': 7,
            'addop': 6,
            '+': 6,
            '-': 6,
            'relop': 4,
        }
        return precedence.get(op, 0)

    def compute_first_last(self):
        for nt in self.non_terminals:
            self.first_set[nt] = set()
            self.last_set[nt] = set()

        changed = True
        while changed:
            changed = False
            for lhs in self.grammar:
                for rhs in self.grammar[lhs]:
                    symbols = rhs.split()
                    if symbols:
                        first_symbol = symbols[0]
                        if first_symbol in self.terminals or first_symbol in self.operators:
                            if first_symbol not in self.first_set[lhs]:
                                self.first_set[lhs].add(first_symbol)
                                changed = True
                        elif first_symbol in self.non_terminals:
                            for s in self.first_set[first_symbol]:
                                if s not in self.first_set[lhs]:
                                    self.first_set[lhs].add(s)
                                    changed = True

                        last_symbol = symbols[-1]
                        if last_symbol in self.terminals or last_symbol in self.operators:
                            if last_symbol not in self.last_set[lhs]:
                                self.last_set[lhs].add(last_symbol)
                                changed = True
                        elif last_symbol in self.non_terminals:
                            for s in self.last_set[last_symbol]:
                                if s not in self.last_set[lhs]:
                                    self.last_set[lhs].add(s)
                                    changed = True

    def build_precedence_table(self):
        for lhs in self.grammar:
            for rhs in self.grammar[lhs]:
                symbols = rhs.split()
                for i in range(len(symbols) - 1):
                    a = symbols[i]
                    b = symbols[i + 1]

                    a_is_terminal = a in self.terminals or a in self.operators
                    b_is_terminal = b in self.terminals or b in self.operators
                    a_is_nt = a in self.non_terminals
                    b_is_nt = b in self.non_terminals

                    if a_is_terminal and b_is_terminal:
                        self.set_relation(a, b, '=')
                    elif a_is_terminal and b_is_nt:
                        for f in self.first_set[b]:
                            self.set_relation(a, f, '<')
                    elif a_is_nt and b_is_terminal:
                        for l in self.last_set[a]:
                            self.set_relation(l, b, '>')
                    elif i + 2 < len(symbols):
                        a_nt = a
                        b_ter = symbols[i + 1]
                        c_nt = symbols[i + 2]
                        if (a_nt in self.non_terminals and
                            (b_ter in self.terminals or b_ter in self.operators) and
                            c_nt in self.non_terminals):
                            for l in self.last_set[a_nt]:
                                self.set_relation(l, b_ter, '>')
                            for f in self.first_set[c_nt]:
                                self.set_relation(b_ter, f, '<')

        self.set_relation('(', ')', '=')

        arithmetic_ops = ['+', '-', '*', '/', 'addop', 'mulop', 'relop']
        for t in arithmetic_ops:
            self.set_relation('(', t, '<')
            self.set_relation(t, ')', '>')
        self.set_relation('(', 'id', '<')
        self.set_relation('(', 'num', '<')
        self.set_relation('(', 'not', '<')
        self.set_relation('(', '(', '<')

        self.set_relation('id', ')', '>')
        self.set_relation('num', ')', '>')

        for t in arithmetic_ops:
            self.set_relation('$', t, '<')
            self.set_relation(t, '$', '>')
        self.set_relation('$', 'id', '<')
        self.set_relation('$', 'num', '<')
        self.set_relation('$', '(', '<')
        self.set_relation('$', 'not', '<')
        self.set_relation('id', '$', '>')
        self.set_relation('num', '$', '>')
        self.set_relation(')', '$', '>')
        self.set_relation('$', '$', '=')

        self.set_relation('+', '+', '>')
        self.set_relation('+', '-', '>')
        self.set_relation('-', '+', '>')
        self.set_relation('-', '-', '>')
        self.set_relation('*', '*', '>')
        self.set_relation('*', '/', '>')
        self.set_relation('/', '*', '>')
        self.set_relation('/', '/', '>')
        self.set_relation('*', '+', '>')
        self.set_relation('*', '-', '>')
        self.set_relation('/', '+', '>')
        self.set_relation('/', '-', '>')
        self.set_relation('+', '*', '<')
        self.set_relation('+', '/', '<')
        self.set_relation('-', '*', '<')
        self.set_relation('-', '/', '<')

        self.set_relation('addop', 'addop', '>')
        self.set_relation('mulop', 'mulop', '>')
        self.set_relation('mulop', 'addop', '>')
        self.set_relation('addop', 'mulop', '<')
        self.set_relation('relop', 'relop', '>')
        self.set_relation('not', 'not', '<')

        self.set_relation('addop', '*', '<')
        self.set_relation('addop', '/', '<')
        self.set_relation('mulop', '+', '>')
        self.set_relation('mulop', '-', '>')
        self.set_relation('*', 'addop', '>')
        self.set_relation('/', 'addop', '>')
        self.set_relation('+', 'mulop', '<')
        self.set_relation('-', 'mulop', '<')

        for op in ['id', 'num']:
            self.set_relation(op, '+', '>')
            self.set_relation(op, '-', '>')
            self.set_relation(op, '*', '>')
            self.set_relation(op, '/', '>')
            self.set_relation(op, 'addop', '>')
            self.set_relation(op, 'mulop', '>')
            self.set_relation(op, 'relop', '>')

        for op in ['+', '-', '*', '/', 'addop', 'mulop', 'relop']:
            self.set_relation(op, 'id', '<')
            self.set_relation(op, 'num', '<')
            self.set_relation(op, '(', '<')
            self.set_relation(op, 'not', '<')

        self.set_relation('not', 'id', '<')
        self.set_relation('not', 'num', '<')
        self.set_relation('not', '(', '<')

    def set_relation(self, a, b, rel):
        if b not in self.precedence_table[a]:
            self.precedence_table[a][b] = rel

    def get_relation(self, a, b):
        return self.precedence_table[a].get(b, None)

    def tokenize(self, input_str):
        tokens = []
        i = 0
        input_str = input_str.strip()
        while i < len(input_str):
            if input_str[i:].startswith('id'):
                tokens.append('id')
                i += 2
            elif input_str[i:].startswith('num'):
                tokens.append('num')
                i += 3
            elif input_str[i:].startswith('addop'):
                tokens.append('addop')
                i += 5
            elif input_str[i:].startswith('mulop'):
                tokens.append('mulop')
                i += 5
            elif input_str[i:].startswith('relop'):
                tokens.append('relop')
                i += 5
            elif input_str[i:].startswith('not'):
                tokens.append('not')
                i += 3
            elif input_str[i] in '()+-*/':
                tokens.append(input_str[i])
                i += 1
            elif input_str[i].isalpha():
                j = i
                while j < len(input_str) and (input_str[j].isalpha() or input_str[j] == '_'):
                    j += 1
                word = input_str[i:j]
                if word in {'addop', 'mulop', 'relop', 'not'}:
                    tokens.append(word)
                else:
                    tokens.append('id')
                i = j
            elif input_str[i].isdigit():
                j = i
                while j < len(input_str) and input_str[j].isdigit():
                    j += 1
                tokens.append('num')
                i = j
            elif input_str[i].isspace():
                i += 1
            else:
                i += 1
        tokens.append('$')
        return tokens

    def find_handle(self, stack):
        stack_symbols = []
        for s in stack:
            if s not in ['<', '=', '>']:
                stack_symbols.append(s)

        for lhs in self.grammar:
            for rhs in self.grammar[lhs]:
                rhs_symbols = rhs.split()
                if len(rhs_symbols) <= len(stack_symbols):
                    match = True
                    for i in range(len(rhs_symbols)):
                        rhs_sym = rhs_symbols[-(i + 1)]
                        stack_sym = stack_symbols[-(i + 1)]
                        if rhs_sym != stack_sym:
                            match = False
                            break
                    if match:
                        return rhs, len(stack) - len(rhs_symbols)

        return None, 0

    def reduce(self, handle):
        for lhs in self.grammar:
            for rhs in self.grammar[lhs]:
                if rhs == handle:
                    return lhs
        return None

    def parse(self, input_str):
        tokens = self.tokenize(input_str)
        stack = ['$']
        input_ptr = 0

        print("\n" + "=" * 80)
        print("OPERATOR PRECEDENCE PARSER STEPS")
        print("=" * 80)
        print(f"\nInput: {' '.join(tokens[:-1])}")
        print(f"\n{'Stack':<35} {'Input':<25} {'Action':<10} {'Detail'}")
        print("-" * 80)

        while True:
            stack_top = None
            for s in reversed(stack):
                if s not in ['<', '=', '>']:
                    stack_top = s
                    break

            if stack_top is None:
                stack_top = stack[-1]

            current_input = tokens[input_ptr]

            stack_str = ''.join(stack)
            input_str_rem = ''.join(tokens[input_ptr:])

            if stack_top == '$' and current_input == '$' and len(stack) == 1:
                print(f"{stack_str:<35} {input_str_rem:<25} {'Accept':<10}")
                print("\n" + "=" * 80)
                print("PARSING COMPLETE: String accepted!")
                print("=" * 80)
                return True

            relation = self.get_relation(stack_top, current_input)

            if relation is None:
                print(f"{stack_str:<35} {input_str_rem:<25} {'Error':<10}")
                print(f"\nError: No precedence relation between '{stack_top}' and '{current_input}'")
                return False

            if relation in ['<', '=']:
                print(f"{stack_str:<35} {input_str_rem:<25} {'Shift':<10} {stack_top} {relation} {current_input}")
                stack.append(relation)
                stack.append(current_input)
                input_ptr += 1
            elif relation == '>':
                handle, handle_start = self.find_handle(stack)
                if handle:
                    lhs = self.reduce(handle)
                    if lhs:
                        print(f"{stack_str:<35} {input_str_rem:<25} {'Reduce':<10} {handle} -> {lhs}")
                        stack = stack[:handle_start]
                        stack.append(lhs)
                    else:
                        print(f"{stack_str:<35} {input_str_rem:<25} {'Error':<10}")
                        print(f"\nError: No production matches handle '{handle}'")
                        return False
                else:
                    print(f"{stack_str:<35} {input_str_rem:<25} {'Error':<10}")
                    print("\nError: Could not find handle")
                    return False

    def print_grammar(self):
        print("\n" + "=" * 80)
        print("OPERATOR GRAMMAR (Filtered for Operator Precedence Parser)")
        print("=" * 80)
        print("\nOriginal expression grammar:")
        for lhs in sorted(self.grammar.keys()):
            productions = []
            for rhs in self.grammar[lhs]:
                productions.append(rhs)
            print(f"  {lhs:<2} -> {' | '.join(productions)}")

        print("\n\nNote: Operator grammar rules:")
        print("  1. No epsilon (null) productions")
        print("  2. No two adjacent non-terminals on RHS")
        print("  3. All operators have defined precedence")

    def print_first_last(self):
        print("\n" + "=" * 80)
        print("FIRST and LAST SETS")
        print("=" * 80)
        for nt in sorted(self.non_terminals):
            print(f"\n{nt}:")
            print(f"  FIRST: {sorted(self.first_set[nt])}")
            print(f"  LAST:  {sorted(self.last_set[nt])}")

    def print_precedence_table(self):
        print("\n" + "=" * 80)
        print("OPERATOR PRECEDENCE TABLE")
        print("=" * 80)

        key_terminals = ['$', 'id', 'num', '+', '-', '*', '/', '(', ')',
                         'addop', 'mulop', 'relop', 'not']

        print(f"\n{'':<8}", end='')
        for t in key_terminals:
            print(f"{t:<8}", end='')
        print()
        print("-" * (8 + len(key_terminals) * 8))

        for row in key_terminals:
            print(f"{row:<8}", end='')
            for col in key_terminals:
                rel = self.get_relation(row, col)
                if rel:
                    print(f"{rel:<8}", end='')
                else:
                    print(f"{'':<8}", end='')
            print()

        print("\n\nPrecedence Relations:")
        print("  <  : a < b  (a has lower precedence than b)")
        print("  >  : a > b  (a has higher precedence than b)")
        print("  =  : a = b  (a and b have equal precedence or are paired)")

    def print_precedence_levels(self):
        print("\n" + "=" * 80)
        print("OPERATOR PRECEDENCE LEVELS")
        print("=" * 80)
        print("""
  Level    Operators    Associativity
  -----    ---------    -------------
    8      not          right
    7      mulop (*,/) left
    6      addop (+,-) left
    4      relop        none
    2      = (assign)   right

  Note:
  - Parentheses () have highest precedence
  - $ is the sentinel marker
""")


def main():
    parser = OperatorPrecedenceParser()

    parser.print_grammar()
    parser.print_precedence_levels()
    parser.print_first_last()
    parser.print_precedence_table()

    test_inputs = [
        "id + id * id",
        "( id + id ) * id",
        "id * id + id",
        "not id + id",
        "id addop id mulop id",
        "id relop id",
        "( ( id + id ) )",
        "num + num * num",
    ]

    print("\n" + "=" * 80)
    print("BOTTOM-UP PARSING TEST CASES")
    print("=" * 80)

    for test in test_inputs:
        parser.parse(test)
        print()


if __name__ == '__main__':
    main()
