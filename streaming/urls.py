from django.urls import path
from .views import (
    VideoStreamView, VideoListView, HomeView,
    ScraperView, TorrentStatusView, TorrentStatusJSON,
    PauseTorrent, ResumeTorrent, ForceStartTorrent, DeleteTorrent
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('videos/', VideoListView.as_view(), name='video-list'),
    path('stream/<str:filename>/', VideoStreamView.as_view(), name='video-stream'),
    path('scraper/', ScraperView.as_view(), name='scraper-page'),
    path('torrents/', TorrentStatusView.as_view(), name='torrent-status'),
    path('torrents/json/', TorrentStatusJSON.as_view(), name='torrent_status_json'),

    # Action URLs
    path('torrents/pause/',  PauseTorrent.as_view(),     name='torrent_pause'),
    path('torrents/resume/', ResumeTorrent.as_view(),    name='torrent_resume'),
    path('torrents/force/',  ForceStartTorrent.as_view(),name='torrent_force'),
    path('torrents/delete/', DeleteTorrent.as_view(),    name='torrent_delete'),
]
