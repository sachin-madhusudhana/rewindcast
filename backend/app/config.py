"""Application configuration loaded from environment variables / .env file."""

from pathlib import Path

from pydantic_settings import BaseSettings

# Resolve paths relative to the backend/ directory
_BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Global settings for the RewindCast backend.

    Values are loaded from a ``.env`` file located in the project root
    (one level above ``backend/``) and can be overridden by real
    environment variables.
    """

    # ── Required ──────────────────────────────────────────────────────
    GEMINI_API_KEY: str

    # ── Whisper ───────────────────────────────────────────────────────
    WHISPER_MODEL_SIZE: str = "base"

    # ── TTS ───────────────────────────────────────────────────────────
    TTS_VOICE: str = "en-US-AriaNeural"

    # ── File paths ────────────────────────────────────────────────────
    MEDIA_DIR: Path = _BACKEND_DIR / "media"
    RECAPS_DIR: Path = _BACKEND_DIR / "recaps"

    # ── Database ──────────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./rewindcast.db"

    model_config = {
        "env_file": str(_BACKEND_DIR.parent / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance.

    We intentionally avoid ``lru_cache`` here so that tests can
    monkeypatch environment variables and get fresh instances via
    FastAPI dependency overrides.
    """
    return Settings()  # type: ignore[call-arg]
