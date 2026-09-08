import pytest
from backend.app.utils.security import (
    validate_youtube_url,
    extract_video_id,
    sanitize_filename,
)


def test_valid_youtube_urls():
    valid_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "http://youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://music.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/dQw4w9WgXcQ",
        "https://www.youtube.com/live/dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=42s",
        "https://youtu.be/dQw4w9WgXcQ?si=abcdef123456",
    ]
    for url in valid_urls:
        assert validate_youtube_url(url) is True, f"Failed for {url}"
        assert extract_video_id(url) == "dQw4w9WgXcQ"


def test_invalid_youtube_urls():
    invalid_urls = [
        "https://vimeo.com/12345678",
        "https://notyoutube.com/watch?v=dQw4w9WgXcQ",
        "http://localhost:8000/malicious",
        "http://127.0.0.1/test",
        "http://169.254.169.254/latest/meta-data/",
        "file:///etc/passwd",
        "javascript:alert(1)",
        "",
        None,
        "https://youtube.com/watch?v=short",  # Invalid ID length
        "https://youtube.com/notwatch/12345",
    ]
    for url in invalid_urls:
        assert validate_youtube_url(url) is False, f"Should be invalid: {url}"


def test_sanitize_filename():
    assert sanitize_filename("Normal Title") == "Normal Title"
    assert sanitize_filename('Title with <illegal> : characters "and" / slashes') == "Title with illegal characters and slashes"
    assert sanitize_filename("../../../etc/passwd") == "etcpasswd"
    assert sanitize_filename("...hidden...file...") == "hiddenfile"
    assert sanitize_filename("   A   B    C   ") == "A B C"
    # Long filename truncation
    long_name = "a" * 200
    sanitized = sanitize_filename(long_name, max_length=50)
    assert len(sanitized) <= 50
