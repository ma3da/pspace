from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'timetable'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('new/', views.new, name='new'),
    path('<int:block_id>/delete/', views.delete, name='delete'),
    path('pouet', views.ActivityList.as_view(), name='pouet'),
    path('pouet/<int:pk>', views.ActivityDetail.as_view(), name='pouet_detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
