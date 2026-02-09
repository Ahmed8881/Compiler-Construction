# Task 3: Parser and evaluator (human-readable output)

from task1 import tokenize, TokenType

class ASTNode:
	pass

class NumberNode(ASTNode):
	def __init__(self, value):
		self.value = value

	def __repr__(self):
		return f'Number({self.value})'

class VarNode(ASTNode):
	def __init__(self, name):
		self.name = name

	def __repr__(self):
		return f'Var({self.name})'

class BinOpNode(ASTNode):
	def __init__(self, op, left, right):
		self.op = op
		self.left = left
		self.right = right

	def __repr__(self):
		return f'BinOp({self.op}, {self.left}, {self.right})'

class AssignNode(ASTNode):
	def __init__(self, name, expr):
		self.name = name
		self.expr = expr

	def __repr__(self):
		return f'Assign({self.name} = {self.expr})'

class Parser:
	def __init__(self, tokens):
		self.tokens = tokens
		self.pos = 0
		self.cur = tokens[0]

	def advance(self):
		self.pos += 1
		if self.pos < len(self.tokens):
			self.cur = self.tokens[self.pos]
		else:
			self.cur = None

	def expect(self, ttype):
		if self.cur.type == ttype:
			self.advance()
		else:
			raise SyntaxError(f'Expected {ttype} but got {self.cur.type}')

	def parse(self):
		node = self.parse_statement()
		return node

	def parse_statement(self):
		# assignment or expression
		if self.cur.type == TokenType.IDENTIFIER and self._peek().type == TokenType.ASSIGN:
			name = self.cur.value
			self.advance()  # ident
			self.expect(TokenType.ASSIGN)
			expr = self.parse_expr()
			return AssignNode(name, expr)
		else:
			return self.parse_expr()

	def _peek(self):
		if self.pos + 1 < len(self.tokens):
			return self.tokens[self.pos + 1]
		return TokenType.EOF

	def parse_expr(self):
		node = self.parse_term()
		while self.cur.type in (TokenType.PLUS, TokenType.MINUS):
			op = self.cur.type
			self.advance()
			right = self.parse_term()
			node = BinOpNode(op, node, right)
		return node

	def parse_term(self):
		node = self.parse_factor()
		while self.cur.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
			op = self.cur.type
			self.advance()
			right = self.parse_factor()
			node = BinOpNode(op, node, right)
		return node

	def parse_factor(self):
		if self.cur.type == TokenType.NUMBER:
			val = self.cur.value
			self.advance()
			return NumberNode(val)
		elif self.cur.type == TokenType.IDENTIFIER:
			name = self.cur.value
			self.advance()
			return VarNode(name)
		elif self.cur.type == TokenType.LPAREN:
			self.advance()
			node = self.parse_expr()
			self.expect(TokenType.RPAREN)
			return node
		else:
			raise SyntaxError(f'Unexpected token in factor: {self.cur}')

class Evaluator:
	def __init__(self):
		self.vars = {}
		self.logs = []

	def eval(self, node):
		# human-readable evaluation that records steps in self.logs
		if isinstance(node, NumberNode):
			self.logs.append(f'Number literal: {node.value}')
			return node.value
		if isinstance(node, VarNode):
			if node.name in self.vars:
				val = self.vars[node.name]
				self.logs.append(f'Lookup variable {node.name} => {val}')
				return val
			else:
				raise NameError(f'Undefined variable: {node.name}')
		if isinstance(node, AssignNode):
			self.logs.append(f'Evaluating assignment to {node.name}')
			val = self.eval(node.expr)
			self.vars[node.name] = val
			self.logs.append(f'Assigned {node.name} = {val}')
			return val
		if isinstance(node, BinOpNode):
			self.logs.append(f'Evaluating left side of {node.op.name}')
			left = self.eval(node.left)
			self.logs.append(f'Evaluating right side of {node.op.name}')
			right = self.eval(node.right)
			if node.op == TokenType.PLUS:
				res = left + right
			elif node.op == TokenType.MINUS:
				res = left - right
			elif node.op == TokenType.MULTIPLY:
				res = left * right
			elif node.op == TokenType.DIVIDE:
				res = left / right
			else:
				raise SyntaxError('Unknown binary operator')
			self.logs.append(f'Computed {left} {node.op.name} {right} = {res}')
			return res

def ast_to_string(node, indent=0):
	sp = '  ' * indent
	if isinstance(node, NumberNode):
		return sp + f'Number({node.value})'
	if isinstance(node, VarNode):
		return sp + f'Var({node.name})'
	if isinstance(node, AssignNode):
		s = sp + f'Assign({node.name})\n'
		s += ast_to_string(node.expr, indent + 1)
		return s
	if isinstance(node, BinOpNode):
		s = sp + f'BinOp({node.op.name})\n'
		s += ast_to_string(node.left, indent + 1) + '\n'
		s += ast_to_string(node.right, indent + 1)
		return s
	return sp + 'Unknown'

def main():
	evaluator = Evaluator()
	print('Enter expressions (empty line to quit):')
	while True:
		try:
			line = input('> ').strip()
		except EOFError:
			break
		if line == '':
			break
		print('\nExpression:', line)
		# Tokenize
		try:
			toks = tokenize(line)
			# pretty-format tokens (skip EOF)
			display = []
			for t in toks:
				if t.type.name == 'EOF':
					continue
				if t.value is None:
					display.append(f'{t.type.name}')
				else:
					display.append(f'{t.type.name}:{t.value}')
			print('Tokens:', '[' + ', '.join(display) + ']')
		except Exception as e:
			print('Lexing error:', e)
			continue
		# Parse
		try:
			parser = Parser(toks)
			ast = parser.parse()
			print('\nAST:')
			print(ast_to_string(ast))
		except Exception as e:
			print('Parsing error:', e)
			continue
		# Evaluate
		try:
			print('\nEvaluation steps:')
			evaluator.logs = []
			result = evaluator.eval(ast)
			# print numbered logs
			for i, msg in enumerate(evaluator.logs, start=1):
				print(f'  Step {i}: {msg}')
			if isinstance(ast, AssignNode):
				print(f'\nResult: Variable {ast.name} = {result}')
			else:
				print(f'\nResult: {result}')
			# show symbol table
			if evaluator.vars:
				print('\nSymbol table:')
				for name, val in evaluator.vars.items():
					print(f'  {name} = {val}')
		except Exception as e:
			print('Evaluation error:', e)

if __name__ == '__main__':
	main()

