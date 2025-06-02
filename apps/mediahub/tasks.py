import os
import subprocess
import logging
import time
import shutil
from pathlib import Path
from celery import shared_task
from django.conf import settings
from celery.exceptions import Ignore
from django.utils import timezone

logger = logging.getLogger(__name__)

# Keep track of whether the task is running
conversion_task_running = False
# File to store the lock info
LOCK_FILE = os.path.join(settings.BASE_DIR, 'media', '.conversion_lock')

def is_task_locked():
    """Check if the conversion task is locked"""
    if os.path.exists(LOCK_FILE):
        # Check if the lock is stale (older than 8 hours)
        mtime = os.path.getmtime(LOCK_FILE)
        if time.time() - mtime > 8 * 3600:  # 8 hours
            logger.warning("Found stale lock file. Removing it.")
            os.remove(LOCK_FILE)
            return False
        return True
    return False

def create_lock():
    """Create a lock file"""
    lock_dir = os.path.dirname(LOCK_FILE)
    if not os.path.exists(lock_dir):
        os.makedirs(lock_dir)
    
    with open(LOCK_FILE, 'w') as f:
        f.write(f"Locked at {timezone.now().isoformat()}")

def remove_lock():
    """Remove the lock file"""
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

@shared_task(bind=True)
def convert_media_files(self):
    """
    Task to convert non-MP4/AAC media files to MP4/AAC format.
    Runs on a configurable schedule if no instance is already running.
    """
    global conversion_task_running
    print("Task triggered!")  # quick test
    
    # Check both in-memory flag and lock file
    if conversion_task_running or is_task_locked():
        logger.info("Media conversion task is already running. Skipping this execution.")
        raise Ignore()
    
    try:
        conversion_task_running = True
        create_lock()
        
        # Get the media directory from settings or use default
        media_dir = os.path.join(settings.BASE_DIR, 'media', 'videos')
        
        # Ensure directory exists
        if not os.path.exists(media_dir):
            logger.warning(f"Media directory {media_dir} does not exist.")
            return "No media directory found"
        
        converted_count = 0
        skipped_count = 0
        failed_count = 0
        
        # List all files in the media directory
        for file_path in Path(media_dir).rglob('*'):
            if not file_path.is_file():
                continue
                # Skip files that are already in target format or don't need conversion
            if file_path.suffix.lower() in ('.mp4', '.mp3', '.aac'):
                skipped_count += 1
                continue
                
            # Skip files that are being processed or temporary files
            if file_path.name.startswith('.') or file_path.name.endswith('.part') or file_path.name.endswith('.temp'):
                logger.info(f"Skipping temporary or hidden file: {file_path.name}")
                skipped_count += 1
                continue
                
            # Target output file path
            output_file = file_path.with_suffix('.mp4')
            
            # Skip if output file already exists
            if output_file.exists():
                skipped_count += 1
                continue
                
            logger.info(f"Converting {file_path.name} to MP4/AAC format")
            
            try:
                # Run ffmpeg with high-speed encoding options
                cmd = [
                    'ffmpeg',
                    '-y',  # Overwrite output files
                    '-i', str(file_path),
                    '-c:v', 'libx264',  # Video codec
                    '-preset', 'veryfast',  # Speed optimization
                    '-crf', '23',  # Quality (lower = better, 23 is a good balance)
                    '-c:a', 'aac',  # Audio codec
                    '-b:a', '128k',  # Audio bitrate
                    '-movflags', '+faststart',  # Web optimization
                    str(output_file)
                ]
                
                # Execute the command
                result = subprocess.run(
                    cmd, 
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # If conversion was successful, remove the original file
                if os.path.exists(output_file):
                    os.remove(file_path)
                    converted_count += 1
                    logger.info(f"Successfully converted {file_path.name}")
                else:
                    logger.error(f"Failed to convert {file_path.name}: Output file not created")
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
