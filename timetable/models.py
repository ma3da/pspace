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
        if not lines:
            raise ValueError("parsing an empty text")
        if len(lines) == 1:
            line = lines[0]
            return cls(activity=line, time_start=now, time_end=now)
        else:  # >= 2 lines
            time_line = lines[0]
            activity = "\n".join(lines[1:])
            try:
                time_start, time_end = parse_time(time_line, now)
            except:
                raise ValueError(f"Could not parse time: {time_line}")
            return cls(activity=activity, time_start=time_start, time_end=time_end)


def parse_time(line: str, now: datetime.datetime):
    format = "%Y-%m-%d %H%M"
    time_start = datetime.datetime.strptime(line[:15], format)
    time_end = datetime.datetime.strptime(line[:11] + line[16:20], format)
    return time_start, time_end
