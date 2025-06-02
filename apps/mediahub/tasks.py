import os
import subprocess
import logging
import time
from pathlib import Path

from celery import shared_task
from celery.exceptions import Ignore
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# Keep track of whether the task is running (in-memory flag)
conversion_task_running = False

# File to store the lock info
LOCK_FILE = os.path.join(settings.BASE_DIR, 'media', '.conversion_lock')

# Only these source extensions will be converted
CONVERTIBLE_EXTENSIONS = {
    '.mkv',
    '.avi',
    '.mov',
    '.flv',
    '.wmv',
    '.m4v',
    '.mpg',
    '.mpeg',
    # add more if needed
}

def is_task_locked():
    """Check if the conversion task is locked (and remove stale locks)."""
    if os.path.exists(LOCK_FILE):
        mtime = os.path.getmtime(LOCK_FILE)
        # If lock is older than 8 hours, assume stale and delete
        if time.time() - mtime > 8 * 3600:
            logger.warning("Found stale lock file. Removing it.")
            os.remove(LOCK_FILE)
            return False
        return True
    return False

def create_lock():
    """Create a lock file to prevent concurrent runs."""
    lock_dir = os.path.dirname(LOCK_FILE)
    if not os.path.exists(lock_dir):
        os.makedirs(lock_dir)
    with open(LOCK_FILE, 'w') as f:
        f.write(f"Locked at {timezone.now().isoformat()}")

def remove_lock():
    """Remove the lock file."""
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

@shared_task(bind=True)
def convert_media_files(self):
    """
    Celery task to convert only “source” video files (e.g. .mkv, .avi) to HLS.
    Skips anything not in CONVERTIBLE_EXTENSIONS, so it will not re-convert .ts, .vtt, .m3u8, etc.
    """
    global conversion_task_running
    print("Task triggered!")  # quick test
    
    # If already running (in-memory flag or lock file), skip
    if conversion_task_running or is_task_locked():
        logger.info("Media conversion task is already running. Skipping this execution.")
        raise Ignore()
    
    try:
        conversion_task_running = True
        create_lock()
        
        media_dir = os.path.join(settings.BASE_DIR, 'media', 'videos')
        if not os.path.exists(media_dir):
            logger.warning(f"Media directory {media_dir} does not exist.")
            return "No media directory found"
        
        converted_count = 0
        skipped_count = 0
        failed_count = 0
        
        # Walk through all files under media_dir
        for file_path in Path(media_dir).rglob('*'):
            if not file_path.is_file():
                continue
            
            ext = file_path.suffix.lower()
            
            # If file is not one of the source extensions, skip immediately
            if ext not in CONVERTIBLE_EXTENSIONS:
                skipped_count += 1
                continue
            
            # Prepare the HLS output directory (one folder per source video)
            output_dir = file_path.with_suffix('')  # remove the extension
            playlist_file = output_dir / 'index.m3u8'
            
            # If we already converted (playlist exists), skip
            if playlist_file.exists():
                skipped_count += 1
                continue
            
            # Create output directory if it doesn’t exist
            if not output_dir.exists():
                output_dir.mkdir(parents=True)
            
            logger.info(f"Converting {file_path.name} to HLS streaming format")
            
            try:
                cmd = [
                    'ffmpeg',
                    '-y',
                    '-i', str(file_path),
                    # Video settings
                    '-codec:v', 'libx264',
                    '-preset', 'veryfast',
                    '-crf', '23',
                    # Audio settings
                    '-codec:a', 'aac',
                    '-b:a', '128k',
                    # Include subtitles as WebVTT if embedded
                    '-codec:s', 'webvtt',
                    # HLS output settings
                    '-f', 'hls',
                    '-hls_time', '10',              # each segment ~10s
                    '-hls_playlist_type', 'vod',    # VOD‐style playlist
                    '-hls_segment_filename', str(output_dir / 'segment_%03d.ts'),
                    str(playlist_file),
                ]
                
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                
                # If the playlist was created successfully, delete original
                if playlist_file.exists():
                    os.remove(file_path)
                    converted_count += 1
                    logger.info(f"Successfully converted {file_path.name} to HLS")
                else:
                    logger.error(f"Failed to convert {file_path.name}: Playlist not found")
                    failed_count += 1
            
            except subprocess.SubprocessError as e:
                logger.error(f"Error converting {file_path.name}: {str(e)}")
                failed_count += 1
        
        return f"Conversion completed: {converted_count} converted, {skipped_count} skipped, {failed_count} failed"
    
    except Exception as e:
        logger.exception(f"Error in media conversion task: {str(e)}")
        raise e
    
    finally:
        conversion_task_running = False
        remove_lock()
