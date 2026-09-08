import logging
import shutil
import subprocess
from typing import Tuple, Optional
from ..config import settings

logger = logging.getLogger(__name__)


class FFmpegService:
    """Service to inspect and verify FFmpeg binary availability."""

    def __init__(self):
        self._available: Optional[bool] = None
        self._version: Optional[str] = None

    def check_availability(self) -> Tuple[bool, Optional[str]]:
        """Check if FFmpeg is installed and accessible."""
        if self._available is not None:
            return self._available, self._version

        # First check custom location or PATH
        binary = settings.FFMPEG_LOCATION or "ffmpeg"
        resolved = shutil.which(binary)
        if not resolved:
            logger.warning("FFmpeg binary not found in PATH or settings.FFMPEG_LOCATION")
            self._available = False
            self._version = None
            return False, None

        try:
            result = subprocess.run(
                [resolved, "-version"],
                capture_output=True,
                text=True,
                check=True,
                timeout=5,
            )
            first_line = result.stdout.splitlines()[0] if result.stdout else "FFmpeg present"
            self._available = True
            self._version = first_line
            logger.info("FFmpeg detected: %s at %s", first_line, resolved)
            return True, first_line
        except Exception as exc:
            logger.error("FFmpeg check failed: %s", exc)
            self._available = False
            self._version = None
            return False, None

    def get_ffmpeg_dir(self) -> Optional[str]:
        """Return the directory containing ffmpeg and ffprobe binaries."""
        binary = settings.FFMPEG_LOCATION or "ffmpeg"
        resolved = shutil.which(binary)
        if resolved:
            from pathlib import Path
            return str(Path(resolved).parent)
        return None


ffmpeg_service = FFmpegService()
