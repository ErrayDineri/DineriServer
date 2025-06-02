import os
import json
import subprocess
import logging
import time
import platform
from pathlib import Path

from celery import shared_task
from celery.exceptions import Ignore
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify

logger = logging.getLogger(__name__)

LOCK_FILE = Path(settings.BASE_DIR) / 'media' / '.conversion_lock'
CONVERTIBLE_EXTENSIONS = {
    '.mkv', '.avi', '.mov', '.flv', '.wmv', '.m4v',
    '.mpg', '.mpeg', '.mp4', '.webm', '.3gp',
    '.asf', '.mts', '.mxf',
}
conversion_task_running = False


def is_task_locked():
    if LOCK_FILE.exists():
        mtime = LOCK_FILE.stat().st_mtime
        if time.time() - mtime > 8 * 3600:
            LOCK_FILE.unlink()
            return False
        return True
    return False


def create_lock():
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOCK_FILE.write_text(f"Locked at {timezone.now().isoformat()}")


def remove_lock():
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()


def run_ffmpeg_command(cmd_list):
    """
    Run ffmpeg/ffprobe command. On Windows, use CREATE_NO_WINDOW to avoid console popups.
    """
    kwargs = {'check': True, 'capture_output': True, 'text': True}
    if platform.system() == 'Windows':
        kwargs['creationflags'] = 0x08000000  # CREATE_NO_WINDOW

    try:
        return subprocess.run(cmd_list, **kwargs)
    except subprocess.CalledProcessError as e:
        logger.error(
            f"FFmpeg command failed:\n{' '.join(cmd_list)}\n\nSTDERR:\n{e.stderr}"
        )
        raise


def ffprobe_json(file_path):
    cmd = [
        'ffprobe', '-v', 'quiet', '-print_format', 'json',
        '-show_format', '-show_streams', str(Path(file_path).resolve())
    ]
    result = run_ffmpeg_command(cmd)
    return json.loads(result.stdout)


def extract_metadata_and_tracks(file_path):
    info = ffprobe_json(file_path)
    metadata = info.get('format', {}).get('tags', {})
    duration = float(info.get('format', {}).get('duration', 0))

    audio_tracks = []
    subtitle_tracks = []

    for stream in info.get('streams', []):
        codec_type = stream.get('codec_type')
        tags = stream.get('tags', {})
        language = tags.get('language', 'und')

        if codec_type == 'audio':
            audio_tracks.append({
                'index': stream['index'],
                'language': language,
                'codec': stream.get('codec_name'),
                'channels': stream.get('channels'),
            })
        elif codec_type == 'subtitle':
            subtitle_tracks.append({
                'index': stream['index'],
                'language': language,
                'codec': stream.get('codec_name'),
            })

    return {
        'metadata': metadata,
        'duration': duration,
        'audio_tracks': audio_tracks,
        'subtitle_tracks': subtitle_tracks,
    }


def extract_thumbnail(file_path, output_path, time_point='00:00:05', resolution='1280x720'):
    cmd = [
        'ffmpeg', '-y', '-ss', time_point, '-i', str(Path(file_path).resolve()),
        '-vframes', '1', '-s', resolution,
        str(Path(output_path).resolve())
    ]
    run_ffmpeg_command(cmd)
    return Path(output_path).exists()


def create_adaptive_hls(input_file, output_dir):
    """
    Create 720p and 1080p adaptive HLS streams, converting subtitles to WebVTT.
    """
    input_path = Path(input_file).resolve()
    output_dir = Path(output_dir).resolve()

    qualities = [
        {'height': 1080, 'bitrate': '5000k', 'audio_bitrate': '192k', 'name': 'fullhd'},
        {'height': 720,  'bitrate': '2500k', 'audio_bitrate': '128k', 'name': 'hd'},
    ]

    playlists = []

    for quality in qualities:
        quality_dir = output_dir / quality['name']
        quality_dir.mkdir(exist_ok=True)

        playlist_file = quality_dir / 'index.m3u8'
        segment_filename = quality_dir / 'segment_%03d.ts'

        cmd = [
            'ffmpeg', '-y', '-i', str(input_path),
            '-filter:v', f'scale=-2:{quality["height"]}',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
            '-pix_fmt', 'yuv420p', '-profile:v', 'main', '-level', '4.0',
            '-c:a', 'aac', '-b:a', quality['audio_bitrate'], '-ar', '48000', '-ac', '2',
            '-c:s', 'webvtt',                            # Convert subtitles to WebVTT
            '-f', 'hls',
            '-hls_time', '6',
            '-hls_playlist_type', 'vod',
            '-hls_flags', 'independent_segments+temp_file',
            '-hls_segment_filename', str(segment_filename),
            '-force_key_frames', 'expr:gte(t,n_forced*6)',
            str(playlist_file),
        ]

        run_ffmpeg_command(cmd)

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
            f.write(
                f'#EXT-X-STREAM-INF:BANDWIDTH={pl["bandwidth"]},RESOLUTION={pl["resolution"]}\n'
            )
            f.write(f'{pl["path"]}\n')

    return master_playlist.exists()


def extract_subtitles_separately(input_file, output_dir, subtitle_tracks):
    """
    Extract each subtitle track separately to WebVTT, with language in the filename.
    """
    input_path = str(Path(input_file).resolve())
    output_dir = Path(output_dir).resolve()

    for i, sub in enumerate(subtitle_tracks):
        lang = sub.get('language', 'und')
        lang_safe = ''.join(c for c in lang if c.isalnum())
        output_sub = output_dir / f'subtitles_{lang_safe}_{i}.vtt'

        cmd = [
            'ffmpeg', '-y', '-i', input_path,
            '-map', f'0:s:{sub["index"]}',
            '-c:s', 'webvtt',
            str(output_sub)
        ]
        run_ffmpeg_command(cmd)


@shared_task(bind=True)
def convert_media_files(self):
    global conversion_task_running
    if conversion_task_running or is_task_locked():
        logger.info("Conversion task already running. Skipping.")
        raise Ignore()

    try:
        conversion_task_running = True
        create_lock()

        media_dir = Path(settings.BASE_DIR) / 'media' / 'videos'
        if not media_dir.exists():
            return "No media directory found"

        converted = skipped = failed = 0

        for file_path in media_dir.rglob('*'):
            if not file_path.is_file():
                continue

            ext = file_path.suffix.lower()
            if ext not in CONVERTIBLE_EXTENSIONS:
                skipped += 1
                continue

            # Remove '[' and ']' from filename to avoid FFmpeg parsing issues
            clean_name = file_path.stem.replace('[', '').replace(']', '')
            output_slug = slugify(clean_name)
            output_dir = file_path.parent / output_slug
            master_playlist = output_dir / 'master.m3u8'
            thumbnail_file = output_dir / 'thumbnail.jpg'

            if master_playlist.exists():
                skipped += 1
                continue

            output_dir.mkdir(parents=True, exist_ok=True)

            try:
                metadata_info = extract_metadata_and_tracks(file_path)

                if not create_adaptive_hls(file_path, output_dir):
                    raise Exception("HLS conversion failed")

                extract_thumbnail(file_path, thumbnail_file)

                extract_subtitles_separately(
                    file_path, output_dir, metadata_info['subtitle_tracks']
                )

                with open(output_dir / 'metadata.json', 'w', encoding='utf-8') as f:
                    json.dump(metadata_info, f, indent=2)

                if master_playlist.exists():
                    file_path.unlink()
                    converted += 1
                else:
                    failed += 1

            except Exception as e:
                logger.error(f"Conversion failed for {file_path}:\n{e}")
                failed += 1

        return f"Converted: {converted}, Skipped: {skipped}, Failed: {failed}"

    finally:
        conversion_task_running = False
        remove_lock()
