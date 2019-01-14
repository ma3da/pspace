from rest_framework import serializers
from .models import Activity, Place, Block


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ('id', 'name')


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ('time_in', 'time_out')


class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ('activity', 'place')
        depth = 1
