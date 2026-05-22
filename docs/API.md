# RewindCast API Documentation

**Base URL**: `http://localhost:8000`

All endpoints return JSON. File streaming endpoints return binary data.

---

## Health Check

### `GET /api/health`

Check if the API is running.

**Response** `200 OK`
```json
{
  "status": "ok",
  "service": "rewindcast"
}
```

---

## Media

### `POST /api/media/upload`

Upload an audio or video file.

**Content-Type**: `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File | Yes | Audio/video file (MP3, WAV, M4A, OGG, FLAC, MP4, WebM, AAC) |

**Response** `200 OK`
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "My Podcast Episode",
  "filename": "a1b2c3d4-e5f6-7890-abcd-ef1234567890.mp3",
  "duration_seconds": 2700.5,
  "created_at": "2026-05-21T23:00:00Z"
}
```

**Errors**
- `400` — Unsupported file type or missing filename

---

### `POST /api/media/url`

Download and import audio from a YouTube or podcast URL.

**Content-Type**: `application/json`

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

**Response**: Same as upload endpoint.

**Errors**
- `400` — Failed to download (invalid URL, private video, etc.)
- `500` — `yt-dlp` not installed

> **Note**: This endpoint may take 30-60 seconds for long videos.

---

### `GET /api/media`

List all uploaded media, ordered by newest first.

**Response** `200 OK`
```json
[
  {
    "id": "a1b2c3d4-...",
    "title": "My Podcast",
    "filename": "a1b2c3d4-....mp3",
    "duration_seconds": 2700.5,
    "created_at": "2026-05-21T23:00:00Z"
  }
]
```

---

### `GET /api/media/{media_id}`

Get details for a single media item.

**Response** `200 OK` — Same schema as list items.

**Errors**
- `404` — Media not found

---

### `GET /api/media/{media_id}/file`

Stream the media file for playback.

**Response** — Binary audio/video file with appropriate `Content-Type` header.

**Errors**
- `404` — Media not found or file missing from disk

---

## Recap

### `POST /api/recap` ⭐

**The core product endpoint.** Generates a recap for a media item.

This endpoint orchestrates the full pipeline:
1. Transcribes the audio (cached after first run)
2. Extracts transcript for the listened range
3. Summarizes with Gemini (map-reduce for long content)
4. Generates TTS audio
5. Returns the recap

**Content-Type**: `application/json`

```json
{
  "media_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "listened_until_seconds": 900,
  "style": "conversational",
  "max_words": 300
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `media_id` | string | Yes | — | ID of the media item |
| `listened_until_seconds` | number | Yes | — | How far the user listened (seconds) |
| `style` | string | No | `"conversational"` | Recap narration style |
| `max_words` | integer | No | `300` | Target word count (50-2000) |

**Response** `200 OK`
```json
{
  "id": "recap_xyz789",
  "media_id": "a1b2c3d4-...",
  "summary_text": "Previously on this episode, the host kicked off by exploring how artificial intelligence is reshaping healthcare...",
  "key_points": [
    "AI diagnostics achieving 94% accuracy on mammograms",
    "Three key challenges: data quality, regulation, trust",
    "Stanford's new model could reduce false positives by 30%"
  ],
  "audio_url": "/api/recap/recap_xyz789/audio",
  "estimated_listen_seconds": 145,
  "created_at": "2026-05-21T23:00:00Z"
}
```

**Errors**
- `400` — Invalid `listened_until_seconds` or no content in range
- `404` — Media not found or file missing

> **Note**: First request for a media item includes transcription time
> (30-120 seconds depending on audio length and model size).
> Subsequent recaps for the same media reuse the cached transcript.

---

### `GET /api/recap/{recap_id}`

Retrieve a previously generated recap.

**Response** — Same schema as create endpoint.

---

### `GET /api/recap/{recap_id}/audio`

Stream the generated recap audio (MP3).

**Response** — Binary MP3 file.

**Errors**
- `404` — Recap not found or no audio generated

---

## Error Format

All errors follow this format:

```json
{
  "detail": "Human-readable error message"
}
```

Common HTTP status codes:
- `400` — Bad request (invalid input)
- `404` — Resource not found
- `422` — Validation error (Pydantic)
- `500` — Internal server error

---

## Rate Limiting

No rate limiting in the MVP. For production deployment, we recommend:
- 10 recap requests per minute per user
- 100 upload requests per hour per user
- Implement via API gateway (nginx, CloudFlare, etc.)
