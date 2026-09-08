import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "ffmpeg_available" in data


@pytest.mark.asyncio
async def test_analyze_invalid_url():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/api/analyze", json={"url": "https://notyoutube.com/watch?v=123"})
        assert response.status_code == 400
        assert "valid YouTube video URL" in response.json()["detail"]


@pytest.mark.asyncio
async def test_progress_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/progress/nonexistent-job-id")
        assert response.status_code == 404
