"""Audiobookshelf integration endpoints for RewindCast.

Provides browsing, importing, and one-click recap generation for items
stored in a self-hosted Audiobookshelf instance.
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.database import get_db
from app.db_models import Media, Transcript, Recap
from app.models import (
    ABSItemSummary,
    ABSLibrary,
    ABSRecapRequest,
    ABSStatusResponse,
    MediaResponse,
    RecapResponse,
)
from app.routers.recap import (
    _get_summarizer,
    _get_transcriber,
    calculate_recap_params,
)
from app.services.audiobookshelf import AudiobookshelfClient, AudiobookshelfError
from app.services.audio_utils import concatenate_audio_files, determine_files_needed
from app.services.tts import estimate_listen_seconds, generate_recap_audio

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/abs", tags=["audiobookshelf"])

# ── Helpers ──────────────────────────────────────────────────────────


def _get_abs_client(settings: Settings) -> AudiobookshelfClient:
    """Build an :class:`AudiobookshelfClient` from current settings.

    Raises HTTP 503 when the integration is not configured.
    """
    if not settings.AUDIOBOOKSHELF_URL or not settings.AUDIOBOOKSHELF_API_TOKEN:
        raise HTTPException(
            status_code=503,
            detail=(
                "Audiobookshelf integration is not configured. "
                "Set AUDIOBOOKSHELF_URL and AUDIOBOOKSHELF_API_TOKEN in your .env"
            ),
        )
    return AudiobookshelfClient(
        base_url=settings.AUDIOBOOKSHELF_URL,
        api_token=settings.AUDIOBOOKSHELF_API_TOKEN,
    )


def _extract_audio_files(item_detail: dict) -> list[dict]:
    """Extract the audio-file list from an ABS item-detail payload.

    Handles both audiobook and podcast structures.
    """
    media = item_detail.get("media", {})

    # Audiobooks: media.audioFiles
    audio_files = media.get("audioFiles", [])
    if audio_files:
        return audio_files

    # Podcasts: episodes → audioFile
    episodes = media.get("episodes", [])
    for ep in episodes:
        af = ep.get("audioFile")
        if af:
            audio_files.append(af)

    return audio_files


async def _import_abs_item(
    item_id: str,
    client: AudiobookshelfClient,
    settings: Settings,
    db: AsyncSession,
) -> Media:
    """Download audio from Audiobookshelf and create a local Media record.

    This is the shared import logic used by both the import and recap
    endpoints.
    """
    item_detail = await client.get_item_detail(item_id)
    media_info = item_detail.get("media", {})
    metadata = media_info.get("metadata", {})

    audio_files = _extract_audio_files(item_detail)
    if not audio_files:
        raise HTTPException(
            status_code=400,
            detail=f"No audio files found for ABS item {item_id}",
        )

    total_duration = media_info.get("duration", 0)
    needed = determine_files_needed(audio_files, total_duration)

    # Download each needed file
    downloaded: list[Path] = []
    for af in needed:
        ino = af.get("ino", af.get("id", "0"))
        ext = Path(af.get("metadata", {}).get("filename", "audio.mp3")).suffix or ".mp3"
        dest = settings.MEDIA_DIR / f"abs_{item_id}_{ino}{ext}"
        if not dest.exists():
            await client.download_audio_file(item_id, str(ino), dest)
        downloaded.append(dest)

    # Concatenate if multiple files
    if len(downloaded) > 1:
        merged_path = settings.MEDIA_DIR / f"abs_{item_id}_merged.mp3"
        final_path = await concatenate_audio_files(downloaded, merged_path)
    else:
        final_path = downloaded[0]

    # Create DB record
    authors = metadata.get("authors", [])
    author_name = (
        authors[0]["name"] if authors else metadata.get("authorName", "")
    )
    title = metadata.get("title", "Untitled")
    if author_name:
        title = f"{title} — {author_name}"

    media_record = Media(
        title=title,
        filename=final_path.name,
        duration_seconds=total_duration,
        source_type="audiobookshelf",
        external_id=item_id,
    )
    db.add(media_record)
    await db.flush()
    await db.refresh(media_record)

    logger.info("Imported ABS item %s as media %s", item_id, media_record.id)
    return media_record


# ── Endpoints ────────────────────────────────────────────────────────


@router.get("/status", response_model=ABSStatusResponse)
async def abs_status(
    settings: Settings = Depends(get_settings),
) -> ABSStatusResponse:
    """Test the connection to the configured Audiobookshelf server."""
    if not settings.AUDIOBOOKSHELF_URL or not settings.AUDIOBOOKSHELF_API_TOKEN:
        return ABSStatusResponse(
            connected=False,
            error="Audiobookshelf integration is not configured",
        )

    client = _get_abs_client(settings)
    try:
        info = await client.test_connection()
        return ABSStatusResponse(
            connected=True,
            server_url=settings.AUDIOBOOKSHELF_URL,
            username=info.get("username"),
        )
    except AudiobookshelfError as e:
        return ABSStatusResponse(
            connected=False,
            server_url=settings.AUDIOBOOKSHELF_URL,
            error=str(e),
        )
    finally:
        await client.close()


@router.get("/libraries", response_model=list[ABSLibrary])
async def abs_libraries(
    settings: Settings = Depends(get_settings),
) -> list[dict]:
    """List all Audiobookshelf libraries."""
    client = _get_abs_client(settings)
    try:
        return await client.get_libraries()
    except AudiobookshelfError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    finally:
        await client.close()


@router.get("/in-progress", response_model=list[ABSItemSummary])
async def abs_in_progress(
    settings: Settings = Depends(get_settings),
) -> list[dict]:
    """List items the user is currently listening to."""
    client = _get_abs_client(settings)
    try:
        return await client.get_items_in_progress()
    except AudiobookshelfError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    finally:
        await client.close()


@router.post("/import/{item_id}", response_model=MediaResponse)
async def abs_import(
    item_id: str,
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Import an Audiobookshelf item as a local media record.

    If the item was previously imported the existing record is returned
    without re-downloading.
    """
    # Check for existing import
    result = await db.execute(
        select(Media).where(Media.external_id == item_id)
    )
    existing = result.scalars().first()
    if existing:
        logger.info("ABS item %s already imported as %s", item_id, existing.id)
        return {
            "id": existing.id,
            "title": existing.title,
            "filename": existing.filename,
            "duration_seconds": existing.duration_seconds,
            "source_type": existing.source_type,
            "external_id": existing.external_id,
            "created_at": existing.created_at,
        }

    client = _get_abs_client(settings)
    try:
        media_record = await _import_abs_item(item_id, client, settings, db)
        return {
            "id": media_record.id,
            "title": media_record.title,
            "filename": media_record.filename,
            "duration_seconds": media_record.duration_seconds,
            "source_type": media_record.source_type,
            "external_id": media_record.external_id,
            "created_at": media_record.created_at,
        }
    except AudiobookshelfError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    finally:
        await client.close()


@router.post("/recap/{item_id}", response_model=RecapResponse)
async def abs_recap(
    item_id: str,
    body: ABSRecapRequest,
    settings: Settings = Depends(get_settings),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """One-click recap: import from ABS → transcribe → summarize → TTS.

    This is the hero endpoint.  It resolves the listening position from
    the ABS server (or the ``listened_until_seconds`` override), ensures
    the audio is imported locally, and runs the full recap pipeline.
    """
    client = _get_abs_client(settings)
    try:
        # 1. Resolve listened position
        listened_until: float | None = body.listened_until_seconds
        if listened_until is None:
            progress = await client.get_item_progress(item_id, body.episode_id)
            if progress:
                listened_until = progress.get("currentTime", 0)

        if not listened_until or listened_until <= 0:
            raise HTTPException(
                status_code=400,
                detail=(
                    "No listening progress found in Audiobookshelf and no "
                    "listened_until_seconds override was provided."
                ),
            )

        # 2. Ensure media is imported
        result = await db.execute(
            select(Media).where(Media.external_id == item_id)
        )
        media_record = result.scalars().first()

        if not media_record:
            media_record = await _import_abs_item(item_id, client, settings, db)

    except AudiobookshelfError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    finally:
        await client.close()

    # 3. Get or create transcript
    result = await db.execute(
        select(Transcript).where(Transcript.media_id == media_record.id)
    )
    transcript = result.scalars().first()

    if not transcript:
        logger.info(
            "Transcribing ABS media %s for recap...", media_record.id
        )
        transcriber = _get_transcriber(settings)
        media_path = settings.MEDIA_DIR / media_record.filename

        if not media_path.exists():
            raise HTTPException(
                status_code=404, detail="Media file not found on disk"
            )

        full_text, segments = await asyncio.to_thread(
            transcriber.transcribe, media_path
        )

        transcript = Transcript(
            media_id=media_record.id,
            full_text=full_text,
            segments_json=json.dumps(segments),
        )
        db.add(transcript)
        await db.flush()
        await db.refresh(transcript)
        logger.info("Transcript cached for ABS media %s", media_record.id)

    # 4. Extract text for listened range
    from app.services.transcriber import TranscriberService

    range_text = TranscriberService.get_text_for_range(
        transcript.segments_json,
        start_seconds=0,
        end_seconds=listened_until,
    )

    if not range_text.strip():
        raise HTTPException(
            status_code=400,
            detail="No transcript content found in the specified time range",
        )

    logger.info(
        "Extracted %d chars for ABS recap [0, %.1f]s",
        len(range_text),
        listened_until,
    )

    # 5. Summarize with Gemini
    summarizer = _get_summarizer(settings)
    auto_max_words, num_key_points = calculate_recap_params(listened_until)

    summary_text, key_points = await summarizer.summarize(
        text=range_text,
        max_words=auto_max_words,
        num_key_points=num_key_points,
    )

    # 6. Generate TTS audio
    audio_filename = await generate_recap_audio(
        text=summary_text,
        output_dir=settings.RECAPS_DIR,
        voice=settings.TTS_VOICE,
    )

    estimated_seconds = estimate_listen_seconds(summary_text)

    # 7. Save recap to DB
    recap = Recap(
        media_id=media_record.id,
        listened_until_seconds=listened_until,
        summary_text=summary_text,
        key_points_json=json.dumps(key_points),
        audio_filename=audio_filename,
        estimated_listen_seconds=estimated_seconds,
    )
    db.add(recap)
    await db.flush()
    await db.refresh(recap)

    logger.info(
        "ABS recap generated: %s (est. %ds listen time)",
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
