from fastapi import APIRouter
from ..models.schemas import HealthResponse
from ..services.ffmpeg_service import ffmpeg_service

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for Render and monitoring tools."""
    available, version = ffmpeg_service.check_availability()
    return HealthResponse(
        status="ok",
        ffmpeg_available=available,
        ffmpeg_version=version,
    )
