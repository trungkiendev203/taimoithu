import React from 'react';
import UrlInput from './UrlInput';

const HeroSection = ({ url, setUrl, handleAnalyze, isLoading }) => {
  return (
    <section className="hero-section section-padding">
      <div className="container hero-container">
        <h1 className="hero-title">Tải video chất lượng cao từ <span>mọi nền tảng</span></h1>
        <p className="hero-subtitle">
          Công cụ tải video trực tuyến miễn phí tốt nhất. Hỗ trợ 1080p, 4K, tải âm thanh gốc không giảm chất lượng từ YouTube, TikTok, Facebook và hơn thế nữa.
        </p>
        
        <div className="hero-action">
          <UrlInput 
            value={url} 
            onChange={setUrl} 
            onSubmit={handleAnalyze} 
            isLoading={isLoading} 
          />
          <p className="hero-security-note">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
            An toàn 100% • Không yêu cầu cài đặt phần mềm • Tải xuống tức thì
          </p>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;
