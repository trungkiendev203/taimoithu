import React, { useState, useEffect } from 'react';
import FeedbackModal from './FeedbackModal';

const Navbar = ({ activeView, navigateTo }) => {
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light');
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <nav className="navbar">
      <div className="container navbar-container">
        <div className="navbar-logo">
          <svg aria-hidden="true" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM11 19.93C7.05 19.43 4 16.05 4 12C4 7.95 7.05 4.57 11 4.07V19.93ZM13 4.07C16.95 4.57 20 7.95 20 12C20 16.05 16.95 19.43 13 19.93V4.07Z" fill="var(--color-primary)"/>
          </svg>
          <span>Tải Mọi Thứ</span>
        </div>
        
        <div className="navbar-center-menu">
          <a 
            href="/"
            className={`nav-menu-btn ${activeView === 'downloader' ? 'active' : ''}`}
            aria-current={activeView === 'downloader' ? 'page' : undefined}
            onClick={(e) => { e.preventDefault(); navigateTo('downloader', '/'); }}
          >
            Công cụ tải video
          </a>
          <a 
            href="/nhan-tao-website"
            className={`nav-menu-btn ${activeView === 'webdesign' ? 'active' : ''}`}
            aria-current={activeView === 'webdesign' ? 'page' : undefined}
            onClick={(e) => { e.preventDefault(); navigateTo('webdesign', '/nhan-tao-website'); }}
          >
            Nhận tạo website
          </a>
          <a 
            href="/tra-cuu-diem-thi"
            className={`nav-menu-btn ${activeView === 'thpt' ? 'active' : ''}`}
            aria-current={activeView === 'thpt' ? 'page' : undefined}
            onClick={(e) => { e.preventDefault(); navigateTo('thpt', '/tra-cuu-diem-thi'); }}
          >
            Tra cứu điểm thi
          </a>
        </div>

        <div className="navbar-actions">
          <button className="feedback-btn" onClick={() => setIsFeedbackOpen(true)} aria-label="Góp ý">
            Góp ý
          </button>
          <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle Dark Mode">
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
        </div>
      </div>
      <FeedbackModal isOpen={isFeedbackOpen} onClose={() => setIsFeedbackOpen(false)} />
    </nav>
  );
};

export default Navbar;
