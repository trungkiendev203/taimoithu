# Danh Sách Các Nền Tảng Hỗ Trợ Tải Video

Hệ thống sử dụng lõi **yt-dlp** mạnh mẽ ở backend, kết hợp với các parser tối ưu hóa để hỗ trợ tải xuống từ hơn **1000+ trang web** chia sẻ video, âm thanh và mạng xã hội trên toàn cầu. Dưới đây là danh sách chi tiết các nền tảng phổ biến nhất được phân loại theo nhóm.

---

## 1. Mạng Xã Hội Phổ Biến (Popular Social Media)

| Nền tảng | Định dạng hỗ trợ | Chất lượng tối đa | Tính năng đặc biệt |
| :--- | :--- | :--- | :--- |
| **YouTube** | MP4, MKV, WebM, MP3, M4A | **8K / 4K / 1080p / 720p / 360p** | Tải video Shorts, YouTube Music, Playlist, Hỗ trợ gộp video và audio chất lượng cao bằng FFmpeg. |
| **TikTok** | MP4, MP3 | **1080p (Full HD)** | Tải video **không logo (No Watermark)**, tải nhạc nền (audio MP3), hỗ trợ cả Douyin (TikTok Trung Quốc). |
| **Facebook** | MP4 | **HD 1080p / SD** | Tải video từ Watch, Reels, bài viết cá nhân (công khai), Group (công khai). |
| **Instagram** | MP4 | **1080p** | Tải Reels, Stories, IGTV và video bài đăng thông thường. |
| **Twitter / X** | MP4 | **720p / 480p / 360p** | Tải video từ các bài tweet. |

---

## 2. Nền Tảng Chia Sẻ Ảnh & Sáng Tạo (Visual & Photo Sharing)

| Nền tảng | Định dạng hỗ trợ | Chất lượng tối đa | Ghi chú |
| :--- | :--- | :--- | :--- |
| **Pinterest** | MP4, JPG | **Gốc (Original)** | Tải Video Pins, Story Pins, GIF và ảnh chất lượng cao. |
| **Reddit** | MP4 | **1080p** | Tự động gộp luồng âm thanh và hình ảnh của Reddit (v.redd.it). |
| **Tumblr** | MP4, GIF | **Gốc** | Tải video bài đăng và ảnh động. |
| **Flickr** | MP4, JPG | **4K / Gốc** | Tải video ngắn và hình ảnh chất lượng gốc của nhiếp ảnh gia. |

---

## 3. Nền Tảng Stream & Truyền Hình (Streaming & Video Platforms)

| Nền tảng | Định dạng hỗ trợ | Chất lượng tối đa | Ghi chú |
| :--- | :--- | :--- | :--- |
| **Twitch** | MP4 | **1080p 60fps** | Tải các Clips ngắn, các buổi stream đã lưu (VODs). |
| **Vimeo** | MP4 | **4K / 1080p** | Hỗ trợ tải video chất lượng cao từ các nhà làm phim chuyên nghiệp. |
| **Dailymotion** | MP4 | **1080p** | Tải video chia sẻ cộng đồng. |
| **TED** | MP4 | **1080p** | Tải các bài thuyết trình kèm phụ đề đa ngôn ngữ nếu có. |

---

## 4. Nền Tảng Âm Nhạc & Âm Thanh (Audio & Music Platforms)

| Nền tảng | Định dạng âm thanh | Chất lượng (Bitrate) | Ghi chú |
| :--- | :--- | :--- | :--- |
| **SoundCloud** | MP3, AAC | **Up to 320kbps** | Tải các bài hát, playlist, podcast. |
| **Mixcloud** | M4A, MP3 | **192kbps / 128kbps** | Tải các bản mix dài, liveshow của các DJ. |
| **Bandcamp** | MP3, FLAC | **320kbps / Lossless** | Tải nhạc từ các nghệ sĩ độc lập. |

---

## 5. Nền Tảng Nội Địa & Đặc Thù (Regional & Other Platforms)

- **Trung Quốc:** Douyin (抖音), Bilibili (哔哩哔哩), Kuaishou (快手), Weibo (微博), IQIYI, Tencent Video.
- **Việt Nam:** VTV Go (truyền hình trực tuyến), Zing MP3, Nhaccuatui (NCT).
- **Khác:** Steam (video giới thiệu game), Kick (livestream VODs), Rumble, v.v.

---

## 6. Cơ Chế Nhận Diện & Xử Lý URL

1. **Bước 1: Trích xuất URL:** Client gửi URL cần tải lên API backend.
2. **Bước 2: Phân tích nguồn (Extractor Matching):** Backend sử dụng regex của `yt-dlp` để xác định trang web nguồn phù hợp.
3. **Bước 3: Lấy Metadata:** Trích xuất tiêu đề, thumbnail, thời lượng và danh sách định dạng (Format list).
4. **Bước 4: Trả kết quả:** Trả về giao diện người dùng danh sách định dạng kèm dung lượng ước tính để người dùng lựa chọn tải về.
