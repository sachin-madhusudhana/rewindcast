"""Gemini-powered summarization with map-reduce for long transcripts."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from google import genai
from google.genai import types

from app.services.chunker import split_into_chunks

logger = logging.getLogger(__name__)

# ── Prompt Templates ─────────────────────────────────────────────────

CHUNK_SUMMARY_PROMPT = """\
You are a podcast recap assistant. Summarize the following transcript segment \
in a concise paragraph, preserving the key facts, arguments, and any \
notable quotes. Keep it under {max_words} words.

Transcript segment:
\"\"\"
{text}
\"\"\"
"""

FINAL_RECAP_PROMPT = """\
You are a podcast recap narrator creating a "Previously On..." style summary.

Below are summaries of consecutive segments of a podcast/audio that the \
listener has already heard. Combine them into ONE cohesive, engaging recap.

Rules:
- Write in a conversational, narrator-like tone
- Use present tense ("The host discusses...", "They explore...")
- Keep it under {max_words} words total
- Highlight the most important points
- Include any notable quotes or surprising facts mentioned
- End with a smooth transition like "And that's where we pick back up..."

Also extract exactly {num_key_points} key points as short bullet phrases.

Return your response as valid JSON with this exact structure:
{{
  "summary": "The full recap text...",
  "key_points": ["Point 1", "Point 2", "Point 3"]
}}

Segment summaries:
{summaries}
"""

SINGLE_RECAP_PROMPT = """\
You are a podcast recap narrator creating a "Previously On..." style summary.

Summarize the following transcript that the listener has already heard.

Rules:
- Write in a conversational, narrator-like tone
- Use present tense ("The host discusses...", "They explore...")
- Keep it under {max_words} words total
- Highlight the most important points
- Include any notable quotes or surprising facts
- End with a smooth transition like "And that's where we pick back up..."

Also extract exactly {num_key_points} key points as short bullet phrases.

Return your response as valid JSON with this exact structure:
{{
  "summary": "The full recap text...",
  "key_points": ["Point 1", "Point 2", "Point 3"]
}}

Transcript:
\"\"\"
{text}
\"\"\"
"""


class SummarizerService:
    """Summarizes transcripts using Google Gemini with map-reduce strategy."""

    def __init__(self, api_key: str) -> None:
        self._client = genai.Client(api_key=api_key)
        self._model = "gemini-2.5-flash"

    async def _generate(self, prompt: str) -> str:
        """Call Gemini and return the response text."""
        response = await asyncio.to_thread(
            self._client.models.generate_content,
            model=self._model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,
                max_output_tokens=2048,
            ),
        )
        return response.text or ""

    async def _summarize_chunk(self, text: str, max_words: int = 150) -> str:
        """Summarize a single chunk of transcript text."""
        prompt = CHUNK_SUMMARY_PROMPT.format(text=text, max_words=max_words)
        return await self._generate(prompt)

    def _parse_json_response(self, text: str) -> dict[str, Any]:
        """Parse JSON from model response, handling markdown fences."""
        cleaned = text.strip()
        # Remove markdown code fences if present
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            # Remove first line (```json) and last line (```)
            lines = [l for l in lines if not l.strip().startswith("```")]
            cleaned = "\n".join(lines)

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response, using raw text")
            return {
                "summary": text.strip(),
                "key_points": [],
            }

    async def summarize(
        self,
        text: str,
        max_words: int = 300,
        num_key_points: int = 3,
    ) -> tuple[str, list[str]]:
        """Summarize transcript text using map-reduce if needed.

        Args:
            text: The transcript text to summarize.
            max_words: Target maximum words for the final recap.
            num_key_points: Number of key points to extract.

        Returns:
            A tuple of ``(summary_text, key_points_list)``.
        """
        chunks = split_into_chunks(text, max_tokens=1500, overlap_ratio=0.15)
        logger.info("Split transcript into %d chunks for summarization", len(chunks))

        if len(chunks) <= 1:
            # Short enough for a single pass
            prompt = SINGLE_RECAP_PROMPT.format(
                text=text,
                max_words=max_words,
                num_key_points=num_key_points,
            )
            raw = await self._generate(prompt)
            result = self._parse_json_response(raw)
            return result.get("summary", raw), result.get("key_points", [])

        # Map phase: summarize each chunk (can be parallel)
        chunk_tasks = [
            self._summarize_chunk(chunk, max_words=max(50, max_words // len(chunks)))
            for chunk in chunks
        ]
        chunk_summaries = await asyncio.gather(*chunk_tasks)

        # Reduce phase: combine chunk summaries into final recap
        numbered_summaries = "\n\n".join(
            f"[Segment {i + 1}]: {s}" for i, s in enumerate(chunk_summaries)
        )
        prompt = FINAL_RECAP_PROMPT.format(
            summaries=numbered_summaries,
            max_words=max_words,
            num_key_points=num_key_points,
        )
        raw = await self._generate(prompt)
        result = self._parse_json_response(raw)

        summary = result.get("summary", raw)
        key_points = result.get("key_points", [])

        logger.info(
            "Summarization complete: %d words, %d key points",
            len(summary.split()),
            len(key_points),
        )
        return summary, key_points
