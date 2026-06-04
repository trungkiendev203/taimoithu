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
import { api } from './services/api';

function App() {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [analyzeResult, setAnalyzeResult] = useState(null);
  const [activeJobId, setActiveJobId] = useState(null);
  const [toastMsg, setToastMsg] = useState('');

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

  return (
    <div className="app-container">
      <Navbar />

      <main>
        <HeroSection 
          url={url} 
          setUrl={setUrl} 
          handleAnalyze={handleAnalyze} 
          isLoading={isLoading} 
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
        <HowItWorks />
        <SupportedPlatforms />
        <FAQ />
      </main>

      <Footer />

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
