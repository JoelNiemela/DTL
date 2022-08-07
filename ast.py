class Segment:
	def __init__(self, name, timelist):
		self.name = name
		self.timelist = timelist

	def __repr__(self):
		return 'Segment(' + self.name + ', ' + str(self.timelist) + ')'

class Time:
	def __init__(self, time, description, attributes):
		self.time = time
		self.description = description
		self.attributes = attributes

	def __repr__(self):
		return 'Time(' + self.time + ', ' + self.description + ', ' + str(self.attributes) + ')'

class Cmd:
	def __init__(self, command, description, options):
		self.command = command
		self.description = description
		self.options = options

	def __repr__(self):
		return 'Cmd(' + self.command + ', ' + self.description + ', ' + str(self.options) + ')'

class Option:
	def __init__(self, name, value):
		self.name = name
		self.value = value

	def __repr__(self):
		return 'Option(' + self.name + ', ' + self.value + ')'
