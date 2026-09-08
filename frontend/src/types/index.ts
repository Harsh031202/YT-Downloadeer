export type MediaType = 'video' | 'audio';

export interface FormatItem {
  format_id: string;
  type: MediaType;
  quality: string;
  height?: number | null;
  width?: number | null;
  fps?: number | null;
  codec: string;
  ext: string;
  audio_merged: boolean;
  filesize?: number | null;
  filesize_approx?: number | null;
  formatted_size: string;
  bitrate_kbps?: number | null;
  description: string;
}

export interface VideoInfo {
  id: string;
  title: string;
  thumbnail: string;
  duration: number;
  formatted_duration: string;
  uploader: string;
  uploader_url?: string | null;
  view_count?: number | null;
  best_video_quality?: string | null;
  best_audio_quality?: string | null;
  video_formats: FormatItem[];
  audio_formats: FormatItem[];
}

export type JobStatus =
  | 'queued'
  | 'downloading_video'
  | 'downloading_audio'
  | 'merging'
  | 'finalizing'
  | 'complete'
  | 'error';

export interface JobProgress {
  job_id: string;
  status: JobStatus;
  progress: number;
  message: string;
  downloaded_bytes: number;
  total_bytes: number;
  formatted_downloaded: string;
  formatted_total: string;
  speed: number;
  formatted_speed: string;
  eta: number;
  formatted_eta: string;
  filename?: string | null;
  filesize?: number | null;
  formatted_filesize?: string | null;
  error?: string | null;
}

export type AppPhase =
  | 'initial'
  | 'analyzing'
  | 'ready'
  | 'downloading'
  | 'processing'
  | 'complete'
  | 'error';
