from rest_framework import serializers

from .models import Transaction, Group


# apparently DecimalField (like amount) need to be deserialized as string, and are
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = "__all__"
        extra_kwargs = {"text": {"allow_blank": True}}


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"
