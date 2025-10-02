from flask import Blueprint, request, jsonify, current_app, render_template
from flask_pymongo import PyMongo
from bson import ObjectId
from datetime import datetime
import json
import os

main = Blueprint('main', __name__)

def get_mongo():
    return PyMongo(current_app)

def serialize_document(doc):
    """Convert MongoDB document to JSON serializable format"""
    if doc is None:
        return None
    
    # Convert ObjectId to string
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    
    # Convert datetime to ISO format
    for key, value in doc.items():
        if isinstance(value, datetime):
            doc[key] = value.isoformat()
    
    return doc

def serialize_documents(docs):
    """Convert list of MongoDB documents to JSON serializable format"""
    return [serialize_document(doc) for doc in docs]

# Custom JSON encoder để xử lý ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super(JSONEncoder, self).default(obj)

# Trang chủ
@main.route('/')
def home():
    print("Home")
    return jsonify({
        'message': 'Chào mừng đến với PlayFantasy365 API',
        'version': '1.0.0',
        'endpoints': {
            'users': '/api/users',
            'games': '/api/games',
            'teams': '/api/teams',
            'youtube_channels': '/api/youtube-channels'
        }
    })

# YouTube Channels Management Page
@main.route('/youtube-channels')
def youtube_channels_page():
    return render_template('index.html')

# Channel Detail Page
@main.route('/channel-detail')
def channel_detail_page():
    return render_template('channel_detail.html')

# API Users
@main.route('/api/users', methods=['GET'])
def get_users():
    try:
        mongo = get_mongo()
        users = list(mongo.db.users.find())
        users = serialize_documents(users)
        return jsonify({
            'success': True,
            'data': users,
            'count': len(users)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        
        # Validation cơ bản
        if not data or 'username' not in data or 'email' not in data:
            return jsonify({
                'success': False,
                'error': 'Username và email là bắt buộc'
            }), 400
        
        mongo = get_mongo()
        # Kiểm tra user đã tồn tại
        existing_user = mongo.db.users.find_one({'email': data['email']})
        if existing_user:
            return jsonify({
                'success': False,
                'error': 'Email đã được sử dụng'
            }), 400
        
        # Tạo user mới
        user_data = {
            'username': data['username'],
            'email': data['email'],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Thêm các field optional
        if 'full_name' in data:
            user_data['full_name'] = data['full_name']
        if 'phone' in data:
            user_data['phone'] = data['phone']
        
        result = mongo.db.users.insert_one(user_data)
        
        return jsonify({
            'success': True,
            'message': 'User được tạo thành công',
            'user_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/users/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        mongo = get_mongo()
        user = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        user = serialize_document(user)
        return jsonify({
            'success': True,
            'data': user
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API Games
@main.route('/api/games', methods=['GET'])
def get_games():
    try:
        mongo = get_mongo()
        games = list(mongo.db.games.find())
        games = serialize_documents(games)
        return jsonify({
            'success': True,
            'data': games,
            'count': len(games)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/games', methods=['POST'])
def create_game():
    try:
        data = request.get_json()
        
        if not data or 'name' not in data or 'sport' not in data:
            return jsonify({
                'success': False,
                'error': 'Tên game và môn thể thao là bắt buộc'
            }), 400
        
        game_data = {
            'name': data['name'],
            'sport': data['sport'],
            'status': data.get('status', 'upcoming'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        if 'description' in data:
            game_data['description'] = data['description']
        if 'start_time' in data:
            game_data['start_time'] = data['start_time']
        if 'end_time' in data:
            game_data['end_time'] = data['end_time']
        
        mongo = get_mongo()
        result = mongo.db.games.insert_one(game_data)
        
        return jsonify({
            'success': True,
            'message': 'Game được tạo thành công',
            'game_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API Teams
@main.route('/api/teams', methods=['GET'])
def get_teams():
    try:
        mongo = get_mongo()
        teams = list(mongo.db.teams.find())
        teams = serialize_documents(teams)
        return jsonify({
            'success': True,
            'data': teams,
            'count': len(teams)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/teams', methods=['POST'])
def create_team():
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({
                'success': False,
                'error': 'Tên team là bắt buộc'
            }), 400
        
        team_data = {
            'name': data['name'],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        if 'description' in data:
            team_data['description'] = data['description']
        if 'sport' in data:
            team_data['sport'] = data['sport']
        if 'players' in data:
            team_data['players'] = data['players']
        
        mongo = get_mongo()
        result = mongo.db.teams.insert_one(team_data)
        
        return jsonify({
            'success': True,
            'message': 'Team được tạo thành công',
            'team_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API YouTube Channels
@main.route('/api/youtube-channels', methods=['GET'])
def get_youtube_channels():
    try:
        mongo = get_mongo()
        channels = list(mongo.db.youtube_channels.find().sort('created_at', -1))
        
        # Convert to JSON serializable format
        channels = serialize_documents(channels)
        
        return jsonify({
            'success': True,
            'data': channels,
            'count': len(channels)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/youtube-channels', methods=['POST'])
def create_youtube_channel():
    try:
        data = request.get_json()
        
        if not data or 'url' not in data or 'channel_id' not in data:
            return jsonify({
                'success': False,
                'error': 'URL và Channel ID là bắt buộc'
            }), 400
        
        mongo = get_mongo()
        # Kiểm tra channel đã tồn tại
        existing_channel = mongo.db.youtube_channels.find_one({'channel_id': data['channel_id']})
        if existing_channel:
            return jsonify({
                'success': False,
                'error': 'Channel ID đã được sử dụng'
            }), 400
        
        # Tạo channel mới
        channel_data = {
            'url': data['url'],
            'channel_id': data['channel_id'],
            'title': data.get('title', ''),
            'description': data.get('description', ''),
            'subscriber_count': data.get('subscriber_count', 0),
            'video_count': data.get('video_count', 0),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        result = mongo.db.youtube_channels.insert_one(channel_data)
        
        return jsonify({
            'success': True,
            'message': 'YouTube channel được tạo thành công',
            'channel_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/youtube-channels/<channel_id>', methods=['GET'])
def get_youtube_channel(channel_id):
    try:
        mongo = get_mongo()
        channel = mongo.db.youtube_channels.find_one({'_id': ObjectId(channel_id)})
        if not channel:
            return jsonify({
                'success': False,
                'error': 'YouTube channel not found'
            }), 404
        
        # Convert to JSON serializable format
        channel = serialize_document(channel)
        
        return jsonify({
            'success': True,
            'data': channel
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/youtube-channels/<channel_id>', methods=['PUT'])
def update_youtube_channel(channel_id):
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Dữ liệu cập nhật là bắt buộc'
            }), 400
        
        # Cập nhật thời gian
        data['updated_at'] = datetime.utcnow()
        
        mongo = get_mongo()
        result = mongo.db.youtube_channels.update_one(
            {'_id': ObjectId(channel_id)},
            {'$set': data}
        )
        
        if result.matched_count == 0:
            return jsonify({
                'success': False,
                'error': 'YouTube channel không tồn tại'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'YouTube channel được cập nhật thành công'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/youtube-channels/<channel_id>', methods=['DELETE'])
def delete_youtube_channel(channel_id):
    try:
        mongo = get_mongo()
        result = mongo.db.youtube_channels.delete_one({'_id': ObjectId(channel_id)})
        
        if result.deleted_count == 0:
            return jsonify({
                'success': False,
                'error': 'YouTube channel không tồn tại'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'YouTube channel được xóa thành công'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API Videos
@main.route('/api/videos', methods=['GET'])
def get_videos():
    try:
        mongo = get_mongo()
        channel_id = request.args.get('channel_id')
        
        query = {}
        if channel_id:
            query['channel_id'] = channel_id
        
        videos = list(mongo.db.videos.find(query).sort('published_at', -1))
        videos = serialize_documents(videos)
        
        return jsonify({
            'success': True,
            'data': videos,
            'count': len(videos)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/videos/<video_id>', methods=['DELETE'])
def delete_video(video_id):
    try:
        mongo = get_mongo()
        result = mongo.db.videos.delete_one({'_id': ObjectId(video_id)})
        
        if result.deleted_count == 0:
            return jsonify({
                'success': False,
                'error': 'Video not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Video deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Test endpoint
@main.route('/api/test', methods=['GET'])
def test_endpoint():
    return jsonify({
        'success': True,
        'message': 'API is working',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

# Debug endpoint - list all routes
@main.route('/api/debug/routes', methods=['GET'])
def debug_routes():
    from flask import current_app
    routes = []
    for rule in current_app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': str(rule)
        })
    return jsonify({
        'success': True,
        'routes': routes
    }), 200

# Crawl Videos API
@main.route('/api/crawl-videos', methods=['POST'])
def crawl_videos():
    try:
        data = request.get_json()
        channel_id = data.get('channel_id')
        
        if not channel_id:
            return jsonify({
                'success': False,
                'error': 'Channel ID is required'
            }), 400
        
        # YouTube API configuration
        API_KEY = os.getenv('YOUTUBE_API_KEY')
        if not API_KEY:
            return jsonify({
                'success': False,
                'error': 'YouTube API key not configured. Please set YOUTUBE_API_KEY environment variable.'
            }), 500
        
        try:
            from googleapiclient.discovery import build
            youtube = build('youtube', 'v3', developerKey=API_KEY)
        except ImportError as e:
            return jsonify({
                'success': False,
                'error': f'Google API client not installed: {str(e)}'
            }), 500
        
        mongo = get_mongo()
        
        # Get channel's uploads playlist
        channel_request = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        )
        channel_response = channel_request.execute()
        
        if 'items' not in channel_response or not channel_response['items']:
            return jsonify({
                'success': False,
                'error': 'Channel not found'
            }), 404
        
        playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # Get latest 10 videos
        videos = []
        next_page_token = None
        max_results = 10
        
        while len(videos) < max_results:
            playlist_request = youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=min(50, max_results - len(videos)),
                pageToken=next_page_token
            )
            playlist_response = playlist_request.execute()
            
            for item in playlist_response['items']:
                if len(videos) >= max_results:
                    break
                    
                video_title = item['snippet']['title']
                video_id = item['snippet']['resourceId']['videoId']
                video_url = f'https://www.youtube.com/watch?v={video_id}'
                published_at = item['snippet']['publishedAt']
                description = item['snippet'].get('description', '')
                thumbnail_url = item['snippet']['thumbnails'].get('high', {}).get('url', '')
                
                # Get additional video details
                try:
                    video_request = youtube.videos().list(
                        part='statistics,contentDetails',
                        id=video_id
                    )
                    video_response = video_request.execute()
                    
                    if video_response['items']:
                        video_data = video_response['items'][0]
                        view_count = int(video_data['statistics'].get('viewCount', 0))
                        like_count = int(video_data['statistics'].get('likeCount', 0))
                        duration = video_data['contentDetails'].get('duration', '')
                    else:
                        view_count = 0
                        like_count = 0
                        duration = ''
                except:
                    view_count = 0
                    like_count = 0
                    duration = ''
                
                videos.append({
                    'title': video_title,
                    'url': video_url,
                    'video_id': video_id,
                    'description': description,
                    'thumbnail_url': thumbnail_url,
                    'view_count': view_count,
                    'like_count': like_count,
                    'duration': duration,
                    'published_at': datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                })
            
            next_page_token = playlist_response.get('nextPageToken')
            if not next_page_token:
                break
        
        # Save videos to database
        crawled_count = 0
        for video_data in videos:
            # Check if video already exists
            existing_video = mongo.db.videos.find_one({'url': video_data['url']})
            if existing_video:
                continue
            
            # Create video document
            video_doc = {
                'url': video_data['url'],
                'channel_id': channel_id,
                'title': video_data['title'],
                'description': video_data['description'],
                'video_id': video_data['video_id'],
                'thumbnail_url': video_data['thumbnail_url'],
                'duration': video_data['duration'],
                'view_count': video_data['view_count'],
                'like_count': video_data['like_count'],
                'published_at': video_data['published_at'],
                'status': 0,  # pending
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            mongo.db.videos.insert_one(video_doc)
            crawled_count += 1
        
        return jsonify({
            'success': True,
            'message': f'Successfully crawled {crawled_count} new videos',
            'crawled_count': crawled_count,
            'total_found': len(videos)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Health check endpoint
@main.route('/health')
def health_check():
    try:
        # Kiểm tra kết nối MongoDB
        mongo = get_mongo()
        mongo.db.command('ping')
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500