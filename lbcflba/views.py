import datetime

from django.contrib.auth import get_user_model
from pspace.models import User
from django.views import generic
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import TransactionSerializer, GroupSerializer
from . import app_name
from .models import Transaction, to_list, Spender, Group, to_entry_from_list, to_dict, to_entry_from_dict


def get_main_user(request):
    return get_user_model().objects.get(id=request.user.id)


def _user2json(user):
    return {"spenderId": user.spender.id, "username": user.username}


def _spender2json(spender):
    return {"spenderId": spender.id, "username": spender.user.username}


def allowed_groups(user):
    return to_list(user.spender.groups)


class IndexView(generic.ListView):
    template_name = f"{app_name}/index.html"
    context_object_name = 'users'

    def get_queryset(self):
        return []


class OptionsView(generic.ListView):
    template_name = f"{app_name}/options.html"
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
            data = {
                "time": datetime.datetime.now(),
                "status": 0,
            }
            data.update(request.data)
            serializer = TransactionSerializer(data=data)
            if serializer.is_valid():
                # todo check source in destination
                serializer.save()
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# todo: restrict access on pk
class TransactionDelete(APIView):
    def post(self, request, format=None):
        try:
            pk = request.data["pk"]

            Transaction.objects.get(pk=pk).delete()
            return Response()
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# todo: restrict access on pk
class TransactionUpdate(APIView):
    def post(self, request, format=None):
        try:
            pk = request.data["pk"]
            args = {"text": str(request.data["text"]),
                    "category": int(request.data["categoryId"])}
            try:
                args["date"] = datetime.datetime.strptime(str(request.data["date"]), "%Y-%m-%d").date()
            except ValueError or AttributeError as e:
                pass

            Transaction.objects.filter(pk=pk).update(**args)
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
        """
        :return: json [{"members":[Spender_json], "id":int}]
        """
        try:
            spender = get_main_user(request).spender
            groups = Group.objects.filter(pk__in=to_list(spender.groups))
            serializer = GroupSerializer(groups, many=True)
            member_ids = set()
            # members (Spender) inflation + group name
            for group in serializer.data:
                member_ids.update(to_list(group["members"]))
            spenders = Spender.objects.filter(pk__in=member_ids)
            spender_by_id = {member.id: member for member in spenders}
            for group in serializer.data:
                group["members"] = [_spender2json(spender_by_id[member_id]) for member_id in to_list(group["members"])]
                group["name"] = ", ".join(spender["username"] for spender in group["members"])
            # categoryDict inflation
            for group in serializer.data:
                group["categoryDict"] = to_dict(group["categoryDict"])
                group["categoryDict"].update({0: "uncategorized"})
            return Response(serializer.data)
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, format=None):
        try:
            data = {
                "members": to_entry_from_list(request.data["member_ids"]),
                "categoryDict": to_entry_from_dict(request.data["categoryDict"]),
            }
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


class GroupCategory(APIView):
    def post(self, request, format=None):
        try:
            group_id = int(request.data["groupId"])
            if group_id not in allowed_groups(get_main_user(request)):
                raise PermissionError("Nope")
            group = Group.objects.get(id=group_id)
            group.add_category(category_name=request.data["categoryName"])
            group.save()
            return Response(GroupSerializer(group).data, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GroupCategoryDelete(APIView):
    def post(self, request, format=None):
        try:
            group_id = int(request.data["groupId"])
            category_id = int(request.data["categoryId"])
            if group_id not in allowed_groups(get_main_user(request)):
                raise PermissionError("Nope")
            group = Group.objects.get(id=group_id)
            group.delete_category(category_id=category_id)
            group.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(data=str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
