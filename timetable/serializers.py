from rest_framework import serializers

from .models import Block


class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ('id', 'activity', 'time_start', 'time_end')
