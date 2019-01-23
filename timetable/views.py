import datetime

from django.http import Http404
from django.views import generic
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Block
from .serializers import BlockSerializer


class IndexView(generic.ListView):
    template_name = 'timetable/index.html'
    context_object_name = 'weekly_blocks'

    def get_queryset(self):
        return Block.objects.all().order_by("time_start", "time_end")


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
            blocks = Block.objects.filter(time_start__gte=dt0).filter(time_start__lt=dt1).order_by('time_start')
            serializer = BlockSerializer(blocks, many=True)

            block_json_list = serializer.data
            block_json_w_key_list = list(map(dict,
                                             map(lambda id_items: id_items[1] + [('key', id_items[0])],
                                                 enumerate(map(list, map(dict.items, block_json_list))))))

            result.append({"date": dt0.isoformat(), "blocks": block_json_w_key_list})
        return Response(result)


class BlockNew(APIView):
    def post(self, request, format=None):
        try:
            text = request.data["text"]
            block = Block.create_from_text(text)
            block.save()
            return Response()
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BlockDelete(APIView):
    def post(self, request, format=None):
        try:
            pk = request.data["pk"]
            block = Block.objects.get(pk=pk)
            block.delete()
            return Response()
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
