"""Recap generation endpoints — the core product feature."""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.database import get_db
from app.db_models import Media, Transcript, Recap
from app.models import RecapRequest, RecapResponse
from app.services.transcriber import TranscriberService
from app.services.summarizer import SummarizerService
from app.services.tts import generate_recap_audio, estimate_listen_seconds

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/recap", tags=["recap"])

# Lazy-initialized services (created on first request)
_transcriber: TranscriberService | None = None
_summarizer: SummarizerService | None = None


def _get_transcriber(settings: Settings) -> TranscriberService:
    global _transcriber
    if _transcriber is None:
        _transcriber = TranscriberService(model_size=settings.WHISPER_MODEL_SIZE)
    return _transcriber


def _get_summarizer(settings: Settings) -> SummarizerService:
    global _summarizer
    if _summarizer is None:
        _summarizer = SummarizerService(api_key=settings.GEMINI_API_KEY)
    return _summarizer


def calculate_recap_params(listened_seconds: float) -> tuple[int, int]:
    """Calculate target max_words and number of key points based on listened time."""
    if listened_seconds <= 60:
        # For ~50s of content, recap should be ~10s (approx 20-30 words, 3 quick points)
        return 30, 3
    elif listened_seconds <= 300:  # 5 mins
        # For ~5 mins of content, recap should be ~20s (approx 50 words, 3 points)
        return 50, 3
    elif listened_seconds <= 900:  # 15 mins
        # For ~15 mins of content, recap should be ~30-40s (approx 80-100 words, 4 points)
        return 90, 4
    elif listened_seconds <= 3600:  # 1 hour
        # For ~1 hour of content, recap should be ~1-2 mins (approx 150-200 words, 5 points)
        return 180, 5
    else:
        # Over 1 hour, cap recap at ~2-3 mins (approx 250 words, 5 points)
        return 250, 5


@router.post("", response_model=RecapResponse)
async def create_recap(
    body: RecapRequest,
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Generate a recap for a media item up to a specific timestamp.

    This is the core product endpoint. It:
    1. Verifies the media exists
    2. Transcribes the audio (or uses cached transcript)
    3. Extracts the transcript for the listened range
    4. Summarizes using Gemini (map-reduce for long content)
    5. Generates TTS audio of the recap
    6. Saves and returns the recap
    """
    # 1. Verify media exists
    media = await db.get(Media, body.media_id)
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    if body.listened_until_seconds <= 0:
        raise HTTPException(
            status_code=400,
            detail="listened_until_seconds must be greater than 0",
        )

    # 2. Get or create transcript
    result = await db.execute(
        select(Transcript).where(Transcript.media_id == body.media_id)
    )
    transcript = result.scalars().first()

    if not transcript:
        logger.info("No cached transcript for media %s, transcribing...", body.media_id)
        transcriber = _get_transcriber(settings)
        media_path = settings.MEDIA_DIR / media.filename

        if not media_path.exists():
            raise HTTPException(status_code=404, detail="Media file not found on disk")

        import asyncio

        full_text, segments = await asyncio.to_thread(
            transcriber.transcribe, media_path
        )

        transcript = Transcript(
            media_id=body.media_id,
            full_text=full_text,
            segments_json=json.dumps(segments),
        )
        db.add(transcript)
        await db.flush()
        await db.refresh(transcript)
        logger.info("Transcript created and cached for media %s", body.media_id)

    # 3. Extract text for the listened range [0, listened_until_seconds]
    range_text = TranscriberService.get_text_for_range(
        transcript.segments_json,
        start_seconds=0,
        end_seconds=body.listened_until_seconds,
    )

    if not range_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No transcript content found in the specified time range",
        )

    logger.info(
        "Extracted %d chars for range [0, %.1f]s",
        len(range_text),
        body.listened_until_seconds,
    )

    # 4. Summarize with Gemini (with auto-scaled word count and key point targets)
    summarizer = _get_summarizer(settings)
    auto_max_words, num_key_points = calculate_recap_params(body.listened_until_seconds)
    target_max_words = body.max_words if body.max_words is not None else auto_max_words

    logger.info(
        "Recap targets for %.1fs listened: max_words=%d, num_key_points=%d",
        body.listened_until_seconds,
        target_max_words,
        num_key_points,
    )

    summary_text, key_points = await summarizer.summarize(
        text=range_text,
        max_words=target_max_words,
        num_key_points=num_key_points,
    )

    # 5. Generate TTS audio
    audio_filename = await generate_recap_audio(
        text=summary_text,
        output_dir=settings.RECAPS_DIR,
        voice=settings.TTS_VOICE,
    )

    estimated_seconds = estimate_listen_seconds(summary_text)

    # 6. Save recap to DB
    recap = Recap(
        media_id=body.media_id,
        listened_until_seconds=body.listened_until_seconds,
        summary_text=summary_text,
        key_points_json=json.dumps(key_points),
        audio_filename=audio_filename,
        estimated_listen_seconds=estimated_seconds,
    )
    db.add(recap)
    await db.flush()
    await db.refresh(recap)

    logger.info(
        "Recap generated: %s (est. %ds listen time)",
        recap.id,
        estimated_seconds,
    )

    return {
        "id": recap.id,
        "media_id": recap.media_id,
        "summary_text": recap.summary_text,
        "key_points": key_points,
        "audio_url": f"/api/recap/{recap.id}/audio",
        "estimated_listen_seconds": recap.estimated_listen_seconds,
        "created_at": recap.created_at,
    }


@router.get("/{recap_id}", response_model=RecapResponse)
async def get_recap(
    recap_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Retrieve a previously generated recap."""
    recap = await db.get(Recap, recap_id)
    if not recap:
        raise HTTPException(status_code=404, detail="Recap not found")

    key_points = json.loads(recap.key_points_json) if recap.key_points_json else []

    return {
        "id": recap.id,
        "media_id": recap.media_id,
        "summary_text": recap.summary_text,
        "key_points": key_points,
        "audio_url": f"/api/recap/{recap.id}/audio" if recap.audio_filename else None,
        "estimated_listen_seconds": recap.estimated_listen_seconds,
        "created_at": recap.created_at,
    }


@router.get("/{recap_id}/audio")
async def get_recap_audio(
    recap_id: str,
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_db),
) -> FileResponse:
    """Stream the generated recap audio file."""
    recap = await db.get(Recap, recap_id)
    if not recap:
        raise HTTPException(status_code=404, detail="Recap not found")

    if not recap.audio_filename:
        raise HTTPException(status_code=404, detail="No audio generated for this recap")

    file_path = settings.RECAPS_DIR / recap.audio_filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found on disk")

    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        filename=recap.audio_filename,
    )
