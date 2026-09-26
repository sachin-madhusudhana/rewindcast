'use client';

import { ABSStatusResponse } from '../lib/types';

interface ABSConnectionStatusProps {
  status: ABSStatusResponse;
  onRefresh: () => void;
  loading?: boolean;
}

export function ABSConnectionStatus({
  status,
  onRefresh,
  loading = false,
}: ABSConnectionStatusProps) {
  const isConnected = status.connected;

  return (
    <div
      className={`abs-connection-status ${
        isConnected ? 'abs-connected' : 'abs-disconnected'
      }`}
    >
      <div className="abs-status-indicator">
        <span className={`abs-status-dot ${isConnected ? 'abs-dot-green' : 'abs-dot-red'}`} />
        <div className="abs-status-text">
          {isConnected ? (
            <>
              <strong>Connected to Audiobookshelf</strong>
              <span className="abs-status-detail">
                {status.server_url}
                {status.username && (
                  <> &middot; Logged in as <em>{status.username}</em></>
                )}
              </span>
            </>
          ) : (
            <>
              <strong>Not Connected</strong>
              <span className="abs-status-detail abs-status-error">
                {status.error || 'Configure ABS_SERVER_URL and ABS_API_TOKEN in your .env file'}
              </span>
            </>
          )}
        </div>
      </div>

      <button
        className="btn btn-secondary abs-refresh-btn"
        onClick={onRefresh}
        disabled={loading}
        aria-label="Refresh connection status"
      >
        {loading ? (
          <span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
        ) : (
          '↻'
        )}{' '}
        Refresh
      </button>
    </div>
  );
}
