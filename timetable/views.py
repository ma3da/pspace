import datetime

from django.http import HttpResponseRedirect, Http404, HttpResponseServerError
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import BlockForm
from .models import Block
from .serializers import BlockSerializer


class IndexView(generic.ListView):
    template_name = 'timetable/index.html'
    context_object_name = 'weekly_blocks'

    def get_queryset(self):
        return Block.objects.all().order_by("time_start", "time_end")


def new(request):
    if request.method == "POST":
        form = BlockForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            text = data["text"]
            try:
                block = Block.create_from_text(text)
                block.save()
            except Exception as e:
                return HttpResponseServerError(content=f"an error occured: {e}")

            return HttpResponseRedirect(reverse("timetable:index"))
    form = BlockForm()
    return render(request, "timetable/new.html", {"form": form})


def delete(request, pk):
    Block.objects.get(pk=pk).delete()
    return HttpResponseRedirect(reverse("timetable:index"))


class BlockList(APIView):
    def get(self, request, format=None):
        blocks = Block.objects.all()
        serializer = BlockSerializer(blocks, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = BlockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


class BlockDetail(APIView):
    def get_object(self, pk):
        try:
            return Block.objects.get(pk=pk)
        except Block.DoesNotExist:
            return Http404

    def get(self, request, pk, format=None):
        serializer = BlockSerializer(self.get_object(pk))
        return Response(serializer.data)


class BlockListByDate(APIView):
    def get(self, request, format=None):
        n_weekdays = 7
        now = datetime.datetime.now().date()
        result = []
        for i in range(n_weekdays):
            dt0 = now + datetime.timedelta(days=i)
            dt1 = dt0 + datetime.timedelta(days=1)
            blocks = Block.objects.filter(time_start__gte=dt0).filter(time_start__lt=dt1)
            serializer = BlockSerializer(blocks, many=True)
            result.append({"date": dt0.isoformat(), "blocks": serializer.data})
        return Response(result)


class BlockNew(APIView):
    def post(self, request, format=None):
        text = request.data["text"]
        try:
            print("text:", request.data)
            block = Block.create_from_text(text)
            block.save()
            print("saved blooooock")
            return Response()
        except Exception as e:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
