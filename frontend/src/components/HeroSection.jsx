import React, { useState } from 'react';
import UrlInput from './UrlInput';
import BatchDownload from './BatchDownload';

const HeroSection = ({ url, setUrl, handleAnalyze, isLoading, setToastMsg, isActive }) => {
  const [activeTab, setActiveTab] = useState('single'); // 'single' or 'batch'

  const TitleTag = isActive ? 'h1' : 'div';

  return (
    <section className="hero-section section-padding">
      <div className="container hero-container">
        <TitleTag className="hero-title">Tải video chất lượng cao từ <span>mọi nền tảng</span></TitleTag>
        <p className="hero-subtitle">
          Công cụ tải video trực tuyến miễn phí tốt nhất. Hỗ trợ 1080p, 4K, tải âm thanh gốc không giảm chất lượng từ YouTube, TikTok, Facebook và hơn thế nữa.
        </p>
        
        <div className="hero-action">
          <div className="download-tabs">
            <button 
              className={`download-tab-btn tab-single ${activeTab === 'single' ? 'active' : ''}`}
              onClick={() => setActiveTab('single')}
            >
              Tải 1 video
            </button>
            <button 
              className={`download-tab-btn tab-batch ${activeTab === 'batch' ? 'active' : ''}`}
              onClick={() => setActiveTab('batch')}
            >
              <svg className="tab-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="21 8 21 21 3 21 3 8"></polyline><rect x="1" y="3" width="22" height="5"></rect><line x1="10" y1="12" x2="14" y2="12"></line></svg>
              Tải nhiều video
            </button>
          </div>

          {activeTab === 'single' ? (
            <UrlInput 
              value={url} 
              onChange={setUrl} 
              onSubmit={handleAnalyze} 
              isLoading={isLoading} 
            />
          ) : (
            <BatchDownload setToastMsg={setToastMsg} />
          )}

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
