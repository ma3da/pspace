from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views, app_name

app_name = app_name  # registering namespace ?

urlpatterns = [
    path('', login_required(views.IndexView.as_view()), name='index'),
    path('options', login_required(views.OptionsView.as_view()), name='options'),
    path('api/all', login_required(views.TransactionList.as_view()), name='all'),
    path('api/userinfo', login_required(views.UserInfo.as_view()), name='userinfo'),
    path('api/new', login_required(views.TransactionList.as_view()), name='new'),
    path('api/delete', login_required(views.TransactionDelete.as_view()), name='delete'),
    path('api/contacts/all', login_required(views.ContactList.as_view()), name='contact_list'),
    path('api/groups', login_required(views.GroupList.as_view()), name='groups'),
    path('api/group/category/new', login_required(views.GroupCategory.as_view()), name='group_category'),
    path('api/group/category/delete', login_required(views.GroupCategoryDelete.as_view()), name='group_category_del'),
    path('api/members/<int:group_id>', login_required(views.MemberList.as_view()), name='members'),
]
