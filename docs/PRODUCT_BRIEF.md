# RewindCast — Product Brief

## Executive Summary

**RewindCast** is an AI-powered recap engine that generates personalized,
spoken summaries of previously consumed podcast and audio content. When a
listener returns to a partially-finished episode, they receive a 2-3 minute
audio recap of everything they already heard — eliminating the "where was I?"
friction that causes 60% of podcast listeners to abandon episodes.

---

## Problem Statement

### The "Lost Context" Problem

- **500M+** people listen to podcasts globally (Spotify, Apple, YouTube)
- Average podcast episode length: **45-90 minutes**
- Average completion rate: **only 40%**
- **#1 reason** for abandonment: forgetting context after pausing

When a listener pauses a podcast and returns days later, they face a bad choice:
1. **Rewind** — wastes 15-30 minutes re-listening
2. **Skip ahead** — misses context, gets confused
3. **Give up** — drops the episode entirely

All three outcomes hurt the listener, the creator, and the platform.

### Impact on Revenue

For platforms like Spotify (ad-supported podcasts):
- Each abandoned episode = **lost mid-roll ad impressions**
- A 10% improvement in completion = **10% more ad revenue**
- For a $200M/year podcast ad business, that's **$20M in recovered revenue**

---

## Solution

### One-Tap Recap

RewindCast adds a single button — **"Recap"** — to any podcast player. When
tapped, it:

1. **Identifies** the portion the user already listened to
2. **Transcribes** that audio segment using Whisper AI
3. **Summarizes** it into a concise, engaging narrative using Gemini
4. **Narrates** the summary as a 2-3 minute spoken audio clip
5. **Plays** the recap, then seamlessly continues playback

The entire process takes 15-30 seconds. The user hears something like:

> *"Previously on this episode: The host discussed how AI is transforming
> healthcare diagnostics, highlighting three key challenges: data quality,
> regulatory compliance, and building patient trust. Dr. Smith from Stanford
> shared that their new model achieved 94% accuracy on mammogram analysis,
> but cautioned that human oversight remains critical. And that's where we
> pick back up..."*

---

## Market Opportunity

| Segment | Size | Opportunity |
|---------|------|-------------|
| Podcast Platforms | $5B market, 500M listeners | Core product |
| Audiobooks | $8B market, 150M listeners | Natural extension |
| Online Courses | $400B market, video lectures | High pain point |
| Meeting Recordings | $50B collaboration market | Enterprise opportunity |

### Total Addressable Market

**$500M+** — assuming 1B podcast episodes consumed per month, even at $0.005/recap
with 10% adoption rate.

---

## Revenue Models

### 1. B2B Platform License (Primary)

Sell directly to Spotify, YouTube, Apple Podcasts, etc.

| Tier | Price | Includes |
|------|-------|----------|
| Starter | $5,000/mo | Up to 100K recaps/mo |
| Growth | $20,000/mo | Up to 1M recaps/mo |
| Enterprise | Custom | Unlimited, dedicated infra |

### 2. API / SDK (Developer)

Allow any podcast app or platform to integrate RewindCast.

- **Pay-per-use**: $0.01 - $0.05 per recap
- **Monthly plans**: Starting at $99/mo for indie developers

### 3. Premium User Feature

Platforms can upsell RewindCast as a premium feature:

- **Spotify Premium add-on**: $1-2/mo
- **Apple Podcasts+**: Built into subscription
- Revenue share model: 70/30 split with platform

---

## Cost Analysis

| Component | Cost per Recap | Provider |
|-----------|---------------|----------|
| Transcription | ~$0.001 | faster-whisper (self-hosted) |
| Summarization | ~$0.001 | Google Gemini 2.5 Flash |
| Text-to-Speech | $0.000 | Edge TTS (free) |
| Infrastructure | ~$0.0005 | Cloud compute |
| **Total** | **~$0.003** | — |

At $0.01/recap pricing → **70% gross margin**
At $0.05/recap pricing → **94% gross margin**

---

## Competitive Landscape

| Feature | RewindCast | Podcast Notes Apps | Snipd | YouTube Summaries |
|---------|------------|-------------------|-------|-------------------|
| Timestamp-aware recap | ✅ | ❌ | ❌ | ❌ |
| Spoken audio recap | ✅ | ❌ | ❌ | ❌ |
| Personalized to progress | ✅ | ❌ | Partial | ❌ |
| Real-time generation | ✅ | ❌ | ❌ | ❌ |
| Platform-embeddable | ✅ | ❌ | ❌ | ❌ |
| Works with any audio | ✅ | ❌ | Partial | YouTube only |

**Key differentiator**: No existing product generates timestamp-aware, personalized spoken recaps. All current solutions either provide full-episode summaries (not personalized) or text-only notes (not audio).

---

## Technical Architecture

```
User opens episode → Progress tracked → User returns later
                                          ↓
                                    Click "Recap"
                                          ↓
                              ┌─── Extract listened portion ───┐
                              ↓                                 ↓
                     Whisper Transcribe                         │
                              ↓                                 │
                     Gemini Summarize                           │
                     (Map-Reduce for long content)              │
                              ↓                                 │
                     Edge TTS → Audio                           │
                              ↓                                 │
                     Play Recap → Continue from saved position ─┘
```

### Scaling Considerations

- **Transcription caching**: Each media is transcribed once, cached for all users
- **Summary caching**: Same timestamp ± 30s can reuse existing recaps
- **Edge TTS**: Zero-cost at any scale (uses Microsoft's CDN)
- **Gemini Flash**: Fast, cheap, high-quality at scale

---

## Roadmap

### Phase 1: MVP (Current)
- [x] File upload + YouTube import
- [x] Whisper transcription
- [x] Gemini summarization
- [x] Edge TTS audio generation
- [x] Web demo with premium UI

### Phase 2: Platform Ready
- [ ] REST API with authentication & rate limiting
- [ ] Multi-language support (50+ languages via Whisper)
- [ ] Speaker diarization ("Host said X, Guest replied Y")
- [ ] Customizable recap styles (bullet points, narrative, brief)

### Phase 3: Enterprise
- [ ] SDK for iOS/Android embedding
- [ ] Real-time streaming recap (as user listens)
- [ ] Recap analytics dashboard
- [ ] A/B testing framework for recap styles

### Phase 4: Platform Intelligence
- [ ] Cross-episode context ("Last episode, we covered...")
- [ ] Personalized emphasis based on user interests
- [ ] Recap in the creator's voice (voice cloning)
- [ ] Smart notifications ("You haven't finished 3 episodes")

---

## Contact

For partnership inquiries, platform integrations, or investment discussions:

📧 [your-email@example.com]

---

*RewindCast — Because every listener deserves a "Previously On..."*
