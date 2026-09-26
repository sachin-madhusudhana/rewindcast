'use client';

import { useEffect, useState, useCallback } from 'react';
import {
  ABSStatusResponse,
  ABSItemSummary,
  ABSLibrary,
  RecapResponse,
} from '../../lib/types';
import {
  getABSStatus,
  getABSInProgress,
  getABSLibraries,
  generateABSRecap,
} from '../../lib/api';
import { ABSConnectionStatus } from '../../components/ABSConnectionStatus';
import { ABSContinueListening } from '../../components/ABSContinueListening';
import { ABSLibraryBrowser } from '../../components/ABSLibraryBrowser';
import { RecapModal } from '../../components/RecapModal';

export default function AudiobookshelfPage() {
  // ── State ──────────────────────────────────────────────────────
  const [status, setStatus] = useState<ABSStatusResponse | null>(null);
  const [items, setItems] = useState<ABSItemSummary[]>([]);
  const [libraries, setLibraries] = useState<ABSLibrary[]>([]);

  const [statusLoading, setStatusLoading] = useState(true);
  const [dataLoading, setDataLoading] = useState(false);
  const [recapLoadingItemId, setRecapLoadingItemId] = useState<string | null>(null);

  const [error, setError] = useState<string | null>(null);
  const [recap, setRecap] = useState<RecapResponse | null>(null);

  // ── Fetch helpers ──────────────────────────────────────────────
  const fetchStatus = useCallback(async () => {
    setStatusLoading(true);
    setError(null);
    try {
      const res = await getABSStatus();
      setStatus(res);
      return res;
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to fetch status';
      setStatus({
        connected: false,
        server_url: null,
        username: null,
        error: message,
      });
      return null;
    } finally {
      setStatusLoading(false);
    }
  }, []);

  const fetchData = useCallback(async () => {
    setDataLoading(true);
    try {
      const [inProgress, libs] = await Promise.all([
        getABSInProgress(),
        getABSLibraries(),
      ]);
      setItems(inProgress);
      setLibraries(libs);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to load data';
      setError(message);
    } finally {
      setDataLoading(false);
    }
  }, []);

  // ── Init ───────────────────────────────────────────────────────
  useEffect(() => {
    (async () => {
      const s = await fetchStatus();
      if (s?.connected) {
        await fetchData();
      }
    })();
  }, [fetchStatus, fetchData]);

  // ── Recap handler ──────────────────────────────────────────────
  const handleRecap = async (itemId: string) => {
    setRecapLoadingItemId(itemId);
    setError(null);
    try {
      const result = await generateABSRecap(itemId);
      setRecap(result);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to generate recap';
      setError(message);
    } finally {
      setRecapLoadingItemId(null);
    }
  };

  const handleRefresh = async () => {
    const s = await fetchStatus();
    if (s?.connected) {
      await fetchData();
    }
  };

  // ── Render ─────────────────────────────────────────────────────
  return (
    <div className="abs-page">
      {/* Hero Banner */}
      <section className="abs-hero">
        <div className="hero-orb hero-orb-1" />
        <div className="hero-orb hero-orb-2" />
        <div className="hero-orb hero-orb-3" />
        <div className="container">
          <h1 className="abs-hero-title">
            📚 <span className="gradient-text">Audiobookshelf</span> Integration
          </h1>
          <p className="abs-hero-subtitle">
            Connect your Audiobookshelf library and get AI-powered recaps of
            everything you&apos;ve been listening to. Pick up right where you
            left off.
          </p>
        </div>
      </section>

      {/* Content */}
      <div className="abs-content container">
        {/* Connection Status */}
        {status && (
          <ABSConnectionStatus
            status={status}
            onRefresh={handleRefresh}
            loading={statusLoading}
          />
        )}

        {/* Loading state while fetching initial status */}
        {statusLoading && !status && (
          <div className="empty-state">
            <div className="spinner" style={{ margin: '0 auto var(--space-4)' }} />
            <p className="loading-text">Connecting to Audiobookshelf…</p>
          </div>
        )}

        {/* Error banner */}
        {error && (
          <div className="error-banner" style={{ marginBottom: 'var(--space-6)' }}>
            ⚠️ {error}
          </div>
        )}

        {/* Not connected guidance */}
        {status && !status.connected && !statusLoading && (
          <div className="glass-card" style={{ marginTop: 'var(--space-8)', textAlign: 'center' }}>
            <div style={{ fontSize: '3rem', marginBottom: 'var(--space-4)' }}>🔌</div>
            <h3 style={{ fontSize: 'var(--text-xl)', marginBottom: 'var(--space-3)' }}>
              Configure Your Connection
            </h3>
            <p style={{ color: 'var(--color-text-secondary)', lineHeight: 1.8, maxWidth: 500, margin: '0 auto' }}>
              Set the following environment variables in your backend <code>.env</code> file to connect
              to your Audiobookshelf server:
            </p>
            <pre
              style={{
                marginTop: 'var(--space-4)',
                padding: 'var(--space-4)',
                background: 'var(--color-bg)',
                border: '1px solid var(--color-border)',
                borderRadius: 'var(--radius-md)',
                textAlign: 'left',
                fontSize: 'var(--text-sm)',
                color: 'var(--color-accent)',
                display: 'inline-block',
              }}
            >
              {`ABS_SERVER_URL=http://your-server:13378\nABS_API_TOKEN=your-api-token`}
            </pre>
          </div>
        )}

        {/* Connected — show content */}
        {status?.connected && (
          <>
            {dataLoading ? (
              <div className="empty-state" style={{ padding: 'var(--space-12)' }}>
                <div className="spinner" style={{ margin: '0 auto var(--space-4)' }} />
                <p className="loading-text">Loading your library…</p>
              </div>
            ) : (
              <>
                <ABSContinueListening
                  items={items}
                  onRecap={handleRecap}
                  loadingItemId={recapLoadingItemId}
                />
                <ABSLibraryBrowser libraries={libraries} />
              </>
            )}
          </>
        )}
      </div>

      {/* Recap Modal */}
      {recap && (
        <RecapModal
          recap={recap}
          onClose={() => setRecap(null)}
          onContinueListening={() => setRecap(null)}
        />
      )}
    </div>
  );
}
