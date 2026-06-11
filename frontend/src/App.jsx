import React, { useState } from 'react';
import Navbar from './components/Navbar';
import HeroSection from './components/HeroSection';
import ResultCard from './components/ResultCard';
import FeatureHighlights from './components/FeatureHighlights';
import SupportedPlatforms from './components/SupportedPlatforms';
import HowItWorks from './components/HowItWorks';
import FAQ from './components/FAQ';
import Footer from './components/Footer';
import ProgressModal from './components/ProgressModal';
import Toast from './components/Toast';
import WebDesignLanding from './components/WebDesignLanding';
import ThptScoreSearch from './components/ThptScoreSearch';
import { api } from './services/api';

function App() {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [analyzeResult, setAnalyzeResult] = useState(null);
  const [activeJobId, setActiveJobId] = useState(null);
  const [toastMsg, setToastMsg] = useState('');
  const [activeView, setActiveView] = useState(() => {
    const path = window.location.pathname;
    if (path === '/nhan-tao-website') return 'webdesign';
    if (path === '/tra-cuu-diem-thi') return 'thpt';
    return 'downloader';
  });

  React.useEffect(() => {
    const handlePopState = () => {
      const path = window.location.pathname;
      if (path === '/nhan-tao-website') setActiveView('webdesign');
      else if (path === '/tra-cuu-diem-thi') setActiveView('thpt');
      else setActiveView('downloader');
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  React.useEffect(() => {
    let title = "Tải Mọi Thứ - Video Downloader";
    let description = "Tải Mọi Thứ - Công cụ tải video trực tuyến chất lượng cao từ YouTube, TikTok, Facebook và nhiều nền tảng khác hoàn toàn miễn phí.";
    let url = "https://taimoithu.com/";

    if (activeView === 'webdesign') {
      title = "Nhận Thiết Kế Website Trọn Gói - Chuyên Nghiệp & Chuẩn SEO";
      description = "Dịch vụ thiết kế website chuyên nghiệp, giao diện hiện đại, chuẩn SEO, tối ưu trải nghiệm người dùng, tốc độ tải trang nhanh chóng.";
      url = "https://taimoithu.com/nhan-tao-website";
    } else if (activeView === 'thpt') {
      title = "Tra Cứu Điểm Thi THPT Quốc Gia - Nhanh Chóng & Chính Xác";
      description = "Tra cứu điểm thi THPT Quốc Gia nhanh chóng, chính xác. Cập nhật dữ liệu điểm thi các môn Toán, Ngữ Văn, Ngoại Ngữ, Lý, Hóa, Sinh, Sử, Địa, GDCD.";
      url = "https://taimoithu.com/tra-cuu-diem-thi";
    }

    document.title = title;

    const setMeta = (name, content, isProperty = false) => {
      const attr = isProperty ? 'property' : 'name';
      let tag = document.querySelector(`meta[${attr}="${name}"]`);
      if (!tag) {
        tag = document.createElement('meta');
        tag.setAttribute(attr, name);
        document.head.appendChild(tag);
      }
      tag.content = content;
    };

    setMeta("description", description);
    setMeta("og:title", title, true);
    setMeta("og:description", description, true);
    setMeta("og:url", url, true);
    setMeta("twitter:title", title);
    setMeta("twitter:description", description);

    let canonical = document.querySelector('link[rel="canonical"]');
    if (!canonical) {
      canonical = document.createElement('link');
      canonical.rel = "canonical";
      document.head.appendChild(canonical);
    }
    canonical.href = url;

  }, [activeView]);

  const navigateTo = (view, slug) => {
    setActiveView(view);
    window.history.pushState({}, '', slug);
  };

  const handleAnalyze = async () => {
    if (!url || !url.trim()) return;
    
    try {
      new URL(url);
    } catch (err) {
      setToastMsg("Vui lòng nhập liên kết video hợp lệ.");
      return;
    }

    setAnalyzeResult(null);
    setIsLoading(true);
    setToastMsg('');
    try {
      const data = await api.analyzeUrl(url);
      setAnalyzeResult(data);
    } catch (err) {
      setToastMsg(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async (formatId, itemIndex = null) => {
    try {
      const data = await api.submitDownload(url, formatId, itemIndex);
      setActiveJobId(data.job_id);
    } catch (err) {
      setToastMsg(err.message);
    }
  };

  const webAppSchema = {
    "@context": "https://schema.org",
    "@type": "WebApplication",
    "name": "Tải Mọi Thứ",
    "url": "https://taimoithu.com/",
    "applicationCategory": "MultimediaApplication",
    "operatingSystem": "All",
    "description": "Công cụ tải video trực tuyến chất lượng cao từ YouTube, TikTok, Facebook và nhiều nền tảng khác hoàn toàn miễn phí."
  };

  const getBreadcrumbSchema = () => {
    let items = [
      {
        "@type": "ListItem",
        "position": 1,
        "name": "Trang Chủ",
        "item": "https://taimoithu.com/"
      }
    ];

    if (activeView === 'webdesign') {
      items.push({
        "@type": "ListItem",
        "position": 2,
        "name": "Nhận Thiết Kế Website",
        "item": "https://taimoithu.com/nhan-tao-website"
      });
    } else if (activeView === 'thpt') {
      items.push({
        "@type": "ListItem",
        "position": 2,
        "name": "Tra Cứu Điểm Thi",
        "item": "https://taimoithu.com/tra-cuu-diem-thi"
      });
    }

    return {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      "itemListElement": items
    };
  };

  return (
    <div className="app-container">
      <Navbar activeView={activeView} navigateTo={navigateTo} />

      <main>
        <div className={activeView === 'downloader' ? '' : 'hidden-view'}>
          <HeroSection 
            url={url} 
            setUrl={setUrl} 
            handleAnalyze={handleAnalyze} 
            isLoading={isLoading} 
            setToastMsg={setToastMsg}
            isActive={activeView === 'downloader'}
          />
          
          {analyzeResult && (
            <section className="result-section section-padding">
              <div className="container">
                <ResultCard 
                  data={analyzeResult} 
                  onDownload={handleDownload} 
                />
              </div>
            </section>
          )}

          <FeatureHighlights />
          <div id="how-it-works"><HowItWorks /></div>
          <SupportedPlatforms />
          <div id="faq"><FAQ isActive={activeView === 'downloader'} /></div>
        </div>

        {activeView === 'webdesign' && (
          <div>
            <WebDesignLanding />
          </div>
        )}

        {activeView === 'thpt' && (
          <div>
            <ThptScoreSearch />
          </div>
        )}
      </main>

      <Footer navigateTo={navigateTo} />

      {activeView === 'downloader' && (
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(webAppSchema) }} />
      )}
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(getBreadcrumbSchema()) }} />

      <ProgressModal 
        jobId={activeJobId} 
        onClose={() => setActiveJobId(null)} 
      />

      <Toast 
        message={toastMsg} 
        onClose={() => setToastMsg('')} 
      />
    </div>
  );
}

export default App;
