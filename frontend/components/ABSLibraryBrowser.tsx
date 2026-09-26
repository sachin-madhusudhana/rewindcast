'use client';

import { useState } from 'react';
import { ABSLibrary } from '../lib/types';

interface ABSLibraryBrowserProps {
  libraries: ABSLibrary[];
}

function mediaIcon(mediaType: string): string {
  switch (mediaType) {
    case 'podcast':
      return '🎙️';
    case 'book':
      return '📖';
    case 'music':
      return '🎵';
    default:
      return '📁';
  }
}

export function ABSLibraryBrowser({ libraries }: ABSLibraryBrowserProps) {
  const [activeTab, setActiveTab] = useState<string | null>(
    libraries.length > 0 ? libraries[0].id : null,
  );

  if (libraries.length === 0) {
    return (
      <div className="abs-library-browser">
        <h2 className="abs-section-title">📚 Libraries</h2>
        <div className="empty-state" style={{ padding: 'var(--space-8)' }}>
          <div className="empty-state-icon">📂</div>
          <p className="empty-state-title">No libraries found</p>
          <p className="empty-state-text">
            Add libraries to your Audiobookshelf server to browse them here.
          </p>
        </div>
      </div>
    );
  }

  const activeLibrary = libraries.find((lib) => lib.id === activeTab);

  return (
    <div className="abs-library-browser">
      <h2 className="abs-section-title">📚 Libraries</h2>

      {/* Tab Row */}
      <div className="abs-library-tabs">
        {libraries.map((lib) => (
          <button
            key={lib.id}
            className={`abs-library-tab ${
              activeTab === lib.id ? 'abs-library-tab--active' : ''
            }`}
            onClick={() => setActiveTab(lib.id)}
          >
            {mediaIcon(lib.media_type)} {lib.name}
          </button>
        ))}
      </div>

      {/* Library Content Grid */}
      <div className="abs-library-grid">
        {libraries
          .filter((lib) => !activeTab || lib.id === activeTab)
          .map((lib) => (
            <div key={lib.id} className="abs-library-card">
              <div className="abs-library-card-icon">
                {mediaIcon(lib.media_type)}
              </div>
              <div className="abs-library-card-info">
                <h3>{lib.name}</h3>
                <p className="abs-library-card-meta">
                  {lib.media_type.charAt(0).toUpperCase() + lib.media_type.slice(1)}
                </p>
              </div>
              <div className="abs-library-card-count">
                <span className="abs-library-count-number">{lib.item_count}</span>
                <span className="abs-library-count-label">items</span>
              </div>
            </div>
          ))}
      </div>

      {activeLibrary && (
        <div className="abs-library-detail">
          <p className="abs-library-detail-text">
            {mediaIcon(activeLibrary.media_type)}{' '}
            <strong>{activeLibrary.name}</strong> contains{' '}
            <strong>{activeLibrary.item_count}</strong>{' '}
            {activeLibrary.media_type === 'podcast' ? 'podcasts' : 'books'}
          </p>
        </div>
      )}
    </div>
  );
}
