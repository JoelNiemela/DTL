import re

from collections import deque

class Token:
	def __init__(self, tok_type, value=None):
		self.type = tok_type
		self.value = value

class Lexer:
	def __init__(self):
		self.tokens = deque()

	def tokenize(self, src):
		types = {
			'AT'       : r'@',
			'TIME'     : r'\d?\d:\d\d(-\d?\d:\d\d)?',
			'NAME'     : r'[A-Za-z]+',
			'DURATION' : r'([0-9]+\s(seconds|minutes|hours))|(second|minute|hour)',
			'CMD'      : r'![A-Za-z]+',
			'OPTION'   : r'#[A-Za-z]+',
			'DESC'     : r'\[(?P<val>[^\]]*)\]',
			'COLON'    : r':',
			'NL'       : r'\n+',
			'TAB'      : r'\t',
			'WS'       : r'\s',
			'ERROR'    : r'.',
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
					if 'val' in match.groupdict():
						token_val = match.group('val')
					else:
						token_val = match.group(0)
					pos += len(match.group(0))
					break

			if at_line_start and token_type != 'TAB':
				if line_indent > prev_line_indent:
					for _ in range(line_indent-prev_line_indent):
						self.tokens.append(Token('OPEN'))
				elif line_indent < prev_line_indent:
					for _ in range(prev_line_indent-line_indent):
						self.tokens.append(Token('END'))

			match token_type:
				case 'NL':
					at_line_start = True
					prev_line_indent = line_indent
					line_indent = 0

					self.tokens.append(Token('NL'))
				case 'TAB':
					if at_line_start:
						line_indent += 1
				case 'WS':
					continue
				case _:
					at_line_start = False
					self.tokens.append(Token(token_type, token_val))

		for _ in range(prev_line_indent):
			self.tokens.append(Token('END'))

		print([t.type for t in self.tokens])

	def peak(self):
		if len(self.tokens) > 0:
			return self.tokens[0]
		else:
			return Token('EOF')

	def pop(self):
		print(self.peak().type)
		if len(self.tokens) > 0:
			return self.tokens.popleft()
		else:
			return Token('EOF')

	def assert_token(self, tok_t):
		token = self.peak()

		if token.type != tok_t:
			print(f'Error: expected {tok_t}, found {token.type}')
			return None
		else:
			return self.pop()

class Parser:
	def __init__(self):
		self.lexer = Lexer()

	def parse(self, src):
		self.lexer.tokenize(src)

		return self.parse_segments()

	def parse_block(self, fn):
		self.lexer.assert_token('OPEN')

		ln = []
		while self.lexer.peak().type != 'END':
			ln.append(fn())

		self.lexer.assert_token('END')

		return ln

	def parse_segments(self):
		segments = []
		while self.lexer.peak().type == 'AT':
			segments.append(self.parse_segment())

		return segments

	def parse_segment(self):
		self.lexer.assert_token('AT')
		name = self.lexer.assert_token('NAME')
		self.lexer.assert_token('NL')

		if self.lexer.peak().type == 'OPEN':
			timelist = self.parse_timelist()
		else:
			timelist = [self.parse_time()]

		return (name.value, timelist)

	def parse_timelist(self):
		return self.parse_block(self.parse_time)

	def parse_time(self):
		self.lexer.assert_token('AT')

		time = self.lexer.assert_token('TIME')

		desc = self.lexer.assert_token('DESC')

		self.lexer.assert_token('NL')

		if self.lexer.peak().type == 'OPEN':
			attr = self.parse_attrs()
		else:
			attr = None

		return (time.value, desc.value, attr)

	def parse_attrs(self):
		return self.parse_block(self.parse_attr)

	def parse_attr(self):
		match self.lexer.peak().type:
			case 'CMD':
				return self.parse_cmd()
			case err:
				print(f'Error: expected (CMD, AT), found {err}')
				return None

	def parse_cmd(self):
		cmd = self.lexer.assert_token('CMD')

		desc = self.lexer.assert_token('DESC')

		self.lexer.assert_token('NL')

		if self.lexer.peak().type == 'OPEN':
			options = self.parse_options()
		else:
			options = None

		return (cmd.value, desc.value, options)

	def parse_options(self):
		return self.parse_block(self.parse_option)

	def parse_option(self):
		option = self.lexer.assert_token('OPTION')

		match self.lexer.peak().type:
			case 'DURATION':
				value = self.lexer.assert_token('DURATION').value
			case 'DESC':
				value = self.lexer.assert_token('DESC').value
			case err:
				print(f'Error: expected (DURATION, DESC), found {err}')

		self.lexer.assert_token('NL')

		return (option.value, value)
