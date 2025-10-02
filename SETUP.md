# YouTube Channels Manager - Setup Guide

## 🔑 YouTube API Key Configuration

### Cách 1: Sử dụng Environment Variable (Khuyến nghị)

1. **Tạo file `.env` trong thư mục gốc:**
```bash
# Copy từ env.example
cp env.example .env
```

2. **Chỉnh sửa file `.env`:**
```env
# YouTube API Configuration
YOUTUBE_API_KEY=your-actual-youtube-api-key-here
```

3. **Hoặc set environment variable trực tiếp:**
```bash
# Windows
set YOUTUBE_API_KEY=your-actual-youtube-api-key-here

# Linux/Mac
export YOUTUBE_API_KEY=your-actual-youtube-api-key-here
```

### Cách 2: Sử dụng Docker Compose

1. **Chỉnh sửa `docker-compose.yml`:**
```yaml
environment:
  - YOUTUBE_API_KEY=your-actual-youtube-api-key-here
```

2. **Hoặc tạo file `.env` và Docker sẽ tự động load:**
```env
YOUTUBE_API_KEY=your-actual-youtube-api-key-here
```

### Cách 3: Chỉnh sửa trực tiếp trong code

1. **Mở file `config.py`:**
```python
YOUTUBE_API_KEY = 'your-actual-youtube-api-key-here'
```

## 🚀 Lấy YouTube API Key

1. **Truy cập Google Cloud Console:**
   - Đi đến: https://console.cloud.google.com/

2. **Tạo project mới hoặc chọn project hiện có**

3. **Enable YouTube Data API v3:**
   - Vào "APIs & Services" > "Library"
   - Tìm "YouTube Data API v3"
   - Click "Enable"

4. **Tạo API Key:**
   - Vào "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy API key được tạo

5. **Cấu hình API Key:**
   - Click vào API key vừa tạo
   - Trong "API restrictions", chọn "Restrict key"
   - Chọn "YouTube Data API v3"
   - Save

## 🔧 Cấu hình hiện tại

**API Key mặc định:** `AIzaSyBfvol09E1FSgzoDQgf0c4r5oNj8PC4buY`

**Vị trí cấu hình:**
- `config.py` - Cấu hình chính
- `docker-compose.yml` - Environment variables cho Docker
- `env.example` - Template file
- `app/routes.py` - Sử dụng trong crawl API

## ⚠️ Lưu ý bảo mật

1. **Không commit API key vào Git:**
   - Thêm `.env` vào `.gitignore`
   - Sử dụng environment variables

2. **Giới hạn API Key:**
   - Chỉ enable YouTube Data API v3
   - Set IP restrictions nếu cần
   - Monitor usage trong Google Cloud Console

3. **Quota limits:**
   - YouTube API có giới hạn 10,000 units/day
   - Mỗi request tốn khoảng 1-100 units
   - Monitor usage để tránh vượt quota

## 🧪 Test API Key

```bash
# Test API key có hoạt động không
curl "https://www.googleapis.com/youtube/v3/search?part=snippet&q=test&key=YOUR_API_KEY"
```

## 📝 Troubleshooting

**Lỗi "API key not configured":**
- Kiểm tra environment variable `YOUTUBE_API_KEY`
- Restart Docker container sau khi thay đổi

**Lỗi "API key not valid":**
- Kiểm tra API key có đúng không
- Đảm bảo YouTube Data API v3 đã được enable
- Kiểm tra quota còn lại

**Lỗi "Quota exceeded":**
- Đợi đến ngày hôm sau (quota reset daily)
- Hoặc tạo API key mới
