import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

const FeedbackModal = ({ isOpen, onClose }) => {
  const [formData, setFormData] = useState({ name: '', email: '', message: '' });
  const [status, setStatus] = useState('idle'); // idle, loading, success, error
  const [errorMsg, setErrorMsg] = useState('');

  // Handle ESC key to close
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        handleClose();
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  if (!isOpen) return null;

  const handleChange = (e) => {
    const { name, value } = e.target;
    if (name === 'message' && value.length > 1000) return;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const { message } = formData;
    
    if (!message.trim() || message.trim().length < 5) {
      setStatus('error');
      setErrorMsg('Vui lòng nhập nội dung góp ý (tối thiểu 5 ký tự).');
      return;
    }

    setStatus('loading');
    setErrorMsg('');

    try {
      await api.submitFeedback({
        name: formData.name.trim() || undefined,
        email: formData.email.trim() || undefined,
        message: formData.message.trim()
      });
      setStatus('success');
      setFormData({ name: '', email: '', message: '' });
    } catch (err) {
      setStatus('error');
      setErrorMsg(err.message || 'Không thể gửi góp ý lúc này.');
    }
  };

  const handleClose = () => {
    setStatus('idle');
    setErrorMsg('');
    onClose();
  };

  return (
    <div className="feedback-modal-overlay" onClick={handleClose}>
      <div className="feedback-modal-solid" onClick={e => e.stopPropagation()}>
        <button className="feedback-close-btn-solid" onClick={handleClose} aria-label="Close">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
        
        {status === 'success' ? (
          <div className="feedback-success-solid">
            <div className="success-icon-solid">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </div>
            <h3 className="feedback-title-solid">Gửi thành công!</h3>
            <p>Cảm ơn bạn đã đóng góp ý kiến để cải thiện hệ thống.</p>
            <button className="btn-primary feedback-submit-solid" onClick={handleClose}>Đóng</button>
          </div>
        ) : (
          <form className="feedback-form-solid" onSubmit={handleSubmit}>
            <div className="feedback-header-solid">
              <div className="header-icon-solid">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
              </div>
              <div className="header-text-solid">
                <h2 className="feedback-title-solid">Góp ý / Báo lỗi</h2>
                <p className="feedback-desc-solid">Mọi phản hồi của bạn đều rất quý giá với chúng tôi.</p>
              </div>
            </div>
            
            <div className="form-group-solid">
              <label>Tên của bạn <span>(Không bắt buộc)</span></label>
              <input 
                type="text" 
                name="name" 
                value={formData.name} 
                onChange={handleChange}
                placeholder="Nhập tên..."
                maxLength={100}
                disabled={status === 'loading'}
              />
            </div>
            
            <div className="form-group-solid">
              <label>Email <span>(Không bắt buộc)</span></label>
              <input 
                type="email" 
                name="email" 
                value={formData.email} 
                onChange={handleChange}
                placeholder="Để lại email nếu cần phản hồi..."
                maxLength={150}
                disabled={status === 'loading'}
              />
            </div>

            <div className="form-group-solid">
              <label>Nội dung <span className="required">*</span></label>
              <textarea 
                name="message" 
                value={formData.message} 
                onChange={handleChange}
                placeholder="Nhập chi tiết góp ý hoặc báo lỗi..."
                required
                disabled={status === 'loading'}
                rows={4}
              ></textarea>
              <div className="char-count-solid">{formData.message.length}/1000</div>
            </div>

            {status === 'error' && <div className="feedback-error-solid">{errorMsg}</div>}

            <button 
              type="submit" 
              className={`btn-primary feedback-submit-solid ${status === 'loading' ? 'loading' : ''}`}
              disabled={status === 'loading' || !formData.message.trim()}
            >
              {status === 'loading' ? <span className="spinner"></span> : 'Gửi góp ý'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default FeedbackModal;
