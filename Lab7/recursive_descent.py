import sys
from dataclasses import dataclass


KEYWORDS = {
	"program","var","integer","real","array","of","function","procedure","begin","end","if","then","else","while","do","not","div","mod","and","or",
}

@dataclass
class Token:
	kind: str
	value: str
	line: int

class ParseError(Exception):
	pass

class Lexer:
	def __init__(self, source: str):
		self.source = source
		self.length = len(source)
		self.index = 0
		self.line = 1

	def tokenize(self):
		tokens = []
		while True:
			self._skip_whitespace_and_comments()
			if self.index >= self.length:
				tokens.append(Token("EOF", "EOF", self.line))
				return tokens

			ch = self.source[self.index]

			if ch.isalpha() or ch == "_":
				tokens.append(self._scan_word())
				continue

			if ch.isdigit():
				tokens.append(self._scan_number())
				continue

			two = self.source[self.index : self.index + 2]
			if two == ":=":
				tokens.append(self._make_token("ASSIGNOP", ":="))
				self.index += 2
				continue
			if two in {"<=", ">=", "<>", ".."}:
				kind = "DOTDOT" if two == ".." else "RELOP"
				tokens.append(self._make_token(kind, two))
				self.index += 2
				continue

			single = {
				"+": ("ADDOP", "+"),
				"-": ("ADDOP", "-"),
				"*": ("MULOP", "*"),
				"/": ("MULOP", "/"),
				"=": ("RELOP", "="),
				"<": ("RELOP", "<"),
				">": ("RELOP", ">"),
				"(": ("LPAREN", "("),
				")": ("RPAREN", ")"),
				"[": ("LBRACKET", "["),
				"]": ("RBRACKET", "]"),
				";": ("SEMICOLON", ";"),
				",": ("COMMA", ","),
				":": ("COLON", ":"),
				".": ("DOT", "."),
			}
			if ch in single:
				kind, value = single[ch]
				tokens.append(self._make_token(kind, value))
				self.index += 1
				continue

			raise ParseError(f"Line {self.line}: unexpected character {ch!r}")

	def _make_token(self, kind: str, value: str):
		return Token(kind, value, self.line)

	def _skip_whitespace_and_comments(self):
		while self.index < self.length:
			ch = self.source[self.index]
			if ch in " \t\r":
				self.index += 1
				continue
			if ch == "\n":
				self.index += 1
				self.line += 1
				continue
			if ch == "{":
				self.index += 1
				while self.index < self.length and self.source[self.index] != "}":
					if self.source[self.index] == "\n":
						self.line += 1
					self.index += 1
				if self.index >= self.length:
					raise ParseError(f"Line {self.line}: unterminated comment")
				self.index += 1
				continue
			break

	def _scan_word(self):
		start = self.index
		while self.index < self.length and (
			self.source[self.index].isalnum() or self.source[self.index] == "_"
		):
			self.index += 1
		word = self.source[start:self.index]
		lower = word.lower()
		if lower in KEYWORDS:
			if lower in {"div", "mod", "and"}:
				return Token("MULOP", lower, self.line)
			if lower == "or":
				return Token("ADDOP", lower, self.line)
			return Token("KEYWORD", lower, self.line)
		return Token("ID", word, self.line)

	def _scan_number(self):
		start = self.index
		while self.index < self.length and self.source[self.index].isdigit():
			self.index += 1

		if self.index < self.length and self.source[self.index] == ".":
			if self.index + 1 < self.length and self.source[self.index + 1] == ".":
				pass
			else:
				self.index += 1
				while self.index < self.length and self.source[self.index].isdigit():
					self.index += 1

		if self.index < self.length and self.source[self.index] in {"e", "E"}:
			self.index += 1
			if self.index < self.length and self.source[self.index] in {"+", "-"}:
				self.index += 1
			if self.index >= self.length or not self.source[self.index].isdigit():
				raise ParseError(f"Line {self.line}: malformed exponent")
			while self.index < self.length and self.source[self.index].isdigit():
				self.index += 1

		return Token("NUM", self.source[start:self.index], self.line)


class RecursiveDescentParser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.pos = 0

	def parse(self):
		self.program()
		self.expect("EOF")
		return True

	def current(self):
		return self.tokens[self.pos]

	def advance(self):
		token = self.current()
		self.pos += 1
		return token

	def match(self, kind=None, value=None):
		token = self.current()
		if kind is not None and token.kind != kind:
			return False
		if value is not None and token.value != value:
			return False
		self.pos += 1
		return True

	def expect(self, kind=None, value=None):
		token = self.current()
		if kind is not None and token.kind != kind:
			expected = value if value is not None else kind
			raise ParseError(
				f"Line {token.line}: expected {expected}, got {token.kind}({token.value})"
			)
		if value is not None and token.value != value:
			raise ParseError(
				f"Line {token.line}: expected {value}, got {token.kind}({token.value})"
			)
		self.pos += 1
		return token

	def check(self, kind=None, value=None):
		token = self.current()
		if kind is not None and token.kind != kind:
			return False
		if value is not None and token.value != value:
			return False
		return True

	def program(self):
		self.expect("KEYWORD", "program")
		self.expect("ID")
		self.expect("LPAREN")
		self.identifier_list()
		self.expect("RPAREN")
		self.expect("SEMICOLON")
		self.declarations()
		self.subprogram_declarations()
		self.compound_statement()

	def identifier_list(self):
		self.expect("ID")
		while self.match("COMMA"):
			self.expect("ID")

	def declarations(self):
		while self.check("KEYWORD", "var"):
			self.expect("KEYWORD", "var")
			self.identifier_list()
			self.expect("COLON")
			self.type_spec()
			self.expect("SEMICOLON")

	def type_spec(self):
		if self.match("KEYWORD", "integer"):
			return
		if self.match("KEYWORD", "real"):
			return
		if self.match("KEYWORD", "array"):
			self.expect("LBRACKET")
			self.expect("NUM")
			self.expect("DOTDOT")
			self.expect("NUM")
			self.expect("RBRACKET")
			self.expect("KEYWORD", "of")
			self.standard_type()
			return
		token = self.current()
		raise ParseError(f"Line {token.line}: expected type specification")

	def standard_type(self):
		if self.match("KEYWORD", "integer"):
			return
		if self.match("KEYWORD", "real"):
			return
		token = self.current()
		raise ParseError(f"Line {token.line}: expected integer or real")

	def subprogram_declarations(self):
		while self.check("KEYWORD", "function") or self.check("KEYWORD", "procedure"):
			self.subprogram_declaration()


	def subprogram_declaration(self):
		self.subprogram_head()
		self.declarations()
		self.compound_statement()

	def subprogram_head(self):
		if self.match("KEYWORD", "function"):
			self.expect("ID")
			self.arguments()
			self.expect("COLON")
			self.standard_type()
			self.expect("SEMICOLON")
			return
		if self.match("KEYWORD", "procedure"):
			self.expect("ID")
			self.arguments()
			self.expect("SEMICOLON")
			return
		token = self.current()
		raise ParseError(f"Line {token.line}: expected function or procedure")

	def arguments(self):
		if self.match("LPAREN"):
			self.parameter_list()
			self.expect("RPAREN")

	def parameter_list(self):
		self.identifier_list()
		self.expect("COLON")
		self.type_spec()
		while self.match("SEMICOLON"):
			self.identifier_list()
			self.expect("COLON")
			self.type_spec()

	def compound_statement(self):
		self.expect("KEYWORD", "begin")
		self.optional_statements()
		self.expect("KEYWORD", "end")

	def optional_statements(self):
		if self.check_statement_start():
			self.statement_list()

	def statement_list(self):
		self.statement()
		while self.match("SEMICOLON"):
			if self.check("KEYWORD", "end"):
				break
			self.statement()

	def statement(self):
		if self.check("ID"):
			if self.next_is("ASSIGNOP") or self.next_is("LBRACKET"):
				self.variable()
				self.expect("ASSIGNOP")
				self.expression()
			else:
				self.procedure_statement()
			return

		if self.check("KEYWORD", "begin"):
			self.compound_statement()
			return

		if self.match("KEYWORD", "if"):
			self.expression()
			self.expect("KEYWORD", "then")
			self.statement()
			self.expect("KEYWORD", "else")
			self.statement()
			return

		if self.match("KEYWORD", "while"):
			self.expression()
			self.expect("KEYWORD", "do")
			self.statement()
			return

		token = self.current()
		raise ParseError(f"Line {token.line}: invalid statement")

	def variable(self):
		self.expect("ID")
		if self.match("LBRACKET"):
			self.expression()
			self.expect("RBRACKET")

	def procedure_statement(self):
		self.expect("ID")
		if self.match("LPAREN"):
			self.expression_list()
			self.expect("RPAREN")

	def expression_list(self):
		self.expression()
		while self.match("COMMA"):
			self.expression()

	def expression(self):
		self.simple_expression()
		if self.check("RELOP"):
			self.advance()
			self.simple_expression()

	def simple_expression(self):
		if self.check("ADDOP") and self.current().value in {"+", "-"}:
			self.advance()
		self.term()
		while self.check("ADDOP"):
			self.advance()
			self.term()

	def term(self):
		self.factor()
		while self.check("MULOP"):
			self.advance()
			self.factor()

	def factor(self):
		if self.match("ID"):
			if self.match("LPAREN"):
				self.expression_list()
				self.expect("RPAREN")
			return
		if self.match("NUM"):
			return
		if self.match("LPAREN"):
			self.expression()
			self.expect("RPAREN")
			return
		if self.match("KEYWORD", "not"):
			self.factor()
			return
		token = self.current()
		raise ParseError(f"Line {token.line}: invalid factor")

	def check_statement_start(self):
		if self.check("ID"):
			return True
		if self.check("KEYWORD", "begin"):
			return True
		if self.check("KEYWORD", "if"):
			return True
		if self.check("KEYWORD", "while"):
			return True
		return False

	def next_is(self, kind):
		if self.pos + 1 >= len(self.tokens):
			return False
		return self.tokens[self.pos + 1].kind == kind


def parse_source(source: str):
	tokens = Lexer(source).tokenize()
	parser = RecursiveDescentParser(tokens)
	return parser.parse()


def parse_file(path: str):
	with open(path, "r", encoding="utf-8", errors="ignore") as handle:
		return parse_source(handle.read())


def main():
	try:
		if len(sys.argv) >= 2:
			parse_file(sys.argv[1])
		else:
			print("Enter Pascal code  line by line.")
			print("Press Enter on an empty line to check ans.")
			lines = []
			while True:
				try:
					line = input()
				except EOFError:
					break
				if line == "":
					break
				lines.append(line)
			source = "\n".join(lines)
			if not source.strip():
				print("No input provided.")
				sys.exit(1)
			parse_source(source)
		print("Input accepted: syntax is valid.")
	except ParseError as error:
		print(f"Syntax error: {error}")
		sys.exit(1)


if __name__ == "__main__":
	main()
