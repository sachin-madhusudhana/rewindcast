export interface MediaItem {
  id: string;
  title: string;
  filename: string;
  duration_seconds: number;
  created_at: string;
}

export interface RecapRequest {
  media_id: string;
  listened_until_seconds: number;
  style?: string;
  max_words?: number;
}

export interface RecapResponse {
  id: string;
  media_id: string;
  summary_text: string;
  key_points: string[];
  audio_url: string;
  estimated_listen_seconds: number;
  created_at: string;
}

export type UploadResponse = MediaItem;

// ── Audiobookshelf ───────────────────────────────────────────

export interface ABSStatusResponse {
  connected: boolean;
  server_url: string | null;
  username: string | null;
  error: string | null;
}

export interface ABSLibrary {
  id: string;
  name: string;
  media_type: string;
  item_count: number;
}

export interface ABSItemSummary {
  id: string;
  title: string;
  author: string | null;
  cover_url: string | null;
  duration_seconds: number;
  current_time: number;
  progress_percent: number;
  media_type: string;
  episode_title: string | null;
}

export interface ABSRecapRequest {
  listened_until_seconds?: number | null;
  episode_id?: string | null;
  style?: string;
}
