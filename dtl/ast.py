from __future__ import annotations
from datetime import datetime
from collections import defaultdict
from functools import reduce
from operator import concat

class File:
    def __init__(self, header_time: Time, segments: list[Segment]) -> None:
        self.header_time = header_time

        self.segments = defaultdict(list)
        for segment in segments:
            self.segments[segment.time].append(segment)

    def find(
        self,
        description: str,
        ongoing: bool | None = None,
        with_parent: bool = False,
    ) -> list[Segment] | list[tuple[Segment, Segment | File]]:
        finds: list = []
        for sub_time in self.segments.keys():
            for segment in self.segments[sub_time]:
                segment.find(description, finds, ongoing=ongoing, with_parent=with_parent, parent_ref=self)

        return finds

    def insert_segment(self, segment: Segment) -> bool:
        if not self.header_time.contains(segment.time):
            return False

        for sub_time in self.segments.keys():
            for seg in self.segments[sub_time]:
                if seg.insert_segment(segment):
                    return True

        self.segments[segment.time].append(segment)
        return True

    def __repr__(self) -> str:
        return 'File(' + str(self.header_time) + ', ' + str(self.segments) + ')'

    def format(self) -> str:
        fstr = ''
        if self.header_time.year is not None:
            fstr += f'for {self.header_time.format(Time({}))}:\n\n'
        fstr += ''.join([segment.format(self.header_time) for segment in reduce(concat, self.segments.values(), [])])
        return fstr

    def validate(self, header_time: Time) -> None:
        self.segments = defaultdict(list, {k: reduce(lambda acc, s: s.merge_into(acc), v, {'tagged': [], 'merged': Segment(k, None, [], [], False)}) for k, v in self.segments.items()})

        def filter_empty(v):
            if len(v.segments) == 0:
                return []
            else:
                return [v]

        self.segments = defaultdict(list, {k: v['tagged'] + filter_empty(v['merged']) for k, v in self.segments.items()})

        self.segments = defaultdict(list, dict(sorted(self.segments.items())))

        for sub_time in self.segments.keys():
            for segment in self.segments[sub_time]:
                segment.validate(header_time)

class Segment:
    def __init__(
        self,
        time: Time,
        description: str,
        segments: list[Segment] = [],
        commands: list[Cmd] = [],
        ongoing: bool = False,
    ) -> None:
        self.time = time
        self.description = description

        self.segments: defaultdict[Time, list[Segment]] = defaultdict(list)
        for segment in segments:
            self.segments[segment.time].append(segment)

        self.commands = commands
        self.ongoing = ongoing

    def find(self, description: str, finds, ongoing: bool | None = None, with_parent: bool = False, parent_ref = None) -> None:
        if description == self.description:
            if ongoing == self.ongoing or ongoing is None:
                if with_parent:
                    finds.append((self, parent_ref))
                else:
                    finds.append(self)

        for sub_time in self.segments.keys():
            for segment in self.segments[sub_time]:
                segment.find(description, finds, ongoing=ongoing, with_parent=with_parent, parent_ref=self)

    def create_entry(self, time: Time, description: str, ongoing: bool = False) -> bool:
        if not self.time.contains(time):
            return False

        for sub_time in self.segments.keys():
            for seg in self.segments[sub_time]:
                if seg.create_entry(time, description, ongoing=ongoing):
                    return True

        segment: Segment = Segment(time, description, [], [], ongoing)

        self.segments[segment.time].append(segment)
        return True

    def insert_segment(self, segment: Segment) -> bool:
        if not self.time.contains(segment.time):
            return False

        for sub_time in self.segments.keys():
            for seg in self.segments[sub_time]:
                if seg.insert_segment(segment):
                    return True

        self.segments[segment.time].append(segment)
        return True

    def __repr__(self):
        return 'Segment(' + str(self.time) + ', ' + (self.description or '') + ', ' + str(self.segments) + ', ' + str(self.commands) + ', ' + str(self.ongoing) + ')'

    def merge_into(self, segments):
        if self.description is None and self.commands == []:
            for time, seg in self.segments.items():
                segments['merged'].segments[time] += seg
        else:
            segments['tagged'].append(self)

        return segments

    def format(self, scope_time: Time, tab: int = 0) -> str:
        fstr = '\t' * tab
        fstr += f'@{self.time.format(scope_time)}'
        if self.ongoing:
            fstr += '...'
        if self.description != None:
            fstr += f' [{self.description}]'
        fstr += '\n'
        fstr += ''.join([cmd.format(tab+1)  for cmd  in self.commands])
        fstr += ''.join([segment.format(self.time, tab+1) for segment in reduce(concat, self.segments.values(), [])])
        return fstr

    def validate(self, scope_time: Time) -> None:
        self.segments = defaultdict(list, {k: reduce(lambda acc, s: s.merge_into(acc), v, {'tagged': [], 'merged': Segment(k, None, [], [], False)}) for k, v in self.segments.items()})

        def filter_empty(v):
            if len(v.segments) == 0:
                return []
            else:
                return [v]

        self.segments = defaultdict(list, {k: v['tagged'] + filter_empty(v['merged']) for k, v in self.segments.items()})

        self.segments = defaultdict(list, dict(sorted(self.segments.items())))

        for sub_time in self.segments:
            for segment in self.segments[sub_time]:
                segment.validate(self.time)

class Time:
    @classmethod
    def validate_time(cls, time) -> None:
        if not all([time[i].index() < time[i+1].index() for i in range(len(time)-1)]):
            print('Error: segment time not in order.')
            print(f'"{", ".join([t.type + " (" + t.value + ")" for t in time])}"')

        types = [t.type for t in time]
        if 'DAY' in types and 'DATE' in types:
            print('Error: segment time contains both weekday and date."')
            print(f'{", ".join([t.type + " (" + t.value + ")" for t in time])}"')

    @classmethod
    def remove_prefix(cls, prefix, time) -> bool:
        if len(prefix) > len(time):
            return False

        if not all(time[i] == prefix[i] for i in range(len(prefix))):
            return False

        return list(time)[len(prefix):]

    @classmethod
    def now(cls) -> Time:
        now = datetime.now()

        year = now.strftime('%Y')
        month = now.strftime('%B')

        date = int(now.strftime('%d'))
        if 4 <= date <= 20 or 24 <= date <= 30:
            date = str(date) + "th"
        else:
            date = str(date) + ["st", "nd", "rd"][date % 10 - 1]

        time = now.strftime('%H:%M')

        return Time({'YEAR': year, 'MONTH': month, 'DATE': date, 'TIME': time})

    @classmethod
    def year_value(cls, value) -> int:
        return int(value)

    @classmethod
    def month_value(cls, value: str) -> int:
        months = [
            'January', 'February', 'March', 'April',
            'May', 'June', 'July', 'August',
            'September', 'October', 'November', 'December'
        ]

        if value in months:
            return months.index(value) + 1
        else:
            return -1

    @classmethod
    def date_value(cls, value) -> int:
        return int(value[:-2])

    @classmethod
    def time_value(cls, value: str) -> int:
        hour, minutes = value.split(':')
        return int(minutes) + 60 * int(hour)

    @classmethod
    def year_str(cls, value: int) -> str:
        return str(value)

    @classmethod
    def month_str(cls, value: int) -> str:
        months = [
            'January', 'February', 'March', 'April',
            'May', 'June', 'July', 'August',
            'September', 'October', 'November', 'December'
        ]

        return months[value-1]

    @classmethod
    def date_str(cls, value: int) -> str:
        if value in [1, 21, 31]:
            return str(value) + 'st'
        elif value in [2, 22]:
            return str(value) + 'nd'
        elif value in [3, 23]:
            return str(value) + 'rd'
        else:
            return str(value) + 'th'

    @classmethod
    def time_str(cls, value) -> str:
        time = int(value)
        minutes = time % 60
        hour = round((time - minutes)/60)

        return str(hour) + ':' + str(minutes).zfill(2)

    def __init__(self, values, parent=None):
        self.year = self.month = self.date = self.time = None
        if parent:
            self.year = parent.year
            self.month = parent.month
            self.date = parent.date
            self.time = parent.time

        self.period = False
        self.end = None

        for time_type, value in values.items():
            match time_type:
                case 'YEAR':
                    self.year = Time.year_value(value)
                case 'MONTH':
                    self.month = Time.month_value(value)
                case 'DATE':
                    self.date = Time.date_value(value)
                case 'TIME':
                    self.time = Time.time_value(value)

    def __hash__(self):
        return hash(str((self.year, self.month, self.date, self.time)))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Time):
            return NotImplemented

        return (self.year, self.month, self.date, self.time) == (other.year, other.month, other.date, other.time)

    def __lt__(self, other: Time) -> bool:
        if self.year is None: return True
        if other.year is None: return False
        if self.year < other.year: return True
        if self.year > other.year: return False

        if self.month is None: return True
        if other.month is None: return False
        if self.month < other.month: return True
        if self.month > other.month: return False

        if self.date is None: return True
        if other.date is None: return False
        if self.date < other.date: return True
        if self.date > other.date: return False

        if self.time is None: return True
        if other.time is None: return False
        if self.time < other.time: return True
        if self.time > other.time: return False

        return False

    def __repr__(self) -> str:
        return 'Time' + str((self.year, self.month, self.date, self.time))

    def interval(self) -> int:
        start: datetime = datetime(self.year, self.month, self.date, self.time//60, self.time%60, 0)
        end: datetime = datetime(self.end.year, self.end.month, self.end.date, self.end.time//60, self.end.time%60, 0)

        return int(end.timestamp() - start.timestamp()) // 60

    def contains(self, other: Time) -> bool:
        time_list = [self.year, self.month, self.date, self.time]
        other_time_list = [other.year, other.month, other.date, other.time]

        for t, o in zip(time_list, other_time_list):
            if o is None: return False
            if t is None: return True

            if t != o: return False

        return False

    def format(self, scope_time: Time) -> str:
        parts = []
        if scope_time.year is None and self.year is not None:
            parts.append(Time.year_str(self.year))
        if scope_time.month is None and self.month is not None:
            parts.append(Time.month_str(self.month))
        if scope_time.date is None and self.date is not None:
            parts.append(Time.date_str(self.date))
        if scope_time.time is None and self.time is not None:
            parts.append(Time.time_str(self.time))

        if self.period and self.end is not None:
            end = self.end.format(scope_time)
            return ' '.join(parts) + '-' + end
        elif self.period:
            return ' '.join(parts) + '...'

        return ' '.join(parts)

class Cmd:
    def __init__(self, command: str, description: str, options: list[Option]) -> None:
        self.command = command
        self.description = description
        self.options = options

    def create_entry(self, time: Time, description: str) -> bool:
        return False

    def insert_segment(self, segment: Segment) -> bool:
        return False

    def __repr__(self) -> str:
        return 'Cmd(' + self.command + ', ' + self.description + ', ' + str(self.options) + ')'

    def format(self, tab: int = 0) -> str:
        fstr = '\t' * tab
        fstr += f'{self.command} [{self.description}]\n'
        fstr += ''.join([option.format(tab+1) for option in self.options])
        return fstr

    def validate(self, time: Time) -> None:
        return None

class Option:
    def __init__(self, name: str, value: str) -> None:
        self.name = name
        self.value = value

    def __repr__(self) -> str:
        return 'Option(' + self.name + ', ' + self.value + ')'

    def format(self, tab: int = 0) -> str:
        fstr = '\t' * tab
        fstr += f'{self.name} {self.value}\n'
        return fstr
