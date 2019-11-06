from rest_framework import serializers

from .models import Transaction, Group


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('id', 'source', 'destination', 'amount', 'text', 'time', 'status')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("id", "members")
