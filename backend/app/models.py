"""Pydantic request / response schemas for the RewindCast API."""

from __future__ import annotations
from datetime import datetime

from pydantic import BaseModel, Field


# ── Transcript ────────────────────────────────────────────────────────


class TranscriptSegment(BaseModel):
    """A single timestamped segment of a transcript."""

    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    text: str


# ── Media ─────────────────────────────────────────────────────────────


class MediaResponse(BaseModel):
    """Public representation of a media item."""

    id: str
    title: str
    filename: str
    duration_seconds: float | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class MediaListResponse(BaseModel):
    """Wrapper for listing media items."""

    items: list[MediaResponse]
    total: int


class MediaUrlRequest(BaseModel):
    """Request body for downloading media from a URL."""

    url: str = Field(..., description="Public URL (YouTube, podcast RSS, etc.)")


# ── Recap ─────────────────────────────────────────────────────────────


class RecapRequest(BaseModel):
    """Request body for generating a recap."""

    media_id: str
    listened_until_seconds: float = Field(
        ..., ge=0, description="Playback position the user reached (seconds)"
    )
    style: str = Field(
        default="conversational",
        description="Narration style for the recap",
    )
    max_words: int | None = Field(
        default=None,
        ge=50,
        le=2000,
        description="Approximate max words in the recap. If not specified, it will be automatically scaled based on the listened duration.",
    )


class RecapResponse(BaseModel):
    """Public representation of a generated recap."""

    id: str
    media_id: str
    summary_text: str
    key_points: list[str]
    audio_url: str | None = None
    estimated_listen_seconds: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}
