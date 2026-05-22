import re
from collections import defaultdict

class OperatorPrecedenceParser:
    def __init__(self):
        self.grammar = defaultdict(list)
        self.non_terminals = set()
        self.terminals = set()
        self.precedence_table = defaultdict(dict)
        self.define_grammar()
        self.define_precedence_table()

    def define_grammar(self):
        self.grammar = {
            'E': ['E relop T', 'T'],
            'T': ['T addop F', 'F'],
            'F': ['F mulop P', 'P'],
            'P': ['id', 'num', '( E )', 'not P']
        }
        self.non_terminals = {'E', 'T', 'F', 'P'}
        self.terminals = {'id', 'num', '+', '-', '*', '/', '(', ')',
                          'relop', 'addop', 'mulop', 'not', '$'}

    def define_precedence_table(self):
        pt = self.precedence_table

        rels = [
            ('$', '$', '='),
            ('$', 'id', '<'), ('$', 'num', '<'), ('$', '(', '<'),
            ('$', '+', '<'), ('$', '-', '<'), ('$', '*', '<'), ('$', '/', '<'),
            ('$', 'addop', '<'), ('$', 'mulop', '<'), ('$', 'relop', '<'), ('$', 'not', '<'),

            ('id', '$', '>'), ('id', '+', '>'), ('id', '-', '>'),
            ('id', '*', '>'), ('id', '/', '>'),
            ('id', 'addop', '>'), ('id', 'mulop', '>'), ('id', 'relop', '>'),
            ('id', ')', '>'), ('id', ';', '>'),

            ('num', '$', '>'), ('num', '+', '>'), ('num', '-', '>'),
            ('num', '*', '>'), ('num', '/', '>'),
            ('num', 'addop', '>'), ('num', 'mulop', '>'), ('num', 'relop', '>'),
            ('num', ')', '>'),

            ('+', '$', '>'), ('+', 'id', '<'), ('+', 'num', '<'), ('+', '(', '<'),
            ('+', ')', '>'), ('+', '+', '>'), ('+', '-', '>'),
            ('+', '*', '<'), ('+', '/', '<'),
            ('+', 'addop', '>'), ('+', 'mulop', '<'), ('+', 'relop', '>'),
            ('+', 'not', '<'),

            ('-', '$', '>'), ('-', 'id', '<'), ('-', 'num', '<'), ('-', '(', '<'),
            ('-', ')', '>'), ('-', '+', '>'), ('-', '-', '>'),
            ('-', '*', '<'), ('-', '/', '<'),
            ('-', 'addop', '>'), ('-', 'mulop', '<'), ('-', 'relop', '>'),
            ('-', 'not', '<'),

            ('*', '$', '>'), ('*', 'id', '<'), ('*', 'num', '<'), ('*', '(', '<'),
            ('*', ')', '>'), ('*', '+', '>'), ('*', '-', '>'),
            ('*', '*', '>'), ('*', '/', '>'),
            ('*', 'addop', '>'), ('*', 'mulop', '>'), ('*', 'relop', '>'),
            ('*', 'not', '<'),

            ('/', '$', '>'), ('/', 'id', '<'), ('/', 'num', '<'), ('/', '(', '<'),
            ('/', ')', '>'), ('/', '+', '>'), ('/', '-', '>'),
            ('/', '*', '>'), ('/', '/', '>'),
            ('/', 'addop', '>'), ('/', 'mulop', '>'), ('/', 'relop', '>'),
            ('/', 'not', '<'),

            ('(', '$', ''), ('(', 'id', '<'), ('(', 'num', '<'), ('(', '(', '<'),
            ('(', ')', '='), ('(', '+', '<'), ('(', '-', '<'),
            ('(', '*', '<'), ('(', '/', '<'),
            ('(', 'addop', '<'), ('(', 'mulop', '<'), ('(', 'relop', '<'),
            ('(', 'not', '<'),

            (')', '$', '>'), (')', '+', '>'), (')', '-', '>'),
            (')', '*', '>'), (')', '/', '>'),
            (')', 'addop', '>'), (')', 'mulop', '>'), (')', 'relop', '>'),
            (')', ')', '>'),

            ('addop', '$', '>'), ('addop', 'id', '<'), ('addop', 'num', '<'), ('addop', '(', '<'),
            ('addop', ')', '>'), ('addop', 'addop', '>'), ('addop', 'mulop', '<'),
            ('addop', 'relop', '>'), ('addop', 'not', '<'),

            ('mulop', '$', '>'), ('mulop', 'id', '<'), ('mulop', 'num', '<'), ('mulop', '(', '<'),
            ('mulop', ')', '>'), ('mulop', 'addop', '>'), ('mulop', 'mulop', '>'),
            ('mulop', 'relop', '>'), ('mulop', 'not', '<'),

            ('relop', '$', '>'), ('relop', 'id', '<'), ('relop', 'num', '<'), ('relop', '(', '<'),
            ('relop', ')', '>'), ('relop', 'addop', '<'), ('relop', 'mulop', '<'),
            ('relop', 'relop', '>'), ('relop', 'not', '<'),

            ('not', '$', '>'), ('not', 'id', '<'), ('not', 'num', '<'), ('not', '(', '<'),
            ('not', 'not', '<'), ('not', '+', '>'), ('not', '-', '>'),
            ('not', '*', '>'), ('not', '/', '>'), ('not', 'addop', '>'),
            ('not', 'mulop', '>'), ('not', 'relop', '>'),
        ]

        for a, b, rel in rels:
            if rel:
                pt[a][b] = rel

    def get_relation(self, a, b):
        return self.precedence_table[a].get(b, None)

    def tokenize(self, input_str):
        tokens = []
        i = 0
        input_str = input_str.strip()
        special_tokens = ['id', 'num', 'addop', 'mulop', 'relop', 'not']
        special_tokens.sort(key=len, reverse=True)

        while i < len(input_str):
            matched = False
            for tok in special_tokens:
                if input_str[i:].startswith(tok):
                    tokens.append(tok)
                    i += len(tok)
                    matched = True
                    break
            if matched:
                continue

            if input_str[i] in '()+-*/':
                tokens.append(input_str[i])
                i += 1
            elif input_str[i].isalpha():
                j = i
                while j < len(input_str) and (input_str[j].isalpha() or input_str[j] == '_'):
                    j += 1
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

    def get_top_terminal(self, stack):
        for s in reversed(stack):
            if s in self.terminals:
                return s
        return None

    def find_handle_position(self, stack):
        left_pos = None
        right_pos = None

        for i in range(len(stack) - 1, -1, -1):
            if stack[i] in self.terminals:
                if right_pos is None:
                    right_pos = i
                elif left_pos is None:
                    left_pos = i
                    break

        if right_pos is None:
            return None, None

        if left_pos is None:
            if stack[right_pos] in ['id', 'num']:
                return right_pos, right_pos
            return None, None

        return left_pos, right_pos

    def try_reduce(self, stack):
        stack_str = ' '.join(stack)

        patterns = [
            ('P', 'id'),
            ('P', 'num'),
            ('F', 'P'),
            ('T', 'F'),
            ('E', 'T'),
        ]

        for lhs, rhs in patterns:
            if stack[-1] == rhs:
                return lhs, 1

        binops = [
            ('F', 'mulop'),
            ('T', 'addop'),
            ('E', 'relop'),
            ('T', '+'),
            ('T', '-'),
            ('F', '*'),
            ('F', '/'),
        ]

        for lhs, op in binops:
            if len(stack) >= 3:
                if stack[-2] == op:
                    if (stack[-3] in self.non_terminals or stack[-3] in ['id', 'num', ')']) and \
                       (stack[-1] in self.non_terminals or stack[-1] in ['id', 'num', '(']):
                        return lhs, 3

        if len(stack) >= 2 and stack[-2] == 'not':
            if stack[-1] in self.non_terminals or stack[-1] in ['id', 'num', '(']:
                return 'P', 2

        if len(stack) >= 3 and stack[-3] == '(' and stack[-1] == ')':
            if stack[-2] in self.non_terminals:
                return 'P', 3

        return None, 0

    def reduce(self, stack):
        nt, count = self.try_reduce(stack)
        if nt:
            handle = stack[-count:]
            for _ in range(count):
                stack.pop()
            stack.append(nt)
            return nt, handle
        return None, None

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

        steps = 0
        max_steps = 100

        while steps < max_steps:
            steps += 1

            stack_top_term = self.get_top_terminal(stack)
            current_input = tokens[input_ptr]

            stack_str = ' '.join(stack)
            input_str_rem = ' '.join(tokens[input_ptr:])

            if stack_top_term == '$' and current_input == '$':
                if len(stack) == 2 and stack[-1] in self.non_terminals:
                    nt = stack.pop()
                    print(f"{stack_str:<35} {input_str_rem:<25} {'Reduce':<10} {nt} -> E")
                    stack_str = ' '.join(stack)
                    print(f"{stack_str:<35} {input_str_rem:<25} {'Accept':<10}")
                    print("\n" + "=" * 80)
                    print("PARSING COMPLETE: String accepted!")
                    print("=" * 80)
                    return True
                elif len(stack) == 1:
                    print(f"{stack_str:<35} {input_str_rem:<25} {'Accept':<10}")
                    print("\n" + "=" * 80)
                    print("PARSING COMPLETE: String accepted!")
                    print("=" * 80)
                    return True

            if stack_top_term is None:
                stack_top_term = '$'

            relation = self.get_relation(stack_top_term, current_input)

            if relation is None:
                if stack_top_term in self.non_terminals:
                    pass
                print(f"{stack_str:<35} {input_str_rem:<25} {'Error':<10}")
                print(f"\nError: No precedence relation between '{stack_top_term}' and '{current_input}'")
                return False

            if relation in ['<', '=']:
                print(f"{stack_str:<35} {input_str_rem:<25} {'Shift':<10} {stack_top_term} {relation} {current_input}")
                stack.append(current_input)
                input_ptr += 1
            elif relation == '>':
                nt, handle = self.reduce(stack)
                if nt and handle:
                    handle_str = ' '.join(handle)
                    print(f"{stack_str:<35} {input_str_rem:<25} {'Reduce':<10} {handle_str} -> {nt}")
                else:
                    print(f"{stack_str:<35} {input_str_rem:<25} {'Error':<10}")
                    print("\nError: Could not reduce")
                    return False

        print("\nError: Too many steps")
        return False

    def print_grammar(self):
        print("\n" + "=" * 80)
        print("OPERATOR GRAMMAR (Filtered for Operator Precedence Parser)")
        print("=" * 80)
        print("""
Expression Grammar (Operator Grammar):
  E -> E relop T | T
  T -> T addop F | F | T + F | T - F
  F -> F mulop P | P | F * F | F / F
  P -> id | num | ( E ) | not P

Filtered Grammar Rules Applied:
  1. Removed productions with null (epsilon)
  2. Removed productions with adjacent non-terminals (kept only operator grammar)
  3. Kept only expression-related productions (actual operator grammar)

Note: Original Pascal grammar had many productions that are NOT operator grammars:
  - declarations -> declarations var identifier_list : type ;
  - subprogram_declaration -> subprogram_head declarations compound_statement
  These have adjacent non-terminals and are skipped for operator precedence parsing.
""")

    def print_precedence_levels(self):
        print("\n" + "=" * 80)
        print("OPERATOR PRECEDENCE LEVELS")
        print("=" * 80)
        print("""
  Level    Operators       Associativity    Description
  -----    ---------       -------------    -----------
    9      ( )             left             Parentheses (highest)
    8      not             right            Logical NOT
    7      mulop, *, /     left             Multiplicative
    6      addop, +, -     left             Additive
    4      relop           none             Relational (<, <=, =, <>, >=, >)
    1      =               right            Assignment (lowest)

Precedence Table Construction Method:
  1. FIRST sets: For each non-terminal, find first terminal symbols
  2. LAST sets: For each non-terminal, find last terminal symbols  
  3. For production X -> aYb: a = b
  4. For production X -> aY: a < FIRST(Y)
  5. For production X -> Ya: LAST(Y) > a
  6. For arithmetic: add manual precedence based on standard levels
""")

    def print_precedence_table(self):
        print("\n" + "=" * 80)
        print("OPERATOR PRECEDENCE TABLE")
        print("=" * 80)

        terminals = ['$', 'id', 'num', '(', ')', '+', '-', '*', '/',
                     'addop', 'mulop', 'relop', 'not']

        print(f"\n{'':<8}", end='')
        for t in terminals:
            print(f"{t:<8}", end='')
        print()
        print("-" * (8 + len(terminals) * 8))

        for row in terminals:
            print(f"{row:<8}", end='')
            for col in terminals:
                rel = self.get_relation(row, col)
                if rel:
                    print(f"{rel:<8}", end='')
                else:
                    print(f"{'':<8}", end='')
            print()

        print("""
Precedence Relation Legend:
  <  : Stack terminal has LOWER precedence than input terminal (Shift)
  >  : Stack terminal has HIGHER precedence than input terminal (Reduce)
  =  : Stack and input terminals have EQUAL precedence or are paired (Shift)
""")


def main():
    parser = OperatorPrecedenceParser()

    parser.print_grammar()
    parser.print_precedence_levels()
    parser.print_precedence_table()

    test_inputs = [
        "id + id * id",
        "( id + id ) * id",
        "id * id + id",
        "not id",
        "( ( id + id ) )",
        "num + num * num",
        "id addop id mulop id",
        "id relop id",
    ]

    print("\n" + "=" * 80)
    print("BOTTOM-UP PARSING TEST CASES")
    print("=" * 80)

    for test in test_inputs:
        parser.parse(test)
        print()


if __name__ == '__main__':
    main()
