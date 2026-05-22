"""Smart transcript chunking for map-reduce summarization."""

import re


def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~0.75 words per token for English."""
    return int(len(text.split()) / 0.75)


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences, preserving sentence boundaries."""
    # Split on sentence-ending punctuation followed by whitespace
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def split_into_chunks(
    text: str,
    max_tokens: int = 1500,
    overlap_ratio: float = 0.15,
) -> list[str]:
    """Split text into overlapping chunks for map-reduce summarization.

    Uses sentence-level splitting to maintain coherent boundaries.
    Each chunk overlaps with the next by ``overlap_ratio`` of its size
    to prevent losing context at boundaries.

    Args:
        text: The full transcript text to chunk.
        max_tokens: Approximate maximum tokens per chunk.
        overlap_ratio: Fraction of chunk to overlap with the next chunk.

    Returns:
        A list of text chunks, each under ``max_tokens`` (approximately).
    """
    if not text or not text.strip():
        return []

    sentences = _split_sentences(text)
    if not sentences:
        return []

    # If the whole text fits in one chunk, return it directly
    total_tokens = _estimate_tokens(text)
    if total_tokens <= max_tokens:
        return [text.strip()]

    chunks: list[str] = []
    current_sentences: list[str] = []
    current_tokens = 0
    overlap_tokens = int(max_tokens * overlap_ratio)

    for sentence in sentences:
        sentence_tokens = _estimate_tokens(sentence)

        # If adding this sentence would exceed the limit, finalize chunk
        if current_tokens + sentence_tokens > max_tokens and current_sentences:
            chunk_text = " ".join(current_sentences)
            chunks.append(chunk_text)

            # Keep the last few sentences as overlap for the next chunk
            overlap_sents: list[str] = []
            overlap_count = 0
            for s in reversed(current_sentences):
                s_tokens = _estimate_tokens(s)
                if overlap_count + s_tokens > overlap_tokens:
                    break
                overlap_sents.insert(0, s)
                overlap_count += s_tokens

            current_sentences = overlap_sents
            current_tokens = overlap_count

        current_sentences.append(sentence)
        current_tokens += sentence_tokens

    # Don't forget the last chunk
    if current_sentences:
        chunk_text = " ".join(current_sentences)
        chunks.append(chunk_text)

    return chunks
