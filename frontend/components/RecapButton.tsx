'use client';

import { useState, useEffect } from 'react';
import { generateRecap, getRecapAudioUrl } from '../lib/api';
import { RecapResponse } from '../lib/types';

interface RecapButtonProps {
  mediaId: string;
  listenedSeconds: number;
  onRecapReady: (recap: RecapResponse) => void;
  autoTriggerTime?: number;
}

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

function getEstimatedRecapTimeText(seconds: number): string {
  if (seconds <= 60) return '10s';
  if (seconds <= 300) return '20s';
  if (seconds <= 900) return '30-40s';
  if (seconds <= 3600) return '1-2m';
  return '2-3m';
}

const LOADING_PHASES = [
  { text: 'Transcribing audio...', icon: '🎙️' },
  { text: 'Summarizing content...', icon: '🧠' },
  { text: 'Generating audio recap...', icon: '🔊' },
];

export function RecapButton({
  mediaId,
  listenedSeconds,
  onRecapReady,
  autoTriggerTime,
}: RecapButtonProps) {
  const [loading, setLoading] = useState(false);
  const [loadingPhase, setLoadingPhase] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [hasAutoTriggered, setHasAutoTriggered] = useState(false);

  const handleClick = async (timeOverride?: number) => {
    const targetTime = timeOverride ?? listenedSeconds;
    setLoading(true);
    setError(null);
    setLoadingPhase(0);

    // Progress through loading phases on a timer
    const phaseInterval = setInterval(() => {
      setLoadingPhase((prev) =>
        prev < LOADING_PHASES.length - 1 ? prev + 1 : prev
      );
    }, 8000);

    try {
      const recap = await generateRecap({
        media_id: mediaId,
        listened_until_seconds: targetTime,
        style: 'conversational',
      });

      // Rewrite audio_url to use our API client helper
      recap.audio_url = getRecapAudioUrl(recap.id);
      onRecapReady(recap);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate recap');
    } finally {
      clearInterval(phaseInterval);
      setLoading(false);
    }
  };

  // Auto-trigger recap if autoTriggerTime parameter is passed from YouTube URL input
  useEffect(() => {
    if (autoTriggerTime && autoTriggerTime >= 30 && !hasAutoTriggered && !loading) {
      setHasAutoTriggered(true);
      handleClick(autoTriggerTime);
    }
  }, [autoTriggerTime, hasAutoTriggered, loading]);

  if (listenedSeconds < 30 && !autoTriggerTime) return null;

  return (
    <div className="recap-section">
      <button
        className={`recap-btn ${loading ? 'loading' : 'pulse'}`}
        onClick={() => handleClick()}
        disabled={loading}
      >
        {loading ? (
          <>
            <div className="spinner" />
            <span className="recap-btn-label">
              {LOADING_PHASES[loadingPhase].icon}{' '}
              {LOADING_PHASES[loadingPhase].text}
            </span>
            <span className="recap-btn-sub">This may take a minute...</span>
          </>
        ) : (
          <>
            <span className="recap-btn-icon">⏪</span>
            <span className="recap-btn-label">
              Recap {formatDuration(listenedSeconds)} of listening
            </span>
            <span className="recap-btn-sub">
              ~{getEstimatedRecapTimeText(listenedSeconds)} summary
            </span>
          </>
        )}
      </button>

      {error && (
        <div className="error-banner" style={{ marginTop: '1rem', maxWidth: 500, margin: '1rem auto' }}>
          ⚠️ {error}
        </div>
      )}
    </div>
  );
}
