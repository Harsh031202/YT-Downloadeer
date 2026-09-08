import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional

from ..config import settings
from .download_service import download_service

logger = logging.getLogger(__name__)


@dataclass
class Job:
    job_id: str
    url: str
    format_id: str
    media_type: str
    quality_label: str = ""
    status: str = "queued"  # queued, downloading_video, downloading_audio, merging, finalizing, complete, error
    progress: float = 0.0
    message: str = "Preparing your download..."
    downloaded_bytes: int = 0
    total_bytes: int = 0
    speed: float = 0.0
    eta: int = 0
    filename: Optional[str] = None
    filepath: Optional[str] = None
    filesize: Optional[int] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    is_downloaded: bool = False


class JobManager:
    """Manages active and historical download jobs with concurrency control."""

    def __init__(self):
        self._jobs: Dict[str, Job] = {}
        self._semaphore: Optional[asyncio.Semaphore] = None
        self._lock = asyncio.Lock()

    def _get_semaphore(self) -> asyncio.Semaphore:
        if self._semaphore is None:
            self._semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_DOWNLOADS)
        return self._semaphore

    def create_job(self, url: str, format_id: str, media_type: str, quality_label: Optional[str] = None) -> Job:
        job_id = uuid.uuid4().hex[:12]
        job = Job(
            job_id=job_id,
            url=url,
            format_id=format_id,
            media_type=media_type,
            quality_label=quality_label or "",
            status="queued",
            message="Waiting for server capacity...",
        )
        self._jobs[job_id] = job
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        return self._jobs.get(job_id)

    async def run_job(self, job_id: str):
        """Worker task processing the job within concurrency limits."""
        job = self.get_job(job_id)
        if not job:
            return

        sem = self._get_semaphore()
        logger.info("Job %s entering queue waiting for semaphore", job_id)

        try:
            async with sem:
                job.status = "downloading_video" if job.media_type == "video" else "downloading_audio"
                job.message = "Starting download..."
                job.updated_at = time.time()
                logger.info("Job %s acquired slot, starting download", job_id)

                def sync_progress_callback(update: dict):
                    # Progress hook executed from worker thread
                    job.status = update.get("status", job.status)
                    job.progress = update.get("progress", job.progress)
                    job.message = update.get("message", job.message)
                    if "downloaded_bytes" in update:
                        job.downloaded_bytes = update["downloaded_bytes"]
                    if "total_bytes" in update:
                        job.total_bytes = update["total_bytes"]
                    if "speed" in update:
                        job.speed = update["speed"]
                    if "eta" in update:
                        job.eta = update["eta"]
                    job.updated_at = time.time()

                # Run heavy download synchronously in thread pool
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(
                    None,
                    download_service.download,
                    job.job_id,
                    job.url,
                    job.format_id,
                    job.media_type,
                    sync_progress_callback,
                )

                job.filename = result["filename"]
                job.filepath = result["filepath"]
                job.filesize = result["filesize"]
                job.status = "complete"
                job.progress = 100.0
                job.message = "Your download is ready."
                job.completed_at = time.time()
                job.updated_at = time.time()
                logger.info("Job %s completed successfully: %s", job_id, job.filename)

        except asyncio.CancelledError:
            logger.warning("Job %s was cancelled", job_id)
            job.status = "error"
            job.error = "The download task was cancelled."
            job.message = "Download cancelled."
            job.updated_at = time.time()
        except Exception as exc:
            logger.error("Job %s failed with exception: %s", job_id, exc)
            job.status = "error"
            # Map exception to clean human error message
            err_text = str(exc)
            if "unavailable" in err_text.lower():
                human_msg = "This video or format is no longer available on YouTube."
            elif "private" in err_text.lower():
                human_msg = "This video is private."
            elif "disk" in err_text.lower() or "space" in err_text.lower():
                human_msg = "The server ran out of temporary storage space."
            elif "timeout" in err_text.lower():
                human_msg = "The connection timed out while downloading the stream."
            else:
                human_msg = "We couldn't process this video. Please check the link and try again."
            job.error = human_msg
            job.message = human_msg
            job.updated_at = time.time()


job_manager = JobManager()
