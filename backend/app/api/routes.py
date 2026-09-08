import asyncio
import logging
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi.responses import FileResponse

from ..config import settings
from ..models.schemas import (
    AnalyzeRequest,
    DownloadRequest,
    JobResponse,
    ProgressResponse,
    VideoInfo,
)
from ..services.cleanup_service import cleanup_service
from ..services.job_manager import job_manager
from ..services.ytdlp_service import ytdlp_service
from ..utils.formatting import format_bytes, format_eta, format_speed
from ..utils.security import sanitize_filename, validate_youtube_url

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Downloader"])


@router.post("/analyze", response_model=VideoInfo)
async def analyze_video(req: AnalyzeRequest):
    """Analyze YouTube URL and retrieve clean normalized format options."""
    url = req.url.strip()
    if not validate_youtube_url(url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid YouTube video URL.",
        )

    try:
        loop = asyncio.get_running_loop()
        video_info = await loop.run_in_executor(None, ytdlp_service.extract_info, url)
        return video_info
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )
    except Exception as exc:
        logger.error("Analyze video error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve video metadata. Please try again.",
        )


@router.post("/download", response_model=JobResponse)
async def start_download(req: DownloadRequest, background_tasks: BackgroundTasks):
    """Queue a download job for processing."""
    url = req.url.strip()
    if not validate_youtube_url(url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid YouTube video URL.",
        )

    if not req.format_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A valid format selection is required.",
        )

    job = job_manager.create_job(
        url=url,
        format_id=req.format_id,
        media_type=req.type,
        quality_label=req.quality_label,
    )

    # Launch background job worker
    background_tasks.add_task(job_manager.run_job, job.job_id)

    return JobResponse(
        job_id=job.job_id,
        status=job.status,
        message="Your download has been queued.",
    )


@router.get("/progress/{job_id}", response_model=ProgressResponse)
async def get_progress(job_id: str):
    """Retrieve real-time download & merging progress for a job."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or expired.",
        )

    formatted_dl = format_bytes(job.downloaded_bytes)
    formatted_tot = format_bytes(job.total_bytes) if job.total_bytes > 0 else "--"
    formatted_sz = format_bytes(job.filesize) if job.filesize else None

    return ProgressResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        message=job.message,
        downloaded_bytes=job.downloaded_bytes,
        total_bytes=job.total_bytes,
        formatted_downloaded=formatted_dl,
        formatted_total=formatted_tot,
        speed=job.speed,
        formatted_speed=format_speed(job.speed),
        eta=job.eta,
        formatted_eta=format_eta(job.eta),
        filename=job.filename,
        filesize=job.filesize,
        formatted_filesize=formatted_sz,
        error=job.error,
    )


async def delayed_cleanup(job_id: str, delay_seconds: int = 120):
    """Clean up job files after giving browser ample time to finish saving."""
    await asyncio.sleep(delay_seconds)
    cleanup_service.delete_job_files(job_id)


@router.get("/download/{job_id}")
async def download_file(job_id: str, background_tasks: BackgroundTasks):
    """Serve the completed media file and schedule ephemeral cleanup."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Download job not found or expired.",
        )

    if job.status != "complete" or not job.filepath:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This file is not ready for download yet.",
        )

    file_path = Path(job.filepath)
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="The requested file is no longer available on the server.",
        )

    job.is_downloaded = True
    safe_name = sanitize_filename(job.filename or file_path.name)
    media_type = "video/mp4" if safe_name.endswith(".mp4") else "audio/mpeg"

    # Schedule deferred cleanup so file isn't deleted while streaming
    background_tasks.add_task(delayed_cleanup, job_id, delay_seconds=180)

    return FileResponse(
        path=str(file_path),
        filename=safe_name,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{safe_name}"',
            "Cache-Control": "no-cache",
        },
    )
