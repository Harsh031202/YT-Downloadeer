import { VideoInfo, JobProgress, MediaType } from '../types';

const API_BASE = '/api';

export async function analyzeVideo(url: string): Promise<VideoInfo> {
  const response = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    const message = errorData?.detail || 'Failed to analyze video. Please check the URL and try again.';
    throw new Error(message);
  }

  return response.json();
}

export async function startDownload(
  url: string,
  formatId: string,
  type: MediaType,
  qualityLabel?: string
): Promise<{ job_id: string; status: string }> {
  const response = await fetch(`${API_BASE}/download`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      url,
      format_id: formatId,
      type,
      quality_label: qualityLabel,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    const message = errorData?.detail || 'Failed to initiate download job.';
    throw new Error(message);
  }

  return response.json();
}

export async function getProgress(jobId: string): Promise<JobProgress> {
  const response = await fetch(`${API_BASE}/progress/${encodeURIComponent(jobId)}`);

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    const message = errorData?.detail || 'Failed to fetch job progress.';
    throw new Error(message);
  }

  return response.json();
}

export function getDownloadUrl(jobId: string): string {
  return `${API_BASE}/download/${encodeURIComponent(jobId)}`;
}
