"""Faster-Whisper transcription service with caching."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from faster_whisper import WhisperModel

from app.models import TranscriptSegment

logger = logging.getLogger(__name__)


class TranscriberService:
    """Transcribes audio files using faster-whisper (CTranslate2 backend).

    The model is lazily loaded on first use and cached for subsequent calls.
    """

    def __init__(self, model_size: str = "base") -> None:
        self._model_size = model_size
        self._model: WhisperModel | None = None

    def _get_model(self) -> "WhisperModel":
        """Lazy-load the Whisper model."""
        if self._model is None:
            from faster_whisper import WhisperModel

            logger.info("Loading Whisper model '%s' ...", self._model_size)
            self._model = WhisperModel(
                self._model_size,
                device="cpu",
                compute_type="int8",
            )
            logger.info("Whisper model loaded successfully.")
        return self._model

    def transcribe(self, audio_path: str | Path) -> tuple[str, list[dict]]:
        """Transcribe an audio file and return full text + segments.

        Args:
            audio_path: Path to the audio file.

        Returns:
            A tuple of ``(full_text, segments_list)`` where each segment
            is a dict with ``start``, ``end``, and ``text`` keys.
        """
        model = self._get_model()
        audio_path = str(audio_path)

        logger.info("Transcribing: %s", audio_path)
        segments_iter, info = model.transcribe(
            audio_path,
            beam_size=5,
            language=None,  # auto-detect
            vad_filter=True,  # filter out silence
        )

        segments: list[dict] = []
        full_text_parts: list[str] = []

        for segment in segments_iter:
            seg_dict = {
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": segment.text.strip(),
            }
            segments.append(seg_dict)
            full_text_parts.append(segment.text.strip())

        full_text = " ".join(full_text_parts)
        logger.info(
            "Transcription complete: %d segments, %d chars, language=%s",
            len(segments),
            len(full_text),
            info.language,
        )
        return full_text, segments

    @staticmethod
    def get_text_for_range(
        segments_json: str,
        start_seconds: float,
        end_seconds: float,
    ) -> str:
        """Extract transcript text for a specific time range.

        Args:
            segments_json: JSON string of segment dicts.
            start_seconds: Start of the range in seconds.
            end_seconds: End of the range in seconds.

        Returns:
            Concatenated text of all segments within the range.
        """
        segments: list[dict] = json.loads(segments_json)
        parts: list[str] = []

        for seg in segments:
            seg_start = seg.get("start", 0)
            seg_end = seg.get("end", 0)

            # Include segment if it overlaps with the requested range
            if seg_end >= start_seconds and seg_start <= end_seconds:
                parts.append(seg.get("text", ""))

        return " ".join(parts)
