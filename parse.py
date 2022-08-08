from tokenize import Lexer, Token
import ast

class Parser:
	def __init__(self, debug=False):
		self.lexer = Lexer(debug=debug)

	def parse(self, src):
		self.lexer.tokenize(src)

		segments = []
		while self.lexer.peak().type == 'AT':
			segments.append(self.parse_segment())

		return ast.File(segments)

	def parse_block(self, fn):
		self.lexer.assert_token('OPEN')

		ln = []
		while self.lexer.peak().type != 'END':
			ln.append(fn())

		self.lexer.assert_token('END')

		return ln

	def parse_segments(self):
		return self.parse_block(self.parse_segment)

	def parse_segment(self):
		match self.lexer.peak().type:
			case 'AT':
				return self.parse_time()
			case 'CMD':
				return self.parse_cmd()
			case err:
				print(f'Error: expected CMD, AT, found {err}')
				return None

	def parse_time(self):
		self.lexer.assert_token('AT')
		time = [self.lexer.assert_token(['YEAR', 'MONTH', 'DATE', 'DAY', 'TIME'])]
		while self.lexer.peak().type in ['YEAR', 'MONTH', 'DATE', 'DAY', 'TIME']:
			time.append(self.lexer.pop())

		if self.lexer.peak().type == 'DESC':
			desc = self.lexer.assert_token('DESC').value
		else:
			desc = None

		self.lexer.assert_token('NL')

		segments = []
		if self.lexer.peak().type == 'OPEN':
			segments = self.parse_segments()

		return ast.Segment([t.value for t in time], desc, segments, [])

	def parse_cmd(self):
		cmd = self.lexer.assert_token('CMD')

		desc = self.lexer.assert_token('DESC')

		self.lexer.assert_token('NL')

		if self.lexer.peak().type == 'OPEN':
			options = self.parse_options()
		else:
			options = []

		return ast.Cmd(cmd.value, desc.value, options)

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

		return ast.Option(option.value, value)
