import datetime

from django.contrib.auth import get_user_model
from pspace.models import User
from django.views import generic
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import TransactionSerializer
from . import app_name
from .models import Transaction, to_list, Spender, Group


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
            other_id = request.data["other"]
            direction = request.data["direction"]
            if direction == "from_user":
                src_id, dest_id = request.user.id, other_id
            elif direction == "to_user":
                src_id, dest_id = other_id, request.user.id
            else:
                raise ValueError(f"Direction should be either 'from_user' or 'to_user', not: {direction}")
            amount = request.data["amount"]
            text = request.data["text"]

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


def _user2json(user):
    return {"id": user.id, "username": user.username}


def get_main_user(request):
    return get_user_model().objects.get(id=request.user.id)


class ContactList(APIView):
    def get(self, request, format=None):
        try:
            main_user = get_main_user(request)
            users = get_user_model().objects.exclude(id=request.user.id)
            return Response({"me": _user2json(main_user),
                             "contacts": [_user2json(user) for user in users]})
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GroupList(APIView):
    def get(self, request, format=None):
        try:
            spender = get_main_user(request).spender
            groups = to_list(spender.groups)
            return Response(groups)
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberList(APIView):
    def get(self, request, format=None):
        try:
            group_id = request.data["group"]
            members = to_list(Group.objects.get(id=group_id).members)
            return members
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
