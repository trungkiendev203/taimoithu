import React from 'react';

const HowItWorks = () => {
  const steps = [
    {
      number: "01",
      title: "Copy Link Video",
      description: "Mở ứng dụng (YouTube, TikTok, FB) và sao chép đường link của video bạn muốn tải."
    },
    {
      number: "02",
      title: "Dán & Phân tích",
      description: "Dán link vào ô nhập liệu phía trên và nhấn 'Bắt đầu' để hệ thống bẻ khóa dữ liệu."
    },
    {
      number: "03",
      title: "Chọn & Tải xuống",
      description: "Chọn định dạng (1080p, 720p, MP3) và nhấn Tải về. File sẽ tự động lưu vào máy của bạn."
    }
  ];

  return (
    <section className="how-it-works-section section-padding bg-tertiary">
      <div className="container">
        <h2 className="section-title">Cách hoạt động</h2>
        <p className="section-subtitle">Chỉ 3 bước đơn giản để lưu trữ video yêu thích</p>
        
        <div className="steps-container">
          {steps.map((step, idx) => (
            <div className="step-card" key={idx}>
              <div className="step-number">{step.number}</div>
              <h3 className="step-title">{step.title}</h3>
              <p className="step-description">{step.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
