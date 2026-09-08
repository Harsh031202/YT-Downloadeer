import os
import tempfile
from pathlib import Path
from typing import List
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


settings = Settings()

# Ensure download root directory exists
Path(settings.DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)
