class File:
	def __init__(self, segments):
		self.segments = segments

	def __repr__(self):
		return 'File(' + str(self.segments) + ')'

	def format(self):
		return ''.join([segment.format() for segment in self.segments])

class Segment:
	def __init__(self, name, timelist):
		self.name = name
		self.timelist = timelist

	def __repr__(self):
		return 'Segment(' + self.name + ', ' + str(self.timelist) + ')'

	def format(self):
		str = f'@{self.name}\n'
		return str + ''.join([time.format() for time in self.timelist])

class Time:
	def __init__(self, time, description, attributes):
		self.time = time
		self.description = description
		self.attributes = attributes

	def __repr__(self):
		return 'Time(' + self.time + ', ' + self.description + ', ' + str(self.attributes) + ')'

	def format(self):
		str = f'\t@{self.time} [{self.description}]\n'
		return str + ''.join([attr.format() for attr in self.attributes])

class Cmd:
	def __init__(self, command, description, options):
		self.command = command
		self.description = description
		self.options = options

	def __repr__(self):
		return 'Cmd(' + self.command + ', ' + self.description + ', ' + str(self.options) + ')'

	def format(self):
		str = f'\t\t{self.command} [{self.description}]\n'
		return str + ''.join([option.format() for option in self.options])

class Option:
	def __init__(self, name, value):
		self.name = name
		self.value = value

	def __repr__(self):
		return 'Option(' + self.name + ', ' + self.value + ')'

	def format(self):
		return f'\t\t\t{self.name} {self.value}\n'
