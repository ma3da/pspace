import datetime

from django.contrib.auth import get_user_model
from pspace.models import User
from django.views import generic
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import TransactionSerializer
from . import app_name
from .models import Transaction


class IndexView(generic.ListView):
    template_name = f"{app_name}/index.html"
    context_object_name = 'users'

    def get_queryset(self):
        return User.objects.all()


class TransactionList(APIView):
    def get(self, request, format=None):
        blocks = Transaction.objects.all()
        serializer = TransactionSerializer(blocks, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)


class TransactionNew(APIView):
    def post(self, request, format=None):
        try:
            src_id = request.user.id
            dest_id = request.data["destination"]
            amount = request.data["amount"]
            text = request.data["text"]

            transaction = Transaction(source=get_user_model().objects.get(id=src_id),
                                      destination=get_user_model().objects.get(id=dest_id),
                                      amount=amount, text=text, time=datetime.datetime.now(), status=0)
            transaction.save()
            return Response()
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
