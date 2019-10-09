from django.db import models
from django.conf import settings


class Transaction(models.Model):
    source = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    destination = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    text = models.TextField()
    time = models.DateTimeField()
    status = models.PositiveSmallIntegerField()
