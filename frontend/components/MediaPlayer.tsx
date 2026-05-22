'use client';

import { useCallback, useEffect, useRef, useState } from 'react';

interface MediaPlayerProps {
  mediaId: string;
  title: string;
  audioUrl: string;
  durationSeconds?: number;
  onTimeUpdate?: (currentTime: number) => void;
  onSeek?: (time: number) => void;
}

const SPEEDS = [0.5, 0.75, 1, 1.25, 1.5, 2];

function formatTime(seconds: number): string {
  if (!seconds || isNaN(seconds)) return '0:00';
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) {
    return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  }
  return `${m}:${s.toString().padStart(2, '0')}`;
}

export function MediaPlayer({
  mediaId,
  title,
  audioUrl,
  durationSeconds,
  onTimeUpdate,
  onSeek,
}: MediaPlayerProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const progressRef = useRef<HTMLDivElement>(null);

  const [playing, setPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(durationSeconds || 0);
  const [speed, setSpeed] = useState(1);
  const [showResume, setShowResume] = useState(false);
  const [savedTime, setSavedTime] = useState(0);

  // Check for saved progress on mount
  useEffect(() => {
    const saved = localStorage.getItem(`rewindcast_progress_${mediaId}`);
    if (saved) {
      const time = parseFloat(saved);
      if (time > 10) {
        setSavedTime(time);
        setShowResume(true);
      }
    }
  }, [mediaId]);

  // Save progress periodically
  useEffect(() => {
    const interval = setInterval(() => {
      if (audioRef.current && currentTime > 0) {
        localStorage.setItem(
          `rewindcast_progress_${mediaId}`,
          currentTime.toString()
        );
      }
    }, 5000);
    return () => clearInterval(interval);
  }, [mediaId, currentTime]);

  const handleTimeUpdate = useCallback(() => {
    if (audioRef.current) {
      const time = audioRef.current.currentTime;
      setCurrentTime(time);
      onTimeUpdate?.(time);
    }
  }, [onTimeUpdate]);

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
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

  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!progressRef.current || !audioRef.current) return;
    const rect = progressRef.current.getBoundingClientRect();
    const fraction = (e.clientX - rect.left) / rect.width;
    const newTime = fraction * duration;
    audioRef.current.currentTime = newTime;
    setCurrentTime(newTime);
    onSeek?.(newTime);
  };

  const handleSpeedChange = (newSpeed: number) => {
    setSpeed(newSpeed);
    if (audioRef.current) {
      audioRef.current.playbackRate = newSpeed;
    }
  };

  const handleResume = () => {
    if (audioRef.current) {
      audioRef.current.currentTime = savedTime;
      setCurrentTime(savedTime);
      audioRef.current.play();
      setPlaying(true);
    }
    setShowResume(false);
  };

  const handleDismissResume = () => {
    setShowResume(false);
  };

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  // Generate decorative waveform bars
  const waveformBars = Array.from({ length: 40 }, (_, i) => {
    const barProgress = (i / 40) * 100;
    const isActive = barProgress <= progress;
    const height = 15 + Math.sin(i * 0.7) * 25 + Math.cos(i * 1.3) * 15;
    return (
      <div
        key={i}
        className={`waveform-bar ${isActive ? 'active' : ''}`}
        style={{
          height: playing
            ? `${height + Math.sin(Date.now() / 200 + i) * 10}%`
            : `${height}%`,
        }}
      />
    );
  });

  return (
    <div className="player-card">
      <audio
        ref={audioRef}
        src={audioUrl}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={() => setPlaying(false)}
        preload="metadata"
      />

      <h2 className="player-title">{title}</h2>

      {showResume && (
        <div className="resume-prompt">
          <p>📍 Resume from {formatTime(savedTime)}?</p>
          <button className="btn btn-accent" onClick={handleResume} style={{ padding: '0.4rem 1rem', fontSize: '0.8rem' }}>
            Resume
          </button>
          <button className="btn btn-secondary" onClick={handleDismissResume} style={{ padding: '0.4rem 1rem', fontSize: '0.8rem' }}>
            Start Over
          </button>
        </div>
      )}

      <div className="player-waveform">{waveformBars}</div>

      <div className="player-controls">
        <button
          className="play-btn"
          onClick={togglePlay}
          aria-label={playing ? 'Pause' : 'Play'}
        >
          {playing ? '⏸' : '▶'}
        </button>

        <div className="progress-wrapper">
          <div
            className="progress-bar-track"
            ref={progressRef}
            onClick={handleProgressClick}
          >
            <div
              className="progress-bar-fill"
              style={{ width: `${progress}%` }}
            />
          </div>
          <div className="progress-time">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>
      </div>

      <div className="player-extras">
        {SPEEDS.map((s) => (
          <button
            key={s}
            className={`speed-btn ${speed === s ? 'active' : ''}`}
            onClick={() => handleSpeedChange(s)}
          >
            {s}x
          </button>
        ))}
      </div>
    </div>
  );
}
