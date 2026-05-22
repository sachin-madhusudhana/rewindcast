'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { UploadZone } from '../components/UploadZone';
import { listMedia } from '../lib/api';
import { MediaItem } from '../lib/types';

function formatDuration(seconds: number | null | undefined): string {
  if (!seconds) return '—';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (h > 0) return `${h}h ${m}m`;
  return `${m} min`;
}

export default function HomePage() {
  const [mediaItems, setMediaItems] = useState<MediaItem[]>([]);

  useEffect(() => {
    listMedia()
      .then(setMediaItems)
      .catch(() => {});
  }, []);

  return (
    <>
      {/* ── Hero ─────────────────────────────────────────────── */}
      <section className="hero">
        <div className="hero-orb hero-orb-1" />
        <div className="hero-orb hero-orb-2" />
        <div className="hero-orb hero-orb-3" />

        <div className="container" style={{ position: 'relative', zIndex: 1 }}>
          <div className="hero-badge">
            ✨ AI-Powered Podcast Recaps
          </div>

          <h1 className="hero-title">
            Never Lose Your
            <br />
            <span className="gradient-text">Place Again</span>
          </h1>

          <p className="hero-subtitle">
            Pick up any podcast right where you left off with a personalized,
            AI-generated spoken summary of everything you&apos;ve already heard.
          </p>

          <a href="#try-it" className="btn btn-primary btn-lg">
            Try It Now →
          </a>
        </div>
      </section>

      {/* ── How It Works ─────────────────────────────────────── */}
      <section className="section" id="how-it-works">
        <div className="container">
          <div className="section-heading">
            <h2>How It Works</h2>
            <p>Three simple steps to never lose context again</p>
          </div>

          <div className="steps-grid">
            <div className="glass-card step-card">
              <span className="step-number">1</span>
              <span className="step-icon">🎧</span>
              <h3 className="step-title">Listen</h3>
              <p className="step-description">
                Play any podcast, audiobook, or long-form audio. We
                automatically track your progress as you listen.
              </p>
            </div>

            <div className="glass-card step-card">
              <span className="step-number">2</span>
              <span className="step-icon">💤</span>
              <h3 className="step-title">Take a Break</h3>
              <p className="step-description">
                Life happens. Come back hours, days, or weeks later
                — your progress is always saved.
              </p>
            </div>

            <div className="glass-card step-card">
              <span className="step-number">3</span>
              <span className="step-icon">⏪</span>
              <h3 className="step-title">Get Your Recap</h3>
              <p className="step-description">
                One tap generates a 2-3 minute spoken summary of
                what you already heard. Then jump right back in.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Upload / Try It ──────────────────────────────────── */}
      <section className="section" id="try-it">
        <div className="container-narrow">
          <div className="section-heading">
            <h2>Try It Now</h2>
            <p>Upload a podcast episode or paste a YouTube link</p>
          </div>

          <div style={{ marginTop: '2rem' }}>
            <UploadZone />
          </div>

          {/* Previously uploaded media */}
          {mediaItems.length > 0 && (
            <div style={{ marginTop: '3rem' }}>
              <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem', color: 'var(--color-text-secondary)' }}>
                Your Library
              </h3>
              <div className="media-list">
                {mediaItems.map((item) => (
                  <Link
                    key={item.id}
                    href={`/player/${item.id}`}
                    className="media-item"
                  >
                    <div className="media-item-icon">🎧</div>
                    <div className="media-item-info">
                      <p className="media-item-title">{item.title}</p>
                      <p className="media-item-meta">
                        {formatDuration(item.duration_seconds)}
                      </p>
                    </div>
                    <span className="media-item-arrow">→</span>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      </section>

      {/* ── Built for Platforms ───────────────────────────────── */}
      <section className="section">
        <div className="container">
          <div className="section-heading">
            <h2>Built for Platforms</h2>
            <p>Integrate RewindCast into any audio experience</p>
          </div>

          <div className="platforms-grid">
            <div className="platform-card">
              <span className="platform-icon">🟢</span>
              <span className="platform-name">Spotify</span>
            </div>
            <div className="platform-card">
              <span className="platform-icon">🔴</span>
              <span className="platform-name">YouTube</span>
            </div>
            <div className="platform-card">
              <span className="platform-icon">🟣</span>
              <span className="platform-name">Apple Podcasts</span>
            </div>
            <div className="platform-card">
              <span className="platform-icon">🟠</span>
              <span className="platform-name">Audible</span>
            </div>
            <div className="platform-card">
              <span className="platform-icon">🔵</span>
              <span className="platform-name">Overcast</span>
            </div>
          </div>
        </div>
      </section>

      {/* ── Footer ───────────────────────────────────────────── */}
      <footer className="footer">
        <div className="container">
          <p>
            ⏪ RewindCast — AI-powered recaps for podcasts
          </p>
          <div className="footer-links">
            <a href="https://github.com" target="_blank" rel="noopener noreferrer">
              GitHub
            </a>
            <a href="#how-it-works">How it Works</a>
            <a href="#try-it">Try It</a>
          </div>
        </div>
      </footer>
    </>
  );
}
