# SRT Crawl và Processing Guide

## Tổng quan

Hệ thống đã được cập nhật để hỗ trợ crawl và xử lý file SRT (subtitle) từ YouTube videos. Các tính năng chính:

1. **Crawl SRT**: Tải file subtitle từ YouTube videos
2. **Process SRT**: Chia nhỏ nội dung SRT thành các chunks
3. **Store Chunks**: Lưu trữ chunks vào MongoDB
4. **Web Interface**: Giao diện web để quản lý SRT files

## API Endpoints

### 1. Crawl SRT từ Video URL
```http
POST /api/crawl-srt
Content-Type: application/json

{
    "video_url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

### 2. Crawl SRT cho Video cụ thể (từ database)
```http
POST /api/crawl-video-srt
Content-Type: application/json

{
    "video_id": "MONGODB_VIDEO_ID"
}
```

### 3. Process SRT File
```http
POST /api/process-srt
Content-Type: application/json

{
    "srt_id": "MONGODB_OBJECT_ID"
}
```

### 4. Process SRT cho Video cụ thể
```http
POST /api/process-video-srt
Content-Type: application/json

{
    "video_id": "MONGODB_VIDEO_ID"
}
```

### 5. Get Video Details (bao gồm transcription)
```http
GET /api/videos/{video_id}
```

**Response:**
```json
{
    "success": true,
    "data": {
        "video": {
            "title": "Video Title",
            "url": "https://www.youtube.com/watch?v=...",
            "description": "Video description...",
            "view_count": 1000,
            "like_count": 50,
            "srt_status": 2
        },
        "srt_files": [...],
        "chunks": [
            {
                "text": "Sample chunk text...",
                "time": "00:00:01,000",
                "chunk_index": 0
            }
        ],
        "chunks_count": 25
    }
}
```

### 6. Get SRT Files List
```http
GET /api/srt-files
```

### 7. Get SRT Chunks
```http
GET /api/srt-chunks/{srt_id}
```

## Cài đặt Dependencies

Cập nhật `requirements.txt` với các thư viện mới:

```bash
pip install -r requirements.txt
```

Các thư viện mới được thêm:
- `pysrt==1.1.2` - Xử lý file SRT
- `sentence-transformers==2.2.2` - Mã hóa text (cho tương lai)
- `elasticsearch==8.11.0` - Elasticsearch client (cho tương lai)
- `uuid==1.30` - Tạo unique IDs

## Cấu trúc Database

### Collection: `srt_files`
```json
{
    "_id": "ObjectId",
    "video_url": "https://www.youtube.com/watch?v=...",
    "srt_file_path": "srt_files/video_id_uuid.srt",
    "srt_filename": "video_id_uuid.srt",
    "status": 0,  // 0: pending, 1: processed, 2: error
    "chunks_count": 25,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
}
```

### Collection: `srt_chunks`
```json
{
    "_id": "ObjectId",
    "srt_id": "ObjectId",
    "video_url": "https://www.youtube.com/watch?v=...",
    "chunk_index": 0,
    "text": "Chunk content text...",
    "time": "00:00:01,000",
    "created_at": "2024-01-01T00:00:00Z"
}
```

## Sử dụng Web Interface

### 1. Truy cập Channel Detail Page
- Vào `http://localhost:5001/youtube-channels`
- Click vào một channel để xem chi tiết

### 2. Crawl Videos (nếu chưa có)
- Click "Crawl 10 Latest Videos" để lấy danh sách videos

### 3. Crawl SRT Files (2 cách)

#### Cách 1: Crawl cho tất cả videos
- Click "Crawl SRT for All Videos" để tải subtitle cho tất cả videos
- Quá trình này có thể mất vài phút tùy thuộc vào số lượng videos

#### Cách 2: Crawl cho từng video riêng lẻ
- Click nút "SRT" trên từng video card
- Hoặc click "Details" để vào trang chi tiết video, sau đó click "Crawl SRT"

### 4. Process SRT Files (2 cách)

#### Cách 1: Process tất cả SRT files
- Click "Process SRT Files" để xử lý các file SRT đã tải

#### Cách 2: Process cho từng video riêng lẻ
- Vào trang chi tiết video (click "Details")
- Click "Process SRT" để xử lý SRT cho video đó

### 5. View Results

#### Trong Channel Detail Page:
- Xem danh sách SRT files trong section "SRT Files"
- Click "View Chunks" để xem nội dung đã được chia nhỏ

#### Trong Video Detail Page:
- Xem thông tin chi tiết video
- Xem danh sách SRT files của video
- Xem transcription đầy đủ với tìm kiếm
- Export transcription ra file text

## Testing

Chạy script test để kiểm tra API:

```bash
python test_srt_api.py
```

Script sẽ test:
1. Kết nối API
2. Crawl SRT từ một video test
3. Process SRT file
4. Lấy danh sách SRT files
5. Lấy chunks của SRT file

## Cấu hình

### Environment Variables
Đảm bảo các biến môi trường sau được cấu hình:

```bash
YOUTUBE_API_KEY=your_youtube_api_key
MONGO_URI=mongodb://admin:password123@localhost:27017/playfantasy365?authSource=admin
```

### Thư mục SRT Files
- Thư mục `srt_files/` sẽ được tạo tự động
- Chứa các file SRT đã tải về
- Tên file có format: `{video_id}_{uuid}.srt`

## Xử lý Lỗi

### Lỗi thường gặp:

1. **"Failed to download subtitle"**
   - Video có thể không có subtitle
   - Thử với video khác có subtitle

2. **"No chunks extracted from SRT file"**
   - File SRT có thể bị lỗi format
   - Kiểm tra file SRT trong thư mục `srt_files/`

3. **"YouTube API key not configured"**
   - Cấu hình `YOUTUBE_API_KEY` trong environment

## Tương lai

Các tính năng có thể mở rộng:
1. **Elasticsearch Integration**: Lưu trữ và tìm kiếm chunks
2. **Vector Embeddings**: Mã hóa chunks thành vectors
3. **Search Interface**: Tìm kiếm nội dung trong chunks
4. **Batch Processing**: Xử lý hàng loạt videos
5. **Multiple Languages**: Hỗ trợ nhiều ngôn ngữ subtitle

## Troubleshooting

### Kiểm tra logs:
```bash
# Xem logs của Flask app
tail -f logs/app.log

# Kiểm tra MongoDB
mongo playfantasy365 --eval "db.srt_files.find().count()"
```

### Reset database:
```bash
# Xóa tất cả SRT data
mongo playfantasy365 --eval "db.srt_files.drop(); db.srt_chunks.drop()"
```

### Kiểm tra file system:
```bash
# Xem các file SRT đã tải
ls -la srt_files/

# Xóa file SRT cũ
rm srt_files/*
```
