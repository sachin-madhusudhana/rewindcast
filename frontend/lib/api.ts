import { MediaItem, RecapRequest, RecapResponse } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const body = await response.json();
      message = body.detail || body.message || message;
    } catch {
      // ignore parse errors
    }
    throw new ApiError(message, response.status);
  }
  return response.json() as Promise<T>;
}

export async function uploadMedia(file: File): Promise<MediaItem> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/api/media/upload`, {
    method: 'POST',
    body: formData,
  });

  return handleResponse<MediaItem>(response);
}

export async function uploadUrl(url: string): Promise<MediaItem> {
  const response = await fetch(`${API_BASE}/api/media/url`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });

  return handleResponse<MediaItem>(response);
}

export async function getMedia(id: string): Promise<MediaItem> {
  const response = await fetch(`${API_BASE}/api/media/${id}`);
  return handleResponse<MediaItem>(response);
}

export async function listMedia(): Promise<MediaItem[]> {
  const response = await fetch(`${API_BASE}/api/media`);
  return handleResponse<MediaItem[]>(response);
}

export function getMediaFileUrl(id: string): string {
  return `${API_BASE}/api/media/${id}/file`;
}

export async function generateRecap(request: RecapRequest): Promise<RecapResponse> {
  const response = await fetch(`${API_BASE}/api/recap`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  return handleResponse<RecapResponse>(response);
}

export function getRecapAudioUrl(id: string): string {
  return `${API_BASE}/api/recap/${id}/audio`;
}
