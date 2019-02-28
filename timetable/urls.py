from django.contrib.auth.decorators import login_required
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'timetable'

urlpatterns = [
    path('', login_required(views.IndexView.as_view()), name='index'),
    path('api/blocks/new', views.BlockNew.as_view(), name='new'),
    path('api/blocks/delete', views.BlockDelete.as_view(), name='delete'),
    path('api/blocks', views.BlockList.as_view(), name='blocks'),
    path('api/blocks/<int:pk>', views.BlockDetail.as_view(), name='blocks_detail'),
    path('api/blocks/week', views.WeekBlocks.as_view(), name='blocks_week'),
    path('api/blocks/future', views.FutureBlocks.as_view(), name='blocks_future'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
