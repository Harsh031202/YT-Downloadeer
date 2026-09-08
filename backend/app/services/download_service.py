import logging
import os
import re
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional
import yt_dlp

from ..config import settings
from ..utils.formatting import format_bytes
from ..utils.security import sanitize_filename
from .ffmpeg_service import ffmpeg_service

logger = logging.getLogger(__name__)


class DownloadService:
    """Service to execute yt-dlp media downloads with progress tracking and FFmpeg merging."""

    def download(
        self,
        job_id: str,
        url: str,
        format_id: str,
        media_type: str,
        progress_callback: Callable[[Dict[str, Any]], None],
    ) -> Dict[str, Any]:
        """Execute download synchronously in a worker thread."""
        job_dir = Path(settings.DOWNLOAD_DIR) / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        current_stream = {"phase": "video" if media_type == "video" else "audio"}
        last_progress_time = 0.0

        def yt_progress_hook(d: Dict[str, Any]):
            nonlocal last_progress_time
            now = time.time()
            # Throttle progress updates to at most ~10 updates/sec to prevent excessive lock contention
            if d.get("status") == "downloading" and (now - last_progress_time < 0.1):
                return
            last_progress_time = now

            status = d.get("status")
            if status == "downloading":
                total_bytes = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                downloaded_bytes = d.get("downloaded_bytes") or 0
                speed = d.get("speed") or 0.0
                eta = d.get("eta") or 0

                percent = 0.0
                if total_bytes > 0:
                    percent = min(99.0, (downloaded_bytes / total_bytes) * 100.0)
                elif d.get("_percent_str"):
                    try:
                        clean_pct = re.sub(r"[^\d.]", "", d["_percent_str"])
                        percent = min(99.0, float(clean_pct))
                    except Exception:
                        pass

                # Detect if audio stream is currently being downloaded
                filename = d.get("filename", "")
                info_dict = d.get("info_dict", {})
                vcodec = info_dict.get("vcodec")
                acodec = info_dict.get("acodec")

                if vcodec == "none" and acodec != "none":
                    current_stream["phase"] = "audio"
                    phase_status = "downloading_audio"
                    message = "Downloading the audio track..."
                elif media_type == "audio":
                    phase_status = "downloading_audio"
                    message = "Downloading audio track..."
                else:
                    phase_status = "downloading_video"
                    message = "Downloading your selected video..."

                progress_callback({
                    "status": phase_status,
                    "progress": round(percent, 1),
                    "message": message,
                    "downloaded_bytes": downloaded_bytes,
                    "total_bytes": total_bytes,
                    "speed": speed,
                    "eta": eta,
                })

            elif status == "finished":
                # Download finished, entering postprocessing / merging
                if media_type == "video":
                    progress_callback({
                        "status": "merging",
                        "progress": 96.0,
                        "message": "Combining video and audio...",
                        "downloaded_bytes": d.get("total_bytes") or 0,
                        "total_bytes": d.get("total_bytes") or 0,
                        "speed": 0.0,
                        "eta": 0,
                    })
                else:
                    progress_callback({
                        "status": "finalizing",
                        "progress": 97.0,
                        "message": "Finalizing your audio file...",
                        "downloaded_bytes": d.get("total_bytes") or 0,
                        "total_bytes": d.get("total_bytes") or 0,
                        "speed": 0.0,
                        "eta": 0,
                    })

        def yt_postprocessor_hook(d: Dict[str, Any]):
            status = d.get("status")
            if status == "started":
                postprocessor = d.get("postprocessor", "")
                if "Merger" in postprocessor:
                    msg = "Combining video and audio streams..."
                    phase = "merging"
                    pct = 97.0
                else:
                    msg = "Putting the finishing touches on your file..."
                    phase = "finalizing"
                    pct = 98.5
                progress_callback({
                    "status": phase,
                    "progress": pct,
                    "message": msg,
                })
            elif status == "finished":
                progress_callback({
                    "status": "finalizing",
                    "progress": 99.5,
                    "message": "Wrapping up...",
                })

        # Out template with safe sanitized title
        # Output template in yt-dlp: %(title).80B restricts length safely
        out_tmpl = str(job_dir / "%(title).80B [%(id)s].%(ext)s")

        ffmpeg_dir = ffmpeg_service.get_ffmpeg_dir()

        ydl_opts: Dict[str, Any] = {
            "outtmpl": out_tmpl,
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": [yt_progress_hook],
            "postprocessor_hooks": [yt_postprocessor_hook],
            "retries": 3,
            "socket_timeout": 30,
            # Force IPv4 if desired to prevent IPv6 routing delays on some cloud providers
            "source_address": "0.0.0.0",
        }

        if ffmpeg_dir:
            ydl_opts["ffmpeg_location"] = ffmpeg_dir

        if media_type == "video":
            # Select specified video format and merge with best audio
            ydl_opts["format"] = f"{format_id}+bestaudio[ext=m4a]/bestaudio/best"
            ydl_opts["merge_output_format"] = "mp4"
        else:
            # Audio only
            ydl_opts["format"] = f"{format_id}/bestaudio/best"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
        except Exception as exc:
            logger.error("Download failed for job %s: %s", job_id, exc)
            raise ValueError(f"Download failed: {str(exc)}")

        # Locate resulting file in job_dir
        final_file = self._find_completed_file(job_dir)
        if not final_file or not final_file.exists():
            raise FileNotFoundError("The output media file could not be found after processing.")

        file_size = final_file.stat().st_size
        safe_name = sanitize_filename(final_file.name)
        
        # If the sanitized name differs or needs normalization, rename safely
        if safe_name != final_file.name:
            target_path = final_file.parent / safe_name
            try:
                final_file.rename(target_path)
                final_file = target_path
            except Exception:
                pass

        return {
            "filename": final_file.name,
            "filepath": str(final_file),
            "filesize": file_size,
            "title": info.get("title", "video") if info else "video",
        }

    def _find_completed_file(self, job_dir: Path) -> Optional[Path]:
        """Find the final processed file in the job directory, ignoring temporary fragments."""
        candidates = []
        for p in job_dir.iterdir():
            if not p.is_file():
                continue
            # Ignore intermediate yt-dlp / ffmpeg temporary files
            if p.suffix in [".part", ".ytdl", ".temp", ".tmp"]:
                continue
            if p.name.endswith(".temp.mp4"):
                continue
            if p.stat().st_size > 0:
                candidates.append(p)

        if not candidates:
            return None
        # Return the newest or largest candidate
        candidates.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return candidates[0]


download_service = DownloadService()
