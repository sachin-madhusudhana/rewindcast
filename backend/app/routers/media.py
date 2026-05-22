"""Media upload and management endpoints."""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.database import get_db
from app.db_models import Media
from app.models import MediaResponse, MediaListResponse, MediaUrlRequest

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/media", tags=["media"])

ALLOWED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".mp4", ".webm", ".aac"}


def _get_audio_duration(file_path: Path) -> float | None:
    """Get audio duration in seconds using pydub, with ffprobe fallback."""
    try:
        from pydub import AudioSegment

        audio = AudioSegment.from_file(str(file_path))
        return len(audio) / 1000.0  # pydub returns ms
    except Exception as e:
        logger.warning("pydub duration detection failed: %s", e)
        # Fallback: try ffprobe directly
        try:
            result = subprocess.run(
                [
                    "ffprobe",
                    "-v", "quiet",
                    "-show_entries", "format=duration",
                    "-of", "csv=p=0",
                    str(file_path),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0 and result.stdout.strip():
                return float(result.stdout.strip())
        except Exception as e2:
            logger.warning("ffprobe fallback failed: %s", e2)
    return None


@router.post("/upload", response_model=MediaResponse)
async def upload_media(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_db),
) -> Media:
    """Upload an audio or video file."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # Save file
    media_id = str(uuid4())
    safe_name = f"{media_id}{ext}"
    media_dir = settings.MEDIA_DIR
    media_dir.mkdir(parents=True, exist_ok=True)
    file_path = media_dir / safe_name

    content = await file.read()
    file_path.write_bytes(content)

    # Get duration
    duration = _get_audio_duration(file_path)

    # Create DB record
    title = Path(file.filename).stem.replace("_", " ").replace("-", " ").title()
    media = Media(
        id=media_id,
        title=title,
        filename=safe_name,
        duration_seconds=duration,
    )
    db.add(media)
    await db.flush()
    await db.refresh(media)

    logger.info("Uploaded media: %s (%s, %.1fs)", title, safe_name, duration or 0)
    return media


@router.post("/url", response_model=MediaResponse)
async def ingest_from_url(
    body: MediaUrlRequest,
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_db),
) -> Media:
    """Download audio from a YouTube or podcast URL using yt-dlp."""
    import asyncio

    media_id = str(uuid4())
    media_dir = settings.MEDIA_DIR
    media_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(media_dir / f"{media_id}.%(ext)s")

    cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "5",  # medium quality, smaller file
        "--output", output_template,
        "--no-playlist",
        "--quiet",
        body.url,
    ]

    logger.info("Downloading audio from URL: %s", body.url)
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode().strip() if stderr else "Unknown error"
            raise HTTPException(
                status_code=400,
                detail=f"Failed to download audio: {error_msg}",
            )
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="yt-dlp is not installed. Run: pip install yt-dlp",
        )

    # Find the downloaded file
    mp3_path = media_dir / f"{media_id}.mp3"
    if not mp3_path.exists():
        # Check for other extensions
        candidates = list(media_dir.glob(f"{media_id}.*"))
        if not candidates:
            raise HTTPException(status_code=500, detail="Download succeeded but file not found")
        mp3_path = candidates[0]

    # Get title from yt-dlp
    title = f"Downloaded Audio {media_id[:8]}"
    try:
        title_proc = await asyncio.create_subprocess_exec(
            "yt-dlp", "--get-title", "--no-playlist", body.url,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, _ = await title_proc.communicate()
        if title_proc.returncode == 0 and stdout:
            title = stdout.decode().strip()[:512]
    except Exception:
        pass

    duration = _get_audio_duration(mp3_path)

    media = Media(
        id=media_id,
        title=title,
        filename=mp3_path.name,
        duration_seconds=duration,
    )
    db.add(media)
    await db.flush()
    await db.refresh(media)

    logger.info("Ingested from URL: %s (%s)", title, mp3_path.name)
    return media


@router.get("", response_model=list[MediaResponse])
async def list_media(
    db: AsyncSession = Depends(get_db),
) -> list[Media]:
    """List all uploaded media."""
    result = await db.execute(select(Media).order_by(Media.created_at.desc()))
    return list(result.scalars().all())


@router.get("/{media_id}", response_model=MediaResponse)
async def get_media(
    media_id: str,
    db: AsyncSession = Depends(get_db),
) -> Media:
    """Get a single media item by ID."""
    media = await db.get(Media, media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    return media


@router.get("/{media_id}/file")
async def get_media_file(
    media_id: str,
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Stream the media file for playback."""
    media = await db.get(Media, media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    file_path = settings.MEDIA_DIR / media.filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Media file not found on disk")

    # Determine content type
    ext = file_path.suffix.lower()
    content_types = {
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
        ".ogg": "audio/ogg",
        ".flac": "audio/flac",
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".aac": "audio/aac",
    }
    content_type = content_types.get(ext, "application/octet-stream")

    return FileResponse(
        path=file_path,
        media_type=content_type,
        filename=media.filename,
    )
