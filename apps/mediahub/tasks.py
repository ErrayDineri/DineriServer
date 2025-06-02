import os
import subprocess
import logging
import time
from pathlib import Path

from celery import shared_task
from celery.exceptions import Ignore
from django.conf import settings
from django.utils import timezone
from slugify import slugify

logger = logging.getLogger(__name__)

LOCK_FILE = os.path.join(settings.BASE_DIR, 'media', '.conversion_lock')

CONVERTIBLE_EXTENSIONS = {
    '.mkv', '.avi', '.mov', '.flv', '.wmv', '.m4v', '.mpg',
    '.mpeg', '.mp4', '.webm', '.3gp', '.asf', '.mts', '.mxf',
}

conversion_task_running = False


def is_task_locked():
    if os.path.exists(LOCK_FILE):
        mtime = os.path.getmtime(LOCK_FILE)
        if time.time() - mtime > 8 * 3600:
            os.remove(LOCK_FILE)
            return False
        return True
    return False


def create_lock():
    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
    with open(LOCK_FILE, 'w') as f:
        f.write(f"Locked at {timezone.now().isoformat()}")


def remove_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)


@shared_task(bind=True)
def convert_media_files(self):
    global conversion_task_running
    if conversion_task_running or is_task_locked():
        logger.info("Conversion task already running. Skipping.")
        raise Ignore()

    try:
        conversion_task_running = True
        create_lock()

        media_dir = os.path.join(settings.BASE_DIR, 'media', 'videos')
        if not os.path.exists(media_dir):
            return "No media directory found"

        converted, skipped, failed = 0, 0, 0

        for file_path in Path(media_dir).rglob('*'):
            if not file_path.is_file():
                continue

            ext = file_path.suffix.lower()
            if ext not in CONVERTIBLE_EXTENSIONS:
                skipped += 1
                continue

            # Slugify output folder name
            output_slug = slugify(file_path.stem)
            output_dir = file_path.parent / output_slug
            master_playlist = output_dir / 'master.m3u8'

            if master_playlist.exists():
                skipped += 1
                continue

            output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Converting {file_path.name} to HLS")

            try:
                if create_adaptive_hls(file_path, output_dir):
                    logger.info(f"HLS created for {file_path.name}")
                else:
                    raise Exception("HLS conversion failed")

                subtitle_cmd = [
                    'ffmpeg', '-y', '-i', str(file_path),
                    '-map', '0:s:0', '-codec:s', 'webvtt',
                    str(output_dir / 'subtitles.vtt')
                ]
                subprocess.run(subtitle_cmd, check=True, capture_output=True, text=True)

                create_mp4_fallback(file_path, output_dir)

                if master_playlist.exists():
                    os.remove(file_path)
                    converted += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"Conversion failed: {e}")
                failed += 1

        return f"Converted: {converted}, Skipped: {skipped}, Failed: {failed}"

    finally:
        conversion_task_running = False
        remove_lock()


def create_adaptive_hls(input_file, output_dir):
    qualities = [
        {'height': 1080, 'bitrate': '5000k', 'audio_bitrate': '192k', 'name': 'fullhd'},
        {'height': 720,  'bitrate': '2500k', 'audio_bitrate': '128k', 'name': 'hd'},
    ]

    playlists = []

    for quality in qualities:
        quality_dir = output_dir / quality['name']
        quality_dir.mkdir(exist_ok=True)

        playlist_file = quality_dir / 'index.m3u8'

        cmd = [
            'ffmpeg', '-y', '-i', str(input_file),
            '-codec:v', 'libx264', '-preset', 'medium', '-crf', '23',
            '-pix_fmt', 'yuv420p', '-profile:v', 'main', '-level', '4.0',
            '-movflags', '+faststart',
            '-vf', f'scale=-2:{quality["height"]}',
            '-b:v', quality['bitrate'],
            '-maxrate', str(int(quality['bitrate'][:-1]) * 1200)[:-1] + 'k',
            '-bufsize', str(int(quality['bitrate'][:-1]) * 2000)[:-1] + 'k',
            '-codec:a', 'aac', '-b:a', quality['audio_bitrate'], '-ar', '48000', '-ac', '2',
            '-f', 'hls', '-hls_time', '6', '-hls_playlist_type', 'vod',
            '-hls_flags', 'independent_segments+temp_file',
            '-hls_segment_filename', str(quality_dir / 'segment_%03d.ts'),
            '-force_key_frames', 'expr:gte(t,n_forced*6)',
            str(playlist_file),
        ]

        subprocess.run(cmd, check=True, capture_output=True, text=True)

        if playlist_file.exists():
            res_map = {1080: '1920x1080', 720: '1280x720'}
            playlists.append({
                'path': f'{quality["name"]}/index.m3u8',
                'bandwidth': int(quality['bitrate'][:-1]) * 1000,
                'resolution': res_map.get(quality['height'], f'1280x{quality["height"]}')
            })

    master_playlist = output_dir / 'master.m3u8'
    with open(master_playlist, 'w') as f:
        f.write('#EXTM3U\n#EXT-X-VERSION:3\n\n')
        for pl in playlists:
            f.write(f'#EXT-X-STREAM-INF:BANDWIDTH={pl["bandwidth"]},RESOLUTION={pl["resolution"]}\n')
            f.write(f'{pl["path"]}\n')

    return master_playlist.exists()


def create_mp4_fallback(input_file, output_dir):
    mp4_file = output_dir / 'fallback.mp4'
    cmd = [
        'ffmpeg', '-y', '-i', str(input_file),
        '-codec:v', 'libx264', '-preset', 'medium', '-crf', '23',
        '-pix_fmt', 'yuv420p', '-profile:v', 'main', '-level', '4.0',
        '-movflags', '+faststart',
        '-vf', 'scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2',
        '-codec:a', 'aac', '-b:a', '128k', '-ar', '48000', '-ac', '2',
        str(mp4_file),
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return mp4_file.exists()
