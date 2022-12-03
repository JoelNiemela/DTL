from __future__ import annotations

from sortedcontainers import SortedDict

class DTL:
    def __init__(self, header_time: Time, entries: list[Entry]):
        self._header_time = header_time

        self._entries = SortedDict()
        for entry in entries:
            time = entry.time.copy()

            if time not in self._entries:
                self._entries[time] = []

            self._entries[time].append(entry)

class Entry:
    def __init__(self, time: Time, description: str, entries: list[Entry]):
        self._time = time
        self._description = description

        self._entries = SortedDict()
        for entry in entries:
            time = entry.time.copy()
            if time not in self._entries:
                self._entries[time] = []

            self._entries[time].append(entry)

class Time:
    def __init__(self, year, month, date, time):
        self._year = year
        self._month = month
        self._date = date
        self._time = time

    def copy(self):
        return Time(self._year, self._month, self._date, self._time)

    def __lt__(self, other):
        if self._year != other.year:
            return self._year < other.year
        if self._month != other.month:
            return self._month < other.month
        if self._date != other.date:
            return self._date < other.date
        if self._time != other.time:
            return self._time < other.time

        return False
