import React from 'react';
import './WebDesignLanding.css';

const IconCart = () => <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="9" cy="21" r="1"></circle><circle cx="20" cy="21" r="1"></circle><path d="M1 1h4l2.68 13.39a2 2 0 0 0 2 1.61h9.72a2 2 0 0 0 2-1.61L23 6H6"></path></svg>;
const IconUser = () => <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>;
const IconCoffee = () => <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M18 8h1a4 4 0 0 1 0 8h-1"></path><path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path><line x1="6" y1="1" x2="6" y2="4"></line><line x1="10" y1="1" x2="10" y2="4"></line><line x1="14" y1="1" x2="14" y2="4"></line></svg>;
const IconTarget = () => <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>;

const WebDesignLanding = () => {
  return (
    <div className="webdesign-landing">
      <div className="container">
        {/* HERO SECTION */}
        <section className="wd-hero">
          <div className="wd-hero-bg-glow"></div>
          <div className="wd-hero-content">
            <h1 className="wd-hero-title">
              Kiến tạo <span className="wd-text-gradient">Website</span><br /> Đẳng cấp & Khác biệt
            </h1>
            <p className="wd-hero-subtitle">
              Nâng tầm thương hiệu của bạn với thiết kế chuẩn UX/UI, tối ưu SEO vượt trội, tốc độ tải trang thần tốc và tích hợp thanh toán tự động toàn diện.
            </p>
            <div className="wd-hero-actions">
              <a href="https://zalo.me/0966313528" target="_blank" rel="noreferrer" className="wd-btn wd-btn-primary">
                <span className="wd-btn-text">Liên hệ Zalo tư vấn</span>
                <div className="wd-btn-glow"></div>
              </a>
              <a href="https://zalo.me/0966313528" target="_blank" rel="noreferrer" className="wd-btn wd-btn-outline">
                Xem kho giao diện mẫu
              </a>
            </div>
          </div>
        </section>

        {/* SERVICES SECTION */}
        <section className="wd-services">
          <div className="wd-section-header">
            <h2 className="wd-section-title">Giải pháp <span className="wd-text-gradient">Đa ngành</span></h2>
            <p className="wd-section-desc">Chúng tôi cung cấp các gói thiết kế tối ưu hóa cho từng lĩnh vực kinh doanh cụ thể của bạn.</p>
          </div>
          <div className="wd-grid wd-grid-4">
            <div className="wd-card">
              <div className="wd-card-icon-wrapper wd-icon-blue">
                <IconCart />
              </div>
              <h3>Website Bán Hàng</h3>
              <p>Tích hợp giỏ hàng thông minh, quản lý kho, voucher và thanh toán online đa cổng (VNPay, Momo, thẻ tín dụng).</p>
            </div>
            <div className="wd-card">
              <div className="wd-card-icon-wrapper wd-icon-purple">
                <IconUser />
              </div>
              <h3>Profile Thương Hiệu</h3>
              <p>Trang giới thiệu công ty hoặc portfolio cá nhân sang trọng, tạo ấn tượng mạnh mẽ với đối tác và khách hàng.</p>
            </div>
            <div className="wd-card">
              <div className="wd-card-icon-wrapper wd-icon-orange">
                <IconCoffee />
              </div>
              <h3>Nhà Hàng & Dịch Vụ</h3>
              <p>Hiển thị menu trực quan bắt mắt, hệ thống đặt bàn và gọi món online mượt mà ngay trên điện thoại.</p>
            </div>
            <div className="wd-card">
              <div className="wd-card-icon-wrapper wd-icon-green">
                <IconTarget />
              </div>
              <h3>Landing Page Ads</h3>
              <p>Trang đích chuẩn AIDA, thiết kế hút mắt tối đa hóa tỷ lệ chuyển đổi cho các chiến dịch quảng cáo FB/Google.</p>
            </div>
          </div>
        </section>

        {/* FEATURES SECTION */}
        <section className="wd-features">
          <div className="wd-features-inner">
            <div className="wd-section-header">
              <h2 className="wd-section-title">Công nghệ <span className="wd-text-gradient">Vượt trội</span></h2>
            </div>
            <div className="wd-grid wd-grid-3">
              <div className="wd-feature-item">
                <div className="wd-feature-icon">🚀</div>
                <div>
                  <h4>Tốc độ siêu tốc</h4>
                  <p>Load trang dưới 1s, kiến trúc hiện đại, tối ưu điểm Google PageSpeed.</p>
                </div>
              </div>
              <div className="wd-feature-item">
                <div className="wd-feature-icon">📱</div>
                <div>
                  <h4>Chuẩn Responsive</h4>
                  <p>Tương thích hoàn hảo mọi thiết bị Mobile, Tablet, Desktop, Smart TV.</p>
                </div>
              </div>
              <div className="wd-feature-item">
                <div className="wd-feature-icon">🔍</div>
                <div>
                  <h4>Tối ưu SEO Onpage</h4>
                  <p>Cấu trúc HTML semantic, URL thân thiện, tự động tạo Sitemap và Schema.</p>
                </div>
              </div>
              <div className="wd-feature-item">
                <div className="wd-feature-icon">🛡️</div>
                <div>
                  <h4>Bảo mật tuyệt đối</h4>
                  <p>Tích hợp SSL miễn phí, chống DDoS, bảo vệ an toàn dữ liệu khách hàng.</p>
                </div>
              </div>
              <div className="wd-feature-item">
                <div className="wd-feature-icon">💳</div>
                <div>
                  <h4>Thanh toán tự động</h4>
                  <p>Kết nối API ngân hàng, ví điện tử, tự động xác nhận đơn khi có biến động số dư.</p>
                </div>
              </div>
              <div className="wd-feature-item">
                <div className="wd-feature-icon">⚙️</div>
                <div>
                  <h4>Admin trực quan</h4>
                  <p>Quản trị CMS dễ sử dụng, kéo thả thân thiện không cần kiến thức lập trình.</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* PROCESS SECTION */}
        <section className="wd-process">
          <div className="wd-section-header">
            <h2 className="wd-section-title">Quy trình <span className="wd-text-gradient">Triển khai</span></h2>
          </div>
          <div className="wd-process-timeline">
            <div className="wd-process-step">
              <div className="wd-step-number">01</div>
              <div className="wd-step-content">
                <h4>Phân tích Yêu cầu</h4>
                <p>Khảo sát chuyên sâu, xác định chân dung khách hàng mục tiêu và tư vấn tính năng lõi.</p>
              </div>
            </div>
            <div className="wd-process-step">
              <div className="wd-step-number">02</div>
              <div className="wd-step-content">
                <h4>Thiết kế UI/UX</h4>
                <p>Lên bản vẽ mockup độc quyền, chốt giao diện đến khi khách hàng hoàn toàn ưng ý.</p>
              </div>
            </div>
            <div className="wd-process-step">
              <div className="wd-step-number">03</div>
              <div className="wd-step-content">
                <h4>Phát triển & Test</h4>
                <p>Code bằng công nghệ mới nhất, kiểm thử khắt khe trên nhiều trình duyệt và thiết bị.</p>
              </div>
            </div>
            <div className="wd-process-step">
              <div className="wd-step-number">04</div>
              <div className="wd-step-content">
                <h4>Bàn giao & Hỗ trợ</h4>
                <p>Cài đặt lên server chính thức, training sử dụng và bảo trì kỹ thuật miễn phí lâu dài.</p>
              </div>
            </div>
          </div>
        </section>

        {/* CTA SECTION */}
        <section className="wd-cta">
          <div className="wd-cta-bg"></div>
          <div className="wd-cta-content">
            <h2>Khởi tạo Website của riêng bạn ngay hôm nay</h2>
            <p>Liên hệ Zalo để nhận báo giá chi tiết và các ưu đãi mới nhất.</p>
            <a href="https://zalo.me/0966313528" target="_blank" rel="noreferrer" className="wd-btn wd-btn-primary wd-btn-large">
              Chat Zalo: 0966.313.528
            </a>
          </div>
        </section>
      </div>
    </div>
  );
};

export default WebDesignLanding;

