import datetime

from django.contrib.auth import get_user_model
from pspace.models import User
from django.views import generic
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import TransactionSerializer, GroupSerializer
from . import app_name
from .models import Transaction, to_list, Spender, Group, to_entry


def get_main_user(request):
    return get_user_model().objects.get(id=request.user.id)


def _user2json(user):
    return {"spenderId": user.spender.id, "username": user.username}


class IndexView(generic.ListView):
    template_name = f"{app_name}/index.html"
    context_object_name = 'users'

    def get_queryset(self):
        return []


class UserInfo(APIView):
    def get(self, request, format=None):
        try:
            return Response(_user2json(get_main_user(request)))
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TransactionList(APIView):
    def get(self, request, format=None):
        try:
            transactions = Transaction.objects.all()
            serializer = TransactionSerializer(transactions, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, format=None):
        try:
            main_user = get_main_user(request)
            data = {
                "source": Spender.objects.get(user=main_user).id,
                "time": datetime.datetime.now(),
                "status": 0,
            }
            data.update(request.data)
            serializer = TransactionSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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

    def post(self, request, format=None):
        try:
            data = {"members": to_entry(request.data["member_ids"])}
            serializer = GroupSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MemberList(APIView):
    def get(self, request, group_id, format=None):
        try:
            group_member_ids = to_list(Group.objects.get(id=group_id).members)
            users = (Spender.objects.get(id=user_id).user for user_id in group_member_ids)
            return Response(list(map(_user2json, users)))
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
