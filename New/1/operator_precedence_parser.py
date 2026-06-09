
PRECEDENCE_TABLE = {
    '$': {
        '$': '=', 'id': '<', 'num': '<', '(': '<', ')': ' ',
        '+': '<', '-': '<', '*': '<', '/': '<', 'addop': '<',
        'mulop': '<', 'relop': '<', 'not': '<'
    },
    'id': {
        '$': '>', 'id': ' ', 'num': ' ', '(': ' ', ')': '>',
        '+': '>', '-': '>', '*': '>', '/': '>', 'addop': '>',
        'mulop': '>', 'relop': '>', 'not': ' '
    },
    'num': {
        '$': '>', 'id': ' ', 'num': ' ', '(': ' ', ')': '>',
        '+': '>', '-': '>', '*': '>', '/': '>', 'addop': '>',
        'mulop': '>', 'relop': '>', 'not': ' '
    },
    '(': {
        '$': ' ', 'id': '<', 'num': '<', '(': '<', ')': '=',
        '+': '<', '-': '<', '*': '<', '/': '<', 'addop': '<',
        'mulop': '<', 'relop': '<', 'not': '<'
    },
    ')': {
        '$': '>', 'id': ' ', 'num': ' ', '(': ' ', ')': '>',
        '+': '>', '-': '>', '*': '>', '/': '>', 'addop': '>',
        'mulop': '>', 'relop': '>', 'not': ' '
    },
    '+': {
        '$': '>', 'id': '<', 'num': '<', '(': '<', ')': '>',
        '+': '>', '-': '>', '*': '<', '/': '<', 'addop': '>',
        'mulop': '<', 'relop': '>', 'not': '<'
    },
    '-': {
        '$': '>', 'id': '<', 'num': '<', '(': '<', ')': '>',
        '+': '>', '-': '>', '*': '<', '/': '<', 'addop': '>',
        'mulop': '<', 'relop': '>', 'not': '<'
    },
    '*': {
        '$': '>', 'id': '<', 'num': '<', '(': '<', ')': '>',
        '+': '>', '-': '>', '*': '>', '/': '>', 'addop': '>',
        'mulop': '>', 'relop': '>', 'not': '<'
    },
    '/': {
        '$': '>', 'id': '<', 'num': '<', '(': '<', ')': '>',
        '+': '>', '-': '>', '*': '>', '/': '>', 'addop': '>',
        'mulop': '>', 'relop': '>', 'not': '<'
    },
    'addop': {
        '$': '>', 'id': '<', 'num': '<', '(': '<', ')': '>',
        '+': ' ', '-': ' ', '*': '<', '/': '<', 'addop': '>',
        'mulop': '<', 'relop': '>', 'not': '<'
    },
    'mulop': {
        '$': '>', 'id': '<', 'num': '<', '(': '<', ')': '>',
        '+': '>', '-': '>', '*': '>', '/': '>', 'addop': '>',
        'mulop': '>', 'relop': '>', 'not': '<'
    },
    'relop': {
        '$': '>', 'id': '<', 'num': '<', '(': '<', ')': '>',
        '+': '<', '-': '<', '*': '>', '/': '>', 'addop': '<',
        'mulop': '>', 'relop': '>', 'not': '<'
    },
    'not': {
        '$': '>', 'id': '<', 'num': '<', '(': '<', ')': ' ',
        '+': ' ', '-': ' ', '*': '>', '/': '>', 'addop': ' ',
        'mulop': '>', 'relop': '>', 'not': '<'
    }
}



def tokenize(input_string):

    tokens = []
    i = 0
    
    while i < len(input_string):
        if input_string[i].isspace():
            i += 1
            continue
        
        if input_string[i:i+3] == 'not':
            tokens.append('not')
            i += 3
            continue
        
        if input_string[i].isdigit():
            j = i
            while j < len(input_string) and input_string[j].isdigit():
                j += 1
            tokens.append(input_string[i:j])
            i = j
            continue
        
        if input_string[i].isalpha() or input_string[i] == '_':
            j = i
            while j < len(input_string) and (input_string[j].isalnum() or input_string[j] == '_'):
                j += 1
            tokens.append(input_string[i:j])
            i = j
            continue
        
        if input_string[i] in '+-*/()==<>':
            # Handle two-character operators
            if i + 1 < len(input_string) and input_string[i:i+2] in ['==', '<>', '<=', '>=']:
                tokens.append(input_string[i:i+2])
                i += 2
            else:
                tokens.append(input_string[i])
                i += 1
            continue
        
        i += 1
    
    return tokens



def get_token_type(token):

    if token == '(':
        return '('
    elif token == ')':
        return ')'
    elif token == 'not':
        return 'not'
    elif token in ['+', '-']:
        return token 
    elif token in ['*', '/']:
        return token 
    elif token in ['<', '>', '<=', '>=', '==', '<>']:
        return 'relop'
    elif token.isdigit() or (token[0].isdigit()):
        return 'num'
    else:
        return 'id'

def get_top_terminal(stack):

    for i in range(len(stack) - 1, -1, -1):
        token = stack[i]
        if not (len(token) == 1 and token.isupper()):
            return token
    return None


def parse(input_string):

    
    tokens = tokenize(input_string)
    input_tokens = [get_token_type(t) for t in tokens]
    input_tokens.append('$') 
    
    stack = ['$']
    ip = 0 
    
    print(f"\n{'='*70}")
    print(f"Parsing: {input_string}")
    print(f"{'='*70}")
    print(f"Tokens: {input_tokens}\n")
    
    step = 1
    
    if len(input_tokens) > 1:  
        first_token = input_tokens[0]
        valid_starts = {'id', 'num', '(', 'not'}
        if first_token not in valid_starts:
            print(f"Step 1:")
            print(f"  ERROR: Expression cannot start with '{first_token}'")
            print(f"  Valid expression starts: id, num, (, not")
            print(f"\n{'='*70}")
            print("✗ STRING IS INVALID")
            print(f"{'='*70}\n")
            return False
    
    while True:
        a = get_top_terminal(stack)
        b = input_tokens[ip]
        
        print(f"Step {step}:")
        print(f"  Stack:  {stack}")
        print(f"  Top Terminal (a): {a}")
        print(f"  Input (b): {b} (position {ip})")
        
        if a == '$' and b == '$':
            print(f"  Action: ACCEPT ✓")
            print(f"\n{'='*70}")
            print("✓ STRING IS VALID")
            print(f"{'='*70}\n")
            return True
        
        if a in PRECEDENCE_TABLE and b in PRECEDENCE_TABLE[a]:
            relation = PRECEDENCE_TABLE[a][b]
        else:
            relation = ' '
        
        print(f"  Precedence({a}, {b}): {relation}")
        
        if relation == '<' or relation == '=':
            stack.append(b)
            ip += 1
            print(f"  Action: PUSH {b}")
        
        elif relation == '>':
            print(f"  Action: REDUCE (pop until finding '<')")

            last_popped_terminal = None
            reduced = False
            while len(stack) > 1:
                popped = stack.pop()
                if not (len(popped) == 1 and popped.isupper()):
                    last_popped_terminal = popped
                left_terminal = get_top_terminal(stack)
                if left_terminal and left_terminal in PRECEDENCE_TABLE and last_popped_terminal:
                    if last_popped_terminal in PRECEDENCE_TABLE[left_terminal]:
                        if PRECEDENCE_TABLE[left_terminal][last_popped_terminal] == '<':
                            stack.append('E')
                            print(f"    Popped handle, pushed generic E")
                            reduced = True
                            break
            if not reduced:
                print(f"  ERROR: Could not find matching '<' for reduce")
                print(f"\n{'='*70}")
                print("✗ STRING IS INVALID")
                print(f"{'='*70}\n")
                return False
        
        else:
            print(f"  Action: ERROR (no valid precedence relation)")
            print(f"\n{'='*70}")
            print("✗ STRING IS INVALID")
            print(f"{'='*70}\n")
            return False
        
        step += 1
        print()


# ============================================================================
# MAIN PROGRAM - Interactive Input
# ============================================================================
def print_precedence_table():
    """Nicely print the PRECEDENCE_TABLE."""
    # Prefer column order from the '$' row when available
    if '$' in PRECEDENCE_TABLE:
        cols = list(PRECEDENCE_TABLE['$'].keys())
    else:
        cols = sorted({c for row in PRECEDENCE_TABLE.values() for c in row.keys()})

    rows = list(PRECEDENCE_TABLE.keys())

    headers = [''] + cols
    # compute column widths
    widths = [max(len(h), 3) for h in headers]
    widths[0] = max(widths[0], max(len(r) for r in rows))
    for i, col in enumerate(cols, start=1):
        w = widths[i]
        for r in rows:
            v = PRECEDENCE_TABLE.get(r, {}).get(col, ' ')
            w = max(w, len(v))
        widths[i] = w

    # print header
    header_line = ' '.join(headers[i].rjust(widths[i]) for i in range(len(headers)))
    print(header_line)
    print(' '.join('-' * widths[i] for i in range(len(headers))))

    # print rows
    for r in rows:
        cells = [r.rjust(widths[0])]
        for i, col in enumerate(cols, start=1):
            cells.append(PRECEDENCE_TABLE.get(r, {}).get(col, ' ').rjust(widths[i]))
        print(' '.join(cells))

def main():
    print("\n" + "="*70)
    print("OPERATOR PRECEDENCE PARSER")
    print("="*70)
    print("\nPrecedence Table:")
    print_precedence_table()
    print("\nGrammar:")
    print("  E  →  E relop T  |  T")
    print("  T  →  T addop F  |  T + F  |  T - F  |  F")
    print("  F  →  F mulop P  |  F * P  |  F / P  |  P")
    print("  P  →  id  |  num  |  ( E )  |  not P")
    print("\nSupported Operators:")
    print("  - Additive: +, -")
    print("  - Multiplicative: *, /")
    print("  - Relational: <, >, <=, >=, ==, <>")
    print("  - Logical: not")
    print("\nOperands:")
    print("  - Numbers: 0-9")
    print("  - Identifiers: a-z, A-Z")
    print("="*70 + "\n")
    
    while True:
        try:
            user_input = input("Enter an expression to parse (or 'quit' to exit): ").strip()
            
            if user_input.lower() == 'quit':
                print("\nThank you for using the parser! Goodbye.\n")
                break
            
            if not user_input:
                print("Please enter a valid expression.\n")
                continue
            
            # Parse the input
            result = parse(user_input)
            
        except Exception as e:
            print(f"\n{'='*70}")
            print(f"ERROR: {e}")
            print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
