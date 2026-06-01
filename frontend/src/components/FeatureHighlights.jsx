import React from 'react';

const FeatureHighlights = () => {
  const features = [
    {
      title: "Chất lượng 1080p & 4K",
      description: "Hỗ trợ tải video ở độ phân giải gốc cao nhất, giữ nguyên độ nét của hình ảnh và âm thanh gốc.",
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <rect x="2" y="7" width="20" height="15" rx="2" ry="2"></rect>
          <polyline points="17 2 12 7 7 2"></polyline>
        </svg>
      )
    },
    {
      title: "Tốc độ siêu tốc",
      description: "Hệ thống tải đa luồng độc quyền giúp tải các video dài hoặc dung lượng lớn chỉ trong chớp mắt.",
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
        </svg>
      )
    },
    {
      title: "Âm thanh gốc M4A/AAC",
      description: "Thuật toán tối ưu tự động chọn và ghép luồng âm thanh tốt nhất, đảm bảo có tiếng 100% trên mọi thiết bị.",
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M9 18V5l12-2v13"></path>
          <circle cx="6" cy="18" r="3"></circle>
          <circle cx="18" cy="16" r="3"></circle>
        </svg>
      )
    },
    {
      title: "Không đóng dấu (No Watermark)",
      description: "Tự động tải video nguyên bản không chứa logo hoặc watermark từ nền tảng gốc như TikTok.",
      icon: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="4.93" y1="4.93" x2="19.07" y2="19.07"></line>
        </svg>
      )
    }
  ];

  return (
    <section className="features-section section-padding">
      <div className="container">
        <h2 className="section-title">Tại sao chọn Tải Mọi Thứ?</h2>
        <p className="section-subtitle">Trải nghiệm tính năng vượt trội được thiết kế riêng cho bạn</p>
        
        <div className="features-grid">
          {features.map((feature, idx) => (
            <div className="feature-card" key={idx}>
              <div className="feature-icon">{feature.icon}</div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeatureHighlights;
