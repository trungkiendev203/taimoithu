export const API_BASE = 'http://localhost:8000/api/v1';

export const api = {
  analyzeUrl: async (url) => {
    const res = await fetch(`${API_BASE}/analyze?url=${encodeURIComponent(url)}`);
    const data = await res.json();
    if (!res.ok || data.status === 'error') {
      throw new Error(data?.error?.message || 'Có lỗi xảy ra khi phân tích URL.');
    }
    return data.data; // AnalyzeResponseData
  },
  
  submitDownload: async (url, format_id, item_index = null) => {
    const res = await fetch(`${API_BASE}/download`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, format_id, item_index })
    });
    const data = await res.json();
    if (!res.ok || data.status === 'error') {
      throw new Error(data?.error?.message || 'Có lỗi xảy ra khi tạo tiến trình tải.');
    }
    return data.data; // { job_id }
  },

  getEventSourceUrl: (job_id) => {
    return `${API_BASE}/download/${job_id}/events`;
  },

  getDownloadFileUrl: (job_id) => {
    return `${API_BASE}/download/${job_id}/file`;
  }
};
