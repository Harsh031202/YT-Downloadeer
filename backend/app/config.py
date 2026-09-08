import os
import tempfile
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application runtime settings with sensible defaults."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = int(os.getenv("PORT", "10000"))
    DEBUG: bool = False
    
    # Download storage
    # If /tmp/ytdlp_jobs is not writable (e.g. Windows), fallback to OS temp dir
    DOWNLOAD_DIR: str = os.getenv(
        "DOWNLOAD_DIR", 
        str(Path(tempfile.gettempdir()) / "ytdlp_jobs")
    )
    
    # Concurrency & limits
    MAX_CONCURRENT_DOWNLOADS: int = int(os.getenv("MAX_CONCURRENT_DOWNLOADS", "2"))
    JOB_TIMEOUT_SECONDS: int = int(os.getenv("JOB_TIMEOUT_SECONDS", "600"))
    
    # Cleanup settings
    CLEANUP_INTERVAL_SECONDS: int = int(os.getenv("CLEANUP_INTERVAL_SECONDS", "180"))
    JOB_TTL_SECONDS: int = int(os.getenv("JOB_TTL_SECONDS", "900"))  # 15 minutes
    
    # Security & CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Optional explicit FFmpeg binary path
    FFMPEG_LOCATION: str = os.getenv("FFMPEG_LOCATION", "ffmpeg")

    # Cloud / Render anti-bot bypass options
    YTDLP_COOKIES: Optional[str] = os.getenv("YTDLP_COOKIES", None)
    YTDLP_COOKIES_FILE: str = os.getenv("YTDLP_COOKIES_FILE", "cookies.txt")
    PROXY_URL: Optional[str] = os.getenv("PROXY_URL", None)
    YTDLP_PO_TOKEN: Optional[str] = os.getenv("YTDLP_PO_TOKEN", None)


settings = Settings()


def get_cookie_file_path() -> Optional[str]:
    """Resolve active cookies file from environment variable or local file."""
    if settings.YTDLP_COOKIES:
        cookie_path = Path(tempfile.gettempdir()) / "ytdlp_runtime_cookies.txt"
        try:
            cookie_path.write_text(settings.YTDLP_COOKIES, encoding="utf-8")
            return str(cookie_path)
        except Exception:
            pass

    if settings.YTDLP_COOKIES_FILE and Path(settings.YTDLP_COOKIES_FILE).is_file():
        return str(Path(settings.YTDLP_COOKIES_FILE).resolve())

    return None

# Ensure download root directory exists
Path(settings.DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)
