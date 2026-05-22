"""Text-to-Speech service using Microsoft Edge TTS (free, high quality)."""

from __future__ import annotations

import logging
from pathlib import Path
from uuid import uuid4

import edge_tts

logger = logging.getLogger(__name__)


async def generate_recap_audio(
    text: str,
    output_dir: str | Path,
    voice: str = "en-US-AriaNeural",
) -> str:
    """Generate an MP3 audio file from recap text using Edge TTS.

    Args:
        text: The recap text to convert to speech.
        output_dir: Directory to save the generated audio file.
        voice: The Edge TTS voice to use. Some good options:
            - en-US-AriaNeural (female, natural, default)
            - en-US-GuyNeural (male, natural)
            - en-GB-SoniaNeural (British female)
            - en-US-JennyNeural (female, conversational)

    Returns:
        The filename (not full path) of the generated MP3 file.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"recap_{uuid4().hex[:12]}.mp3"
    output_path = output_dir / filename

    logger.info("Generating TTS audio with voice '%s' ...", voice)

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(str(output_path))

    file_size = output_path.stat().st_size
    logger.info("TTS audio saved: %s (%d bytes)", filename, file_size)

    return filename


def estimate_listen_seconds(text: str, words_per_minute: int = 150) -> int:
    """Estimate how long it takes to listen to the given text.

    Args:
        text: The text to estimate duration for.
        words_per_minute: Average speaking rate (TTS is ~150 wpm).

    Returns:
        Estimated duration in seconds.
    """
    word_count = len(text.split())
    return max(1, int(word_count / words_per_minute * 60))
