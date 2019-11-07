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
    groups = models.TextField()


class Group(models.Model):
    members = models.TextField()
    categoryDict = models.TextField(default="{}")

    def add_category(self, category_name):
        categories = to_dict(self.categoryDict)
        if category_name not in categories.values():
            categories[int(max(categories.keys(), default=1)) + 1] = category_name
        self.categoryDict = to_entry_from_dict(categories)


class Transaction(models.Model):
    # , related_name="+": create no backward relation
    # see https://docs.djangoproject.com/en/2.2/ref/models/fields/#django.db.models.ForeignKey.related_name
    source = models.ForeignKey(Spender, on_delete=models.CASCADE, related_name="+")
    destination = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="+")
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    text = models.TextField()
    category = models.PositiveSmallIntegerField(default=0)
    time = models.DateTimeField()
    status = models.PositiveSmallIntegerField()


_SEPARATOR = ";"


def to_list(entry):
    return list(map(int, entry.split(_SEPARATOR)))


def to_entry_from_list(list_):
    return _SEPARATOR.join(map(str, list_))


def to_dict(entry):
    return json.loads(entry)


def to_entry_from_dict(dict_):
    return json.dumps(dict_)
