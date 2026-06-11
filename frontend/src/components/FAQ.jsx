import React, { useState } from 'react';

const FAQ = () => {
  const faqs = [
    {
      question: "Tải Mọi Thứ có an toàn và bảo mật không?",
      answer: "Tuyệt đối an toàn. Chúng tôi không lưu trữ lịch sử tải xuống, không yêu cầu cài đặt phần mềm và không chứa quảng cáo độc hại. Mọi tiến trình tải được thực hiện trực tiếp thông qua API mã hóa."
    },
    {
      question: "Tôi có thể tải video độ phân giải 4K không?",
      answer: "Có. Nếu video gốc được đăng tải với chất lượng 4K (trên YouTube, Vimeo...), hệ thống của chúng tôi sẽ tự động bắt được độ phân giải đó để bạn tải về hoàn toàn miễn phí."
    },
    {
      question: "Tại sao tải video TikTok lại không có logo?",
      answer: "Thuật toán của chúng tôi tự động trích xuất luồng video sạch (nguyên bản) trực tiếp từ máy chủ của TikTok trước khi họ đóng dấu Watermark."
    },
    {
      question: "Có giới hạn số lần tải mỗi ngày không?",
      answer: "Hoàn toàn không. Bạn có thể sử dụng Tải Mọi Thứ không giới hạn số lượng và dung lượng tải mỗi ngày."
    }
  ];

  const [openIdx, setOpenIdx] = useState(0);

  const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": faqs.map(faq => ({
      "@type": "Question",
      "name": faq.question,
      "acceptedAnswer": {
        "@type": "Answer",
        "text": faq.answer
      }
    }))
  };

  return (
    <section className="faq-section section-padding">
      <div className="container faq-container">
        <h2 className="section-title">Câu hỏi thường gặp</h2>
        
        <div className="faq-list">
          {faqs.map((faq, idx) => (
            <div className={`faq-item ${openIdx === idx ? 'open' : ''}`} key={idx} onClick={() => setOpenIdx(openIdx === idx ? -1 : idx)}>
              <div className="faq-question">
                <h3>{faq.question}</h3>
                <span className="faq-toggle">{openIdx === idx ? '−' : '+'}</span>
              </div>
              <div className="faq-answer">
                <p>{faq.answer}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqSchema) }} />
    </section>
  );
};

export default FAQ;
