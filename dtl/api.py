from __future__ import annotations

class DTL:
    def __init__(self, header_time: Time):
        pass

class Time:
    def __init__(self, year, month, date, time):
        self.year = year
        self.month = month
        self.date = date
        self.time = time

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
