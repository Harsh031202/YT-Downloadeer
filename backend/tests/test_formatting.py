from backend.app.utils.formatting import format_bytes, format_duration, format_speed, format_eta


def test_format_bytes():
    assert format_bytes(500) == "500 B"
    assert format_bytes(1024) == "1.0 KB"
    assert format_bytes(1024 * 1024 * 12.5) == "12.5 MB"
    assert format_bytes(1024 * 1024 * 1024 * 2.3) == "2.3 GB"
    assert format_bytes(None) == "Unknown size"
    assert format_bytes(0) == "Unknown size"


def test_format_duration():
    assert format_duration(45) == "00:45"
    assert format_duration(65) == "01:05"
    assert format_duration(3665) == "01:01:05"
    assert format_duration(0) == "00:00"
    assert format_duration(None) == "00:00"


def test_format_speed_and_eta():
    assert format_speed(1024 * 1024 * 4.2) == "4.2 MB/s"
    assert format_speed(0) == "--"
    assert format_eta(14) == "00:14"
    assert format_eta(-1) == "--"
