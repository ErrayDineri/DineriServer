from django.urls import path
from .views import (
    TorrentStatusView, TorrentStatusJSON,
    PauseTorrent, ResumeTorrent, ForceStartTorrent, DeleteTorrent
)

urlpatterns = [
    path('torrents/', TorrentStatusView.as_view(), name='torrent'),
    path('torrents/json/', TorrentStatusJSON.as_view(), name='torrent_status_json'),
    path('torrents/pause/', PauseTorrent.as_view(), name='torrent_pause'),
    path('torrents/resume/', ResumeTorrent.as_view(), name='torrent_resume'),
    path('torrents/force/', ForceStartTorrent.as_view(), name='torrent_force'),
    path('torrents/delete/', DeleteTorrent.as_view(), name='torrent_delete'),
]
