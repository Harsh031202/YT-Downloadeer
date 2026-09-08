# Stage 1: Build the React + TypeScript frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci || npm install

COPY frontend/ ./
RUN npm run build

# Stage 2: Production Python runtime with system FFmpeg
FROM python:3.12-slim AS runtime

# Install system dependencies: FFmpeg, curl (for health checks), and ca-certificates
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Install Python requirements
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend application code
COPY backend/ ./backend/

# Copy built frontend assets from builder stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Set up runtime directories & permissions
RUN mkdir -p /tmp/ytdlp_jobs && chmod 777 /tmp/ytdlp_jobs

# Default environment configuration
ENV HOST=0.0.0.0 \
    PORT=10000 \
    DOWNLOAD_DIR=/tmp/ytdlp_jobs \
    MAX_CONCURRENT_DOWNLOADS=2 \
    JOB_TIMEOUT_SECONDS=600 \
    CLEANUP_INTERVAL_SECONDS=180 \
    JOB_TTL_SECONDS=900 \
    PYTHONUNBUFFERED=1

# Expose Render default web service port
EXPOSE 10000

# Health check using the /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:${PORT:-10000}/health || exit 1

# Start the unified FastAPI ASGI server binding to 0.0.0.0 and $PORT
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-10000} --workers 1 --log-level info"]
