import asyncio
import logging
import shutil
import time
from pathlib import Path
from typing import Optional

from ..config import settings

logger = logging.getLogger(__name__)


class CleanupService:
    """Service to automatically purge ephemeral job directories and files."""

    def __init__(self):
        self._task: Optional[asyncio.Task] = None

    def delete_job_files(self, job_id: str) -> bool:
        """Safely delete a job directory and its contents."""
        try:
            job_dir = Path(settings.DOWNLOAD_DIR) / job_id
            if job_dir.exists() and job_dir.is_dir():
                shutil.rmtree(job_dir, ignore_errors=True)
                logger.info("Purged job directory for %s", job_id)
                return True
        except Exception as exc:
            logger.error("Failed to delete job directory for %s: %s", job_id, exc)
        return False

    async def run_periodic_cleanup(self):
        """Continuously clean up stale jobs older than JOB_TTL_SECONDS."""
        logger.info("Starting periodic cleanup worker (interval=%ss, TTL=%ss)",
                    settings.CLEANUP_INTERVAL_SECONDS, settings.JOB_TTL_SECONDS)
        
        while True:
            try:
                await asyncio.sleep(settings.CLEANUP_INTERVAL_SECONDS)
                self._sweep_stale_jobs()
            except asyncio.CancelledError:
                logger.info("Cleanup loop cancelled")
                break
            except Exception as exc:
                logger.error("Error during stale job sweep: %s", exc)

    def _sweep_stale_jobs(self):
        root = Path(settings.DOWNLOAD_DIR)
        if not root.exists():
            return

        now = time.time()
        for item in root.iterdir():
            if not item.is_dir():
                continue
            try:
                mtime = item.stat().st_mtime
                if now - mtime > settings.JOB_TTL_SECONDS:
                    shutil.rmtree(item, ignore_errors=True)
                    logger.info("Purged expired job directory %s (age=%.1fs)", item.name, now - mtime)
            except Exception as e:
                logger.warning("Could not sweep item %s: %e", item.name, e)

    def start(self):
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self.run_periodic_cleanup())

    def stop(self):
        if self._task and not self._task.done():
            self._task.cancel()


cleanup_service = CleanupService()
