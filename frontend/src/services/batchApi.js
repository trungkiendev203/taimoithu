export const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const batchApi = {
  createBatch: async (urls) => {
    const res = await fetch(`${API_BASE}/batch/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ urls })
    });
    const data = await res.json();
    if (!res.ok || data.status === 'error') {
      throw new Error(data?.error?.message || 'Có lỗi xảy ra khi tạo tiến trình tải hàng loạt.');
    }
    return data.data; // { batch_id: "..." }
  },

  getBatchStatus: async (batch_id) => {
    const res = await fetch(`${API_BASE}/batch/${batch_id}`);
    const data = await res.json();
    if (!res.ok || data.status === 'error') {
      throw new Error(data?.error?.message || 'Không thể lấy trạng thái tiến trình tải hàng loạt.');
    }
    return data.data; 
    /* 
    {
      batch_id, status, created_at, total_items, completed_items, zip_url,
      items: [{ index, url, title, status, file_path, error_message }]
    }
    */
  },

  getBatchDownloadUrl: (batch_id) => {
    return `${API_BASE}/batch/download/batch_${batch_id}.zip`;
  }
};
