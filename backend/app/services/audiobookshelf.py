"""Audiobookshelf API client for RewindCast integration."""

from __future__ import annotations

import logging
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)


class AudiobookshelfError(Exception):
    """Raised when an Audiobookshelf API call fails."""


class AudiobookshelfClient:
    """Async HTTP client for the Audiobookshelf REST API."""

    def __init__(self, base_url: str, api_token: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._token = api_token
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            headers={"Authorization": f"Bearer {api_token}"},
            timeout=30.0,
        )

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def _request(self, method: str, path: str, **kwargs) -> dict | list:
        """Send an authenticated request and return parsed JSON.

        Raises :class:`AudiobookshelfError` on HTTP or connection errors.
        """
        try:
            resp = await self._client.request(method, path, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            raise AudiobookshelfError(
                f"ABS API error {e.response.status_code}: {e.response.text[:200]}"
            ) from e
        except httpx.ConnectError as e:
            raise AudiobookshelfError(
                f"Cannot connect to Audiobookshelf at {self._base_url}: {e}"
            ) from e

    # ── Public helpers ────────────────────────────────────────────────

    async def test_connection(self) -> dict:
        """Test connection and return user info."""
        data = await self._request("GET", "/api/me")
        return {"username": data.get("username", "unknown")}

    async def get_libraries(self) -> list[dict]:
        """List all libraries."""
        data = await self._request("GET", "/api/libraries")
        libraries = data.get("libraries", data) if isinstance(data, dict) else data
        results = []
        for lib in libraries:
            results.append(
                {
                    "id": lib["id"],
                    "name": lib.get("name", "Unnamed"),
                    "media_type": lib.get("mediaType", "book"),
                    "item_count": lib.get("stats", {}).get("totalItems", 0),
                }
            )
        return results

    async def get_items_in_progress(self) -> list[dict]:
        """Get items the user is currently listening to."""
        data = await self._request(
            "GET", "/api/me/items-in-progress", params={"limit": 50}
        )
        items = data.get("libraryItems", data) if isinstance(data, dict) else data
        results = []
        for item in items:
            media = item.get("media", {})
            metadata = media.get("metadata", {})
            progress = item.get("userMediaProgress", item.get("mediaProgress", {}))

            authors = metadata.get("authors", [])
            author_name = (
                authors[0]["name"] if authors else metadata.get("authorName")
            )

            cover_url = (
                f"{self._base_url}/api/items/{item['id']}/cover"
                f"?token={self._token}"
            )

            results.append(
                {
                    "id": item["id"],
                    "title": metadata.get("title", "Untitled"),
                    "author": author_name,
                    "cover_url": cover_url,
                    "duration_seconds": media.get("duration", 0),
                    "current_time": (
                        progress.get("currentTime", 0) if progress else 0
                    ),
                    "progress_percent": (
                        progress.get("progress", 0) if progress else 0
                    ),
                    "media_type": item.get("mediaType", "book"),
                    "episode_title": (
                        item.get("recentEpisode", {}).get("title")
                        if item.get("recentEpisode")
                        else None
                    ),
                }
            )
        return results

    async def get_item_detail(self, item_id: str) -> dict:
        """Get full item details with audio files and progress."""
        return await self._request(
            "GET",
            f"/api/items/{item_id}",
            params={"expanded": "1", "include": "progress"},
        )

    async def get_item_progress(
        self, item_id: str, episode_id: str | None = None
    ) -> dict | None:
        """Get user's listening progress for an item.

        Returns ``None`` when the server has no progress record.
        """
        path = f"/api/me/progress/{item_id}"
        if episode_id:
            path += f"/{episode_id}"
        try:
            return await self._request("GET", path)
        except AudiobookshelfError:
            return None

    async def download_audio_file(
        self,
        item_id: str,
        file_ino: str,
        dest_path: Path,
    ) -> Path:
        """Stream an audio file from ABS to disk."""
        url = f"/api/items/{item_id}/file/{file_ino}"
        logger.info("Downloading ABS audio: %s -> %s", url, dest_path)
        async with self._client.stream("GET", url) as resp:
            resp.raise_for_status()
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, "wb") as f:
                async for chunk in resp.aiter_bytes(chunk_size=65536):
                    f.write(chunk)
        logger.info(
            "Download complete: %s (%.1f MB)",
            dest_path.name,
            dest_path.stat().st_size / 1e6,
        )
        return dest_path
