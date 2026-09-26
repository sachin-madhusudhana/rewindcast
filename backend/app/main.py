"""RewindCast API — FastAPI application entry point."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db
from app.routers import media, recap, audiobookshelf

# ── Logging ──────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan ─────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Run startup / shutdown tasks."""
    settings = get_settings()

    # Create media & recap directories
    settings.MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    settings.RECAPS_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize database tables
    await init_db()
    logger.info("Database initialized")
    logger.info("RewindCast API ready 🚀")

    yield  # app is running

    logger.info("Shutting down RewindCast API")


# ── App ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="RewindCast API",
    description=(
        'AI-powered "Previously On..." recap engine for podcasts '
        "and long-form audio. Upload media, generate transcripts, "
        "and create spoken recap summaries."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ───────────────────────────────────────────────────────────

app.include_router(media.router)
app.include_router(recap.router)
app.include_router(audiobookshelf.router)


@app.get("/api/health", tags=["system"])
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok", "service": "rewindcast"}
