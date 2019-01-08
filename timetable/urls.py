from django.urls import path

from . import views

app_name = 'timetable'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('new/', views.new, name='new'),
    path('<int:block_id>/delete/', views.delete, name='delete'),
]
