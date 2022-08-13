from datetime import datetime
from collections import defaultdict
from functools import reduce
from operator import concat

class File:
	def __init__(self, header_time, segments):
		self.header_time = header_time

		self.segments = defaultdict(list)
		for segment in segments:
			self.segments[segment.time].append(segment)

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

		scope_time = sub_time[:-1]
		seg_time = sub_time[-1]

		segment = Segment(seg_time, description, [], [], ongoing)

		for t in reversed(scope_time):
			segment = Segment(t, None, [segment], [], False)

		self.segments[segment.time].append(segment)
		return True

	def insert_segment(self, segment):
		time = Time.remove_prefix(self.header_time, segment.time)

		if time == False or time == []:
			return False

		segment.time = time

		for seg in self.segments:
			if seg.insert_segment(segment):
				return True

		self.segments[segment.time].append(segment)
		return True

	def __repr__(self):
		return 'File(' + str(self.header_time) + ', ' + str(self.segments) + ')'

	def format(self):
		str = ''
		if len(self.header_time) > 0:
			str += f'for {" ".join([t.format() for t in self.header_time])}:\n\n'
		str += ''.join([segment.format() for segment in reduce(concat, self.segments.values(), [])])
		return str

	def validate(self, header_time):
		self.segments = {k: reduce(lambda acc, s: s.merge_into(acc), v, {'tagged': [], 'merged': Segment(k, None, [], [], False)}) for k, v in self.segments.items()}

		def filter_empty(v):
			if len(v.segments) == 0:
				return []
			else:
				return [v]

		self.segments = {k: v['tagged'] + filter_empty(v['merged']) for k, v in self.segments.items()}

		for sub_time in self.segments.keys():
			for segment in self.segments[sub_time]:
				segment.validate(header_time)

class Segment:
	def __init__(self, time, description, segments, commands, ongoing):
		self.time = time
		self.description = description

		self.segments = defaultdict(list)
		for segment in segments:
			self.segments[segment.time].append(segment)

		self.commands = commands
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

		for segment in self.segments.items():
			if segment.create_entry(sub_time, description, ongoing=ongoing):
				return True

		scope_time = sub_time[:-1]
		seg_time = sub_time[-1]

		segment = Segment(seg_time, description, [], [], ongoing)

		for t in reversed(scope_time):
			segment = Segment(t, None, [segment], [], False)

		self.segments[segment.time].append(segment)
		return True

	def insert_segment(self, segment):
		time = Time.remove_prefix(self.time, segment.time)

		if time == False or time == []:
			return False

		segment.time = time

		for seg in self.segments:
			if seg.insert_segment(segment):
				return True

		self.segments[segment.time].append(segment)
		return True

	def __repr__(self):
		return 'Segment(' + str(self.time) + ', ' + (self.description or '') + ', ' + str(self.segments) + ', ' + str(self.commands) + ', ' + str(self.ongoing) + ')'

	def merge_into(self, segments):
		if self.description == None and self.commands == []:
			for time, seg in self.segments.items():
				segments['merged'].segments[time] += seg
		else:
			segments['tagged'].append(self)

		return segments

	def format(self, tab=0, / , full_time=False):
		str = '\t' * tab
		if full_time:
			str += f'@{" ".join([t.format() for t in self.full_time])}'
		else:
			str += f'@{self.time.format()}'
		if self.ongoing:
			str += '...'
		if self.description != None:
			str += f' [{self.description}]'
		str += '\n'
		str += ''.join([cmd.format(tab+1)  for cmd  in self.commands])
		str += ''.join([time.format(tab+1) for time in reduce(concat, self.segments.values(), [])])
		return str

	def validate(self, scope_time):
		time = scope_time + [self.time]
		Time.validate_time(time)

		self.full_time = time

		self.segments = {k: reduce(lambda acc, s: s.merge_into(acc), v, {'tagged': [], 'merged': Segment(k, None, [], [], False)}) for k, v in self.segments.items()}

		def filter_empty(v):
			if len(v.segments) == 0:
				return []
			else:
				return [v]

		self.segments = {k: v['tagged'] + filter_empty(v['merged']) for k, v in self.segments.items()}

		self.segments = dict(sorted(self.segments.items()))

		for sub_time in self.segments:
			for segment in self.segments[sub_time]:
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

		return prefix + [Time('PERIOD', (start, end))]

	@classmethod
	def month_index(cls, month):
		month_order = [
			'January', 'February', 'March', 'April',
			'May', 'June', 'July', 'August',
			'September', 'October', 'November', 'December'
		]
		index = month_order.index(month)
		return index

	@classmethod
	def date_value(cls, date):
		return int(date[:-2])

	@classmethod
	def weekday_index(cls, weekday):
		weekday_order = [
			'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
		]
		index = weekday_order.index(weekday)
		return index

	@classmethod
	def time_minutes(cls, time):
		if len(time) == 5:
			assert time[2] == ':'
			return int(time[:2]) * 60 + int(time[-2:])
		elif len(time) == 4:
			assert time[1] == ':'
			return int(time[:1]) * 60 + int(time[-2:])

		assert False

	def __init__(self, time_type, value):
		self.type = time_type
		self.value = value

	def __hash__(self):
		return hash(self.type + str(self.value))

	def __eq__(self, other):
		return self.type == other.type and self.value == other.value

	def __lt__(self, other):
		if self.type != other.type:
			if self.type == 'PERIOD':
				return self.value[0][0] < other
			elif other.type == 'PERIOD':
				return self < other.value[0][0]
			else:
				return self.index() > other.index()
		else:
			match self.type:
				case 'YEAR':
					if int(self.value) != int(other.value):
						return int(self.value) < int(other.value)
				case 'MONTH':
					if Time.month_index(self.value) != Time.month_index(other.value):
						return Time.month_index(self.value) < Time.month_index(other.value)
				case 'DATE':
					if Time.date_value(self.value) != Time.date_value(other.value):
						return Time.date_value(self.value) < Time.date_value(other.value)
				case 'DAY':
					if Time.weekday_index(self.value) != Time.weekday_index(other.value):
						return Time.weekday_index(self.value) < Time.weekday_index(other.value)
				case 'TIME':
					if Time.time_minutes(self.value) != Time.time_minutes(other.value):
						return Time.time_minutes(self.value) < Time.time_minutes(other.value)
				case 'PERIOD':
					for sv, ov in zip(self.value[0], other.value[0]):
						if sv < ov:
							return True
						if sv > ov:
							return False
				case err:
					print(f'Error: Time.__lt__ not implemented for Time with type of "{err}"')
					return False

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
