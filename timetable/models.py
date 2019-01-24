import datetime
import functools

from django.db import models


@functools.total_ordering
class Block(models.Model):
    activity = models.CharField(max_length=256, default="")
    time_start = models.DateTimeField(default=datetime.date(2000, 1, 1))
    time_end = models.DateTimeField(default=datetime.date(2000, 1, 1))

    @property
    def _tuple(self):
        return self.time_start, self.time_end, self.activity.name

    def time_str(self):
        date_format = "%d/%m"
        time_format = "%Hh%M"
        first_format = f"{date_format} {time_format}"

        second_format = time_format if self.time_start.date() == self.time_start.date() else first_format

        return f"{self.time_start: {first_format}} -> {self.time_end: {second_format}}"

    def __repr__(self):
        return f"< {self.activity}: {self.time_str()} >"

    def __lt__(self, other):
        return (isinstance(other, Block)
                and self._tuple < other._tuple)

    def __eq__(self, other):
        return (isinstance(other, Block)
                and self._tuple == other._tuple)

    @classmethod
    def create_from_text(cls, text: str):
        now = datetime.datetime.now()
        lines = text.split("\n")
        if len(lines) < 2:
            raise ValueError("parsing text with less than 2 lines: time + activity needed")
        else:
            time_line = lines[0]
            activity = "\n".join(lines[1:])
            try:
                time_start, time_end = parse_time(time_line, now)
            except:
                raise ValueError(f"Could not parse time: {time_line}")
            return cls(activity=activity, time_start=time_start, time_end=time_end)


def clean(line: str):
    return line.strip().replace(',', '')


def has_time_format(s: str):
    return len(s) == 4 and s.isnumeric() and int(s[:2]) < 24 and int(s[2:]) < 60


def parse_time(line: str, now: datetime.datetime):
    line = clean(line)
    format = "%Y-%m-%d %H%M"
    date_str = line[:10]

    starttime_str = line[11:15] if has_time_format(line[11:15]) else None

    endtime_str = line[16:20] if has_time_format(line[16:20]) else None

    if starttime_str:
        if not endtime_str:
            endtime_str = starttime_str
    else:
        starttime_str = "0000"
        endtime_str = "2359"

    time_end = datetime.datetime.strptime(f"{date_str} {endtime_str}", format)
    time_start = datetime.datetime.strptime(f"{date_str} {starttime_str}", format)

    return time_start, time_end
