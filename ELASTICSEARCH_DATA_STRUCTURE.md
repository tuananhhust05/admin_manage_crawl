# 📊 Elasticsearch Data Structure

## 🎯 Cấu trúc dữ liệu chính

### **Index Mapping**

```json
{
  "mappings": {
    "properties": {
      "url_channel": {
        "type": "keyword",
        "index": true
      },
      "url": {
        "type": "keyword", 
        "index": true
      },
      "origin_content": {
        "type": "text",
        "analyzer": "custom_text_analyzer",
        "search_analyzer": "custom_text_analyzer",
        "fields": {
          "keyword": {
            "type": "keyword",
            "ignore_above": 256
          }
        }
      },
      "vector": {
        "type": "dense_vector",
        "dims": 384,
        "index": true,
        "similarity": "cosine"
      },
      "time": {
        "type": "text"
      }
    }
  }
}
```

## 📋 Field Descriptions

### **Main Fields (Theo yêu cầu)**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `url_channel` | keyword | Link channel YouTube | `https://youtube.com/channel/UC123` |
| `url` | keyword | Link video YouTube | `https://youtube.com/watch?v=abc123` |
| `origin_content` | text | Nội dung gốc của chunk | `"This is a tutorial about machine learning"` |
| `vector` | dense_vector | Vector embedding (384D) | `[0.1, -0.2, 0.3, ...]` |
| `time` | text | Thời gian bắt đầu chunk | `"10.5"` |

### **Additional Fields (Quản lý video)**

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `video_id` | keyword | ID video trong MongoDB | `"507f1f77bcf86cd799439011"` |
| `chunk_id` | keyword | ID chunk duy nhất | `"507f1f77bcf86cd799439011_chunk_1"` |
| `start_time` | float | Thời gian bắt đầu (seconds) | `10.5` |
| `end_time` | float | Thời gian kết thúc (seconds) | `15.2` |
| `duration` | float | Độ dài chunk (seconds) | `4.7` |
| `chunk_index` | integer | Thứ tự chunk trong video | `0` |
| `video_title` | text | Tiêu đề video | `"Machine Learning Tutorial"` |
| `channel_name` | keyword | Tên channel | `"Tech Channel"` |
| `created_at` | date | Thời gian tạo | `"2024-01-15T10:30:00Z"` |
| `updated_at` | date | Thời gian cập nhật | `"2024-01-15T10:30:00Z"` |

## 🔍 Search Capabilities

### **1. Vector Search (Semantic)**
```json
{
  "query": {
    "knn": {
      "vector": {
        "vector": [0.1, -0.2, 0.3, ...],
        "k": 10
      }
    }
  }
}
```

### **2. Text Search**
```json
{
  "query": {
    "match": {
      "origin_content": "machine learning tutorial"
    }
  }
}
```

### **3. Filter by Channel**
```json
{
  "query": {
    "bool": {
      "must": [
        {"knn": {"vector": {...}}}
      ],
      "filter": [
        {"term": {"url_channel": "https://youtube.com/channel/UC123"}}
      ]
    }
  }
}
```

### **4. Filter by Video**
```json
{
  "query": {
    "bool": {
      "must": [
        {"knn": {"vector": {...}}}
      ],
      "filter": [
        {"term": {"video_id": "507f1f77bcf86cd799439011"}}
      ]
    }
  }
}
```

## 📊 Sample Document

```json
{
  "_id": "507f1f77bcf86cd799439011_chunk_1",
  "_source": {
    "url_channel": "https://youtube.com/channel/UC123",
    "url": "https://youtube.com/watch?v=abc123",
    "origin_content": "This is a tutorial about machine learning and neural networks. We will cover the basics of deep learning.",
    "vector": [0.1, -0.2, 0.3, 0.4, -0.5, ...],
    "time": "10.5",
    "video_id": "507f1f77bcf86cd799439011",
    "chunk_id": "507f1f77bcf86cd799439011_chunk_1",
    "start_time": 10.5,
    "end_time": 15.2,
    "duration": 4.7,
    "chunk_index": 0,
    "video_title": "Machine Learning Tutorial",
    "channel_name": "Tech Channel",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
}
```

## 🚀 API Usage Examples

### **1. Search API**
```bash
GET /api/search?q=machine learning&size=10&from=0
```

**Response:**
```json
{
  "success": true,
  "query": "machine learning",
  "results": [
    {
      "url_channel": "https://youtube.com/channel/UC123",
      "url": "https://youtube.com/watch?v=abc123",
      "origin_content": "This is a tutorial about machine learning...",
      "time": "10.5",
      "video_id": "507f1f77bcf86cd799439011",
      "chunk_id": "507f1f77bcf86cd799439011_chunk_1",
      "start_time": 10.5,
      "end_time": 15.2,
      "score": 0.95,
      "highlights": {
        "origin_content": ["This is a <em>machine learning</em> tutorial..."]
      }
    }
  ],
  "total": 100,
  "took": 15
}
```

### **2. Index Stats API**
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

## 🔧 Custom Analyzer

### **custom_text_analyzer**
```json
{
  "analysis": {
    "analyzer": {
      "custom_text_analyzer": {
        "type": "custom",
        "tokenizer": "standard",
        "filter": ["lowercase", "stop", "snowball"]
      }
    }
  }
}
```

**Features:**
- **Tokenizer**: Standard tokenizer
- **Filters**: 
  - `lowercase`: Chuyển thành chữ thường
  - `stop`: Loại bỏ stop words
  - `snowball`: Stemming algorithm

## 📈 Performance Optimization

### **1. Index Settings**
```json
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "index": {
      "knn": true,
      "knn.algo_param.ef_search": 100
    }
  }
}
```

### **2. Vector Search Optimization**
- **ef_search**: 100 (cân bằng tốc độ vs độ chính xác)
- **similarity**: cosine (phù hợp với text embeddings)
- **dims**: 768 (all-distilroberta-v1 model)

## 🧪 Testing

### **Test Script**
```bash
python test_elasticsearch_structure.py
```

**Test Coverage:**
- ✅ Health check
- ✅ Index stats
- ✅ Search functionality
- ✅ Sample data indexing
- ✅ Data structure validation
- ✅ Cleanup

## 🔍 Monitoring

### **Key Metrics**
- **Document Count**: Số lượng chunks đã index
- **Index Size**: Kích thước index (bytes)
- **Search Latency**: Thời gian tìm kiếm (ms)
- **Index Health**: Trạng thái index (green/yellow/red)

### **Health Check**
```bash
GET /api/elasticsearch/health
```

**Response:**
```json
{
  "success": true,
  "health": {
    "elasticsearch": true,
    "sentence_transformer": true,
    "overall": true
  }
}
```

---

## 📝 Notes

1. **Vector Dimensions**: 768 (all-distilroberta-v1 model)
2. **Similarity**: Cosine similarity cho semantic search
3. **Text Analysis**: Custom analyzer với stemming
4. **Indexing**: Bulk indexing cho performance
5. **Search**: KNN search với vector embeddings

**Happy Searching! 🔍✨**
