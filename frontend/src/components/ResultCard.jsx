import React, { useState } from 'react';
import { API_BASE } from '../services/api';

const MediaItemCard = ({ title, author, item, onDownload }) => {
  const [selectedFormat, setSelectedFormat] = useState(
    item.formats.length > 0 ? item.formats[0].format_id : ''
  );

  const getImageUrl = (url) => {
    if (url && url.startsWith('/api/v1')) {
      return API_BASE.replace('/api/v1', '') + url;
    }
    return url;
  };

  return (
    <div className="result-card media-item-card">
      <div className="result-image-wrapper">
        {item.thumbnail_url ? (
          <img src={getImageUrl(item.thumbnail_url)} alt="Thumbnail" className="result-image" />
        ) : (
          <div className="placeholder-img">No Image</div>
        )}
        <div className="result-duration">
          {item.is_video ? '🎬 Video' : '🖼️ Ảnh'}
        </div>
      </div>
      
      <div className="result-info">
        <div className="result-header">
          <h2 className="result-title" title={title}>{title} {item.index ? `(Phần ${item.index})` : ''}</h2>
          <p className="result-author">👤 {author || 'Unknown Author'}</p>
        </div>
        
        <div className="format-selection">
          <label>Chất lượng tải xuống:</label>
          <div className="quality-grid">
            {item.formats.map((f) => (
              <div 
                key={f.format_id} 
                className={`quality-card ${selectedFormat === f.format_id ? 'selected' : ''}`}
                onClick={() => setSelectedFormat(f.format_id)}
              >
                <div className="quality-type">
                  {f.type === 'video' ? '🎬 Video' : f.type === 'audio' ? '🎵 Audio' : '🖼️ Ảnh'}
                </div>
                <div className="quality-label">{f.quality_label}</div>
                {f.estimated_size_bytes && (
                  <div className="quality-size">~{Math.round(f.estimated_size_bytes / 1024 / 1024)}MB</div>
                )}
              </div>
            ))}
          </div>
        </div>

        <button 
          className="btn-primary download-btn"
          onClick={() => onDownload(selectedFormat, item.index || null)}
          disabled={!selectedFormat}
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          Tải xuống ngay
        </button>
      </div>
    </div>
  );
};

export default function ResultCard({ data, onDownload }) {
  if (data.media_items && data.media_items.length > 0) {
    return (
      <div className="media-carousel-grid">
        <h3 className="carousel-title" style={{marginBottom: '1rem', color: 'var(--text-main)', textAlign: 'center', fontSize: '1.5rem', fontWeight: 600}}>
          Có {data.media_items.length} mục trong bài viết
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {data.media_items.map(item => (
            <MediaItemCard 
              key={item.index} 
              title={data.title} 
              author={data.author_name} 
              item={item} 
              onDownload={onDownload} 
            />
          ))}
        </div>
      </div>
    );
  }

  // Fallback cho single item
  const singleItem = {
    thumbnail_url: data.thumbnail_url,
    is_video: data.duration_seconds !== null,
    formats: data.formats,
  };

  return (
    <MediaItemCard 
      title={data.title}
      author={data.author_name}
      item={singleItem}
      onDownload={onDownload}
    />
  );
}
