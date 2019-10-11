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
        try:
            transactions = Transaction.objects.all()
            serializer = TransactionSerializer(transactions, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TransactionNew(APIView):
    def post(self, request, format=None):
        try:
            src_id = request.user.id
            dest_id = request.data["destination"]
            amount = request.data["amount"]
            text = request.data["text"]
            print(request.data)
            transaction = Transaction(source=get_user_model().objects.get(id=src_id),
                                      destination=get_user_model().objects.get(id=dest_id),
                                      amount=amount, text=text, time=datetime.datetime.now(), status=0)
            transaction.save()
            return Response()
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TransactionDelete(APIView):
    def post(self, request, format=None):
        try:
            pk = request.data["pk"]

            Transaction.objects.get(pk=pk).delete()
            return Response()
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ContactList(APIView):
    def get(self, request, format=None):
        try:
            users = get_user_model().objects.exclude(id=request.user.id)
            return Response([{"id": user.id, "username": user.username} for user in users])
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
