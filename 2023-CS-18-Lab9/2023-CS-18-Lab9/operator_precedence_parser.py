
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


# ============================================================================
# TOKENIZER - Convert input string into tokens
# ============================================================================
def tokenize(input_string):
    """
    Convert input string into tokens (operators, operands, parentheses)
    
    Examples:
        "a+b" → ['a', '+', 'b']
        "12*3" → ['12', '*', '3']
        "not x" → ['not', 'x']
    """
    tokens = []
    i = 0
    
    while i < len(input_string):
        # Skip whitespace
        if input_string[i].isspace():
            i += 1
            continue
        
        # Check for 'not' keyword
        if input_string[i:i+3] == 'not':
            tokens.append('not')
            i += 3
            continue
        
        # Check for numbers
        if input_string[i].isdigit():
            j = i
            while j < len(input_string) and input_string[j].isdigit():
                j += 1
            tokens.append(input_string[i:j])
            i = j
            continue
        
        # Check for identifiers (variable names)
        if input_string[i].isalpha() or input_string[i] == '_':
            j = i
            while j < len(input_string) and (input_string[j].isalnum() or input_string[j] == '_'):
                j += 1
            tokens.append(input_string[i:j])
            i = j
            continue
        
        # Check for operators and parentheses
        if input_string[i] in '+-*/()==<>':
            # Handle two-character operators
            if i + 1 < len(input_string) and input_string[i:i+2] in ['==', '<>', '<=', '>=']:
                tokens.append(input_string[i:i+2])
                i += 2
            else:
                tokens.append(input_string[i])
                i += 1
            continue
        
        # Unknown character
        i += 1
    
    return tokens


# ============================================================================
# GET TOKEN TYPE - Classify each token
# ============================================================================
def get_token_type(token):
    """
    Determine the type of a token for use in the precedence table
    
    Returns: 'id', 'num', '(', ')', operator, or 'not'
    """
    if token == '(':
        return '('
    elif token == ')':
        return ')'
    elif token == 'not':
        return 'not'
    elif token in ['+', '-']:
        return token  # addop
    elif token in ['*', '/']:
        return token  # mulop
    elif token in ['<', '>', '<=', '>=', '==', '<>']:
        return 'relop'
    elif token.isdigit() or (token[0].isdigit()):
        return 'num'
    else:
        return 'id'


# ============================================================================
# GET TOP TERMINAL - Find the topmost terminal on stack (skip non-terminals)
# ============================================================================
def get_top_terminal(stack):
    """
    Look through the stack from top to bottom and find the first terminal
    (skip any non-terminals like 'E', 'F', 'T', 'P')
    """
    for i in range(len(stack) - 1, -1, -1):
        token = stack[i]
        # Non-terminals are single uppercase letters
        if not (len(token) == 1 and token.isupper()):
            return token
    return None


# ============================================================================
# MAIN PARSER - Operator Precedence Parsing Algorithm
# ============================================================================
def parse(input_string):
    """
    Main parsing function using operator precedence algorithm
    
    Algorithm:
    1. Push '$' on stack, read first input symbol
    2. Repeat:
       a. If top-of-stack is '$' and current input is '$', ACCEPT
       b. Compare top terminal and current input using precedence table
       c. If '<' or '=': push current input, advance
       d. If '>': pop stack until finding '<'
       e. If ' ': ERROR
    """
    
    # Tokenize input
    tokens = tokenize(input_string)
    
    # Convert tokens to their types
    input_tokens = [get_token_type(t) for t in tokens]
    input_tokens.append('$')  # Add end-of-input marker
    
    # Initialize
    stack = ['$']
    ip = 0  # Input pointer
    
    print(f"\n{'='*70}")
    print(f"Parsing: {input_string}")
    print(f"{'='*70}")
    print(f"Tokens: {input_tokens}\n")
    
    step = 1
    
    # VALIDATION: First token must be a valid expression start
    # Valid starts: id, num, (, not
    if len(input_tokens) > 1:  # At least one token before '$'
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
        # Get top terminal on stack
        a = get_top_terminal(stack)
        
        # Get current input symbol
        b = input_tokens[ip]
        
        print(f"Step {step}:")
        print(f"  Stack:  {stack}")
        print(f"  Top Terminal (a): {a}")
        print(f"  Input (b): {b} (position {ip})")
        
        # ACCEPT condition
        if a == '$' and b == '$':
            print(f"  Action: ACCEPT ✓")
            print(f"\n{'='*70}")
            print("✓ STRING IS VALID")
            print(f"{'='*70}\n")
            return True
        
        # Get precedence relation from table
        if a in PRECEDENCE_TABLE and b in PRECEDENCE_TABLE[a]:
            relation = PRECEDENCE_TABLE[a][b]
        else:
            relation = ' '
        
        print(f"  Precedence({a}, {b}): {relation}")
        
        # PUSH operation
        if relation == '<' or relation == '=':
            stack.append(b)
            ip += 1
            print(f"  Action: PUSH {b}")
        
        # REDUCE operation
        elif relation == '>':
            print(f"  Action: REDUCE (pop until finding '<')")
            # Pop actual stack elements until we have popped a terminal
            # whose left neighbour terminal (now on top) is related by '<'.
            last_popped_terminal = None
            reduced = False
            while len(stack) > 1:
                popped = stack.pop()
                # If the popped element is a terminal (not a single uppercase non-terminal), record it
                if not (len(popped) == 1 and popped.isupper()):
                    last_popped_terminal = popped
                # Find the terminal now on top of the stack
                left_terminal = get_top_terminal(stack)
                if left_terminal and left_terminal in PRECEDENCE_TABLE and last_popped_terminal:
                    if last_popped_terminal in PRECEDENCE_TABLE[left_terminal]:
                        if PRECEDENCE_TABLE[left_terminal][last_popped_terminal] == '<':
                            # Replace the popped handle with a generic non-terminal E
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
        
        # ERROR operation
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
