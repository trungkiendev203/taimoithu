import React from 'react';

const Footer = () => {
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
              <a href="#">Tải Video YouTube</a>
              <a href="#">Tải Video TikTok</a>
              <a href="#">Tải Video Facebook</a>
            </div>
            <div className="link-group">
              <h4>Hỗ trợ</h4>
              <a href="#">Hướng dẫn sử dụng</a>
              <a href="#">Câu hỏi thường gặp</a>
              <a href="#">Liên hệ</a>
            </div>
            <div className="link-group">
              <h4>Pháp lý</h4>
              <a href="#">Điều khoản sử dụng</a>
              <a href="#">Chính sách bảo mật</a>
              <a href="#">DMCA</a>
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
