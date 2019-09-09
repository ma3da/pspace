from django.contrib.auth.decorators import login_required
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'definition'

urlpatterns = [
    path('', views.index, name='index'),
]

# urlpatterns = format_suffix_patterns(urlpatterns)
