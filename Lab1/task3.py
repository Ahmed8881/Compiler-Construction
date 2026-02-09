from task1 import tokenize_expression
variables = {}
tokens = []
pos = 0

def current_token():
    if pos < len(tokens):
        return tokens[pos]
    return None

def advance():
    global pos
    pos += 1

def parseFactor():
    tok = current_token()
    if tok is None:
        return 0

    if tok.startswith("NUMBER"):
        val = int(tok.split(":")[1])
        print(f"  Factor NUMBER -> {val}")
        advance()
        return val

    elif tok.startswith("IDENT"):
        name = tok.split(":")[1]
        val = variables.get(name, 0)
        if name not in variables:
            print(f"  Factor IDENT '{name}' not defined, assuming 0")
        else:
            print(f"  Factor IDENT '{name}' = {val}")
        advance()
        return val

    elif tok == "OP:(":
        print("  Factor -> Parentheses ( ... )")
        advance()  # skip '('
        val = parseExpression()
        if current_token() == "OP:)":
            advance()  # skip ')'
        else:
            print("  Warning: Missing closing parenthesis")
        return val

    else:
        print(f"  Invalid factor: {tok}")
        advance()
        return 0

def parseTerm():
    left = parseFactor()
    while True:
        tok = current_token()
        if tok is None:
            break
        if tok.startswith("OP"):
            op = tok.split(":")[1]
            if op in "*/":
                advance()
                right = parseFactor()
                if op == "*":
                    print(f"  Applying {left} * {right}")
                    left *= right
                else:
                    print(f"  Applying {left} / {right}")
                    left /= right
            else:
                break
        else:
            break
    return left

def parseExpression():
    left = parseTerm()
    while True:
        tok = current_token()
        if tok is None:
            break
        if tok.startswith("OP"):
            op = tok.split(":")[1]
            if op in "+-":
                advance()
                right = parseTerm()
                if op == "+":
                    print(f"  Applying {left} + {right}")
                    left += right
                else:
                    print(f"  Applying {left} - {right}")
                    left -= right
            else:
                break
        else:
            break
    return left


def evaluate(tokens_input):
    global tokens, pos
    tokens = tokens_input
    pos = 0

    if "OP:=" in tokens:
        idx = tokens.index("OP:=")
        var_name = tokens[idx-1].split(":")[1]
        right_tokens = tokens[idx+1:-1] 
        print(f"[Assignment] {var_name} = ...")
        tokens = right_tokens + ["EOF"]
        pos = 0
        value = parseExpression()
        variables[var_name] = value
        print(f"[Result] {var_name} = {value}")
    else:
        value = parseExpression()
        print(f"[Result] Expression = {value}")


def main():
    print("Task ")
    print("Empty line to quit")
    while True:
        expr = input("> ").strip()
        if not expr:
            break
        toks = tokenize_expression(expr)
        print("[Tokens]", toks)
        evaluate(toks)
        print("-"*50)

if __name__ == "__main__":
    main()
