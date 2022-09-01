from dtl.tokenize import Lexer, Token
import dtl.ast as ast

from functools import partial

class Parser:
	def __init__(self, debug=False):
		self.lexer = Lexer(debug=debug)

	def parse(self, src):
		self.lexer.tokenize(src)

		header_time_tokens = {}
		if self.lexer.peak().type == 'FOR':
			self.lexer.pop()

			while self.lexer.peak().type != 'COLON':
				time = self.lexer.assert_token(['YEAR', 'MONTH', 'DATE', 'DAY', 'TIME'])
				header_time_tokens[time.type] = time.value

			self.lexer.assert_token('COLON')
			self.lexer.assert_token('NL')

		header_time = ast.Time(header_time_tokens)

		segments = []
		while self.lexer.peak().type == 'AT':
			segments.append(self.parse_attribute(header_time))

		tree = ast.File(header_time, segments)
		tree.validate(header_time)

		return tree

	def parse_block(self, fn):
		self.lexer.assert_token('OPEN')

		ln = []
		while self.lexer.peak().type != 'END':
			ln.append(fn())

		self.lexer.assert_token('END')

		return ln

	def parse_attributes(self, parent_time):
		return self.parse_block(partial(self.parse_attribute, parent_time))

	def parse_attribute(self, parent_time):
		match self.lexer.peak().type:
			case 'AT':
				return self.parse_time(parent_time)
			case 'CMD':
				return self.parse_cmd()
			case err:
				print(f'Error: expected CMD, AT, found {err}')
				return None

	def parse_time(self, parent_time):
		self.lexer.assert_token('AT')
		time_tokens = [self.lexer.assert_token(['YEAR', 'MONTH', 'DATE', 'DAY', 'TIME'])]
		while self.lexer.peak().type in ['YEAR', 'MONTH', 'DATE', 'DAY', 'TIME']:
			time_tokens.append(self.lexer.pop())

		time = ast.Time({t.type: t.value for t in time_tokens}, parent=parent_time)

		if self.lexer.peak().type == 'PERIOD':
			self.lexer.assert_token('PERIOD')
			period_end_tokens = [self.lexer.assert_token(['YEAR', 'MONTH', 'DATE', 'DAY', 'TIME'])]
			while self.lexer.peak().type in ['YEAR', 'MONTH', 'DATE', 'DAY', 'TIME']:
				period_end_tokens.append(self.lexer.pop())

			period_end = ast.Time({t.type: t.value for t in period_end_tokens}, parent=parent_time)

			time.period = True
			time.end = period_end

		if self.lexer.peak().type == 'ONGOING':
			self.lexer.assert_token('ONGOING')
			ongoing = True
		else:
			ongoing = False

		if self.lexer.peak().type == 'DESC':
			desc = self.lexer.assert_token('DESC').value
		else:
			desc = None

		self.lexer.assert_token('NL')

		attributes = []
		if self.lexer.peak().type == 'OPEN':
			attributes = self.parse_attributes(time)

		segments = [seg for seg in attributes if isinstance(seg, ast.Segment)]
		commands = [cmd for cmd in attributes if isinstance(cmd, ast.Cmd)]

		segment = ast.Segment(time, desc, segments, commands, ongoing)

		return segment

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
			case 'NL':
				value = ''
			case err:
				print(f'Error: expected (DURATION, DESC), found {err}')

		self.lexer.assert_token('NL')

		return ast.Option(option.value, value)
