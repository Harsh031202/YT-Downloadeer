# StreamForge — High-Fidelity YouTube Media Downloader

StreamForge is a modern, developer-grade YouTube media extraction web service built with **FastAPI**, **yt-dlp**, and **FFmpeg** on the backend, paired with a high-performance **React**, **TypeScript**, **Tailwind CSS**, and **Framer Motion** frontend.

Designed specifically for containerized deployment on **Render**, StreamForge features real-time stream demuxing and merging, adaptive format normalization, humanized progress telemetry, ephemeral storage guarantees, and a cinematic typing hero experience.

---

## ⚡ Core Features

- **Cinematic Typing Hero**: Realistic natural typing animation that smoothly transforms into the permanent top navigation via spring physics.
- **True Backend Processing**: Real `yt-dlp` extraction and format normalization—never simulated or faked.
- **Smart Stream Merging**: Automatically combines modern high-resolution DASH video-only streams (4K/2K/1080p/720p) with the highest-bitrate audio streams using FFmpeg.
- **Dedicated Audio Extraction**: Direct download or conversion to MP3/M4A with explicit bitrate options based on source audio quality.
- **Accurate Size Calculation**: Combines video and audio stream sizes dynamically to show accurate output size estimates before downloading.
- **Anti-Stuck Progress UI**: Real progress reporting (percentage, downloaded/total MB, speed, ETA) with distinct phase transitions (*"Downloading video..."* → *"Combining video and audio..."* → *"Putting the finishing touches..."*) to prevent the progress bar from stalling at 100%.
- **Ephemeral Storage & Auto-Cleanup**: Job directories are isolated (`/tmp/ytdlp_jobs/<job_id>`), served safely to the user, and automatically cleaned up after download or purged by a background TTL garbage collector.
- **Render-First Architecture**: Single multi-stage Docker build running on Render's web service with deterministic OS-level FFmpeg support.

---

## 🛠 Tech Stack

- **Backend**: Python 3.12/3.14, FastAPI, Uvicorn (ASGI), Pydantic V2, yt-dlp, FFmpeg
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Framer Motion, Lucide React, canvas-confetti
- **DevOps**: Docker (multi-stage build), Docker Compose, Render Blueprint (`render.yaml`)

---

## 🏗 Architecture & Stream Logic

```
User Browser
    │
    ▼ (POST /api/analyze)
FastAPI Backend ───► yt-dlp Service (Extract Metadata & Formats)
    │                       │
    ▼ (Returns VideoInfo)   ▼ (Format Normalization: 4K, 1080p, Best Audio, etc.)
Format Selection UI
    │
    ▼ (POST /api/download)
JobManager ───► Concurrency Semaphore (Queue slot)
    │
    ├───► Worker Thread ───► yt-dlp (Download Video & Audio Streams)
    │                             │
    │                             ▼
    │                        FFmpeg (Merge into playable MP4 / Extract MP3)
    │                             │
    │                             ▼
    │                        Ephemeral Output (/tmp/ytdlp_jobs/<job_id>)
    │
    ▼ (GET /api/progress/<job_id>)
Real-time Telemetry (Percentage, Speed, ETA, Status)
    │
    ▼ (GET /api/download/<job_id>)
File Stream to Browser ───► Background Cleanup Task (Purges ephemeral files)
```

---

## 🚀 Local Development

### Prerequisites
1. **Python 3.11+** installed.
2. **Node.js 20+** and `npm` installed.
3. **FFmpeg & FFprobe** installed locally and added to your system `PATH`:
   - **Windows**: Install via `winget install Gyan.FFmpeg` or download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) and add the `bin` directory to your `Path` environment variable.
   - **macOS**: `brew install ffmpeg`
   - **Linux (Ubuntu/Debian)**: `sudo apt update && sudo apt install -y ffmpeg`

Verify FFmpeg is recognized in your terminal:
```bash
ffmpeg -version
ffprobe -version
```

---

### 1. Backend Setup

From the repository root:
```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Start the FastAPI server
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend API is now running at `http://127.0.0.1:8000`. You can inspect the Swagger docs at `http://127.0.0.1:8000/docs` and test `/health`.

---

### 2. Frontend Setup

In a separate terminal:
```bash
cd frontend

# Install Node dependencies
npm install

# Start the Vite development server (with proxy to backend)
npm run dev
```
Open `http://localhost:5173` in your browser. Vite proxies all `/api` and `/health` requests directly to `http://localhost:8000`.

---

### 3. Running Backend Automated Tests

StreamForge includes automated tests for security (URL validation, path traversal prevention, filename sanitization), duration/byte formatting, format normalization, and API routes:
```bash
python -m pytest backend/tests -v
```

---

## 🐳 Docker (Local Container Testing)

To test the container exactly as it will run on Render:

```bash
# Build and run with docker-compose
docker-compose up --build
```
Or directly with the Docker CLI:
```bash
docker build -t streamforge .
docker run -p 10000:10000 -e PORT=10000 streamforge
```
Visit `http://localhost:10000`.

---

## ☁️ Render Deployment Guide

StreamForge is engineered specifically for **Render Web Services** using Docker.

> [!IMPORTANT]
> **Render Filesystem Reality**: Render web services run with an ephemeral filesystem. Any files stored on disk will disappear when the service restarts or deploys. StreamForge is built around this exact architecture: media files are treated as ephemeral artifacts stored in `/tmp/ytdlp_jobs/<job_id>`, delivered directly to the user, and purged immediately after download (or after 15 minutes by the background sweeper).

### Option A: Deploy via Render Blueprint (`render.yaml`) (Recommended)

1. Push your code to a Git repository (GitHub or GitLab).
2. Log into the [Render Dashboard](https://dashboard.render.com).
3. Click **New +** → **Blueprint**.
4. Select your repository. Render will automatically detect [`render.yaml`](render.yaml) and configure the Docker web service with:
   - **Runtime**: Docker
   - **Health Check Path**: `/health`
   - **Port**: `10000` (Render's default)
   - **Auto-Deploy**: Enabled on Git push

---

### Option B: Manual Web Service Setup on Render

1. Go to [dashboard.render.com](https://dashboard.render.com) and click **New +** → **Web Service**.
2. Connect your Git repository.
3. Set the following options:
   - **Name**: `streamforge-downloader`
   - **Language / Runtime**: `Docker`
   - **Branch**: `main`
   - **Region**: Oregon (or your preferred region)
   - **Plan**: `Starter` (recommended: 512 MB – 1 GB RAM ensures ample memory for FFmpeg stream merging)
4. Under **Health Check Path**, enter:
   ```
   /health
   ```
5. Under **Environment Variables**, add:
   | Key | Value | Description |
   |-----|-------|-------------|
   | `PORT` | `10000` | Web service listening port (Render standard) |
   | `MAX_CONCURRENT_DOWNLOADS` | `2` | Protects CPU/RAM from overload |
   | `JOB_TIMEOUT_SECONDS` | `600` | Max job processing time (10 mins) |
   | `JOB_TTL_SECONDS` | `900` | Job directory expiration (15 mins) |
   | `CLEANUP_INTERVAL_SECONDS` | `180` | Background garbage collection frequency |
   | `DOWNLOAD_DIR` | `/tmp/ytdlp_jobs` | Ephemeral disk scratch directory |
6. Click **Create Web Service**. Render will build the Docker container (compiling the frontend and installing FFmpeg) and launch the service.

---

## 🔧 Maintenance: Updating yt-dlp

YouTube frequently updates its internal player algorithms and video delivery mechanisms. To update `yt-dlp` to the latest release:

1. Update `backend/requirements.txt`:
   ```txt
   yt-dlp>=2025.02.19
   ```
2. In your local environment:
   ```bash
   pip install --upgrade yt-dlp
   ```
3. Commit and push the changes. Render will rebuild the Docker container with the latest `yt-dlp` release.

---

## ⚠️ Common Deployment & Runtime Notes

1. **Memory Allocation**: Merging high-bitrate 4K streams with FFmpeg requires sufficient memory. A Render `Starter` plan (512MB RAM) or `Standard` (1GB–2GB RAM) is recommended. If memory limits are exceeded on very large video files, the concurrency limit (`MAX_CONCURRENT_DOWNLOADS=1` or `2`) ensures processes run sequentially.
2. **YouTube Bot Challenges / IP Flagging**: Data center IP addresses (including those of cloud providers like AWS, GCP, and Render) may occasionally encounter YouTube bot verification challenges. If a video fails to download on a cloud provider, yt-dlp will return a human-readable message indicating that YouTube flagged the data center IP, prompting the user to try another link.
3. **No External Serverless Dependencies**: This application does NOT require Vercel, Netlify, or serverless functions. It runs as a self-contained, long-running Linux container service with complete control over the filesystem and subprocess execution.

---

## 📄 License & Fair Use

StreamForge is provided for personal and educational use. Users are solely responsible for ensuring they have lawful permission or authorization to download media content in compliance with YouTube's Terms of Service and applicable copyright laws.
