import math


def format_bytes(num_bytes: int | float | None) -> str:
    """Format bytes into a human-readable string (e.g. 12.5 MB)."""
    if num_bytes is None or num_bytes <= 0 or math.isnan(num_bytes):
        return "Unknown size"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_idx = 0
    val = float(num_bytes)
    
    while val >= 1024.0 and unit_idx < len(units) - 1:
        val /= 1024.0
        unit_idx += 1
        
    if unit_idx == 0:
        return f"{int(val)} B"
    return f"{val:.1f} {units[unit_idx]}"


def format_duration(seconds: int | float | None) -> str:
    """Format duration in seconds into HH:MM:SS or MM:SS."""
    if seconds is None or seconds < 0:
        return "00:00"
        
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def format_speed(bytes_per_sec: float | None) -> str:
    """Format speed in bytes/sec into human readable format (e.g. 3.4 MB/s)."""
    if bytes_per_sec is None or bytes_per_sec <= 0:
        return "--"
    return f"{format_bytes(bytes_per_sec)}/s"


def format_eta(seconds: int | float | None) -> str:
    """Format estimated time remaining into human readable string."""
    if seconds is None or seconds < 0:
        return "--"
    return format_duration(seconds)
