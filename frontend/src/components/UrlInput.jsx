import React from 'react';

export default function UrlInput({ value, onChange, onSubmit, isLoading }) {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      onSubmit();
    }
  };

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      onChange(text);
    } catch (err) {
      console.error("Failed to read clipboard", err);
    }
  };

  return (
    <div className="url-input-wrapper">
      <div className={`url-input-container ${isLoading ? 'loading' : ''}`}>
        <input 
          type="text" 
          className="url-input" 
          placeholder="Dán link Video vào đây (Youtube, TikTok, Fb...)" 
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />
        {!value && (
          <button className="btn-paste" onClick={handlePaste} title="Dán từ Clipboard">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
            </svg>
            <span>Dán</span>
          </button>
        )}
        <button 
          className="btn-primary btn-analyze" 
          onClick={onSubmit}
          disabled={isLoading || !value.trim()}
        >
          {isLoading ? (
            <span className="spinner"></span>
          ) : (
            <>
              <span>Bắt đầu</span>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="5" y1="12" x2="19" y2="12"></line>
                <polyline points="12 5 19 12 12 19"></polyline>
              </svg>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
