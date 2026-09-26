'use client';

import { useEffect, useRef, useState } from 'react';
import { RecapResponse } from '../lib/types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface RecapModalProps {
  recap: RecapResponse;
  onClose: () => void;
  onContinueListening: () => void;
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

export function RecapModal({
  recap,
  onClose,
  onContinueListening,
}: RecapModalProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const overlayRef = useRef<HTMLDivElement>(null);

  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  // Close on Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  // Prevent body scroll
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = '';
    };
  }, []);

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === overlayRef.current) onClose();
  };

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (playing) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setPlaying(!playing);
  };

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div
      className="modal-overlay"
      ref={overlayRef}
      onClick={handleOverlayClick}
    >
      <div className="modal-content">
        <div className="modal-header">
          <h3 className="modal-title">
            ✨ Your Recap
          </h3>
          <button className="modal-close" onClick={onClose} aria-label="Close">
            ✕
          </button>
        </div>

        <div className="modal-body">
          {/* Recap Audio Player */}
          {recap.audio_url && (
            <div className="recap-audio-player">
              <audio
                ref={audioRef}
                src={recap.audio_url ? `${API_BASE}${recap.audio_url}` : undefined}
                onTimeUpdate={() => {
                  if (audioRef.current) {
                    setCurrentTime(audioRef.current.currentTime);
                  }
                }}
                onLoadedMetadata={() => {
                  if (audioRef.current) {
                    setDuration(audioRef.current.duration);
                  }
                }}
                onEnded={() => setPlaying(false)}
                preload="metadata"
              />

              <button
                className="recap-play-btn"
                onClick={togglePlay}
                aria-label={playing ? 'Pause recap' : 'Play recap'}
              >
                {playing ? '⏸' : '▶'}
              </button>

              <div className="recap-audio-progress" style={{ flex: 1 }}>
                <div className="progress-bar-track">
                  <div
                    className="progress-bar-fill"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <div className="progress-time" style={{ marginTop: '0.25rem' }}>
                  <span>{formatTime(currentTime)}</span>
                  <span>{formatTime(recap.estimated_listen_seconds || duration)}</span>
                </div>
              </div>
            </div>
          )}

          {/* Summary Text */}
          <div className="recap-summary">{recap.summary_text}</div>

          {/* Key Points */}
          {recap.key_points && recap.key_points.length > 0 && (
            <div>
              <p className="key-points-title">Key Points</p>
              <div className="key-points-list">
                {recap.key_points.map((point, index) => (
                  <span key={index} className="key-point-pill">
                    💡 {point}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          <button
            className="btn btn-primary btn-lg"
            onClick={onContinueListening}
          >
            ▶ Continue Listening
          </button>
        </div>
      </div>
    </div>
  );
}
