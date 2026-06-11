import React, { useState } from 'react';
import './ThptScoreSearch.css';

const subjectMap = {
    'TOAN': 'Toán học',
    'VAN': 'Ngữ Văn',
    'NGOAI_NGU': 'Ngoại Ngữ',
    'LI': 'Vật Lý',
    'HOA': 'Hóa Học',
    'SINH': 'Sinh Học',
    'SU': 'Lịch Sử',
    'DIA': 'Địa Lý',
    'GIAO_DUC_CONG_DAN': 'GDCD',
    'GDKT_PL': 'GDKT & PL',
    'TIN_HOC': 'Tin Học',
    'CN_CONG_NGHIEP': 'CN Công Nghiệp',
    'CN_NONG_NGHIEP': 'CN Nông Nghiệp'
};

const ThptScoreSearch = () => {
    const [sbd, setSbd] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [result, setResult] = useState(null);

    const searchScore = async (e) => {
        if (e) e.preventDefault();
        const trimmedSbd = sbd.trim();
        if (!trimmedSbd) return;

        setLoading(true);
        setError('');
        setResult(null);

        try {
            const response = await fetch(`https://s6.tuoitre.vn/api/diem-thi-thpt.htm?sbd=${trimmedSbd}&year=2026`);
            const data = await response.json();

            if (data.success && data.data && data.data.length > 0) {
                setResult(data.data[0]);
            } else {
                setError('Không tìm thấy dữ liệu cho số báo danh này.');
            }
        } catch (err) {
            setError('Có lỗi xảy ra khi kết nối đến máy chủ. Vui lòng thử lại sau.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <section className="thpt-container section-padding">
            <div className="thpt-card">
                <header>
                    <h1 className="thpt-title">Tra Điểm THPT Quốc Gia</h1>
                    <p className="thpt-subtitle">Dữ liệu lấy trực tiếp từ hệ thống, nhanh chóng & chính xác</p>
                </header>

                <form className="thpt-search-form" onSubmit={searchScore}>
                    <label htmlFor="sbdInput" className="sr-only">Số báo danh</label>
                    <input 
                        type="text" 
                        id="sbdInput" 
                        placeholder="Nhập số báo danh (VD: 34000001)" 
                        autoComplete="off"
                        value={sbd}
                        onChange={(e) => setSbd(e.target.value)}
                        required
                        aria-label="Số báo danh thi THPT"
                    />
                    <button type="submit" disabled={loading} aria-label="Nút tra cứu điểm thi">
                        {loading ? 'Đang tra...' : 'Tra Cứu'}
                    </button>
                </form>

                {loading && <div className="thpt-loading" role="status" aria-live="polite">Đang tìm kiếm dữ liệu...</div>}
                
                {error && <div className="thpt-error" role="alert">{error}</div>}

                {result && (
                    <article className="thpt-result-container active">
                        <div className="thpt-student-info">
                            <h2>Số báo danh: <span className="thpt-highlight-text">{result.SBD}</span></h2>
                            <div>Tổng điểm khối xét tuyển chính: <span className="thpt-total-score">{result.TONGDIEM > 0 ? result.TONGDIEM : 'N/A'}</span></div>
                        </div>

                        <div className="thpt-scores-grid">
                            {Object.entries(subjectMap).map(([key, name]) => {
                                const scoreValue = result[key];
                                const isTaken = scoreValue !== undefined && scoreValue !== -1 && scoreValue !== "" && scoreValue !== null;
                                const displayScore = isTaken ? scoreValue : '-';
                                const emptyClass = !isTaken ? 'empty' : '';

                                return (
                                    <div className="thpt-score-card" key={key}>
                                        <div className="thpt-subject">{name}</div>
                                        <div className={`thpt-score ${emptyClass}`}>{displayScore}</div>
                                    </div>
                                );
                            })}
                        </div>
                    </article>
                )}
            </div>
        </section>
    );
};

export default ThptScoreSearch;
