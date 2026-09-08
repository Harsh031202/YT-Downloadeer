import re
from pathlib import Path
from urllib.parse import urlparse

# Strict regex matching valid YouTube URLs (standard watch, shorts, share links, music)
YOUTUBE_URL_PATTERNS = [
    # https://www.youtube.com/watch?v=VIDEO_ID
    re.compile(r"^https?://(?:www\.|m\.|music\.)?youtube\.com/watch\?(?:.*&)?v=([a-zA-Z0-9_-]{11})(?:&.*)?$"),
    # https://youtu.be/VIDEO_ID
    re.compile(r"^https?://youtu\.be/([a-zA-Z0-9_-]{11})(?:\?.*)?$"),
    # https://www.youtube.com/shorts/VIDEO_ID
    re.compile(r"^https?://(?:www\.|m\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})(?:\?.*)?$"),
    # https://www.youtube.com/embed/VIDEO_ID
    re.compile(r"^https?://(?:www\.|m\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})(?:\?.*)?$"),
    # https://www.youtube.com/v/VIDEO_ID
    re.compile(r"^https?://(?:www\.|m\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})(?:\?.*)?$"),
    # https://www.youtube.com/live/VIDEO_ID
    re.compile(r"^https?://(?:www\.|m\.)?youtube\.com/live/([a-zA-Z0-9_-]{11})(?:\?.*)?$"),
]


def validate_youtube_url(url: str) -> bool:
    """Validate that the given URL is a legitimate YouTube URL."""
    if not url or not isinstance(url, str):
        return False
    
    url = url.strip()
    if len(url) > 500:
        return False
        
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
        
    hostname = (parsed.hostname or "").lower()
    allowed_domains = {
        "youtube.com",
        "www.youtube.com",
        "m.youtube.com",
        "music.youtube.com",
        "youtu.be",
    }
    if hostname not in allowed_domains:
        return False
        
    return any(pattern.match(url) for pattern in YOUTUBE_URL_PATTERNS)


def extract_video_id(url: str) -> str | None:
    """Extract YouTube video ID if URL is valid."""
    if not url:
        return None
    url = url.strip()
    for pattern in YOUTUBE_URL_PATTERNS:
        match = pattern.match(url)
        if match:
            return match.group(1)
    return None


def sanitize_filename(name: str, max_length: int = 100) -> str:
    """Sanitize a video title or string into a safe filesystem filename."""
    if not name:
        return "download"
        
    # Replace illegal filename characters on Windows & POSIX
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name)
    # Remove control characters
    cleaned = "".join(ch for ch in cleaned if ord(ch) >= 32)
    # Remove consecutive dots (prevent directory traversal or odd file names)
    cleaned = re.sub(r"\.{2,}", "", cleaned)
    # Replace multiple spaces/underscores with single space
    cleaned = re.sub(r"[\s_]+", " ", cleaned).strip()
    # Strip dots at start or end to prevent hidden files or extension issues
    cleaned = cleaned.strip(". ")
    
    if not cleaned:
        cleaned = "video"
        
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rstrip()
        
    return cleaned


def safe_resolve_job_file(base_dir: str, job_id: str, filename: str) -> Path:
    """Safely resolve a job file path, strictly ensuring it is inside the job directory."""
    # Ensure job_id is strictly a valid UUID / safe hex token
    if not re.match(r"^[a-zA-Z0-9_-]+$", job_id):
        raise ValueError("Invalid job ID format")
        
    base_path = Path(base_dir).resolve()
    job_dir = (base_path / job_id).resolve()
    
    # Path traversal check for job dir
    if not str(job_dir).startswith(str(base_path)):
        raise ValueError("Directory traversal detected in job path")
        
    # Safe resolve target file
    clean_name = Path(filename).name
    file_path = (job_dir / clean_name).resolve()
    
    if not str(file_path).startswith(str(job_dir)):
        raise ValueError("Directory traversal detected in file path")
        
    return file_path
