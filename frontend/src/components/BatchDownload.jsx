import React, { useState, useEffect, useRef } from 'react';
import { batchApi } from '../services/batchApi';

// SVG Icons
const IconClipboard = () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>;
const IconRocket = () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"></path><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"></path><path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"></path><path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"></path></svg>;
const IconCheck = () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>;
const IconX = () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>;
const IconClock = () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>;
const IconArchive = () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="21 8 21 21 3 21 3 8"></polyline><rect x="1" y="3" width="22" height="5"></rect><line x1="10" y1="12" x2="14" y2="12"></line></svg>;
const IconDownload = () => <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>;
const IconRefresh = () => <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>;

const BatchDownload = ({ setToastMsg }) => {
  const [inputText, setInputText] = useState('');
  const [urls, setUrls] = useState([]);
  const [batchId, setBatchId] = useState(null);
  const [batchState, setBatchState] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const pollingRef = useRef(null);

  useEffect(() => {
    const lines = inputText.split('\n').map(line => line.trim()).filter(line => line.length > 0);
    setUrls(lines);
  }, [inputText]);

  const stopPolling = () => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  };

  useEffect(() => {
    return () => stopPolling();
  }, []);

  const handlePasteClipboard = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setInputText(prev => prev + (prev ? '\n' : '') + text);
    } catch (err) {
      if (setToastMsg) setToastMsg("Không thể đọc từ clipboard. Vui lòng dán thủ công.");
    }
  };

  const handleSubmit = async () => {
    if (urls.length === 0) return;
    if (urls.length > 5) {
      if (setToastMsg) setToastMsg("Hệ thống hiện chỉ hỗ trợ tối đa 5 liên kết cùng lúc.");
      return;
    }

    setIsSubmitting(true);
    try {
      const data = await batchApi.createBatch(urls);
      setBatchId(data.batch_id);
      startPolling(data.batch_id);
    } catch (err) {
      if (setToastMsg) setToastMsg(err.message);
      setIsSubmitting(false);
    }
  };

  const startPolling = (id) => {
    stopPolling();
    fetchBatchStatus(id);
    pollingRef.current = setInterval(() => {
      fetchBatchStatus(id);
    }, 3000);
  };

  const fetchBatchStatus = async (id) => {
    try {
      const data = await batchApi.getBatchStatus(id);
      setBatchState(data);
      if (data.status === 'completed' || data.status === 'failed') {
        stopPolling();
        setIsSubmitting(false);
      }
    } catch (err) {
      console.error("Batch poll error:", err);
    }
  };

  const resetBatch = () => {
    stopPolling();
    setBatchId(null);
    setBatchState(null);
    setInputText('');
    setUrls([]);
    setIsSubmitting(false);
  };

  // Calculations
  const total = batchState?.total_items || 0;
  const completed = batchState?.completed_items || 0;
  const failedCount = batchState?.items?.filter(i => i.status === 'failed').length || 0;
  const processed = completed + failedCount;
  
  const progressPercent = total > 0 ? Math.round((processed / total) * 100) : 0;
  const isCreatingZip = batchState?.status === 'processing' && processed === total && total > 0;
  
  const isOverLimit = urls.length > 5;
  const isValid = urls.length > 0 && !isOverLimit;

  // View 1: Input Form
  if (!batchId) {
    return (
      <div className="premium-batch-card fade-in">
        <div className="premium-batch-hero">
          <div className="premium-hero-icon">
            <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="21 8 21 21 3 21 3 8"></polyline><rect x="1" y="3" width="22" height="5"></rect><line x1="10" y1="12" x2="14" y2="12"></line></svg>
          </div>
          <h2 className="premium-hero-title">Tải nhiều video</h2>
          <p className="premium-hero-subtitle">
            Tải tối đa 5 liên kết cùng lúc.<br />Hệ thống sẽ tự động tải và đóng gói thành ZIP.
          </p>
        </div>
        
        <div className="premium-hero-divider"></div>

        <div className="premium-batch-input-area">
          <textarea
            className={`premium-batch-textarea ${isOverLimit ? 'has-error' : ''}`}
            placeholder="https://youtube.com/watch?v=...&#10;https://youtube.com/watch?v=...&#10;https://youtube.com/watch?v=..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={isSubmitting}
          ></textarea>
        </div>

        <div className="premium-batch-action-bar">
          <span className={`premium-batch-counter ${isOverLimit ? 'error' : (urls.length > 0 ? 'valid' : '')}`}>
            {urls.length}/5 liên kết
          </span>
          <div className="premium-batch-buttons">
            <button className="premium-btn premium-btn-outline" onClick={handlePasteClipboard} disabled={isSubmitting}>
              <IconClipboard /> <span className="btn-text">Dán từ Clipboard</span>
            </button>
            <button 
              className={`premium-btn premium-btn-primary ${isSubmitting ? 'loading' : ''}`}
              onClick={handleSubmit}
              disabled={isSubmitting || !isValid}
            >
              <IconRocket /> {isSubmitting ? 'Đang khởi tạo...' : 'Bắt đầu tải'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // View 3: Ready / Success
  if (batchState?.status === 'completed' || (batchState?.status === 'failed' && batchState?.zip_url)) {
    return (
      <div className="premium-batch-card fade-in center-content">
        <div className="premium-ready-icon">
          <IconCheck />
        </div>
        <h2 className="premium-ready-title">Batch hoàn tất!</h2>
        <p className="premium-ready-subtitle">Đã tải thành công {completed}/{total} video.</p>
        
        <div className="premium-ready-stats">
          <div className="stat-item success">
            <span className="stat-value">{completed}</span>
            <span className="stat-label">Thành công</span>
          </div>
          <div className="stat-item failed">
            <span className="stat-value">{failedCount}</span>
            <span className="stat-label">Thất bại</span>
          </div>
        </div>

        <div className="premium-ready-actions">
          {batchState.zip_url && (
            <button 
              className="premium-btn premium-btn-giant premium-btn-primary" 
              onClick={async () => {
                try {
                  const url = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'}/batch/download/batch_${batchState.batch_id}.zip`;
                  const res = await fetch(url);
                  if (!res.ok) throw new Error('Download failed');
                  const blob = await res.blob();
                  const blobUrl = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = blobUrl;
                  a.download = `batch_${batchState.batch_id}.zip`;
                  document.body.appendChild(a);
                  a.click();
                  document.body.removeChild(a);
                  URL.revokeObjectURL(blobUrl);
                } catch (err) {
                  console.error('Download error:', err);
                }
              }}
            >
              <IconDownload /> TẢI XUỐNG ZIP
            </button>
          )}
          <button className="premium-btn premium-btn-outline mt-4" onClick={resetBatch}>
            <IconRefresh /> Tạo batch mới
          </button>
        </div>
      </div>
    );
  }

  // View 2: Queue / Dashboard
  return (
    <div className="premium-batch-card fade-in">
      <div className="premium-queue-header">
        <div className="queue-header-left">
          <span className="queue-percentage">{progressPercent}%</span>
          <span className="queue-status-text">
            {isCreatingZip ? "Đang nén file ZIP..." : `${processed} / ${total} video hoàn thành`}
          </span>
        </div>
        {(batchState?.status === 'processing' || batchState?.status === 'pending') && (
          <div className="premium-spinner"></div>
        )}
      </div>

      <div className="premium-progress-track">
        <div className="premium-progress-fill" style={{ width: `${progressPercent}%` }}></div>
      </div>

      <div className="premium-queue-list">
        {batchState?.items?.map((item) => {
          let statusConfig = { text: "Chờ xử lý", class: "pending", icon: <IconClock /> };
          if (item.status === "processing") statusConfig = { text: "Đang tải...", class: "processing", icon: <div className="premium-spinner-small"></div> };
          else if (item.status === "completed") statusConfig = { text: "Thành công", class: "completed", icon: <IconCheck /> };
          else if (item.status === "failed") statusConfig = { text: "Thất bại", class: "failed", icon: <IconX /> };

          return (
            <div className={`premium-queue-item status-${statusConfig.class}`} key={item.index}>
              <div className="queue-item-icon">{statusConfig.icon}</div>
              <div className="queue-item-content">
                <div className="queue-item-title" title={item.url}>
                  {item.title || item.url}
                </div>
                {item.error_message && (
                  <div className="queue-item-error" title={item.error_message}>
                    {item.error_message}
                  </div>
                )}
              </div>
              <div className={`queue-item-badge badge-${statusConfig.class}`}>
                {statusConfig.text}
              </div>
            </div>
          );
        })}
        {isCreatingZip && (
          <div className="premium-queue-item status-creating-zip">
            <div className="queue-item-icon"><IconArchive /></div>
            <div className="queue-item-content">
              <div className="queue-item-title">Đóng gói dữ liệu</div>
            </div>
            <div className="queue-item-badge badge-creating-zip">Đang tạo ZIP...</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BatchDownload;
