from django.urls import path
from .views import (
    VideoStreamView, VideoListView, HomeView,
    ScraperView)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('videos/', VideoListView.as_view(), name='video-list'),
    path('stream/<str:filename>/', VideoStreamView.as_view(), name='video-stream'),
    path('scraper/', ScraperView.as_view(), name='scraper-page'),
]
