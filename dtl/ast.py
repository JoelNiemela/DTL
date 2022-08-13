from datetime import datetime

class File:
	def __init__(self, header_time, segments):
		self.header_time = header_time
		self.segments = segments

	def find(self, description, ongoing=None, with_parent=False):
		finds = []
		for segment in self.segments:
			segment.find(description, finds, ongoing=ongoing, with_parent=with_parent, parent_ref=self)

		return finds

	def create_entry(self, time, description, ongoing=False):
		sub_time = Time.remove_prefix(self.header_time, time)

		if sub_time == False or sub_time == []:
			return False

		for segment in self.segments:
			if segment.create_entry(sub_time, description, ongoing=ongoing):
				return True

		self.segments.append(Segment(sub_time, description, [], [], ongoing))
		return True

	def insert_segment(self, segment):
		time = Time.remove_prefix(self.header_time, segment.time)

		if time == False or time == []:
			return False

		segment.time = time

		for seg in self.segments:
			if seg.insert_segment(segment):
				return True

		self.segments.append(segment)
		return True

	def __repr__(self):
		return 'File(' + str(self.header_time) + ', ' + str(self.segments) + ')'

	def format(self):
		str = ''
		if len(self.header_time) > 0:
			str += f'for {" ".join([t.format() for t in self.header_time])}:\n\n'
		str += ''.join([segment.format() for segment in self.segments])
		return str

	def validate(self, header_time):
		for segment in self.segments:
			segment.validate(header_time)

class Segment:
	def __init__(self, time, description, segments, attributes, ongoing):
		self.time = time
		self.description = description
		self.segments = segments
		self.attributes = attributes
		self.ongoing = ongoing

	def find(self, description, finds, ongoing=None, with_parent=False, parent_ref=None):
		if description == self.description:
			if ongoing == self.ongoing or ongoing == None:
				if with_parent:
					finds.append((self, parent_ref))
				else:
					finds.append(self)

		for segment in self.segments:
			segment.find(description, finds, ongoing=ongoing, with_parent=with_parent, parent_ref=self)

	def create_entry(self, time, description, ongoing=False):
		sub_time = Time.remove_prefix(self.time, time)

		if sub_time == False or sub_time == []:
			return False

		for segment in self.segments:
			if segment.create_entry(sub_time, description, ongoing=ongoing):
				return True

		self.segments.append(Segment(sub_time, description, [], [], ongoing))
		return True

	def insert_segment(self, segment):
		time = Time.remove_prefix(self.time, segment.time)

		if time == False or time == []:
			return False

		segment.time = time

		for seg in self.segments:
			if seg.insert_segment(segment):
				return True

		self.segments.append(segment)
		return True

	def __repr__(self):
		return 'Segment(' + str(self.time) + ', ' + (self.description or '') + ', ' + str(self.segments) + ', ' + str(self.attributes) + ', ' + str(self.ongoing) + ')'

	def format(self, tab=0, / , full_time=False):
		str = '\t' * tab
		if full_time:
			str += f'@{" ".join([t.format() for t in self.full_time])}'
		else:
			str += f'@{" ".join([t.format() for t in self.time])}'
		if self.ongoing:
			str += '...'
		if self.description != None:
			str += f' [{self.description}]'
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

	@classmethod
	def remove_prefix(cls, prefix, time):
		if len(prefix) > len(time):
			return False

		if not all(time[i] == prefix[i] for i in range(len(prefix))):
			return False

		return list(time)[len(prefix):]

	@classmethod
	def now(cls):
		now = datetime.now()

		year = now.strftime('%Y')
		month = now.strftime('%B')

		date = int(now.strftime('%d'))
		if 4 <= date <= 20 or 24 <= date <= 30:
			date = str(date) + "th"
		else:
			date = str(date) + ["st", "nd", "rd"][date % 10 - 1]

		time = now.strftime('%H:%M')

		return [
			Time('YEAR', year),
			Time('MONTH', month),
			Time('DATE', date),
			Time('TIME', time)
		]

	@classmethod
	def timespan(cls, start, end):
		for i in range(len(start)):
			if start[i].type != end[i].type:
				end.insert(i, start[i])
			else:
				break

		if start == end:
			return start

		prefix_len = next((i for i, v in enumerate(zip(start, end)) if v[0] != v[1]), min(len(start), len(end)))

		prefix = start[0:prefix_len]
		del start[0:prefix_len]
		del   end[0:prefix_len]

		print(prefix, start, end)
		return prefix + [Time('PERIOD', (start, end))]

	def __init__(self, time_type, value):
		self.type = time_type
		self.value = value

	def __eq__(self, other):
		return self.type == other.type and self.value == other.value

	def index(self):
		if self.type == 'PERIOD':
			return self.value[0][0].index()

		time_order = ['YEAR', 'MONTH', 'DATE', 'DAY', 'TIME']
		index = time_order.index(self.type)
		return index

	def __repr__(self):
		return 'Time(' + self.type + ', ' + str(self.value) + ')'

	def format(self):
		if self.type == 'PERIOD':
			return ' '.join([t.format() for t in self.value[0]]) + '-' + ' '.join([t.format() for t in self.value[1]])
		else:
			return self.value

class Cmd:
	def __init__(self, command, description, options):
		self.command = command
		self.description = description
		self.options = options

	def create_entry(self, time, description):
		return False

	def insert_segment(self, segment):
		return False

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
