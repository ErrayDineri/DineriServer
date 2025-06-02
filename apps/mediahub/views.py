# views.py
from django.shortcuts import render
from pathlib import Path
import json
from django.conf import settings
from django.utils.text import slugify


def list_videos(request):
    media_dir = Path(settings.MEDIA_ROOT) / 'videos'
    video_folders = [f for f in media_dir.iterdir() if f.is_dir() and (f / 'master.m3u8').exists()]

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

    if not master_playlist.exists():
        return render(request, 'mediahub/error.html', {'message': 'Video not found.'})

    # Find all subtitle .vtt files starting with 'index' (like index0.vtt, index1.vtt, etc.)
    subtitle_files = sorted(video_dir.glob('index*.vtt'))
    subtitles = []
    for sub_file in subtitle_files:
        # Optionally infer language or label here. If you don’t have language info,
        # just label them Subtitle 1, Subtitle 2, etc.
        label = sub_file.stem  # e.g. 'index0'
        subtitles.append({
            'url': f"{settings.MEDIA_URL}videos/{slug}/{sub_file.name}",
            'lang': 'en',  # you can change this or infer it from metadata if available
            'label': label,
        })

    return render(request, 'mediahub/stream.html', {
        'video_name': video_name,
        'video_url': f"{settings.MEDIA_URL}videos/{slug}/master.m3u8",
        'subtitles': subtitles,
    })
