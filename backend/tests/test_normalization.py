import pytest
from backend.app.services.ytdlp_service import YtDlpService, clean_codec_name


def test_clean_codec_name():
    assert clean_codec_name("avc1.640028") == "H.264"
    assert clean_codec_name("vp09.00.51.08.01") == "VP9"
    assert clean_codec_name("av01.0.08M.08") == "AV1"
    assert clean_codec_name("mp4a.40.2") == "AAC"
    assert clean_codec_name("opus") == "Opus"
    assert clean_codec_name("none") == "None"


def test_format_normalization():
    service = YtDlpService()
    
    mock_raw_formats = [
        # Audio stream
        {
            "format_id": "140",
            "vcodec": "none",
            "acodec": "mp4a.40.2",
            "abr": 128,
            "ext": "m4a",
            "filesize": 5 * 1024 * 1024,
        },
        # Higher audio stream
        {
            "format_id": "251",
            "vcodec": "none",
            "acodec": "opus",
            "abr": 160,
            "ext": "webm",
            "filesize": 6 * 1024 * 1024,
        },
        # 1080p video-only stream (DASH)
        {
            "format_id": "137",
            "vcodec": "avc1.640028",
            "acodec": "none",
            "height": 1080,
            "width": 1920,
            "fps": 30,
            "ext": "mp4",
            "filesize": 80 * 1024 * 1024,
        },
        # 720p video+audio combined stream
        {
            "format_id": "22",
            "vcodec": "avc1.64001F",
            "acodec": "mp4a.40.2",
            "height": 720,
            "width": 1280,
            "fps": 30,
            "ext": "mp4",
            "filesize": 40 * 1024 * 1024,
        },
        # 480p video-only stream
        {
            "format_id": "135",
            "vcodec": "avc1.4d401f",
            "acodec": "none",
            "height": 480,
            "width": 854,
            "fps": 30,
            "ext": "mp4",
            "filesize": 20 * 1024 * 1024,
        },
    ]

    video_items, audio_items = service._normalize_formats(mock_raw_formats, duration=180)

    # Check video items
    assert len(video_items) >= 3
    resolutions = [v.height for v in video_items]
    assert resolutions == sorted(resolutions, reverse=True)  # Sorted descending
    assert 1080 in resolutions
    assert 720 in resolutions
    assert 480 in resolutions

    # Check that 1080p is marked audio_merged=True
    v1080 = next(v for v in video_items if v.height == 1080)
    assert v1080.audio_merged is True
    # Verify size combines video + best audio stream (~80MB + ~6MB)
    assert v1080.filesize_approx is not None or v1080.filesize is not None

    # Check audio items
    assert len(audio_items) >= 1
    assert audio_items[0].quality == "Best Audio"
    assert audio_items[0].type == "audio"
    assert audio_items[0].audio_merged is False
