import datetime

from django.db import models


class Transaction(models.Model):
    source = models.CharField(max_length=256)
    destination = models.CharField(max_length=256)
    time = models.DateTimeField()
    amount = models.FloatField()
