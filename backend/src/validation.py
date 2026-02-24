import os

ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'}
ALLOWED_VIDEO_MIME_PREFIXES = ('video/',)

def is_valid_video_file(filename):
    """Check if file has a valid video extension."""
    if not filename:
        return False
    ext = os.path.splitext(filename.lower())[1]
    return ext in ALLOWED_VIDEO_EXTENSIONS
