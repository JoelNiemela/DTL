import re

from collections import deque

class Token:
	def __init__(self, tok_type, value=None):
		self.type = tok_type
		self.value = value

class Lexer:
	def __init__(self, debug=False):
		self.tokens = deque()
		self.debug = debug

	def tokenize(self, src):
		types = {
			'AT'       : r'@',
			'YEAR'     : r'\d{4}',
			'MONTH'    : r'January|February|March|April|May|June|July|August|September|October|November|December',
			'DATE'     : r'([2-3]?1st|2?2nd|2?3rd|[1-2]?[3-9]th|30th|11th|12th|13th)',
			'DAY'      : r'Mon(day)|Tue(sday)|Wed(esday)|Thu(rsday)|Fri(day)|Sat(urday)|Sun(day)',
			'TIME'     : r'\d?\d:\d\d(-\d?\d:\d\d)?',
			'DURATION' : r'([0-9]+\s(seconds|minutes|hours))|(second|minute|hour)',
			'CMD'      : r'![A-Za-z]+',
			'OPTION'   : r'#[A-Za-z]+',
			'DESC'     : r'\[(?P<val>[^\]]*)\]',
			'FOR'      : r'for',
			'COLON'    : r':',
			'ONGOING'  : r'\.\.\.',
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
				case 'ERROR':
					print(f'Error: unexpected charachter "{token_val}"')
					at_line_start = False
					self.tokens.append(Token(token_type, token_val))
				case _:
					at_line_start = False
					self.tokens.append(Token(token_type, token_val))

		for _ in range(prev_line_indent):
			self.tokens.append(Token('END'))

		if self.debug:
			print(' '.join([t.type for t in self.tokens]))

	def peak(self):
		if len(self.tokens) > 0:
			return self.tokens[0]
		else:
			return Token('EOF')

	def pop(self):
		if self.debug:
			print(self.peak().type)

		if len(self.tokens) > 0:
			return self.tokens.popleft()
		else:
			return Token('EOF')

	def assert_token(self, tok_t):
		if not isinstance(tok_t, list):
			tok_t = [tok_t]

		token = self.peak()

		if not token.type in tok_t:
			print(f'Error: expected {", ".join(tok_t)}, found {token.type}')
			return None
		else:
			return self.pop()
