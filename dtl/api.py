from __future__ import annotations

from sortedcontainers import SortedDict

class DTL:
    def __init__(self, header_time: Time, entries: list[Entry]):
        self.entries = SortedDict()

        for entry in entries:
            time = entry.time.copy()

            if time not in self.entries:
                self.entries[time] = []

            self.entries[time].append(entry)

class Entry:
    def __init__(self):
        pass

class Time:
    def __init__(self, year, month, date, time):
        self.year = year
        self.month = month
        self.date = date
        self.time = time

    def copy(self):
        return Time(self.year, self.month, self.date, self.time)

    def __lt__(self, other):
        if self.year != other.year:
            return self.year < other.year
        if self.month != other.month:
            return self.month < other.month
        if self.date != other.date:
            return self.date < other.date
        if self.time != other.time:
            return self.time < other.time

        return False
