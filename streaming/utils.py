import re
import os

def clean_title(filename):
    # Remove extension
    name = os.path.splitext(filename)[0]

    # Replace dots/underscores with spaces
    name = re.sub(r'[._]', ' ', name)

    # Remove common tags [like this], (like this)
    name = re.sub(r'\[.*?\]|\(.*?\)', '', name)

    # Remove resolution and technical tags
    name = re.sub(r'\b(720p|1080p|2160p|4k|hdr|x264|x265|hevc|web[- ]?dl|web[- ]?rip|bluray|aac|mp3|h264|rarbg|cr)\b', '', name, flags=re.I)

    # Remove leftover bracketed IDs or hex
    name = re.sub(r'\b[a-f0-9]{8,}\b', '', name)

    # Collapse multiple spaces
    name = re.sub(r'\s+', ' ', name)

    # Capitalize nicely
    return name.strip().title()
