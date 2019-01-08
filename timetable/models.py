from django.db import models

import functools


class Activity(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name


@functools.total_ordering
class Place(models.Model):
    time_in = models.DateTimeField()
    time_out = models.DateTimeField()

    def __str__(self):
        date_format = "%d/%m"
        time_format = "%Hh%M"
        first_format = f"{date_format} {time_format}"

        second_format = time_format if self.time_in.date() == self.time_out.date() else first_format

        return f"{self.time_in: {first_format}} -> {self.time_out: {second_format}}"

    def __lt__(self, other):
        return (isinstance(other, Place)
                and self.time_in < other.time_in)

    def __eq__(self, other):
        return (isinstance(other, Place)
                and (self.time_in, self.time_out) == (other.time_in, other.time_out))


@functools.total_ordering
class Block(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    place = models.ForeignKey(Place, on_delete=models.CASCADE)

    @property
    def _tuple(self):
        return self.place, self.activity.name

    def __repr__(self):
        return f"< {self.activity}: {self.place} >"

    def __lt__(self, other):
        return (isinstance(other, Block)
                and self._tuple < other._tuple)

    def __eq__(self, other):
        return (isinstance(other, Block)
                and self._tuple == other._tuple)
