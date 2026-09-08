import logging
from typing import Any, Dict, List, Optional, Tuple
import yt_dlp

from ..models.schemas import FormatItem, VideoInfo
from ..utils.formatting import format_bytes, format_duration

logger = logging.getLogger(__name__)


def clean_codec_name(codec_str: Optional[str]) -> str:
    """Normalize technical codec strings (e.g. 'avc1.640028', 'vp09.00.51.08.01') to readable names."""
    if not codec_str or codec_str == "none":
        return "None"
    c = codec_str.lower()
    if c.startswith("avc1") or "h264" in c:
        return "H.264"
    if c.startswith("vp09") or "vp9" in c:
        return "VP9"
    if c.startswith("av01") or "av1" in c:
        return "AV1"
    if c.startswith("mp4a") or "aac" in c:
        return "AAC"
    if "opus" in c:
        return "Opus"
    if "mp3" in c:
        return "MP3"
    return codec_str.split(".")[0].upper()


class YtDlpService:
    """Service to extract and normalize video metadata using yt-dlp."""

    def __init__(self):
        self.ydl_opts: Dict[str, Any] = {
            "quiet": True,
            "no_warnings": True,
            "skip_download": True,
            "extract_flat": False,
            "socket_timeout": 15,
        }

    def extract_info(self, url: str) -> VideoInfo:
        """Extract metadata and return clean normalized format choices."""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
        except yt_dlp.utils.DownloadError as exc:
            msg = str(exc)
            if "Private video" in msg:
                raise ValueError("This video is private and cannot be downloaded.")
            if "Video unavailable" in msg or "not available" in msg:
                raise ValueError("This video is unavailable or has been removed.")
            if "Sign in" in msg or "bot" in msg.lower():
                raise ValueError("YouTube requires authentication or flagged this request. Please try another video.")
            if "age" in msg.lower() and "restricted" in msg.lower():
                raise ValueError("This video is age-restricted and cannot be processed.")
            logger.warning("yt-dlp extraction error: %s", msg)
            raise ValueError("Could not retrieve video information. Please verify the URL.")
        except Exception as exc:
            logger.error("Unexpected extraction error: %s", exc)
            raise ValueError("An error occurred while fetching video details.")

        if not info:
            raise ValueError("No video information could be retrieved for this URL.")

        return self._normalize_info(info)

    def _normalize_info(self, info: Dict[str, Any]) -> VideoInfo:
        video_id = info.get("id", "")
        title = info.get("title", "Untitled Video")
        thumbnail = info.get("thumbnail") or (info.get("thumbnails")[-1]["url"] if info.get("thumbnails") else "")
        duration = int(info.get("duration") or 0)
        uploader = info.get("uploader") or info.get("channel") or "Unknown Creator"
        uploader_url = info.get("uploader_url") or info.get("channel_url")
        view_count = info.get("view_count")

        raw_formats = info.get("formats", [])
        video_formats, audio_formats = self._normalize_formats(raw_formats, duration)

        best_video = video_formats[0].quality if video_formats else "N/A"
        best_audio = audio_formats[0].quality if audio_formats else "N/A"

        return VideoInfo(
            id=video_id,
            title=title,
            thumbnail=thumbnail,
            duration=duration,
            formatted_duration=format_duration(duration),
            uploader=uploader,
            uploader_url=uploader_url,
            view_count=view_count,
            best_video_quality=best_video,
            best_audio_quality=best_audio,
            video_formats=video_formats,
            audio_formats=audio_formats,
        )

    def _normalize_formats(
        self, formats: List[Dict[str, Any]], duration: int
    ) -> Tuple[List[FormatItem], List[FormatItem]]:
        """Group and normalize formats into clear human choices."""
        # Find best audio stream for filesize calculation
        best_audio_size: Optional[int] = None
        for f in formats:
            if f.get("vcodec") == "none" and f.get("acodec") != "none":
                sz = f.get("filesize") or f.get("filesize_approx")
                if sz and (best_audio_size is None or sz > best_audio_size):
                    best_audio_size = sz
        if not best_audio_size and duration > 0:
            # Fallback estimate: ~128 kbps audio
            best_audio_size = int(128 * 1000 * duration / 8)

        # 1. Group video streams by height (resolution)
        # We target standard tiers: 2160, 1440, 1080, 720, 480, 360
        resolution_tiers = [2160, 1440, 1080, 720, 480, 360]
        # Keep best format for each resolution tier
        best_by_tier: Dict[int, Dict[str, Any]] = {}

        for f in formats:
            vcodec = f.get("vcodec")
            if not vcodec or vcodec == "none":
                continue
            height = f.get("height")
            if not height or height < 144:
                continue

            # Match to closest resolution tier
            closest_tier = min(resolution_tiers, key=lambda t: abs(t - height))
            # Only match if height is reasonably close to standard tier (within 15%)
            if abs(closest_tier - height) > (closest_tier * 0.20) and height not in resolution_tiers:
                closest_tier = height

            current = best_by_tier.get(closest_tier)
            if not current:
                best_by_tier[closest_tier] = f
            else:
                # Prefer H.264/AVC for maximum device compatibility and stability, or higher tbr/bitrate
                cur_vcodec = str(current.get("vcodec", "")).lower()
                new_vcodec = str(vcodec).lower()
                cur_is_h264 = "avc1" in cur_vcodec or "h264" in cur_vcodec
                new_is_h264 = "avc1" in new_vcodec or "h264" in new_vcodec
                
                cur_tbr = current.get("tbr") or 0
                new_tbr = f.get("tbr") or 0

                # If current is not H264 and new is H264, switch
                if new_is_h264 and not cur_is_h264:
                    best_by_tier[closest_tier] = f
                elif new_is_h264 == cur_is_h264 and new_tbr > cur_tbr:
                    best_by_tier[closest_tier] = f

        video_items: List[FormatItem] = []
        for tier in sorted(best_by_tier.keys(), reverse=True):
            f = best_by_tier[tier]
            height = f.get("height") or tier
            width = f.get("width")
            fps = f.get("fps")
            vcodec = clean_codec_name(f.get("vcodec"))
            ext = "mp4"

            # Label resolution
            if height >= 2160:
                quality_label = f"{height}p (4K)"
            elif height >= 1440:
                quality_label = f"{height}p (2K)"
            else:
                quality_label = f"{height}p"

            # Filesize calculation
            f_size = f.get("filesize")
            f_approx = f.get("filesize_approx")
            is_video_only = f.get("acodec") == "none"

            total_size: Optional[int] = None
            is_approx = False

            if f_size:
                total_size = f_size + (best_audio_size if is_video_only and best_audio_size else 0)
                is_approx = is_video_only
            elif f_approx:
                total_size = f_approx + (best_audio_size if is_video_only and best_audio_size else 0)
                is_approx = True
            elif f.get("tbr") and duration > 0:
                # Estimate from bitrate
                total_size = int((f["tbr"] * 1000 * duration) / 8) + (best_audio_size if is_video_only and best_audio_size else 0)
                is_approx = True

            if total_size and total_size > 0:
                size_str = f"~{format_bytes(total_size)}" if is_approx else format_bytes(total_size)
            else:
                size_str = "Size calculated during download"

            desc = "Video + Audio merged (playable MP4)" if is_video_only else "Direct Video + Audio (MP4)"

            video_items.append(
                FormatItem(
                    format_id=str(f["format_id"]),
                    type="video",
                    quality=quality_label,
                    height=height,
                    width=width,
                    fps=fps,
                    codec=vcodec,
                    ext=ext,
                    audio_merged=is_video_only,
                    filesize=total_size if not is_approx else None,
                    filesize_approx=total_size if is_approx else None,
                    formatted_size=size_str,
                    bitrate_kbps=int(f.get("tbr")) if f.get("tbr") else None,
                    description=desc,
                )
            )

        # 2. Group audio streams
        audio_items: List[FormatItem] = []
        audio_seen: Dict[int, Dict[str, Any]] = {}

        for f in formats:
            if f.get("vcodec") != "none" or not f.get("acodec") or f.get("acodec") == "none":
                continue

            abr = f.get("abr") or f.get("tbr")
            if not abr or abr <= 0:
                continue

            abr_int = int(round(abr))
            # Bucket into clean bitrates: e.g., 320, 256, 160, 128, 96, 64, 48
            standard_bitrates = [320, 256, 192, 160, 128, 96, 64, 48]
            closest_abr = min(standard_bitrates, key=lambda b: abs(b - abr_int))

            cur = audio_seen.get(closest_abr)
            if not cur or (f.get("filesize") or 0) > (cur.get("filesize") or 0):
                audio_seen[closest_abr] = f

        # If audio_seen is empty, look for any audio-only format
        if not audio_seen:
            for f in formats:
                if f.get("vcodec") == "none" and f.get("acodec") != "none":
                    audio_seen[128] = f
                    break

        sorted_bitrates = sorted(audio_seen.keys(), reverse=True)
        for idx, abr_key in enumerate(sorted_bitrates):
            f = audio_seen[abr_key]
            acodec = clean_codec_name(f.get("acodec"))
            ext = "m4a" if f.get("ext") == "m4a" else "mp3"
            
            quality_label = "Best Audio" if idx == 0 else f"{abr_key} kbps"

            f_size = f.get("filesize")
            f_approx = f.get("filesize_approx")
            if not f_size and not f_approx and duration > 0:
                f_approx = int((abr_key * 1000 * duration) / 8)

            chosen_size = f_size or f_approx
            is_approx = f_size is None and f_approx is not None
            if chosen_size and chosen_size > 0:
                size_str = f"~{format_bytes(chosen_size)}" if is_approx else format_bytes(chosen_size)
            else:
                size_str = "Size calculated during download"

            audio_items.append(
                FormatItem(
                    format_id=str(f["format_id"]),
                    type="audio",
                    quality=quality_label,
                    height=None,
                    width=None,
                    fps=None,
                    codec=acodec,
                    ext=ext,
                    audio_merged=False,
                    filesize=f_size,
                    filesize_approx=f_approx,
                    formatted_size=size_str,
                    bitrate_kbps=abr_key,
                    description=f"Audio track only ({acodec} / {ext.upper()})",
                )
            )

        return video_items, audio_items


ytdlp_service = YtDlpService()
