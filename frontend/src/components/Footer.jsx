import React from 'react';

const Footer = ({ navigateTo }) => {
  const handleNav = (e, targetId) => {
    e.preventDefault();
    if (navigateTo) {
      navigateTo('downloader', '/');
    }
    setTimeout(() => {
      const el = document.getElementById(targetId);
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  return (
    <footer className="footer section-padding">
      <div className="container">
        <div className="footer-content">
          <div className="footer-brand">
            <h3>Tải Mọi Thứ</h3>
            <p>Giải pháp tải video đa nền tảng miễn phí, nhanh chóng và an toàn nhất. Không giới hạn tốc độ, không quảng cáo độc hại.</p>
          </div>
          <div className="footer-links">
            <div className="link-group">
              <h4>Công cụ</h4>
              <a href="/" onClick={(e) => { e.preventDefault(); if(navigateTo) navigateTo('downloader', '/'); }}>Tải Video YouTube</a>
              <a href="/" onClick={(e) => { e.preventDefault(); if(navigateTo) navigateTo('downloader', '/'); }}>Tải Video TikTok</a>
              <a href="/" onClick={(e) => { e.preventDefault(); if(navigateTo) navigateTo('downloader', '/'); }}>Tải Video Facebook</a>
            </div>
            <div className="link-group">
              <h4>Hỗ trợ</h4>
              <a href="/#how-it-works" onClick={(e) => handleNav(e, 'how-it-works')}>Hướng dẫn sử dụng</a>
              <a href="/#faq" onClick={(e) => handleNav(e, 'faq')}>Câu hỏi thường gặp</a>
              <a href="https://zalo.me/0966313528" target="_blank" rel="noopener noreferrer">Liên hệ Zalo</a>
            </div>
            <div className="link-group">
              <h4>Pháp lý</h4>
              <span className="footer-link-dummy">Điều khoản sử dụng</span>
              <span className="footer-link-dummy">Chính sách bảo mật</span>
              <span className="footer-link-dummy">DMCA</span>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; {new Date().getFullYear()} Tải Mọi Thứ. All rights reserved.</p>
          <p className="disclaimer">Chúng tôi không lưu trữ bất kỳ tệp tin nào trên máy chủ của mình. Tất cả nội dung được phân phối trực tiếp từ các nền tảng bên thứ ba.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
