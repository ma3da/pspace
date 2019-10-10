from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views, app_name

app_name = app_name  # registering namespace ?

urlpatterns = [
    path('', login_required(views.IndexView.as_view()), name='index'),
    path('api/all', login_required(views.TransactionList.as_view()), name='all'),
    path('api/new', login_required(views.TransactionNew.as_view()), name='new'),
]
