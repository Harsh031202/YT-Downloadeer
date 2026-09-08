from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    url: str = Field(..., description="YouTube video URL")


class FormatItem(BaseModel):
    format_id: str
    type: Literal["video", "audio"]
    quality: str
    height: Optional[int] = None
    width: Optional[int] = None
    fps: Optional[int] = None
    codec: str
    ext: str
    audio_merged: bool = False
    filesize: Optional[int] = None
    filesize_approx: Optional[int] = None
    formatted_size: str
    bitrate_kbps: Optional[int] = None
    description: str


class VideoInfo(BaseModel):
    id: str
    title: str
    thumbnail: str
    duration: int
    formatted_duration: str
    uploader: str
    uploader_url: Optional[str] = None
    view_count: Optional[int] = None
    best_video_quality: Optional[str] = None
    best_audio_quality: Optional[str] = None
    video_formats: List[FormatItem]
    audio_formats: List[FormatItem]


class DownloadRequest(BaseModel):
    url: str
    format_id: str
    type: Literal["video", "audio"]
    quality_label: Optional[str] = None


class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str


class ProgressResponse(BaseModel):
    job_id: str
    status: str  # "queued", "downloading_video", "downloading_audio", "merging", "finalizing", "complete", "error"
    progress: float
    message: str
    downloaded_bytes: int
    total_bytes: int
    formatted_downloaded: str
    formatted_total: str
    speed: float
    formatted_speed: str
    eta: int
    formatted_eta: str
    filename: Optional[str] = None
    filesize: Optional[int] = None
    formatted_filesize: Optional[str] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = "ok"
    ffmpeg_available: bool = True
    ffmpeg_version: Optional[str] = None
