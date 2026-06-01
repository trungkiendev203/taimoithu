import React, { useEffect, useState, useRef } from 'react';
import { api } from '../services/api';

export default function ProgressModal({ jobId, onClose }) {
  const [jobState, setJobState] = useState(null);
  const hasAutoDownloaded = useRef(false);

  useEffect(() => {
    if (!jobId) {
      hasAutoDownloaded.current = false;
      return;
    }

    const eventSource = new EventSource(api.getEventSourceUrl(jobId));

    eventSource.addEventListener('progress', (e) => {
      try {
        const data = JSON.parse(e.data);
        if (typeof data === 'string') {
           setJobState(JSON.parse(data));
        } else {
           setJobState(data);
        }
      } catch (err) {
        console.error("Lỗi parse SSE", err);
      }
    });

    eventSource.onerror = (err) => {
      console.error("SSE Error:", err);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, [jobId]);

  // Auto-download khi COMPLETED - dùng fetch blob để bypass cross-origin
  useEffect(() => {
    if (jobState?.status === 'COMPLETED' && jobState?.download_url && !hasAutoDownloaded.current) {
      hasAutoDownloaded.current = true;
      triggerDownload(api.getDownloadFileUrl(jobId));
    }
  }, [jobState]);

  const triggerDownload = (url) => {
    // Sử dụng thẻ a để kích hoạt tải xuống trực tiếp thông qua trình duyệt
    // Tránh dùng fetch blob vì sẽ gây crash/out of memory với các file video lớn (vài trăm MB)
    const a = document.createElement('a');
    a.href = url;
    a.download = '';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  if (!jobId) return null;

  const progress = jobState?.progress || 0;
  const status = jobState?.status || 'PENDING';
  const errorMsg = jobState?.error_message;

  return (
    <div className="modal-overlay">
      <div className="modal-content premium-modal">
        <h2 className="modal-title">{status === 'COMPLETED' ? 'Hoàn tất' : status === 'FAILED' ? 'Lỗi tải xuống' : 'Đang xử lý...'}</h2>
        
        {status === 'FAILED' ? (
          <div className="error-message">
            <div className="status-icon error">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="15" y1="9" x2="9" y2="15"></line>
                <line x1="9" y1="9" x2="15" y2="15"></line>
              </svg>
            </div>
            <p className="error-text">Tải thất bại: {errorMsg}</p>
            <button className="btn-secondary w-full" onClick={onClose}>Đóng</button>
          </div>
        ) : status === 'COMPLETED' ? (
          <div className="success-message">
            <div className="status-icon success">
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
              </svg>
            </div>
            <p className="success-text">File đã được tải xuống máy của bạn!</p>
            <button 
              className="btn-primary w-full mt-16" 
              onClick={() => triggerDownload(api.getDownloadFileUrl(jobId))}
            >
              Tải lại file
            </button>
            <button className="btn-secondary w-full mt-8" onClick={onClose}>Đóng</button>
          </div>
        ) : (
          <div className="progress-section">
            <div className="progress-header">
              <span className="progress-percentage">{progress.toFixed(1)}%</span>
            </div>
            <div className="progress-bar-bg">
              <div className="progress-bar-fill" style={{ width: `${progress}%` }}></div>
            </div>
            <div className="progress-stats">
              {jobState?.speed_bytes ? (
                <span className="speed-stat">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
                  {Math.round(jobState.speed_bytes / 1024 / 1024)} MB/s
                </span>
              ) : <span></span>}
              {jobState?.eta_seconds ? (
                <span className="eta-stat">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                  Còn {jobState.eta_seconds}s
                </span>
              ) : <span></span>}
            </div>
            <button className="btn-secondary w-full mt-24" onClick={onClose}>Ẩn cửa sổ</button>
          </div>
        )}
      </div>
    </div>
  );
}
