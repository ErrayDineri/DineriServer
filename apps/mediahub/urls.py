# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_videos, name='video_list'),
    path('<str:video_name>/', views.stream_video, name='stream'),
]
