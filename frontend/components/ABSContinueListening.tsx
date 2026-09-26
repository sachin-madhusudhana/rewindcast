'use client';

import { ABSItemSummary } from '../lib/types';

interface ABSContinueListeningProps {
  items: ABSItemSummary[];
  onRecap: (itemId: string) => void;
  loadingItemId?: string | null;
}

function formatTime(totalSeconds: number): string {
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = Math.floor(totalSeconds % 60);

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds
      .toString()
      .padStart(2, '0')}`;
  }
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

export function ABSContinueListening({
  items,
  onRecap,
  loadingItemId,
}: ABSContinueListeningProps) {
  if (items.length === 0) {
    return (
      <div className="abs-continue-section">
        <h2 className="abs-section-title">⏯ Continue Listening</h2>
        <div className="empty-state" style={{ padding: 'var(--space-8)' }}>
          <div className="empty-state-icon">📭</div>
          <p className="empty-state-title">No items in progress</p>
          <p className="empty-state-text">
            Start listening to something on Audiobookshelf to see it here.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="abs-continue-section">
      <h2 className="abs-section-title">⏯ Continue Listening</h2>
      <div className="abs-card-row">
        {items.map((item) => {
          const isLoading = loadingItemId === item.id;

          return (
            <div key={item.id} className="abs-item-card">
              {/* Cover */}
              <div className="abs-card-cover">
                {item.cover_url ? (
                  <img
                    src={item.cover_url}
                    alt={item.title}
                    loading="lazy"
                  />
                ) : (
                  <div className="abs-card-cover-fallback">
                    <span>{item.media_type === 'podcast' ? '🎙️' : '📖'}</span>
                  </div>
                )}
              </div>

              {/* Info */}
              <div className="abs-card-info">
                <h3 className="abs-card-title">{item.title}</h3>
                {item.episode_title && (
                  <p className="abs-card-episode">{item.episode_title}</p>
                )}
                {item.author && (
                  <p className="abs-card-author">{item.author}</p>
                )}
              </div>

              {/* Progress */}
              <div className="abs-card-progress">
                <div className="abs-progress-track">
                  <div
                    className="abs-progress-fill"
                    style={{
                      width: `${Math.min(item.progress_percent * 100, 100)}%`,
                    }}
                  />
                </div>
                <div className="abs-progress-time">
                  <span>{formatTime(item.current_time)}</span>
                  <span>{formatTime(item.duration_seconds)}</span>
                </div>
              </div>

              {/* Recap Button */}
              <button
                className={`abs-recap-btn ${isLoading ? 'loading' : ''}`}
                onClick={() => onRecap(item.id)}
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <span
                      className="spinner"
                      style={{ width: 14, height: 14, borderWidth: 2 }}
                    />{' '}
                    Generating…
                  </>
                ) : (
                  <>⏪ Recap</>
                )}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
