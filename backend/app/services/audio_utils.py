"""Audio file utilities for handling multi-file audiobooks."""

from __future__ import annotations

import asyncio
import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def determine_files_needed(
    audio_files: list[dict],
    current_time: float,
) -> list[dict]:
    """Determine which audio files are needed to cover [0, current_time].

    Audio files should be sorted by index.  Each file has a ``duration``
    field.  We accumulate durations and return files until the accumulated
    time covers ``current_time``.
    """
    needed: list[dict] = []
    accumulated = 0.0
    for af in sorted(audio_files, key=lambda f: f.get("index", 0)):
        needed.append(af)
        accumulated += af.get("duration", 0)
        if accumulated >= current_time:
            break
    return needed


async def concatenate_audio_files(
    file_paths: list[Path],
    output_path: Path,
) -> Path:
    """Concatenate multiple audio files into one using ffmpeg.

    Uses the *concat demuxer* for lossless concatenation when all
    files share the same codec.  Falls back to a simple copy when
    only a single file is provided.
    """
    if len(file_paths) == 1:
        if not output_path.exists():
            shutil.copy2(file_paths[0], output_path)
        return output_path

    # Create a concat list file
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".txt",
        delete=False,
        dir=str(output_path.parent),
    ) as f:
        for path in file_paths:
            # ffmpeg concat demuxer requires escaped single quotes
            safe = str(path).replace("'", "'\\''")
            f.write(f"file '{safe}'\n")
        concat_list = f.name

    cmd = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        concat_list,
        "-c",
        "copy",
        str(output_path),
    ]

    logger.info("Concatenating %d files -> %s", len(file_paths), output_path.name)
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        _, stderr = await proc.communicate()
        if proc.returncode != 0:
            logger.error("ffmpeg concat failed: %s", stderr.decode()[:500])
            raise RuntimeError(f"ffmpeg concat failed: {stderr.decode()[:200]}")
    finally:
        Path(concat_list).unlink(missing_ok=True)

    logger.info("Concatenation complete: %s", output_path.name)
    return output_path
