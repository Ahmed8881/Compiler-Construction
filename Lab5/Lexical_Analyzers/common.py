TT_KEYWORD   = 'KEYWORD'
TT_ID        = 'ID'
TT_NUM       = 'NUM'
TT_ASSIGNOP  = 'ASSIGNOP'  
TT_RELOP     = 'RELOP'      
TT_ADDOP     = 'ADDOP'     
TT_MULOP     = 'MULOP'      
TT_LPAREN    = 'LPAREN'     
TT_RPAREN    = 'RPAREN'     
TT_LBRACKET  = 'LBRACKET'   
TT_RBRACKET  = 'RBRACKET'   
TT_SEMICOLON = 'SEMICOLON'  
TT_COMMA     = 'COMMA'      
TT_COLON     = 'COLON'      
TT_DOT       = 'DOT'        
TT_DOTDOT    = 'DOTDOT'     
TT_EOF       = 'EOF'

KEYWORDS = {
    'program', 'var', 'integer', 'real', 'array', 'of',
    'function', 'procedure', 'begin', 'end',
    'if', 'then', 'else', 'while', 'do', 'not',
    'div', 'mod', 'and', 'or'
}
ADDOP_KW = {'or'}          
MULOP_KW = {'div', 'mod', 'and'}  


class Token:
    def __init__(self, type, lexeme, value=None, line=1):
        self.type   = type
        self.lexeme = lexeme
        self.value  = value  
        self.line   = line

    def __repr__(self):
        v = f", val={self.value}" if self.value is not None else ""
        return f"Token({self.type}, '{self.lexeme}'{v}, line={self.line})"


class LexicalError(Exception):
    pass

def classify_word(word, line):
    low = word.lower()
    if low in ADDOP_KW:
        return Token(TT_ADDOP,   low,  line=line)
    if low in MULOP_KW:
        return Token(TT_MULOP,   low,  line=line)
    if low in KEYWORDS:
        return Token(TT_KEYWORD, low,  line=line)
    return Token(TT_ID, word, line=line)

class BaseLexer:

    def __init__(self, source: str):
        self.source = source
        self.pos    = 0
        self.line   = 1

    def _peek(self, offset=0) -> str:
        idx = self.pos + offset
        return self.source[idx] if idx < len(self.source) else ''

    def _advance(self) -> str:
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
        return ch

    def _unget(self, ch: str):
        if self.pos > 0:
            self.pos -= 1
            if ch == '\n':
                self.line -= 1

    def tokenize_all(self):
        tokens = []
        while True:
            tok = self.next_token()
            tokens.append(tok)
            if tok.type == TT_EOF:
                break
        return tokens


def print_tokens(tokens, title=""):
    print(f"\n{'='*58}")
    if title:
        print(f"  {title}")
        print(f"{'='*58}")
    print(f"{'Line':<6} {'Type':<13} {'Lexeme':<18} Value")
    print(f"{'-'*58}")
    for t in tokens:
        v = str(t.value) if t.value is not None else "-"
        print(f"{t.line:<6} {t.type:<13} {t.lexeme:<18} {v}")
    print(f"{'-'*58}")
    count = sum(1 for t in tokens if t.type != TT_EOF)
    print(f"Total: {count} tokens")
    print(f"{'='*58}\n")