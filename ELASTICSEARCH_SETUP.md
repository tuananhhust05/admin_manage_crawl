# 🚀 Elasticsearch Vector Search Setup Guide

## 📋 Tổng quan

Hệ thống đã được tích hợp đầy đủ với **Elasticsearch** và **Sentence Transformers** để thực hiện tìm kiếm semantic với vector embeddings.

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   YouTube API   │───▶│   Flask App      │───▶│   MongoDB       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ Elasticsearch    │
                       │ + Vector Search  │
                       └──────────────────┘
```

## 🔧 Cài đặt Dependencies

```bash
pip install -r requirements.txt
```

### Dependencies chính:
- `sentence-transformers==2.2.2` - Model AI để tạo vector embeddings
- `elasticsearch==8.11.0` - Client Elasticsearch
- `elasticsearch-dsl==8.11.0` - DSL cho Elasticsearch

## ⚙️ Cấu hình Environment

Tạo file `.env` từ `env.example`:

```bash
cp env.example .env
```

Cập nhật các biến môi trường:

```env
# Elasticsearch Configuration
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_USER=
ELASTICSEARCH_PASSWORD=
ELASTICSEARCH_INDEX=video_chunks

# Sentence Transformer Model
SENTENCE_TRANSFORMER_MODEL=all-distilroberta-v1
```

## 🐳 Chạy với Docker

### 1. Cập nhật docker-compose.yml

Thêm Elasticsearch service:

```yaml
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    networks:
      - app-network

volumes:
  elasticsearch_data:

networks:
  app-network:
    driver: bridge
```

### 2. Chạy services

```bash
docker-compose up -d
```

## 🚀 Luồng hoạt động

### 1. Crawl & Chunk Video

```bash
POST /api/crawl-and-chunk-srt
{
  "video_id": "video_id_here"
}
```

**Quy trình:**
1. Crawl SRT từ YouTube
2. Chunk SRT thành các đoạn text
3. **Tạo vector embeddings** cho mỗi chunk
4. **Lưu vào Elasticsearch** với vector
5. Lưu chunks vào MongoDB
6. Cập nhật video status

### 2. Semantic Search

```bash
GET /api/search?q=your_search_query&size=10&from=0
```

**Tính năng:**
- Tìm kiếm semantic (ý nghĩa) thay vì keyword
- Vector similarity search
- Highlight kết quả
- Filter theo video_id

### 3. Quản lý Elasticsearch

```bash
# Health check
GET /api/elasticsearch/health

# Thống kê index
GET /api/elasticsearch/stats

# Xóa video
POST /api/elasticsearch/delete-video
{
  "video_id": "video_id_here"
}
```

## 🔍 Vector Search Details

### Model sử dụng: `all-distilroberta-v1`
- **Kích thước vector**: 768 dimensions
- **Tốc độ**: Trung bình, chất lượng cao
- **Độ chính xác**: Rất cao cho semantic search
- **Ngôn ngữ**: Hỗ trợ đa ngôn ngữ

### Index Mapping

```json
{
  "mappings": {
    "properties": {
      "video_id": {"type": "keyword"},
      "chunk_id": {"type": "keyword"},
      "text": {"type": "text", "analyzer": "standard"},
      "start_time": {"type": "float"},
      "end_time": {"type": "float"},
      "text_vector": {
        "type": "dense_vector",
        "dims": 384,
        "index": true,
        "similarity": "cosine"
      }
    }
  }
}
```

## 📊 API Endpoints

### Search API
```bash
GET /api/search?q=query&video_id=optional&size=10&from=0
```

**Response:**
```json
{
  "success": true,
  "query": "your query",
  "results": [
    {
      "video_id": "video_id",
      "chunk_id": "chunk_id",
      "text": "chunk text",
      "start_time": 10.5,
      "end_time": 15.2,
      "score": 0.95,
      "highlights": {...}
    }
  ],
  "total": 100,
  "took": 15
}
```

### Stats API
```bash
GET /api/elasticsearch/stats
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "index_name": "video_chunks",
    "document_count": 1000,
    "index_size": 52428800,
    "health": "green",
    "shards": 1
  }
}
```

## 🛠️ Troubleshooting

### 1. Elasticsearch không kết nối được

```bash
# Kiểm tra Elasticsearch
curl http://localhost:9200

# Kiểm tra logs
docker logs elasticsearch
```

### 2. Model không load được

```bash
# Kiểm tra disk space
df -h

# Clear cache
rm -rf ~/.cache/torch/sentence_transformers/
```

### 3. Vector search chậm

- Tăng `ef_search` trong index settings
- Sử dụng model nhỏ hơn
- Giảm số lượng results

## 📈 Performance Tips

### 1. Tối ưu Elasticsearch
```json
{
  "settings": {
    "index": {
      "knn.algo_param.ef_search": 200,
      "number_of_shards": 1,
      "number_of_replicas": 0
    }
  }
}
```

### 2. Batch Processing
- Xử lý chunks theo batch (100 chunks/lần)
- Sử dụng bulk indexing
- Async processing cho large videos

### 3. Caching
- Cache model trong memory
- Cache embeddings cho queries phổ biến
- Use Redis cho session cache

## 🔒 Security

### 1. Elasticsearch Security
```yaml
# Enable security
xpack.security.enabled=true
xpack.security.transport.ssl.enabled=true
```

### 2. API Security
- Rate limiting
- Authentication
- Input validation

## 📝 Monitoring

### 1. Health Checks
```bash
# Elasticsearch health
GET /api/elasticsearch/health

# Model health
GET /api/elasticsearch/stats
```

### 2. Metrics
- Search latency
- Index size
- Memory usage
- Query success rate

## 🎯 Best Practices

1. **Model Selection**: Sử dụng `all-distilroberta-v1` cho production
2. **Index Management**: Regular cleanup và optimization
3. **Error Handling**: Graceful fallback khi Elasticsearch down
4. **Monitoring**: Track performance metrics
5. **Backup**: Regular backup của index data

## 🚀 Production Deployment

### 1. Elasticsearch Cluster
- Minimum 3 nodes
- Separate master và data nodes
- SSD storage
- Sufficient RAM (8GB+)

### 2. Model Deployment
- Pre-load model at startup
- Model versioning
- A/B testing different models

### 3. Scaling
- Horizontal scaling với multiple app instances
- Load balancing
- Database connection pooling

---

## 📞 Support

Nếu gặp vấn đề, hãy kiểm tra:
1. Elasticsearch logs
2. Application logs
3. Network connectivity
4. Resource usage (CPU, Memory, Disk)

**Happy Searching! 🔍✨**
