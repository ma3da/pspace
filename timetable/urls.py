from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'timetable'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('new/', views.new, name='new'),
    path('api/new', views.BlockNew.as_view(), name='apinew'),
    path('api/blocks/delete/<int:pk>', views.delete, name='delete'),
    path('api/blocks', views.BlockList.as_view(), name='blocks'),
    path('api/blocks/<int:pk>', views.BlockDetail.as_view(), name='blocks_detail'),
    path('api/blocks/week', views.BlockListByDate.as_view(), name='blocks_date'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
