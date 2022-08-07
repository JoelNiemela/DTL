from tokenize import Lexer, Token

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
