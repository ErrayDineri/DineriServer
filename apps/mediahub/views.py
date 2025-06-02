from django.shortcuts import render, get_object_or_404
from pathlib import Path
import os
from django.conf import settings
from django.utils.text import slugify



def list_videos(request):
    media_dir = Path(settings.MEDIA_ROOT) / 'videos'
    video_folders = [f for f in media_dir.iterdir() if f.is_dir() and (f / 'master.m3u8').exists()]
    
    videos = []
    for folder in video_folders:
        # Match original name from the original file or store mapping
        original_name = folder.name
        videos.append({
            'name': original_name,
            'slug': slugify(original_name),
        })

    return render(request, 'mediahub/list.html', {'videos': videos})


def stream_video(request, video_name):
    # Reconstruct the slug to get the correct folder path
    slug = slugify(video_name)
    video_dir = Path(settings.MEDIA_ROOT) / 'videos' / slug
    master_playlist = video_dir / 'master.m3u8'
    subtitles_file = video_dir / 'subtitles.vtt'

    if not master_playlist.exists():
        return render(request, 'mediahub/error.html', {'message': 'Video not found.'})

    return render(request, 'mediahub/stream.html', {
        'video_name': video_name,
        'video_url': f"{settings.MEDIA_URL}videos/{slug}/master.m3u8",
        'subtitles_url': f"{settings.MEDIA_URL}videos/{slug}/subtitles.vtt" if subtitles_file.exists() else None,
    })

