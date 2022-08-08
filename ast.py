class File:
	def __init__(self, segments):
		self.segments = segments

	def __repr__(self):
		return 'File(' + str(self.segments) + ')'

	def format(self):
		return ''.join([segment.format() for segment in self.segments])

	def validate(self, header_time):
		for segment in self.segments:
			segment.validate(header_time)

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

	def validate(self, scope_time):
		time = scope_time + self.time
		Time.validate_time(time)

		self.full_time = time

		for segment in self.segments:
			segment.validate(time)

class Time:

	@classmethod
	def validate_time(cls, time):
		if not all([time[i].index() < time[i+1].index() for i in range(len(time)-1)]):
			print('Error: segment time not in order.')
			print(f'"{", ".join([t.type + " (" + t.value + ")" for t in time])}"')

		types = [t.type for t in time]
		if 'DAY' in types and 'DATE' in types:
			print('Error: segment time contains both weekday and date."')
			print(f'{", ".join([t.type + " (" + t.value + ")" for t in time])}"')

	def __init__(self, time_type, value):
		self.type = time_type
		self.value = value

	def index(self):
		time_order = ['YEAR', 'MONTH', 'DATE', 'DAY', 'TIME']
		index = time_order.index(self.type)
		return index

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
		str += ''.join([option.format(tab+1) for option in self.options])
		return str

	def validate(self, time):
		return None

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
