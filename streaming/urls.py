# urls.py
from django.urls import path
from .views import VideoStreamView, VideoListView, HomeView, ScraperView, TorrentStatusView, torrent_status_json

urlpatterns = [
    path('stream/<str:filename>/', VideoStreamView.as_view(), name='video-stream'),
    path('videos/', VideoListView.as_view(), name='video-list'),
    path('', HomeView.as_view(), name='home'),
    path('scraper/', ScraperView.as_view(), name='scraper-page'),
    path('torrents/', TorrentStatusView.as_view(), name='torrent-status'),
    path('torrents/json/', torrent_status_json, name='torrent_status_json'),
    ]