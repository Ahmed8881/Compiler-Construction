# Operator Precedence Parser for Arithmetic Expressions
# Supports: +, -, *, /, (, ), id, num, not

precedence_table = {
    '+':  {'+': '>', '-': '>', '*': '<', '/': '<', '(': '<', ')': '>', 'id': '<', 'num': '<', 'not': '<', '$': '>'},
    '-':  {'+': '>', '-': '>', '*': '<', '/': '<', '(': '<', ')': '>', 'id': '<', 'num': '<', 'not': '<', '$': '>'},
    '*':  {'+': '>', '-': '>', '*': '>', '/': '>', '(': '<', ')': '>', 'id': '<', 'num': '<', 'not': '<', '$': '>'},
    '/':  {'+': '>', '-': '>', '*': '>', '/': '>', '(': '<', ')': '>', 'id': '<', 'num': '<', 'not': '<', '$': '>'},
    '(':  {'+': '<', '-': '<', '*': '<', '/': '<', '(': '<', ')': '=', 'id': '<', 'num': '<', 'not': '<', '$': ''},
    ')':  {'+': '>', '-': '>', '*': '>', '/': '>', '(': '',  ')': '>', 'id': '',  'num': '',  'not': '>', '$': '>'},
    'id': {'+': '>', '-': '>', '*': '>', '/': '>', '(': '',  ')': '>', 'id': '',  'num': '',  'not': '>', '$': '>'},
    'num':{'+' :'>', '-' :'>', '*' :'>', '/' :'>', '(' :'', ')' :'>', 'id':'', 'num':'', 'not':'>', '$':'>'},
    'not':{'+' :'<', '-' :'<', '*' :'<', '/' :'<', '(' :'<', ')' :'>', 'id':'<', 'num':'<', 'not':'<', '$':'>'},
    '$':  {'+': '<', '-': '<', '*': '<', '/': '<', '(': '<', ')': '',  'id': '<', 'num': '<', 'not': '<', '$': 'acc'},
}

import re

def tokenize(expr):
    tokens = []
    expr = expr.replace(' ', '')
    i = 0
    while i < len(expr):
        if expr[i].isdigit():
            num = expr[i]
            i += 1
            while i < len(expr) and expr[i].isdigit():
                num += expr[i]
                i += 1
            tokens.append(('num', num))
        elif expr[i].isalpha():
            idn = expr[i]
            i += 1
            while i < len(expr) and expr[i].isalnum():
                idn += expr[i]
                i += 1
            if idn == 'not':
                tokens.append(('not', 'not'))
            else:
                tokens.append(('id', idn))
        elif expr[i] in '+-*/()':
            tokens.append((expr[i], expr[i]))
            i += 1
        else:
            raise ValueError(f"Unknown character: {expr[i]}")
    tokens.append(('$', '$'))
    return tokens

def get_top_terminal(stack):
    for sym in reversed(stack):
        if sym in precedence_table:
            return sym
        if sym in ('id', 'num', 'not'):
            return sym
    return '$'

def operator_precedence_parse(expr):
    tokens = tokenize(expr)
    stack = ['$']
    i = 0
    steps = []
    while True:
        a = tokens[i][0]
        top = get_top_terminal(stack)
        rel = precedence_table.get(top, {}).get(a, None)
        steps.append((stack.copy(), [t[0] for t in tokens[i:]], rel))
        if rel in ('<', '='):
            stack.append(a)
            i += 1
        elif rel == '>':
            # Reduce: pop until < or =
            while True:
                sym = stack.pop()
                prev_top = get_top_terminal(stack)
                if precedence_table.get(prev_top, {}).get(sym, None) in ('<', '='):
                    break
        elif rel == 'acc':
            steps.append((stack.copy(), [t[0] for t in tokens[i:]], 'accept'))
            return steps
        else:
            steps.append((stack.copy(), [t[0] for t in tokens[i:]], 'error'))
            return steps

def print_steps(steps):
    print(f"{'Stack':<30} {'Input':<20} Relation")
    print('-'*60)
    for st, inp, rel in steps:
        print(f"{''.join(st):<30} {''.join(inp):<20} {rel}")

if __name__ == "__main__":
    expr = input("Enter arithmetic expression: ")
    steps = operator_precedence_parse(expr)
    print_steps(steps)
    print("\nParsing complete.")
