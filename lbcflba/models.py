import datetime
import enum
import json

from django.conf import settings
from django.db import models


class Status(enum.Enum):
    waiting = 0
    processed = 1

    @classmethod
    def parse(cls, n: int):
        if getattr(cls, "value_mapping", None) is None:
            Status.value_mapping = {status.value: status.name for status in cls}
        return Status.value_mapping.get(n, None)


class Spender(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.TextField(default="noname")
    groups = models.TextField()

    def rename(self, new_name):
        self.name = new_name


class Group(models.Model):
    members = models.TextField()
    categoryDict = models.TextField(default="{}")
    name = models.TextField(default="unnamed group")

    def add_category(self, category_name):
        categories = to_dict(self.categoryDict)
        if category_name not in categories.values():
            categories[max(categories.keys(), default=1) + 1] = category_name
        self.categoryDict = to_entry_from_dict(categories)

    def delete_category(self, category_id):
        categories = to_dict(self.categoryDict)
        if category_id in categories:
            categories.pop(category_id)
        self.categoryDict = to_entry_from_dict(categories)

    def rename(self, new_name):
        self.name = new_name


class Transaction(models.Model):
    # , related_name="+": create no backward relation
    # see https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.ForeignKey.related_name
    source = models.ForeignKey(Spender, on_delete=models.CASCADE, related_name="+")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="+")
    destination = models.TextField(default="")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    text = models.TextField()
    category = models.PositiveSmallIntegerField(default=0)
    time = models.DateTimeField()  # creation_time, immutable
    date = models.DateField(default=datetime.date.today)  # mutable
    status = models.PositiveSmallIntegerField()


_SEPARATOR = ";"


def to_list(entry):
    return list(map(int, entry.split(_SEPARATOR)))


def to_entry_from_list(list_):
    return _SEPARATOR.join(map(str, list_))


def to_dict(entry):
    return {int(k): v for k, v in json.loads(entry).items()}


def to_entry_from_dict(dict_):
    return json.dumps({str(k): v for k, v in dict_.items()})
