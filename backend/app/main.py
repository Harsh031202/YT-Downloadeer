import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .api.health import router as health_router
from .api.routes import router as api_router
from .config import settings
from .services.cleanup_service import cleanup_service
from .services.ffmpeg_service import ffmpeg_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("yt_downloader")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup sequence
    logger.info("Starting YouTube Downloader service...")
    has_ffmpeg, version = ffmpeg_service.check_availability()
    if has_ffmpeg:
        logger.info("FFmpeg operational: %s", version)
    else:
        logger.warning("FFmpeg NOT detected. Merging & audio conversion will fail!")

    # Start periodic file cleanup task
    cleanup_service.start()
    logger.info("Temporary files directory: %s", settings.DOWNLOAD_DIR)

    yield

    # Shutdown sequence
    logger.info("Shutting down YouTube Downloader service...")
    cleanup_service.stop()


app = FastAPI(
    title="YouTube Downloader API",
    description="High-performance, developer-grade media downloader backend powered by yt-dlp & FFmpeg.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routers
app.include_router(health_router)
app.include_router(api_router)

# Production Frontend SPA serving
# Determine if frontend dist directory exists (Render or production container build)
DIST_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if DIST_DIR.exists() and (DIST_DIR / "index.html").exists():
    logger.info("Mounting frontend SPA from: %s", DIST_DIR)
    app.mount("/assets", StaticFiles(directory=str(DIST_DIR / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # If specific file exists in dist, serve it
        target_file = DIST_DIR / full_path
        if full_path and target_file.exists() and target_file.is_file():
            return FileResponse(str(target_file))
        # Otherwise fallback to index.html for client-side routing
        return FileResponse(str(DIST_DIR / "index.html"))
else:
    logger.info("Frontend dist folder not found at %s. Running in API-only mode.", DIST_DIR)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
