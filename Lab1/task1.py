def tokenize_expression(expr):
    tokens = []
    i = 0
    while i < len(expr):
        ch = expr[i]
        if ch in ' \t':
            i += 1
            continue

        if ch.isdigit():
            num = ch
            i += 1
            while i < len(expr) and expr[i].isdigit():
                num += expr[i]
                i += 1
            tokens.append(f"NUMBER:{num}")

        # Identifier 
        elif ch.isalpha():
            ident = ch
            i += 1
            while i < len(expr) and expr[i].isalnum():
                ident += expr[i]
                i += 1
            tokens.append(f"IDENT:{ident}")

        # Operators and parentheses
        elif ch in '+-*/()=':
            tokens.append(f"OP:{ch}")
            i += 1

        # Parentheses 
        elif ch in '()':
            tokens.append(f"OP:{ch}")
            i += 1

        else:
            tokens.append(f"INVALID:{ch}")
            i += 1

    tokens.append("EOF")
    return tokens

def print_tokenization(expr, tokens):
    print("\nInput expression:", expr)
    print("Tokenizing")

    for token in tokens[:-1]:
        if token.startswith("NUMBER"):
            print(f"  Found NUMBER -> {token.split(':')[1]}")
        elif token.startswith("IDENT"):
            print(f"  Found IDENTIFIER -> {token.split(':')[1]}")
        elif token.startswith("OP"):
            print(f"  Found OPERATOR -> {token.split(':')[1]}")
        else:
            print(f"  Invalid character -> {token.split(':')[1]}")

    print("  Found EOF (End of Expression)")
    print("\nAll tokens collected:", tokens)


def main():
    print("Task1")
    print("Enter expressions (empty line to quit):")

    while True:
        expr = input("> ").strip()
        if not expr:
            break
        tokens = tokenize_expression(expr)  
        print_tokenization(expr, tokens)   

if __name__ == "__main__":
    main()
