
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

SINGLE_CHAR = {
    '+': TT_ADDOP,    '-': TT_ADDOP,
    '*': TT_MULOP,    '/': TT_MULOP,
    '=': TT_RELOP,
    '(': TT_LPAREN,   ')': TT_RPAREN,
    '[': TT_LBRACKET, ']': TT_RBRACKET,
    ';': TT_SEMICOLON, ',': TT_COMMA,
}


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

class BaseLexer:
    def __init__(self, source):
        self.source = source
        self.pos    = 0
        self.line   = 1

    def _peek(self, offset=0):
        i = self.pos + offset
        return self.source[i] if i < len(self.source) else ''

    def _advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
        return ch

    def _unget(self, ch):
        if self.pos > 0:
            self.pos -= 1
            if ch == '\n':
                self.line -= 1


    def skip(self):
        while True:
            ch = self._peek()
            if ch == '':
                return                     
            if ch in ' \t\r\n':
                self._advance()             
            elif ch == '{':
                self._advance()            
                self._skip_comment()        
            else:
                return                     

    def _skip_comment(self):
        while True:
            ch = self._peek()
            if ch == '':
                raise LexicalError("Unterminated comment — reached end of file")
            if ch == '{':
                raise LexicalError(f"Line {self.line}: nested '{{' inside comment")
            self._advance()
            if ch == '}':
                return                    

    def scan_word(self, first_char, line):
        word = first_char
        while self._peek() != '' and (self._peek().isalnum() or self._peek() == '_'):
            word += self._advance()

        low = word.lower()
        if low in ('or',):
            return Token(TT_ADDOP,   low,  line=line)
        if low in ('div', 'mod', 'and'):
            return Token(TT_MULOP,   low,  line=line)
        if low in KEYWORDS:
            return Token(TT_KEYWORD, low,  line=line)
        return Token(TT_ID, word, line=line)

    def scan_num(self, first_digit, line):

        lex  = first_digit
        real = False
        while self._peek().isdigit():
            lex += self._advance()
        if self._peek() == '.' and self._peek(1) != '.' and self._peek(1).isdigit():
            lex += self._advance()         
            real = True
            while self._peek().isdigit():
                lex += self._advance()

        if self._peek() in ('E', 'e'):
            lex += self._advance()
            real = True
            if self._peek() in ('+', '-'):
                lex += self._advance()     
            if not self._peek().isdigit():
                raise LexicalError(f"Line {line}: bad exponent in '{lex}'")
            while self._peek().isdigit():
                lex += self._advance()

        val = float(lex) if real else int(lex)
        return Token(TT_NUM, lex, val, line)


    def tokenize_all(self):
        """Keep calling next_token() until EOF and return the list."""
        tokens = []
        while True:
            tok = self.next_token()
            tokens.append(tok)
            if tok.type == TT_EOF:
                break
        return tokens


def print_tokens(tokens, title=""):
    w = 56
    print(f"\n{'='*w}")
    if title:
        print(f"  {title}")
        print(f"{'='*w}")
    print(f"  {'Line':<5} {'Type':<12} {'Lexeme':<16} Value")
    print(f"  {'-'*(w-2)}")
    for t in tokens:
        v = str(t.value) if t.value is not None else "-"
        print(f"  {t.line:<5} {t.type:<12} {t.lexeme:<16} {v}")
    print(f"  {'-'*(w-2)}")
    n = sum(1 for t in tokens if t.type != TT_EOF)
    print(f"  Total: {n} tokens")
    print(f"{'='*w}\n")