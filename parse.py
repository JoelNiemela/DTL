import re

from collections import deque

class Lexer:
	def __init__(self):
		self.tokens = deque()

	def tokenize(self, src):
		types = {
			'AT'    : r'@',
			'TIME'  : r'\d?\d:\d\d',
			'NAME'  : r'[A-Za-z]+',
			'COLON' : r':',
			'NL'    : r'\n+',
			'TAB'   : r'\t',
			'WS'    : r'\s',
			'ERROR' : r'.',
		}

		for tok_type, pattern in types.items():
			types[tok_type] = re.compile(pattern)

		self.tokens = deque()

		at_line_start = True
		line_indent = 0
		prev_line_indent = 0

		pos = 0
		while pos < len(src):
			token_type = "ERROR"
			token_val = ""
			for tok_type, pattern in types.items():
				match = pattern.match(src[pos:])
				if match:
					token_type = tok_type
					token_val = match.group(0)
					pos += len(token_val)
					break

			if at_line_start and token_type != 'TAB':
				if line_indent > prev_line_indent:
					for _ in range(line_indent-prev_line_indent):
						self.tokens.append({
							'tok_t' : 'OPEN',
						})
				elif line_indent < prev_line_indent:
					for _ in range(prev_line_indent-line_indent):
						self.tokens.append({
							'tok_t' : 'END',
						})

			match token_type:
				case 'NL':
					at_line_start = True
					prev_line_indent = line_indent
					line_indent = 0
				case 'TAB':
					if at_line_start:
						line_indent += 1
				case _:
					at_line_start = False
					self.tokens.append({
						'tok_t' : token_type,
						'value' : token_val,
					})

		for _ in range(prev_line_indent):
			self.tokens.append({
				'tok_t' : 'END',
			})

	def peak(self):
		if len(self.tokens) > 0:
			return self.tokens[0]
		else:
			return {'tok_t' : 'ERROR'}

	def pop(self):
		if len(self.tokens) > 0:
			return self.tokens.popleft()
		else:
			return {'tok_t' : 'ERROR'}

	def assert_token(self, tok_t, token=None):
		if token == None:
			token = self.pop()

		if token['tok_t'] != tok_t:
			print(f'Error: expected "{tok_t}", found "{token["tok_t"]}"')
			return False
		else:
			return True

class Parser:
	def __init__(self):
		self.lexer = Lexer()

	def parse(self, src):
		self.lexer.tokenize(src)

		return self.parse_segment()

	def parse_segment(self):
		self.lexer.assert_token('AT')
		name = self.lexer.pop()
		self.lexer.assert_token('NAME', name)

		if self.lexer.peak()['tok_t'] == 'OPEN':
			timelist = self.parse_timelist()
		else:
			timelist = [self.parse_time()]

		return timelist

	def parse_timelist(self):
		self.lexer.assert_token('OPEN')

		timelist = []
		while self.lexer.peak()['tok_t'] != 'END':
			timelist.append(self.parse_time())

		self.lexer.assert_token('END')

		return timelist

	def parse_time(self):
		self.lexer.assert_token('AT')

		time = self.lexer.pop()
		self.lexer.assert_token('TIME', time)

		return time['value']

