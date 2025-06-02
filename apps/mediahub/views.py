# views.py
from django.shortcuts import render
from pathlib import Path
import json
from django.conf import settings
from django.utils.text import slugify


def list_videos(request):
    media_dir = Path(settings.MEDIA_ROOT) / 'videos'

    video_folders = []
    if media_dir.exists() and media_dir.is_dir():
        video_folders = [
            f for f in media_dir.iterdir()
            if f.is_dir() and (f / 'master.m3u8').exists()
        ]
    else:
        media_dir.mkdir(parents=True, exist_ok=True)
        video_folders = []

    videos = []
    for folder in video_folders:
        original_name = folder.name
        thumbnail = folder / 'thumbnail.jpg'
        videos.append({
            'name': original_name,
            'slug': slugify(original_name),
            'thumbnail_url': f"{settings.MEDIA_URL}videos/{folder.name}/thumbnail.jpg" if thumbnail.exists() else None,
        })

    return render(request, 'mediahub/list.html', {'videos': videos})


def stream_video(request, video_name):
    slug = slugify(video_name)
    video_dir = Path(settings.MEDIA_ROOT) / 'videos' / slug
    master_playlist = video_dir / 'master.m3u8'

    if not video_dir.exists() or not video_dir.is_dir() or not master_playlist.exists():
        return render(request, 'mediahub/stream.html', {
            'video_name': video_name,
            'video_url': None,
            'subtitles_list': [],
            'thumbnail_url': None,
        })

    # Look for .vtt subtitle files in the 'hd/' folder
    hd_dir = video_dir / 'hd'
    subtitle_files = []
    if hd_dir.exists():
        subtitle_files = sorted(hd_dir.glob('index*.vtt'))

    subtitles_list = []
    for sub_file in subtitle_files:
        parts = sub_file.stem.split('_')  # e.g. index_en -> ['index', 'en']
        lang = parts[1] if len(parts) > 1 else 'en'
        label = f"{lang.upper()} Subtitle"
        subtitles_list.append({
            'url': f"{settings.MEDIA_URL}videos/{slug}/hd/{sub_file.name}",
            'lang': lang,
            'label': label,
        })

    thumbnail_url = None
    thumbnail_file = video_dir / 'thumbnail.jpg'
    if thumbnail_file.exists():
        thumbnail_url = f"{settings.MEDIA_URL}videos/{slug}/thumbnail.jpg"

    return render(request, 'mediahub/stream.html', {
        'video_name': video_name,
        'video_url': f"{settings.MEDIA_URL}videos/{slug}/master.m3u8",
        'subtitles_list': subtitles_list,
        'thumbnail_url': thumbnail_url,
    })
