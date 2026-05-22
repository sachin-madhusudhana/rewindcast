"""SQLAlchemy ORM models for RewindCast."""

from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _uuid() -> str:
    """Generate a new UUID4 string."""
    return str(uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Shared declarative base for all models."""


class Media(Base):
    """An uploaded or downloaded audio/video file."""

    __tablename__ = "media"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    duration_seconds: Mapped[float] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    # Relationships
    transcripts: Mapped[list["Transcript"]] = relationship(
        back_populates="media", cascade="all, delete-orphan"
    )
    recaps: Mapped[list["Recap"]] = relationship(
        back_populates="media", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Media id={self.id!r} title={self.title!r}>"


class Transcript(Base):
    """Full transcript + timestamped segments for a piece of media."""

    __tablename__ = "transcripts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    media_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("media.id", ondelete="CASCADE"), nullable=False
    )
    full_text: Mapped[str] = mapped_column(Text, nullable=False)
    segments_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")

    # Relationships
    media: Mapped["Media"] = relationship(back_populates="transcripts")

    def __repr__(self) -> str:
        return f"<Transcript id={self.id!r} media_id={self.media_id!r}>"


class Recap(Base):
    """A generated recap for a media item."""

    __tablename__ = "recaps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    media_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("media.id", ondelete="CASCADE"), nullable=False
    )
    listened_until_seconds: Mapped[float] = mapped_column(Float, nullable=False)
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)
    key_points_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    audio_filename: Mapped[str | None] = mapped_column(String(512), nullable=True)
    estimated_listen_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )

    # Relationships
    media: Mapped["Media"] = relationship(back_populates="recaps")

    def __repr__(self) -> str:
        return f"<Recap id={self.id!r} media_id={self.media_id!r}>"
