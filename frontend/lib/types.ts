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
