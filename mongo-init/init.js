// Khởi tạo database và collections
db = db.getSiblingDB('playfantasy365');

// Tạo collections với validation
db.createCollection('users', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['username', 'email', 'created_at'],
      properties: {
        username: {
          bsonType: 'string',
          description: 'Username phải là string và bắt buộc'
        },
        email: {
          bsonType: 'string',
          pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
          description: 'Email phải là string và có định dạng hợp lệ'
        },
        full_name: {
          bsonType: 'string',
          description: 'Tên đầy đủ phải là string'
        },
        phone: {
          bsonType: 'string',
          description: 'Số điện thoại phải là string'
        },
        created_at: {
          bsonType: 'date',
          description: 'Ngày tạo phải là date'
        },
        updated_at: {
          bsonType: 'date',
          description: 'Ngày cập nhật phải là date'
        }
      }
    }
  }
});

db.createCollection('games', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['name', 'sport', 'status', 'created_at'],
      properties: {
        name: {
          bsonType: 'string',
          description: 'Tên game phải là string và bắt buộc'
        },
        sport: {
          bsonType: 'string',
          description: 'Môn thể thao phải là string và bắt buộc'
        },
        status: {
          bsonType: 'string',
          enum: ['upcoming', 'ongoing', 'completed', 'cancelled'],
          description: 'Trạng thái game phải là một trong các giá trị: upcoming, ongoing, completed, cancelled'
        },
        description: {
          bsonType: 'string',
          description: 'Mô tả game phải là string'
        },
        start_time: {
          bsonType: 'date',
          description: 'Thời gian bắt đầu phải là date'
        },
        end_time: {
          bsonType: 'date',
          description: 'Thời gian kết thúc phải là date'
        },
        created_at: {
          bsonType: 'date',
          description: 'Ngày tạo phải là date'
        },
        updated_at: {
          bsonType: 'date',
          description: 'Ngày cập nhật phải là date'
        }
      }
    }
  }
});

db.createCollection('teams', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['name', 'created_at'],
      properties: {
        name: {
          bsonType: 'string',
          description: 'Tên team phải là string và bắt buộc'
        },
        description: {
          bsonType: 'string',
          description: 'Mô tả team phải là string'
        },
        sport: {
          bsonType: 'string',
          description: 'Môn thể thao phải là string'
        },
        players: {
          bsonType: 'array',
          description: 'Danh sách cầu thủ phải là array'
        },
        created_at: {
          bsonType: 'date',
          description: 'Ngày tạo phải là date'
        },
        updated_at: {
          bsonType: 'date',
          description: 'Ngày cập nhật phải là date'
        }
      }
    }
  }
});

db.createCollection('youtube_channels', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['url', 'channel_id', 'created_at'],
      properties: {
        url: {
          bsonType: 'string',
          description: 'URL kênh YouTube phải là string và bắt buộc'
        },
        channel_id: {
          bsonType: 'string',
          description: 'ID kênh YouTube phải là string và bắt buộc'
        },
        title: {
          bsonType: 'string',
          description: 'Tên kênh phải là string'
        },
        description: {
          bsonType: 'string',
          description: 'Mô tả kênh phải là string'
        },
        subscriber_count: {
          bsonType: 'number',
          description: 'Số lượng subscriber phải là number'
        },
        video_count: {
          bsonType: 'number',
          description: 'Số lượng video phải là number'
        },
        created_at: {
          bsonType: 'date',
          description: 'Ngày tạo phải là date'
        },
        updated_at: {
          bsonType: 'date',
          description: 'Ngày cập nhật phải là date'
        }
      }
    }
  }
});

db.createCollection('videos', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['url', 'channel_id', 'status', 'created_at'],
      properties: {
        url: {
          bsonType: 'string',
          description: 'URL video YouTube phải là string và bắt buộc'
        },
        channel_id: {
          bsonType: 'string',
          description: 'ID kênh YouTube phải là string và bắt buộc'
        },
        title: {
          bsonType: 'string',
          description: 'Tiêu đề video phải là string'
        },
        description: {
          bsonType: 'string',
          description: 'Mô tả video phải là string'
        },
        video_id: {
          bsonType: 'string',
          description: 'ID video YouTube phải là string'
        },
        thumbnail_url: {
          bsonType: 'string',
          description: 'URL thumbnail phải là string'
        },
        duration: {
          bsonType: 'string',
          description: 'Thời lượng video phải là string'
        },
        view_count: {
          bsonType: 'number',
          description: 'Số lượt xem phải là number'
        },
        like_count: {
          bsonType: 'number',
          description: 'Số lượt thích phải là number'
        },
        published_at: {
          bsonType: 'date',
          description: 'Ngày đăng phải là date'
        },
        status: {
          bsonType: 'number',
          description: 'Trạng thái video phải là number (0: pending, 1: processed, 2: error)'
        },
        created_at: {
          bsonType: 'date',
          description: 'Ngày tạo phải là date'
        },
        updated_at: {
          bsonType: 'date',
          description: 'Ngày cập nhật phải là date'
        }
      }
    }
  }
});

// Tạo indexes để tối ưu hiệu suất
db.users.createIndex({ 'email': 1 }, { unique: true });
db.users.createIndex({ 'username': 1 });
db.games.createIndex({ 'sport': 1 });
db.games.createIndex({ 'status': 1 });
db.games.createIndex({ 'start_time': 1 });
db.teams.createIndex({ 'name': 1 });
db.teams.createIndex({ 'sport': 1 });
db.youtube_channels.createIndex({ 'channel_id': 1 }, { unique: true });
db.youtube_channels.createIndex({ 'url': 1 });
db.youtube_channels.createIndex({ 'created_at': -1 });
db.videos.createIndex({ 'url': 1 }, { unique: true });
db.videos.createIndex({ 'channel_id': 1 });
db.videos.createIndex({ 'video_id': 1 });
db.videos.createIndex({ 'status': 1 });
db.videos.createIndex({ 'published_at': -1 });
db.videos.createIndex({ 'created_at': -1 });

print('Database và collections đã được khởi tạo thành công!');
