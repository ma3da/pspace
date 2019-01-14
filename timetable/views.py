import datetime

from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, Http404
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Block, Activity, Place
from .forms import BlockForm
from .serializers import ActivitySerializer, BlockSerializer


class IndexView(generic.ListView):
    template_name = 'timetable/index.html'
    context_object_name = 'weekly_blocks'

    def get_queryset(self):
        """Return the last five published questions."""
        return Block.objects.all().order_by("place__time_in", "place__time_out")


def new(request):
    if request.method == "POST":
        form = BlockForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            tomorrow = timezone.now() + datetime.timedelta(days=1)

            dt_in = tomorrow.replace(hour=int(data['hour_in']),
                                     minute=0, second=0, microsecond=0)

            if data['hour_out']:
                dt_out = tomorrow.replace(hour=int(data['hour_out']),
                                          minute=0, second=0, microsecond=0)
            else:
                dt_out = dt_in + datetime.timedelta(hours=1)

            activity = Activity(name=data['activity_name'])
            place = Place(time_in=dt_in, time_out=dt_out)

            activity.save()
            place.save()

            block = Block(activity=activity, place=place)
            block.save()

            return HttpResponseRedirect(reverse("timetable:index"))
    form = BlockForm()
    return render(request, "timetable/new.html", {"form": form})


def delete(request, block_id):
    Block.objects.get(pk=block_id).delete()
    return HttpResponseRedirect(reverse("timetable:index"))


class ActivityList(APIView):
    def get(self, request, format=None):
        activities = Activity.objects.all()
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ActivitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


class ActivityDetail(APIView):
    def get_object(self, pk):
        try:
            return Block.objects.get(pk=pk)
        except Block.DoesNotExist:
            print("mayday")
            return Http404

    def get(self, request, pk, format=None):
        serializer = BlockSerializer(self.get_object(pk))
        return Response(serializer.data)
