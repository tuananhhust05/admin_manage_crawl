# PlayFantasy365 - Hệ thống quản lý Fantasy Sports

Hệ thống quản lý Fantasy Sports được xây dựng với Docker, MongoDB và Python Flask API.

## 🚀 Công nghệ sử dụng

- **Backend**: Python Flask
- **Database**: MongoDB
- **Containerization**: Docker & Docker Compose
- **Database Management**: Mongo Express

## 📁 Cấu trúc dự án

```
admin/
├── app/
│   ├── __init__.py          # Khởi tạo Flask app và MongoDB
│   └── routes.py            # API routes và endpoints
├── mongo-init/
│   └── init.js              # Script khởi tạo MongoDB
├── app.py                   # Entry point của ứng dụng
├── Dockerfile               # Docker configuration cho Flask API
├── docker-compose.yml       # Docker Compose configuration
├── requirements.txt         # Python dependencies
├── env.example              # Environment variables template
└── README.md               # Documentation
```

## 🛠️ Cài đặt và chạy

### Yêu cầu hệ thống

- Docker
- Docker Compose

### Bước 1: Clone repository

```bash
git clone <repository-url>
cd admin
```

### Bước 2: Cấu hình environment

```bash
# Copy file environment template
cp env.example .env

# Chỉnh sửa các biến môi trường trong .env nếu cần
```

### Bước 3: Chạy hệ thống

```bash
# Build và chạy tất cả services
docker-compose up --build

# Hoặc chạy ở background
docker-compose up -d --build
```

### Bước 4: Kiểm tra hệ thống

- **Flask API**: http://localhost:5001
- **MongoDB**: localhost:27019

## 📚 API Endpoints

### Base URL: `http://localhost:5001`

#### 1. Trang chủ
```
GET /
```

#### 2. Health Check
```
GET /health
```

#### 3. Users API

**Lấy danh sách users:**
```
GET /api/users
```

**Tạo user mới:**
```
POST /api/users
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "phone": "0123456789"
}
```

**Lấy thông tin user:**
```
GET /api/users/{user_id}
```

#### 4. Games API

**Lấy danh sách games:**
```
GET /api/games
```

**Tạo game mới:**
```
POST /api/games
Content-Type: application/json

{
  "name": "Premier League Match",
  "sport": "football",
  "description": "Manchester United vs Liverpool",
  "start_time": "2024-01-15T15:00:00Z",
  "status": "upcoming"
}
```

#### 5. Teams API

**Lấy danh sách teams:**
```
GET /api/teams
```

**Tạo team mới:**
```
POST /api/teams
Content-Type: application/json

{
  "name": "Manchester United",
  "sport": "football",
  "description": "Premier League team",
  "players": ["Player 1", "Player 2"]
}
```

## 🗄️ Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "username": "string",
  "email": "string",
  "full_name": "string",
  "phone": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Games Collection
```json
{
  "_id": "ObjectId",
  "name": "string",
  "sport": "string",
  "status": "upcoming|ongoing|completed|cancelled",
  "description": "string",
  "start_time": "datetime",
  "end_time": "datetime",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Teams Collection
```json
{
  "_id": "ObjectId",
  "name": "string",
  "description": "string",
  "sport": "string",
  "players": ["array"],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## 🔧 Quản lý hệ thống

### Dừng hệ thống
```bash
docker-compose down
```

### Dừng và xóa dữ liệu
```bash
# Dừng containers
docker-compose down

# Xóa dữ liệu MongoDB (nếu cần)
rm -rf ./data/mongodb/*
```

### Xem logs
```bash
# Tất cả services
docker-compose logs

# Service cụ thể
docker-compose logs api
docker-compose logs mongodb
```

### Rebuild service
```bash
docker-compose up --build api
```

## 🐳 Docker Services

### 1. MongoDB (mongodb)
- **Port**: 27019
- **Username**: admin
- **Password**: password123
- **Database**: playfantasy365
- **Data Storage**: `./data/mongodb/` (mounted to OS disk)

### 2. Flask API (api)
- **Port**: 5001
- **Environment**: production
- **Health Check**: /health

## 🔒 Bảo mật

⚠️ **Lưu ý**: Đây là cấu hình development. Trong production, hãy:

1. Thay đổi tất cả passwords mặc định
2. Sử dụng environment variables cho sensitive data
3. Cấu hình SSL/TLS
4. Thiết lập firewall rules
5. Sử dụng secrets management

## 🚀 Development

### Chạy local development
```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Chạy MongoDB local
docker run -d -p 27019:27019 --name mongodb mongo:7.0

# Chạy Flask app
python app.py
```

### Testing API
```bash
# Test health check
curl http://localhost:5001/health

# Test tạo user
curl -X POST http://localhost:5001/api/users \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com"}'
```

## 📝 License

MIT License

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
