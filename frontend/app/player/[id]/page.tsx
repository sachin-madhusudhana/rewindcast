'use client';

import { useEffect, useState, useCallback } from 'react';
import { useParams } from 'next/navigation';
import { MediaPlayer } from '../../../components/MediaPlayer';
import { RecapButton } from '../../../components/RecapButton';
import { RecapModal } from '../../../components/RecapModal';
import { getMedia, getMediaFileUrl } from '../../../lib/api';
import { MediaItem, RecapResponse } from '../../../lib/types';

export default function PlayerPage() {
  const params = useParams();
  const mediaId = params.id as string;

  const [media, setMedia] = useState<MediaItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [recap, setRecap] = useState<RecapResponse | null>(null);
  const [showRecapModal, setShowRecapModal] = useState(false);
  const [autoTriggerTime, setAutoTriggerTime] = useState<number | undefined>(undefined);

  useEffect(() => {
    if (!mediaId) return;
    setLoading(true);
    getMedia(mediaId)
      .then((m) => {
        setMedia(m);
        // Check localStorage for saved progress
        const saved = localStorage.getItem(`rewindcast_progress_${mediaId}`);
        if (saved) {
          setCurrentTime(parseFloat(saved));
        }
      })
      .catch((err) => {
        setError(err.message || 'Failed to load media');
      })
      .finally(() => setLoading(false));
  }, [mediaId]);

  // Read recap_at query param on client mount to trigger automatic recap if requested
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const urlParams = new URLSearchParams(window.location.search);
      const recapAt = urlParams.get('recap_at');
      if (recapAt) {
        const seconds = parseFloat(recapAt);
        if (!isNaN(seconds) && seconds >= 30) {
          setAutoTriggerTime(seconds);
        }
      }
    }
  }, []);

  const handleTimeUpdate = useCallback((time: number) => {
    setCurrentTime(time);
  }, []);

  const handleRecapReady = useCallback((recapData: RecapResponse) => {
    setRecap(recapData);
    setShowRecapModal(true);
  }, []);

  const handleContinueListening = useCallback(() => {
    setShowRecapModal(false);
    // The MediaPlayer will resume from its saved position
  }, []);

  if (loading) {
    return (
      <div className="container player-container">
        <div className="player-card">
          <div
            className="skeleton"
            style={{ height: 32, width: '60%', margin: '0 auto 1.5rem' }}
          />
          <div
            className="skeleton"
            style={{ height: 60, marginBottom: '1.5rem' }}
          />
          <div className="skeleton" style={{ height: 56 }} />
        </div>
      </div>
    );
  }

  if (error || !media) {
    return (
      <div className="container player-container">
        <div className="empty-state">
          <span className="empty-state-icon">😕</span>
          <h2 className="empty-state-title">Media Not Found</h2>
          <p className="empty-state-text">
            {error || "We couldn't find this media. It may have been deleted."}
          </p>
          <a href="/" className="btn btn-primary" style={{ marginTop: '1.5rem' }}>
            ← Back to Home
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="container player-container">
      <MediaPlayer
        mediaId={media.id}
        title={media.title}
        audioUrl={getMediaFileUrl(media.id)}
        durationSeconds={media.duration_seconds}
        onTimeUpdate={handleTimeUpdate}
      />

      <RecapButton
        mediaId={media.id}
        listenedSeconds={currentTime}
        onRecapReady={handleRecapReady}
        autoTriggerTime={autoTriggerTime}
      />

      {showRecapModal && recap && (
        <RecapModal
          recap={recap}
          onClose={() => setShowRecapModal(false)}
          onContinueListening={handleContinueListening}
        />
      )}
    </div>
  );
}
