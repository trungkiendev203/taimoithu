import React from 'react';

const SupportedPlatforms = () => {
  const activePlatforms = [
    { name: "YouTube", color: "#FF0000" },
    { name: "TikTok", color: "#000000" },
    { name: "Facebook", color: "#1877F2" },
    { name: "Instagram", color: "#E1306C" },
    { name: "X (Twitter)", color: "#1DA1F2" }
  ];

  const comingSoonPlatforms = [
    "Reddit", "Pinterest", "Twitch", "Vimeo", "SoundCloud"
  ];

  return (
    <section className="platforms-section section-padding">
      <div className="container">
        <h2 className="section-title">Hỗ trợ đa nền tảng</h2>
        <p className="section-subtitle">Tải nội dung bạn yêu thích từ bất cứ đâu</p>
        
        <div className="platforms-container">
          <div className="active-platforms">
            <h3>Hoạt động tốt nhất</h3>
            <div className="platform-pills">
              {activePlatforms.map((p, idx) => (
                <div className="platform-pill active" key={idx} style={{'--pill-color': p.color}}>
                  <span className="dot"></span>
                  {p.name}
                </div>
              ))}
            </div>
          </div>
          
          <div className="coming-soon-platforms">
            <h3>Đang được tối ưu</h3>
            <div className="platform-pills">
              {comingSoonPlatforms.map((name, idx) => (
                <div className="platform-pill soon" key={idx}>
                  {name}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default SupportedPlatforms;
