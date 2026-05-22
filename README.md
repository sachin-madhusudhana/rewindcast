# ⏪ RewindCast

**AI-powered "Previously On..." for podcasts — never lose your place again.**

[![License: MIT](https://img.shields.io/badge/License-MIT-violet.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688.svg)](https://fastapi.tiangolo.com)

---

> You listened to 45 minutes of a podcast, paused, and came back 3 days later.
> You don't remember what was discussed. **RewindCast** generates a 2-3 minute
> spoken recap of exactly what you already heard — so you can jump right back in.

<!-- screenshot placeholder -->

## ✨ Features

- ✅ **One-tap Recap** — Click "Recap" to get an AI summary of your listened portion
- ✅ **Spoken Summaries** — High-quality text-to-speech narrates your recap
- ✅ **Progress Tracking** — Automatically saves where you left off
- ✅ **Smart Transcription** — Uses Whisper AI for accurate speech-to-text
- ✅ **Map-Reduce Summarization** — Handles podcasts of any length with Gemini AI
- ✅ **YouTube Import** — Paste a YouTube URL to import any video/podcast
- ✅ **File Upload** — Drag & drop MP3, WAV, M4A, MP4, or WebM files
- ✅ **Resume Playback** — Always pick up right where you left off
- ✅ **Beautiful UI** — Premium dark theme with glassmorphism design
- ✅ **100% Free TTS** — Uses Microsoft Edge voices (no API cost)

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- FFmpeg (`brew install ffmpeg` on macOS)
- A [Gemini API key](https://ai.google.dev) (free tier available)

### 1. Clone & Configure

```bash
git clone https://github.com/yourusername/rewindcast.git
cd rewindcast
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 2. Start the Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```

### 3. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) and upload a podcast!

## 🏗️ Architecture

```
┌────────────────────────────────────────────────────┐
│              Frontend (Next.js 14)                  │
│  ┌──────────┐  ┌──────────┐  ┌─────────────────┐  │
│  │ Upload   │  │ Audio    │  │ Recap Modal     │  │
│  │ Zone     │  │ Player   │  │ + Audio Summary │  │
│  └────┬─────┘  └──────────┘  └────────┬────────┘  │
└───────┼────────────────────────────────┼───────────┘
        ↓                               ↓
┌───────────────────────────────────────────────────┐
│              Backend (Python FastAPI)               │
│  ┌──────────┐ ┌───────────┐ ┌──────┐ ┌─────────┐ │
│  │ Upload / │→│ Whisper   │→│Gemini│→│Edge TTS │ │
│  │ yt-dlp   │ │Transcribe │ │ LLM  │ │(free)   │ │
│  └──────────┘ └───────────┘ └──────┘ └─────────┘ │
└───────────────────────────────────────────────────┘
```

## 📡 API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/media/upload` | Upload audio/video file |
| `POST` | `/api/media/url` | Import from YouTube URL |
| `GET` | `/api/media` | List all media |
| `GET` | `/api/media/{id}/file` | Stream media file |
| **`POST`** | **`/api/recap`** | **🌟 Generate a recap** |
| `GET` | `/api/recap/{id}/audio` | Stream recap audio |

See [API Documentation](docs/API.md) for full details.

## 🎯 For Platform Partners

RewindCast is designed as a **drop-in feature** for podcast platforms:

| Metric | Impact |
|--------|--------|
| **Completion Rate** | +10-15% (users return and finish content) |
| **Ad Revenue** | More mid-roll impressions from higher completion |
| **User Retention** | Reduced churn from "I forgot where I was" |
| **Cost** | ~$0.002/recap (Gemini) + $0/TTS (Edge) |

**Integration options:**
- REST API for server-side integration
- SDK for client-side embedding
- White-label UI components

See [Product Brief](docs/PRODUCT_BRIEF.md) for the full pitch.

## 🛠️ Tech Stack

| Component | Technology | Cost |
|-----------|-----------|------|
| Transcription | `faster-whisper` (local) | Free |
| Summarization | Google Gemini 2.5 Flash | ~$0.002/recap |
| Text-to-Speech | Microsoft Edge TTS | Free |
| Backend | Python FastAPI | — |
| Frontend | Next.js 14 + TypeScript | — |
| Database | SQLite (async) | — |
| Player | Custom HTML5 Audio | — |

## 📁 Project Structure

```
rewindcast/
├── backend/              # Python FastAPI server
│   ├── app/
│   │   ├── main.py       # App entry point
│   │   ├── routers/      # API endpoints
│   │   └── services/     # Whisper, Gemini, TTS
│   └── pyproject.toml
├── frontend/             # Next.js web app
│   ├── app/              # Pages (App Router)
│   ├── components/       # React components
│   └── lib/              # API client & types
└── docs/                 # Product & API docs
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file.

---

<p align="center">
  Built with ❤️ for podcast lovers everywhere
  <br/>
  <strong>⏪ RewindCast</strong> — Never lose your place again
</p>
