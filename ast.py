class File:
	def __init__(self, segments):
		self.segments = segments

	def __repr__(self):
		return 'File(' + str(self.segments) + ')'

	def format(self):
		return ''.join([segment.format() for segment in self.segments])

class Segment:
	def __init__(self, time, description, segments, attributes):
		self.time = time
		self.description = description
		self.segments = segments
		self.attributes = attributes

	def __repr__(self):
		return 'Segment(' + str(self.time) + ', ' + (self.description or '') + ', ' + str(self.segments) + ', ' + str(self.attributes) + ')'

	def format(self, tab=0):
		str = '\t' * tab
		str += f'@{" ".join([t.format() for t in self.time])} '
		if self.description != None:
			str += f'[{self.description}]'
		str += '\n'
		str += ''.join([attr.format(tab+1) for attr in self.attributes])
		str += ''.join([time.format(tab+1) for time in self.segments])
		return str

class Time:
	def __init__(self, time_type, value):
		self.type = time_type
		self.value = value

	def __repr__(self):
		return 'Time(' + self.type + ', ' + self.value + ')'

	def format(self):
		return self.value


class Cmd:
	def __init__(self, command, description, options):
		self.command = command
		self.description = description
		self.options = options

	def __repr__(self):
		return 'Cmd(' + self.command + ', ' + self.description + ', ' + str(self.options) + ')'

	def format(self, tab=0):
		str = '\t' * tab
		str += f'{self.command} [{self.description}]\n'
		str += ''.join([option.format() for option in self.options])
		return str

class Option:
	def __init__(self, name, value):
		self.name = name
		self.value = value

	def __repr__(self):
		return 'Option(' + self.name + ', ' + self.value + ')'

	def format(self, tab=0):
		str = '\t' * tab
		str += f'{self.name} {self.value}\n'
		return str
