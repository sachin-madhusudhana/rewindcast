import os
import sys
from fpdf import FPDF

class GuidePDF(FPDF):
    def header(self):
        # Only show header on pages after the cover page
        if self.page_no() > 1:
            self.set_font('helvetica', 'I', 8)
            self.set_text_color(140, 120, 200) # Subtle violet
            self.cell(0, 8, 'RewindCast: A Beginner\'s Guide to Full-Stack AI Development', 0, 0, 'L')
            self.set_text_color(150, 150, 150)
            self.cell(0, 8, 'Step-by-Step Tutorial', 0, 1, 'R')
            self.set_draw_color(220, 215, 235)
            self.set_line_width(0.3)
            self.line(self.l_margin, 18, self.w - self.r_margin, 18)
            self.ln(5)
            
    def footer(self):
        self.set_y(-15)
        # Subtle divider above footer
        self.set_draw_color(240, 240, 240)
        self.line(self.l_margin, self.h - 15, self.w - self.r_margin, self.h - 15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, 'RewindCast Product Guide  |  Confidential & Proprietary', 0, 0, 'L')
        self.cell(0, 10, f'Page {self.page_no()}', 0, 1, 'R')

    def add_chapter_title(self, num, title):
        self.set_font('helvetica', 'B', 16)
        self.set_text_color(90, 50, 180) # Premium violet
        self.ln(8)
        self.cell(0, 10, f"Chapter {num}: {title}", 0, 1, 'L')
        self.set_draw_color(90, 50, 180)
        self.set_line_width(1.0)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(6)

    def add_section_title(self, title):
        self.set_font('helvetica', 'B', 12)
        self.set_text_color(40, 40, 80)
        self.ln(4)
        self.cell(0, 8, title, 0, 1, 'L')
        self.ln(2)

    def add_body_text(self, text):
        self.set_font('helvetica', '', 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5.5, text)
        self.ln(3)

    def add_bullet_point(self, title, desc):
        self.set_font('helvetica', 'B', 10)
        self.set_text_color(90, 50, 180)
        self.write(5, "  *  ")
        self.set_text_color(50, 50, 80)
        self.write(5, f"{title}: ")
        self.set_font('helvetica', '', 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, desc)
        self.ln(2)

    def add_code_block(self, code):
        self.set_font('courier', '', 8.5)
        self.set_text_color(0, 100, 80) # Custom green for code
        self.set_fill_color(248, 248, 250) # Light background
        self.set_draw_color(230, 230, 235)
        self.set_line_width(0.3)
        self.multi_cell(0, 4.5, code, border=1, fill=True)
        self.ln(4)

def build_pdf(filepath):
    pdf = GuidePDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    
    # ── COVER PAGE ────────────────────────────────────────────────────────
    pdf.ln(30)
    # Large glowing brand title
    pdf.set_font('helvetica', 'B', 38)
    pdf.set_text_color(90, 50, 180)
    pdf.cell(0, 15, "REWINDCAST", 0, 1, 'C')
    
    # Subtitle
    pdf.set_font('helvetica', 'B', 14)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, "A Step-by-Step Beginner's Guide to Building a Full-Stack AI Product", 0, 1, 'C')
    
    pdf.ln(10)
    # Visual divider
    pdf.set_draw_color(90, 50, 180)
    pdf.set_line_width(2.0)
    pdf.line(40, pdf.get_y(), pdf.w - 40, pdf.get_y())
    
    pdf.ln(25)
    # Description block on cover page
    pdf.set_font('helvetica', '', 11)
    pdf.set_text_color(80, 80, 80)
    intro_desc = (
        "RewindCast is a commercial-grade \"Previously On...\" spoken recap engine "
        "designed for podcasts and long-form audio. This guide takes you from an absolute "
        "beginner to understanding the full-stack architecture, API frameworks, AI model "
        "integrations, and web component engineering used to build it."
    )
    pdf.multi_cell(0, 6, intro_desc, align='C')
    
    # Bottom metadata
    pdf.set_y(-50)
    pdf.set_font('helvetica', 'B', 10)
    pdf.set_text_color(90, 50, 180)
    pdf.cell(0, 6, "ENGINEERED BY ANTIGRAVITY AI", 0, 1, 'C')
    pdf.set_font('helvetica', '', 9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 5, "May 2026 Edition", 0, 1, 'C')
    pdf.cell(0, 5, "Target Stack: Python FastAPI + Next.js 14 + Gemini API", 0, 1, 'C')

    # ── CHAPTER 1 ────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.add_chapter_title("1", "Architecture & Technology Stack")
    
    pdf.add_body_text(
        "To build a production-ready AI application, we choose technologies that balance "
        "performance, simplicity, and scalability. RewindCast is built as a decoupled "
        "full-stack application containing a robust FastAPI backend and a sleek Next.js 14 frontend."
    )
    
    pdf.add_section_title("Why This Stack Was Chosen:")
    
    pdf.add_bullet_point(
        "FastAPI (Python)", 
        "FastAPI is the standard for high-performance AI APIs. Because AI libraries (like "
        "Whisper, PyTorch, and Google GenAI) are natively built in Python, FastAPI is the perfect "
        "bridge, providing async endpoints, auto-generated documentation, and rapid request execution."
    )
    
    pdf.add_bullet_point(
        "Next.js 14 + TypeScript",
        "Provides a world-class framework for rendering highly interactive and visually spectacular "
        "interfaces. It handles fast client-side navigation, component separation, and serves as a "
        "robust interface for media player control."
    )
    
    pdf.add_bullet_point(
        "faster-whisper",
        "Instead of calling external paid APIs, we run transcription locally using the highly optimized "
        "faster-whisper library (a C++ reimplementation of OpenAI's Whisper). It is up to 4x faster "
        "than standard Whisper and has a memory footprint under 500MB on a CPU."
    )
    
    pdf.add_bullet_point(
        "Google Gemini API (gemini-2.5-flash)",
        "Acts as our central reasoning engine. It takes the text segments within the listened timestamp "
        "range and synthesizes them into an engaging narrative while keeping costs under fractions of a penny."
    )
    
    pdf.add_bullet_point(
        "Edge TTS (edge-tts)",
        "A python wrapper that streams audio from Microsoft Edge's translation servers. It provides "
        "exceptionally high-quality, natural-sounding, human-like voice narration entirely for free."
    )

    # ── CHAPTER 2 ────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.add_chapter_title("2", "Workspace & Foundation Setup")
    
    pdf.add_body_text(
        "We start by organizing our codebase. Decoupling the codebase into 'backend/' and "
        "'frontend/' folders keeps the dependencies isolated and standardizes project organization."
    )
    
    pdf.add_section_title("1. Create Directory Structure:")
    pdf.add_body_text(
        "Initialize your workspace and create the primary directories for the backend, frontend, "
        "data cache, and technical documents:"
    )
    
    pdf.add_code_block(
        "mkdir rewindcast && cd rewindcast\n"
        "mkdir -p backend/app/routers backend/app/services backend/media backend/recaps\n"
        "mkdir -p frontend/components frontend/lib frontend/app\n"
        "mkdir -p docs"
    )

    pdf.add_section_title("2. Environmental Configuration (.env):")
    pdf.add_body_text(
        "To securely configure API keys and media directories without hardcoding them, we use an "
        "environmental file (.env). We copy this into the project root and ensure it is added to .gitignore."
    )
    
    pdf.add_code_block(
        "# .env - Configuration Environment\n"
        "GEMINI_API_KEY=AIzaSy...\n"
        "MEDIA_DIR=./media\n"
        "RECAPS_DIR=./recaps\n"
        "TTS_VOICE=en-US-AriaNeural\n"
        "WHISPER_MODEL_SIZE=base"
    )

    pdf.add_section_title("3. Git Integration (.gitignore):")
    pdf.add_body_text(
        "To prevent large media files, compiled virtual environments, databases, and private API keys "
        "from being tracked or accidentally exposed on GitHub, we add them to .gitignore:"
    )
    pdf.add_code_block(
        "# Python virtual environments\n"
        ".venv/\n"
        "\n"
        "# Environment variables containing keys\n"
        ".env\n"
        "\n"
        "# Local directories caching media and transcripts\n"
        "backend/media/*\n"
        "backend/recaps/*\n"
        "frontend/node_modules/\n"
        "*.db"
    )

    # ── CHAPTER 3 ────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.add_chapter_title("3", "Engineering the Backend Core")
    
    pdf.add_body_text(
        "The backend serves as our operational engine, handling database caching, audio transcription, "
        "AI summarization, and speech-to-text generation."
    )
    
    pdf.add_section_title("1. Database & Schema Configuration:")
    pdf.add_body_text(
        "Instead of transcribing the same file every time a user requests a recap, we use SQLite "
        "along with SQLAlchemy to cache transcripts. The db_models.py defines three primary entities:"
    )
    pdf.add_bullet_point("Media", "Stores the title, unique filename on disk, and duration of the imported podcast.")
    pdf.add_bullet_point("Transcript", "Stores the full text and a JSON string of word-by-word segments with start/end times.")
    pdf.add_bullet_point("Recap", "Caches generated recap text, bullet points, and the file path of the generated TTS MP3.")

    pdf.add_section_title("2. Intelligent Text Chunker:")
    pdf.add_body_text(
        "When summarizing long podcasts (e.g., a 1-hour conversation), the text is too massive to "
        "pass directly. We wrote a smart chunker in services/chunker.py that splits the transcript "
        "into 1500-token blocks with a 15% overlap. This preserves continuity between adjacent blocks."
    )

    pdf.add_section_title("3. Google Gemini Orchestration:")
    pdf.add_body_text(
        "To make summaries highly cohesive, we implement a Map-Reduce strategy using Gemini:\n"
        " - Map Phase: Each text chunk is summarized concurrently into a concise paragraph.\n"
        " - Reduce Phase: All paragraph summaries are combined and Gemini synthesizes them into "
        "a single 'Previously On...' script using the present tense and narrator-style tone.\n"
        "The model is instructed to output a structured JSON containing the text and exact bullet points."
    )
    
    pdf.add_section_title("4. Spoken Narrator (TTS):")
    pdf.add_body_text(
        "Once Gemini generates the script, we stream it into edge-tts to write a natural-sounding, "
        "expressive narrator voice as an MP3 file, creating a professional radio-show feel."
    )

    pdf.add_section_title("5. Dynamic Duration Scaling (NEW):")
    pdf.add_body_text(
        "To make the product commercially viable, the recap length dynamically adjusts to match "
        "the amount of content a user has already listened to. A 50-second listen yields a 10s recap, "
        "whereas a 1-hour listen yields a highly polished 1.5-minute summary."
    )
    pdf.add_code_block(
        "if listened_seconds <= 60:\n"
        "    return 30_words, 3_points  # ~10 seconds audio\n"
        "elif listened_seconds <= 300:\n"
        "    return 50_words, 3_points  # ~20 seconds audio\n"
        "elif listened_seconds <= 3600:\n"
        "    return 180_words, 5_points # ~1.5 mins audio"
    )

    # ── CHAPTER 4 ────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.add_chapter_title("4", "Engineering the Next.js Frontend")
    
    pdf.add_body_text(
        "The frontend translates technical API capability into an intuitive, responsive, and "
        "visually exceptional user interface using Next.js client-side components."
    )
    
    pdf.add_section_title("1. Dynamic Theme & Aesthetics (globals.css):")
    pdf.add_body_text(
        "We styled the application using pure vanilla CSS variables to ensure perfect layout control. "
        "The design system incorporates modern, dark-mode glassmorphism:\n"
        " - Color Palette: Deep rich obsidian, high-contrast white text, and glowing neon purple accents.\n"
        " - Blurring & Translucency: Uses backdrop-filters (e.g. backdrop-filter: blur(16px)) to "
        "create glowing layers that hover over other visual elements.\n"
        " - Hover States: Glowing borders, smooth scale transformations, and interactive color shifts."
    )

    pdf.add_section_title("2. Custom Waveform Player (MediaPlayer.tsx):")
    pdf.add_body_text(
        "Instead of a browser-default audio player, we built a fully responsive player from scratch. "
        "It includes a decorative soundwave visualizer of 40 bars that animates in sync with the audio "
        "duration and playback progress. It also supports multiple listening speeds (0.75x to 2x) "
        "and automatically caches playback progress in localStorage, prompting you to resume if you refresh."
    )

    pdf.add_section_title("3. Glowing Recap Trigger (RecapButton.tsx):")
    pdf.add_body_text(
        "The primary product feature button is styled with a subtle pulse animation. It dynamically "
        "calculates the estimated recap duration, and displays a multi-phase loading sequence "
        "('Transcribing...' -> 'Summarizing...' -> 'Synthesizing voice...') during the async generation "
        "process to keep users engaged."
    )

    pdf.add_section_title("4. YouTube Ingest with Custom Time Selector:")
    pdf.add_body_text(
        "To allow users to request summaries of YouTube videos immediately, we built a powerful "
        "timestamp options panel. Users check 'Auto-generate recap up to a custom timestamp', "
        "input the minutes and seconds (e.g., 25 mins), and click submit. The frontend captures "
        "this input, converts it to seconds, and redirects the user with a recap_at query parameter."
    )
    
    pdf.add_code_block(
        "// In page.tsx: Detect query parameters on mount\n"
        "useEffect(() => {\n"
        "  const params = new URLSearchParams(window.location.search);\n"
        "  const recapAt = params.get('recap_at');\n"
        "  if (recapAt) setAutoTriggerTime(parseFloat(recapAt));\n"
        "}, []);"
    )

    # ── CHAPTER 5 ────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.add_chapter_title("5", "Deploying & Launching")
    
    pdf.add_body_text(
        "To run the application or package it as a commercial product, we configure both local run "
        "commands and Docker containers."
    )
    
    pdf.add_section_title("1. Run Locally:")
    pdf.add_body_text(
        "To test or develop locally on your machine, activate the Python virtual environment for "
        "the backend, install the dependencies, and start uvicorn. In another terminal, install "
        "frontend dependencies and start the Next.js dev server:"
    )
    pdf.add_code_block(
        "# Terminal 1: Backend\n"
        "cd backend\n"
        "python3 -m venv .venv && source .venv/bin/activate\n"
        "pip install -e .\n"
        "uvicorn app.main:app --reload --port 8000\n"
        "\n"
        "# Terminal 2: Frontend\n"
        "cd frontend\n"
        "npm install\n"
        "npm run dev"
    )

    pdf.add_section_title("2. One-Command Docker Launch:")
    pdf.add_body_text(
        "For seamless containerized deployment, we added a multi-service docker-compose.yml file. "
        "It sets up a shared network, maps backend storage directories, and starts both services in production:"
    )
    pdf.add_code_block(
        "docker-compose up --build"
    )

    pdf.add_section_title("3. Productization & Pitching:")
    pdf.add_body_text(
        "If you want to present this as a product to platforms like Youtube, Spotify, or venture capitalists:\n"
        " - Reference our docs/PRODUCT_BRIEF.md: It includes complete customer journey plans, "
        "market size data, B2B SaaS licensing fee structures, and detailed operating costs.\n"
        " - Emphasize operating margins: With local Whisper transcription and Microsoft Edge TTS, "
        "your ONLY active operating cost is Gemini API tokens (~$0.002 per recap). This represents a "
        "99.5% gross margin, making the product highly lucrative at scale."
    )
    
    pdf.ln(10)
    pdf.set_font('helvetica', 'B', 12)
    pdf.set_text_color(90, 50, 180)
    pdf.cell(0, 10, "Congratulations! You are now ready to dominate the AI Audio Space.", 0, 1, 'C')

    # Output PDF
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    pdf.output(filepath)
    print(f"Successfully generated PDF: {filepath}")

if __name__ == "__main__":
    build_pdf("/Users/sacmad/Projects/rewindcast/docs/RewindCast_StepByStep_Guide.pdf")
