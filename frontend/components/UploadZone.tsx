'use client';

import { useCallback, useRef, useState } from 'react';
import { useRouter } from 'next/navigation';
import { uploadMedia, uploadUrl } from '../lib/api';

export function UploadZone() {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [isDragOver, setIsDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [urlValue, setUrlValue] = useState('');
  const [urlLoading, setUrlLoading] = useState(false);

  // Custom recap timestamp states
  const [customTimestamp, setCustomTimestamp] = useState(false);
  const [minutes, setMinutes] = useState('25');
  const [seconds, setSeconds] = useState('0');

  const handleFile = useCallback(
    async (file: File) => {
      setError(null);
      setUploading(true);
      setUploadProgress(0);

      // Simulate progress since fetch doesn't support progress
      const progressInterval = setInterval(() => {
        setUploadProgress((prev) => Math.min(prev + 5, 90));
      }, 200);

      try {
        const media = await uploadMedia(file);
        clearInterval(progressInterval);
        setUploadProgress(100);
        setTimeout(() => {
          router.push(`/player/${media.id}`);
        }, 500);
      } catch (err) {
        clearInterval(progressInterval);
        setError(err instanceof Error ? err.message : 'Upload failed');
        setUploading(false);
        setUploadProgress(0);
      }
    },
    [router]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => setIsDragOver(false);

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFile(file);
  };

  const handleUrlSubmit = async () => {
    if (!urlValue.trim()) return;
    setError(null);
    setUrlLoading(true);
    try {
      const media = await uploadUrl(urlValue.trim());
      
      let redirectUrl = `/player/${media.id}`;
      if (customTimestamp) {
        const mins = parseInt(minutes || '0');
        const secs = parseInt(seconds || '0');
        const totalSeconds = mins * 60 + secs;
        if (totalSeconds >= 30) {
          redirectUrl += `?recap_at=${totalSeconds}`;
        }
      }
      
      router.push(redirectUrl);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to process URL');
      setUrlLoading(false);
    }
  };

  return (
    <div>
      <div
        className={`upload-zone ${isDragOver ? 'dragover' : ''}`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => fileInputRef.current?.click()}
        role="button"
        tabIndex={0}
        aria-label="Upload audio or video file"
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*,video/mp4,video/webm"
          onChange={handleFileInput}
          style={{ display: 'none' }}
        />

        {uploading ? (
          <div>
            <span className="upload-icon">📡</span>
            <p className="upload-title">Uploading...</p>
            <div className="upload-progress">
              <div className="upload-progress-bar">
                <div
                  className="upload-progress-fill"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
              <p className="upload-progress-text">{uploadProgress}%</p>
            </div>
          </div>
        ) : (
          <div>
            <span className="upload-icon">🎵</span>
            <p className="upload-title">Drop your audio or video file here</p>
            <p className="upload-subtitle">
              Supports MP3, WAV, M4A, MP4, WebM — up to 500MB
            </p>
          </div>
        )}
      </div>

      <div className="upload-divider">or paste a YouTube URL</div>

      <div className="url-input-group">
        <input
          type="url"
          className="url-input"
          placeholder="https://youtube.com/watch?v=..."
          value={urlValue}
          onChange={(e) => setUrlValue(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleUrlSubmit()}
          disabled={urlLoading}
        />
        <button
          className="btn btn-primary"
          onClick={handleUrlSubmit}
          disabled={urlLoading || !urlValue.trim()}
        >
          {urlLoading ? (
            <span className="spinner" />
          ) : (
            '→'
          )}
        </button>
      </div>

      {/* Modern Advanced Recap Options Panel */}
      <div className="url-options-panel" style={{ marginTop: '1rem', padding: '1rem', borderRadius: '12px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.05)', textAlign: 'left' }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontSize: '0.9rem', color: '#ccc' }}>
          <input
            type="checkbox"
            checked={customTimestamp}
            onChange={(e) => setCustomTimestamp(e.target.checked)}
            style={{ accentColor: 'var(--color-accent)', width: '16px', height: '16px', cursor: 'pointer' }}
          />
          ⚡ Auto-generate recap up to a custom timestamp
        </label>
        
        {customTimestamp && (
          <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginTop: '0.75rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <input
                type="number"
                min="0"
                placeholder="25"
                value={minutes}
                onChange={(e) => setMinutes(e.target.value)}
                style={{ width: '65px', padding: '0.4rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.1)', background: 'rgba(0,0,0,0.3)', color: '#fff', textAlign: 'center', outline: 'none' }}
              />
              <span style={{ fontSize: '0.85rem', color: '#aaa' }}>min</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
              <input
                type="number"
                min="0"
                max="59"
                placeholder="0"
                value={seconds}
                onChange={(e) => setSeconds(e.target.value)}
                style={{ width: '65px', padding: '0.4rem', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.1)', background: 'rgba(0,0,0,0.3)', color: '#fff', textAlign: 'center', outline: 'none' }}
              />
              <span style={{ fontSize: '0.85rem', color: '#aaa' }}>sec</span>
            </div>
            <div style={{ fontSize: '0.8rem', color: 'var(--color-accent)' }}>
              (Recapping first {(parseInt(minutes || '0') * 60 + parseInt(seconds || '0'))} seconds of the podcast)
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="error-banner" style={{ marginTop: '1rem' }}>
          ⚠️ {error}
        </div>
      )}
    </div>
  );
}
