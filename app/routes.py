from flask import Blueprint, request, jsonify, current_app, render_template
from flask_pymongo import PyMongo
from bson import ObjectId
from datetime import datetime
import json
import os
import yt_dlp
import pysrt
import uuid
import logging
from typing import List, Dict, Any
import traceback
# Import Elasticsearch service
from elasticsearch_service import elasticsearch_service

main = Blueprint('main', __name__)

def get_mongo():
    return PyMongo(current_app)

def log_exception(function_name: str, error: Exception):
    """
    Helper function để log exception ra terminal với format đẹp
    """
    print("=" * 60)
    print(f"ERROR in {function_name}:")
    print(f"Error: {str(error)}")
    print("Traceback:")
    traceback.print_exc()
    print("=" * 60)

def serialize_document(doc):
    """Convert MongoDB document to JSON serializable format"""
    if doc is None:
        return None
    
    # Create a copy to avoid modifying original document
    serialized_doc = {}
    
    for key, value in doc.items():
        if isinstance(value, ObjectId):
            # Convert ObjectId to string
            serialized_doc[key] = str(value)
        elif isinstance(value, datetime):
            # Convert datetime to ISO format
            serialized_doc[key] = value.isoformat()
        elif isinstance(value, dict):
            # Recursively serialize nested documents
            serialized_doc[key] = serialize_document(value)
        elif isinstance(value, list):
            # Handle lists that might contain ObjectIds or datetimes
            serialized_doc[key] = []
            for item in value:
                if isinstance(item, ObjectId):
                    serialized_doc[key].append(str(item))
                elif isinstance(item, datetime):
                    serialized_doc[key].append(item.isoformat())
                elif isinstance(item, dict):
                    serialized_doc[key].append(serialize_document(item))
                else:
                    serialized_doc[key].append(item)
        else:
            # Keep other values as is
            serialized_doc[key] = value
    
    return serialized_doc

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

@main.route('/search', methods=['GET'])
def search_page():
    """Render search page"""
    return render_template('search.html')

# Channel Detail Page
@main.route('/channel-detail')
def channel_detail_page():
    return render_template('channel_detail.html')

# Video Detail Page
@main.route('/video-detail')
def video_detail_page():
    return render_template('video_detail.html')

# Article Summarizer Page
@main.route('/article-summarizer', methods=['GET'])
def article_summarizer_page():
    return render_template('article_summarizer.html')

# Articles Page
@main.route('/articles', methods=['GET'])
def articles_page():
    """Render the articles page with type filtering"""
    try:
        mongo = get_mongo()
        
        # Get type filter from query parameter
        selected_type = request.args.get('type', 'fotmob')
        
        # Debug: Check what collections exist
        collections = mongo.db.list_collection_names()
        print(f"Available collections: {collections}")
        
        # Check if articles collection exists and has data
        articles_count = mongo.db.articles.count_documents({})
        print(f"Total articles in collection: {articles_count}")
        
        # Query articles with type filter, sorted by newest first
        query = {'type': selected_type} if selected_type != 'all' else {}
        articles = list(mongo.db.articles.find(query).sort('created_at', -1))
        
        print(f"Found {len(articles)} articles for type: {selected_type}")
        
        # Get unique types for the dropdown
        unique_types = mongo.db.articles.distinct('type')
        print(f"Available types: {unique_types}")
        
        # Convert ObjectId to string for JSON serialization
        for article in articles:
            article['_id'] = str(article['_id'])
            if 'created_at' in article:
                article['created_at'] = article['created_at'].isoformat() if hasattr(article['created_at'], 'isoformat') else str(article['created_at'])
        
        return render_template('articles.html', 
                             articles=articles, 
                             selected_type=selected_type,
                             available_types=unique_types)
        
    except Exception as e:
        log_exception("articles_page", e)
        return render_template('articles.html', 
                             articles=[], 
                             selected_type='fotmob',
                             available_types=['fotmob'],
                             error=str(e))

# Debug API for articles
@main.route('/api/debug-articles', methods=['GET'])
def debug_articles():
    """Debug API to check articles collection"""
    try:
        mongo = get_mongo()
        
        # Get all collections
        collections = mongo.db.list_collection_names()
        
        # Check articles collection
        articles_count = mongo.db.articles.count_documents({})
        
        # Get sample articles
        sample_articles = list(mongo.db.articles.find().limit(5))
        
        # Get unique types
        unique_types = mongo.db.articles.distinct('source')
        
        # Convert ObjectId to string
        for article in sample_articles:
            article['_id'] = str(article['_id'])
        
        return jsonify({
            'success': True,
            'collections': collections,
            'articles_count': articles_count,
            'unique_types': unique_types,
            'sample_articles': sample_articles
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Create sample articles for testing
@main.route('/api/create-sample-articles', methods=['POST'])
def create_sample_articles():
    """Create sample articles for testing"""
    try:
        mongo = get_mongo()
        
        sample_articles = [
            {
                'title': 'FotMob: Premier League Transfer News',
                'content': 'Latest transfer updates from the Premier League including major signings and departures.',
                'summary': 'Comprehensive coverage of Premier League transfer activities with expert analysis.',
                'source': 'fotmob',
                'url': 'https://fotmob.com/news/premier-league-transfers',
                'created_at': datetime.utcnow()
            },
            {
                'title': 'FotMob: Champions League Predictions',
                'content': 'Expert predictions for the upcoming Champions League matches and potential winners.',
                'summary': 'In-depth analysis of Champions League teams and their chances of success.',
                'source': 'fotmob',
                'url': 'https://fotmob.com/news/champions-league-predictions',
                'created_at': datetime.utcnow()
            },
            {
                'title': 'FotMob: La Liga Weekend Review',
                'content': 'Complete review of the weekend matches in La Liga with highlights and analysis.',
                'summary': 'Comprehensive coverage of La Liga weekend action with key moments and statistics.',
                'source': 'fotmob',
                'url': 'https://fotmob.com/news/la-liga-weekend-review',
                'created_at': datetime.utcnow()
            },
            {
                'title': 'General Football News',
                'content': 'General football news and updates from around the world.',
                'summary': 'Latest football news covering various leagues and competitions worldwide.',
                'source': 'news',
                'url': 'https://example.com/football-news',
                'created_at': datetime.utcnow()
            }
        ]
        
        # Insert sample articles
        result = mongo.db.articles.insert_many(sample_articles)
        
        return jsonify({
            'success': True,
            'message': f'Created {len(result.inserted_ids)} sample articles',
            'inserted_ids': [str(id) for id in result.inserted_ids]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API to get articles for frontend
@main.route('/api/articles', methods=['GET'])
def get_articles():
    """API to get articles for frontend with search and filter support"""
    try:
        mongo = get_mongo()
        
        # Get parameters from query
        selected_type = request.args.get('type', 'fotmob')
        search_query = request.args.get('search', '').strip()
        
        # Build query
        query = {}
        
        # Add type filter
        if selected_type != 'all':
            query['source'] = selected_type
        
        # Add search filter
        if search_query:
            query['$or'] = [
                {'title': {'$regex': search_query, '$options': 'i'}},
                {'content': {'$regex': search_query, '$options': 'i'}},
                {'summary': {'$regex': search_query, '$options': 'i'}}
            ]
        
        # Query articles with filters, sorted by newest first
        articles = list(mongo.db.articles.find(query).sort('created_at', -1))
        
        # Get unique types for the dropdown
        unique_types = mongo.db.articles.distinct('source')
        
        # Convert ObjectId to string for JSON serialization
        for article in articles:
            article['_id'] = str(article['_id'])
            if 'created_at' in article:
                article['created_at'] = article['created_at'].isoformat() if hasattr(article['created_at'], 'isoformat') else str(article['created_at'])
        
        return jsonify({
            'success': True,
            'articles': articles,
            'selected_type': selected_type,
            'search_query': search_query,
            'available_types': unique_types,
            'total_count': len(articles)
        })
        
    except Exception as e:
        log_exception("get_articles", e)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API to generate article from selected articles
@main.route('/api/generate-article', methods=['POST'])
def generate_article():
    """Generate article from selected articles"""
    try:
        data = request.get_json()
        articles = data.get('articles', [])
        
        if not articles:
            return jsonify({
                'success': False,
                'error': 'No articles provided'
            }), 400
        
        if len(articles) > 3:
            return jsonify({
                'success': False,
                'error': 'Maximum 3 articles allowed'
            }), 400
        
        # Call external API
        import requests
        external_api_url = 'http://46.62.152.241:5002/generate-article'
        
        payload = {
            'articles': articles
        }
        
        response = requests.post(external_api_url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return jsonify({
                'success': True,
                'generated_article': result.get('generated_article', ''),
                'articles_count': len(articles)
            })
        else:
            return jsonify({
                'success': False,
                'error': f'External API error: {response.status_code}'
            }), 500
            
    except Exception as e:
        log_exception("generate_article", e)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
        
        # Thêm đếm số video cho mỗi channel
        for channel in channels:
            video_count = mongo.db.videos.count_documents({'channel_id': channel['channel_id']})
            channel['video_count'] = video_count
        
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
        
        # Thêm đếm số video cho channel
        video_count = mongo.db.videos.count_documents({'channel_id': channel['channel_id']})
        channel['video_count'] = video_count
        
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

# Proxy API to external summarize service
@main.route('/api/summarize-articles', methods=['POST'])
def summarize_articles():
    try:
        data = request.get_json() or {}
        articles = data.get('articles', [])
        if not isinstance(articles, list) or len(articles) == 0:
            return jsonify({'success': False, 'error': 'articles must be a non-empty list'}), 400

        import requests
        resp = requests.post(
            'http://46.62.152.241:8000/synthesize',
            json={'articles': articles},
            headers={'Content-Type': 'application/json'}
        )
        if resp.status_code == 200:
            payload = resp.json()
            return jsonify({'success': True, 'data': payload}), 200
        return jsonify({'success': False, 'error': f'external service {resp.status_code}'}), 502
    except Exception as e:
        logging.exception('summarize_articles failed')
        return jsonify({'success': False, 'error': str(e)}), 500

# Search Documents API
@main.route('/api/search-documents', methods=['POST'])
def search_documents():
    """Search documents using external search service"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'keyword' not in data:
            return jsonify({
                'success': False,
                'error': 'Keyword is required'
            }), 400
        
        # Prepare search request
        search_request = {
            'keyword': data['keyword'],
            'limit': data.get('limit', 10),
            'min_score': data.get('min_score', 0.6),
            'include_content': data.get('include_content', True),
            'boost_recent': data.get('boost_recent', True)
        }
        
        # Call external search service
        import requests
        search_url = 'http://37.27.181.54:5009/search/relevant/advanced'
        
        response = requests.post(
            search_url,
            json=search_request,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        if response.status_code == 200:
            search_data = response.json()
            return jsonify({
                'success': True,
                'data': search_data
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Search service returned status {response.status_code}'
            }), 500
            
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'Search request timed out'
        }), 408
    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': False,
            'error': 'Unable to connect to search service'
        }), 503
    except Exception as e:
        print(f"Search error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error during search'
        }), 500

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
        log_exception("crawl_videos", e)
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

# ==============================================================================
# SRT PROCESSING FUNCTIONS
# ==============================================================================

def process_srt_file(srt_file_path: str, max_words: int = 350) -> List[Dict[str, Any]]:
    """
    Đọc file SRT và chia thành các chunk với giới hạn số từ
    """
    try:
        subs = pysrt.open(srt_file_path, encoding='utf-8')
    except Exception as e:
        logging.error(f"Lỗi khi đọc file {srt_file_path}: {e}")
        return []

    chunks_data: List[Dict[str, Any]] = []
    current_chunk_captions: List[pysrt.SubRipItem] = []
    current_word_count = 0

    # Logic chunking thông minh
    for caption in subs:
        caption_text = caption.text.replace('\n', ' ')
        caption_word_count = len(caption_text.split())

        # Trường hợp đặc biệt: một caption dài hơn giới hạn
        if caption_word_count > max_words:
            if current_chunk_captions:
                # Hoàn thành chunk hiện tại trước
                full_chunk_text = " ".join([c.text.replace('\n', ' ') for c in current_chunk_captions])
                start_time = str(current_chunk_captions[0].start)
                chunks_data.append({'text': full_chunk_text, 'time': start_time})
                current_chunk_captions = []
                current_word_count = 0

            # Chia nhỏ caption quá dài
            words = caption_text.split()
            for i in range(0, len(words), max_words):
                sub_chunk_words = words[i : i + max_words]
                chunks_data.append({'text': " ".join(sub_chunk_words), 'time': str(caption.start)})
            continue

        # Nếu thêm caption này sẽ vượt quá giới hạn -> hoàn thành chunk hiện tại
        if current_word_count + caption_word_count > max_words and current_chunk_captions:
            full_chunk_text = " ".join([c.text.replace('\n', ' ') for c in current_chunk_captions])
            start_time = str(current_chunk_captions[0].start)
            chunks_data.append({'text': full_chunk_text, 'time': start_time})
            
            # Bắt đầu chunk mới với caption hiện tại
            current_chunk_captions = [caption]
            current_word_count = caption_word_count
        else:
            # Tiếp tục thêm vào chunk hiện tại
            current_chunk_captions.append(caption)
            current_word_count += caption_word_count

    # Đừng quên chunk cuối cùng
    if current_chunk_captions:
        full_chunk_text = " ".join([c.text.replace('\n', ' ') for c in current_chunk_captions])
        start_time = str(current_chunk_captions[0].start)
        chunks_data.append({'text': full_chunk_text, 'time': start_time})

    return chunks_data

def generate_unique_filename(video_url: str, extension: str = 'srt') -> str:
    """
    Tạo tên file unique dựa trên video URL
    """
    # Extract video ID from URL
    video_id = video_url.split('v=')[-1].split('&')[0] if 'v=' in video_url else str(uuid.uuid4())
    unique_id = str(uuid.uuid4())[:8]
    return f"{video_id}_{unique_id}.{extension}"

# ==============================================================================
# CRAWL SRT API ENDPOINTS
# ==============================================================================

@main.route('/api/crawl-srt', methods=['POST'])
def crawl_srt():
    """
    API để crawl SRT từ video YouTube
    """
    try:
        data = request.get_json()
        video_url = data.get('video_url')
        
        if not video_url:
            return jsonify({
                'success': False,
                'error': 'Video URL is required'
            }), 400
        
        # Tạo thư mục lưu trữ SRT nếu chưa tồn tại
        srt_folder = 'srt_files'
        if not os.path.exists(srt_folder):
            os.makedirs(srt_folder)
        
        # Tạo tên file unique
        srt_filename = generate_unique_filename(video_url)
        srt_file_path = os.path.join(srt_folder, srt_filename)
        
        # Cấu hình yt-dlp để download subtitle
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],  # Thử cả tiếng Anh và tiếng Việt
            'subtitlesformat': 'srt',
            'skip_download': True,
            'outtmpl': srt_file_path.replace('.srt', '.%(ext)s'),
        }
        
        success = False
        error_message = ""
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
                
                # Kiểm tra file đã được tạo
                if os.path.exists(srt_file_path):
                    success = True
                else:
                    # Thử tìm file với extension khác
                    for ext in ['srt', 'vtt']:
                        test_path = srt_file_path.replace('.srt', f'.{ext}')
                        if os.path.exists(test_path):
                            os.rename(test_path, srt_file_path)
                            success = True
                            break
                            
        except Exception as e:
            error_message = str(e)
            logging.error(f"Lỗi khi download subtitle: {e}")
        
        if success:
            # Lưu thông tin vào database
            mongo = get_mongo()
            srt_doc = {
                'video_url': video_url,
                'srt_file_path': srt_file_path,
                'srt_filename': srt_filename,
                'status': 0,  # 0: pending processing
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = mongo.db.srt_files.insert_one(srt_doc)
            
            return jsonify({
                'success': True,
                'message': 'SRT file downloaded successfully',
                'srt_id': str(result.inserted_id),
                'srt_filename': srt_filename,
                'srt_file_path': srt_file_path
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to download subtitle: {error_message}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/process-srt', methods=['POST'])
def process_srt():
    """
    API để xử lý file SRT đã crawl và lưu chunks vào MongoDB
    """
    try:
        data = request.get_json()
        srt_id = data.get('srt_id')
        
        if not srt_id:
            return jsonify({
                'success': False,
                'error': 'SRT ID is required'
            }), 400
        
        mongo = get_mongo()
        
        # Lấy thông tin SRT file từ database
        srt_doc = mongo.db.srt_files.find_one({'_id': ObjectId(srt_id)})
        if not srt_doc:
            return jsonify({
                'success': False,
                'error': 'SRT file not found'
            }), 404
        
        srt_file_path = srt_doc['srt_file_path']
        
        # Kiểm tra file tồn tại
        if not os.path.exists(srt_file_path):
            return jsonify({
                'success': False,
                'error': 'SRT file not found on disk'
            }), 404
        
        # Xử lý file SRT
        chunks_data = process_srt_file(srt_file_path)
        
        if not chunks_data:
            return jsonify({
                'success': False,
                'error': 'No chunks extracted from SRT file'
            }), 500
        
        # Lưu chunks vào MongoDB
        chunks_docs = []
        for i, chunk_info in enumerate(chunks_data):
            chunk_doc = {
                'srt_id': ObjectId(srt_id),
                'video_url': srt_doc['video_url'],
                'chunk_index': i,
                'text': chunk_info['text'],
                'time': chunk_info['time'],
                'created_at': datetime.utcnow()
            }
            chunks_docs.append(chunk_doc)
        
        # Insert tất cả chunks
        if chunks_docs:
            mongo.db.srt_chunks.insert_many(chunks_docs)
        
        # Cập nhật status của SRT file
        mongo.db.srt_files.update_one(
            {'_id': ObjectId(srt_id)},
            {
                '$set': {
                    'status': 1,  # 1: processed
                    'chunks_count': len(chunks_data),
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        return jsonify({
            'success': True,
            'message': f'Successfully processed SRT file with {len(chunks_data)} chunks',
            'chunks_count': len(chunks_data),
            'chunks': chunks_data[:5]  # Trả về 5 chunks đầu để preview
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/srt-files', methods=['GET'])
def get_srt_files():
    """
    API để lấy danh sách SRT files
    """
    try:
        mongo = get_mongo()
        srt_files = list(mongo.db.srt_files.find().sort('created_at', -1))
        srt_files = serialize_documents(srt_files)
        
        return jsonify({
            'success': True,
            'data': srt_files,
            'count': len(srt_files)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/srt-chunks/<srt_id>', methods=['GET'])
def get_srt_chunks(srt_id):
    """
    API để lấy chunks của một SRT file
    """
    try:
        mongo = get_mongo()
        chunks = list(mongo.db.srt_chunks.find({'srt_id': ObjectId(srt_id)}).sort('chunk_index', 1))
        chunks = serialize_documents(chunks)
        
        return jsonify({
            'success': True,
            'data': chunks,
            'count': len(chunks)
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# VIDEO DETAILS AND TRANSCRIPTION API
# ==============================================================================

@main.route('/api/videos/<video_id>', methods=['GET'])
def get_video_details(video_id):
    """
    API để lấy chi tiết video và transcription
    """
    try:
        mongo = get_mongo()
        
        # Lấy thông tin video
        video = mongo.db.videos.find_one({'_id': ObjectId(video_id)})
        if not video:
            return jsonify({
                'success': False,
                'error': 'Video not found'
            }), 404
        
        # Lấy SRT files liên quan đến video này
        srt_files = list(mongo.db.srt_files.find({'video_url': video['url']}).sort('created_at', -1))
        
        # Lấy chunks của SRT files đã được xử lý
        chunks_data = []
        for srt_file in srt_files:
            if srt_file.get('status') == 1:  # Chỉ lấy SRT đã được xử lý
                # Sử dụng ObjectId từ srt_file (chưa được serialize)
                srt_object_id = srt_file['_id'] if isinstance(srt_file['_id'], ObjectId) else ObjectId(srt_file['_id'])
                chunks = list(mongo.db.srt_chunks.find({'srt_id': srt_object_id}).sort('chunk_index', 1))
                chunks_data.extend(chunks)
        
        # Serialize data
        video = serialize_document(video)
        srt_files = serialize_documents(srt_files)
        chunks_data = serialize_documents(chunks_data)
        
        return jsonify({
            'success': True,
            'data': {
                'video': video,
                'srt_files': srt_files,
                'chunks': chunks_data,
                'chunks_count': len(chunks_data)
            }
        }), 200
        
    except Exception as e:
        log_exception("get_video_details", e)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/crawl-video-srt', methods=['POST'])
def crawl_video_srt():
    """
    API để crawl SRT cho một video cụ thể
    """
    try:
        data = request.get_json()
        video_id = data.get('video_id')
        
        if not video_id:
            return jsonify({
                'success': False,
                'error': 'Video ID is required'
            }), 400
        
        mongo = get_mongo()
        
        # Lấy thông tin video
        video = mongo.db.videos.find_one({'_id': ObjectId(video_id)})
        if not video:
            return jsonify({
                'success': False,
                'error': 'Video not found'
            }), 404
        
        video_url = video['url']
        print("url video: ", video_url)
        # Kiểm tra xem đã có SRT file chưa
        existing_srt = mongo.db.srt_files.find_one({'video_url': video_url})
        if existing_srt:
            return jsonify({
                'success': False,
                'error': 'SRT file already exists for this video',
                'srt_id': str(existing_srt['_id'])
            }), 400
        
        # Tạo thư mục lưu trữ SRT nếu chưa tồn tại
        srt_folder = 'srt_files'
        if not os.path.exists(srt_folder):
            os.makedirs(srt_folder)
        
        # Tạo tên file unique
        srt_filename = generate_unique_filename(video_url)
        srt_file_path = os.path.join(srt_folder, srt_filename)
        
        # Cấu hình yt-dlp để download subtitle
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],  # Thử cả tiếng Anh và tiếng Việt
            'subtitlesformat': 'srt',
            'skip_download': True,
            'outtmpl': srt_file_path.replace('.srt', '.%(ext)s'),
        }
        
        success = False
        error_message = ""
        actual_srt_file = None
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
                
                # Tìm file SRT thực tế được tạo (yt-dlp có thể tạo tên khác)
                actual_srt_file = None
                
                # Kiểm tra file với tên mong đợi trước
                if os.path.exists(srt_file_path):
                    actual_srt_file = srt_file_path
                    success = True
                else:
                    # Extract video ID từ URL để tìm file
                    video_id_from_url = video_url.split('v=')[-1].split('&')[0] if 'v=' in video_url else ''
                    
                    # Tìm tất cả file .srt trong thư mục
                    for file in os.listdir(srt_folder):
                        if file.endswith('.srt') and video_id_from_url in file:  # Video ID trong tên file
                            actual_srt_file = os.path.join(srt_folder, file)
                            success = True
                            break
                    
                    # Nếu vẫn không tìm thấy, tìm file .srt mới nhất
                    if not actual_srt_file:
                        srt_files = [f for f in os.listdir(srt_folder) if f.endswith('.srt')]
                        if srt_files:
                            # Lấy file mới nhất
                            latest_file = max(srt_files, key=lambda x: os.path.getctime(os.path.join(srt_folder, x)))
                            actual_srt_file = os.path.join(srt_folder, latest_file)
                            success = True
                            
        except Exception as e:
            error_message = str(e)
            logging.error(f"Lỗi khi download subtitle: {e}")
        
        if success and actual_srt_file:
            # Lưu thông tin vào database với file thực tế
            actual_filename = os.path.basename(actual_srt_file)
            srt_doc = {
                'video_url': video_url,
                'video_id': ObjectId(video_id),
                'srt_file_path': actual_srt_file,
                'srt_filename': actual_filename,
                'status': 0,  # 0: pending processing
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = mongo.db.srt_files.insert_one(srt_doc)
            
            # Cập nhật status của video
            mongo.db.videos.update_one(
                {'_id': ObjectId(video_id)},
                {'$set': {'status':1,'srt_status': 1, 'updated_at': datetime.utcnow()}}  # 1: SRT downloaded
            )
            
            return jsonify({
                'success': True,
                'message': 'SRT file downloaded successfully',
                'srt_id': str(result.inserted_id),
                'srt_filename': actual_filename,
                'srt_file_path': actual_srt_file
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to download subtitle: {error_message}'
            }), 500
            
    except Exception as e:
        log_exception("crawl_video_srt", e)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

from elasticsearch import Elasticsearch, exceptions
import time
ES_HOST = "http://37.27.181.54:9200" # Địa chỉ Elasticsearch
ES_INDEX_NAME = "articles"          # Tên index bạn muốn lưu dữ liệu
MODEL_NAME = 'all-distilroberta-v1' # Model dùng để mã hóa
from sentence_transformers import SentenceTransformer
try:
    # --- Khởi tạo kết nối và model (chỉ một lần) ---
    logging.info("🔌 Đang kết nối đến Elasticsearch...")
    es_connection = Elasticsearch([ES_HOST])
    if not es_connection.ping():
        raise ConnectionError(f"Không thể kết nối đến Elasticsearch tại {ES_HOST}")
    logging.info("   ✔ Kết nối Elasticsearch thành công!")

    logging.info(f"🧠 Đang tải model '{MODEL_NAME}'... (có thể mất một lúc)")
    transformer_model = SentenceTransformer('all-distilroberta-v1')
    logging.info("   ✔ Tải model thành công!")
    
except exceptions.ConnectionError as e:
    logging.error(f"🔥 LỖI KẾT NỐI ELASTICSEARCH: {e}")
except Exception as e:
    logging.error(f"🔥 Đã xảy ra lỗi không mong muốn trong quá trình thực thi: {e}")
    
@main.route('/api/crawl-and-chunk-video', methods=['POST'])
def crawl_and_chunk_video():
    """
    API gộp crawl SRT và chunk cho một video cụ thể
    """
    try:
        data = request.get_json()
        video_id = data.get('video_id')
        
        if not video_id:
            return jsonify({
                'success': False,
                'error': 'Video ID is required'
            }), 400
        
        mongo = get_mongo()
        
        # Lấy thông tin video
        video = mongo.db.videos.find_one({'_id': ObjectId(video_id)})
        if not video:
            return jsonify({
                'success': False,
                'error': 'Video not found'
            }), 404
        channel = mongo.db.youtube_channels.find_one({'channel_id': video['channel_id']})
        channel_url = channel['url']
        video_url = video['url']
        print(f"Processing video: {video_url}")
        
        # Kiểm tra xem đã có SRT file chưa - nếu có thì xóa để crawl lại
        existing_srt = mongo.db.srt_files.find_one({'video_url': video_url})
        if existing_srt:
            print(f"Found existing SRT file, deleting to re-crawl: {existing_srt['_id']}")
            # Xóa SRT file cũ và chunks liên quan
            mongo.db.srt_chunks.delete_many({'srt_id': existing_srt['_id']})
            mongo.db.srt_files.delete_one({'_id': existing_srt['_id']})
            
            # Xóa file vật lý nếu tồn tại
            if os.path.exists(existing_srt.get('srt_file_path', '')):
                try:
                    os.remove(existing_srt['srt_file_path'])
                except Exception as e:
                    print(f"Warning: Could not delete old SRT file: {e}")
            
                # Xóa chunks khỏi Elasticsearch
                try:
                    es_delete_result = elasticsearch_service.delete_video_chunks(video_id)
                    if es_delete_result['success']:
                        print(f"✅ Deleted {es_delete_result.get('deleted_count', 0)} Elasticsearch records")
                    else:
                        print(f"⚠️ Elasticsearch deletion warning: {es_delete_result['message']}")
                except Exception as e:
                    print(f"⚠️ Elasticsearch deletion error: {str(e)}")
            
            # Reset video status về pending
            mongo.db.videos.update_one(
                {'_id': ObjectId(video_id)},
                {'$set': {'srt_status': 0, 'updated_at': datetime.utcnow()}}
            )
        
        # BƯỚC 1: CRAWL SRT FILE
        print("Step 1: Crawling SRT file...")
        srt_folder = 'srt_files'
        if not os.path.exists(srt_folder):
            os.makedirs(srt_folder)
        
        # Tạo tên file unique
        srt_filename = generate_unique_filename(video_url)
        srt_file_path = os.path.join(srt_folder, srt_filename)
        
        # Cấu hình yt-dlp để download subtitle
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en'],
            'subtitlesformat': 'srt',
            'skip_download': True,
            'cookies': 'cookies.txt',
            'outtmpl': srt_file_path.replace('.srt', '.%(ext)s'),
        }
        
        srt_success = False
        srt_error_message = ""
        actual_srt_file = None
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
                
                # Tìm file SRT thực tế được tạo
                if os.path.exists(srt_file_path):
                    actual_srt_file = srt_file_path
                    srt_success = True
                else:
                    # Tìm file có chứa video ID
                    video_id_from_url = video_url.split('v=')[-1].split('&')[0] if 'v=' in video_url else ''
                    for file in os.listdir(srt_folder):
                        if file.endswith('.srt') and video_id_from_url in file:
                            actual_srt_file = os.path.join(srt_folder, file)
                            srt_success = True
                            break
                    
                    # Nếu vẫn không tìm thấy, lấy file mới nhất
                    if not actual_srt_file:
                        srt_files = [f for f in os.listdir(srt_folder) if f.endswith('.srt')]
                        if srt_files:
                            latest_file = max(srt_files, key=lambda x: os.path.getctime(os.path.join(srt_folder, x)))
                            actual_srt_file = os.path.join(srt_folder, latest_file)
                            srt_success = True
                            
        except Exception as e:
            srt_error_message = str(e)
            logging.error(f"Lỗi khi download subtitle: {e}")
        
        if not srt_success or not actual_srt_file:
            return jsonify({
                'success': False,
                'error': f'Failed to download subtitle: {srt_error_message}',
                'step': 'crawl_srt'
            }), 500
        
        # Lưu thông tin SRT file vào database
        actual_filename = os.path.basename(actual_srt_file)
        srt_doc = {
            'video_url': video_url,
            'video_id': ObjectId(video_id),
            'srt_file_path': actual_srt_file,
            'srt_filename': actual_filename,
            'status': 0,  # 0: pending processing
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        srt_result = mongo.db.srt_files.insert_one(srt_doc)
        srt_id = srt_result.inserted_id
        
        # BƯỚC 2: CHUNK SRT FILE
        print("Step 2: Chunking SRT file...")
        chunks_data = process_srt_file(actual_srt_file)
        
        if not chunks_data:
            return jsonify({
                'success': False,
                'error': 'No chunks extracted from SRT file',
                'step': 'chunk_srt'
            }), 500
        
        # Lưu chunks vào MongoDB
        chunks_docs = []
        for i, chunk_info in enumerate(chunks_data):
            chunk_doc = {
                'srt_id': srt_id,
                'video_id': ObjectId(video_id),
                'video_url': video_url,
                'chunk_index': i,
                'text': chunk_info['text'],
                'time': chunk_info['time'],
                'created_at': datetime.utcnow()
            }
            chunks_docs.append(chunk_doc)
        
        # Insert tất cả chunks
        if chunks_docs:
            mongo.db.srt_chunks.insert_many(chunks_docs)
        
        # Cập nhật status của SRT file
        mongo.db.srt_files.update_one(
            {'_id': srt_id},
            {
                '$set': {
                    'status': 1,  # 1: processed
                    'chunks_count': len(chunks_data),
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        # BƯỚC 3: ELASTICSEARCH VECTOR INDEXING
        es_result = []
        print("Step 3: Elasticsearch vector indexing...")
        try:
            video_info = {
                'video_id': video_id,
                'title': video.get('title', ''),
                'channel_name': video.get('channel_name', ''),
                'url': video.get('url', ''),
                'channel_url': video.get('channel_url', '')  # Thêm channel URL
            }
            delete_query = {
                "query": {
                    "term": {
                        "url": video.get('url', ''),
                    }
                }
            }
            response = es_connection.delete_by_query(
                index=ES_INDEX_NAME,
                body=delete_query
            )
            deleted_count = response.get('deleted', 0)
            if deleted_count > 0:
                print(f"✅ Đã xóa thành công {deleted_count} document.")
            else:
                print("ℹ️ Không tìm thấy document nào khớp để xóa. Hãy kiểm tra lại giá trị URL và câu query.")
            for data in chunks_data:
                vector = transformer_model.encode(data['text']).tolist()
               
                # 2. Chuẩn bị document để index
                document = {
                    'url': video.get('url', ''),
                    'origin_content': data['text'],
                    'vector': vector,
                    'time': int(time.time()),
                    'url_channel': channel_url,
                }
                # 3. Index document vào Elasticsearch
                logging.info(f"   - Chunk {i+1}/{len(chunks_data)}: Đang index vào '{ES_INDEX_NAME}'...")
                response = es_connection.index(index=ES_INDEX_NAME, body=document)
                response_dict = dict(response)
                pretty_response_str = json.dumps(response_dict, indent=2, ensure_ascii=False)
                print("pretty_response_str",pretty_response_str)
                logging.info(f"   ✔ Chunk {i+1} đã được index thành công với ID:")
                es_result.append(pretty_response_str)
            print("data",chunks_data, video_info)
        except Exception as e:
            print(f"❌ Elasticsearch indexing error: {str(e)}")
            import traceback
            traceback.print_exc()
            # es_result = {
            #     'success': False,
            #     'message': f'Elasticsearch indexing error: {str(e)}',
            #     'indexed_count': 0
            # }
        
        # BƯỚC 4: CẬP NHẬT STATUS VIDEO
        print("Step 4: Updating video status...")
        mongo.db.videos.update_one(
            {'_id': ObjectId(video_id)},
            {'$set': {'status':1,'srt_status': 1, 'updated_at': datetime.utcnow()}}  # 1: SRT processed
        )
        
        return jsonify({
            'success': True,
            'message': f'Successfully crawled and chunked video with {len(chunks_data)} chunks',
            'srt_id': str(srt_id),
            'srt_filename': actual_filename,
            'srt_file_path': actual_srt_file,
            'chunks_count': len(chunks_data),
            'video_status': 1,
            'elasticsearch': es_result
        }), 200
        
    except Exception as e:
        log_exception("crawl_and_chunk_video", e)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/index-content', methods=['POST'])
def index_content():
    """
    API để index content thành chunks và lưu vào Elasticsearch
    Nhận vào: url_channel, url, content
    """
    try:
        data = request.get_json()
        url_channel = data.get('url_channel')
        url = data.get('url')
        content = data.get('content')
        
        if not all([url_channel, url, content]):
            return jsonify({
                'success': False,
                'error': 'url_channel, url, and content are required'
            }), 400
        
        print(f"Processing content for URL: {url}")
        
        # BƯỚC 1: KIỂM TRA VÀ XÓA DỮ LIỆU CŨ (nếu có)
        print("Step 1: Checking and deleting existing data...")
        try:
            delete_query = {
                "query": {
                    "term": {
                        "url": url
                    }
                }
            }
            response = es_connection.delete_by_query(
                index=ES_INDEX_NAME,
                body=delete_query
            )
            deleted_count = response.get('deleted', 0)
            if deleted_count > 0:
                print(f"✅ Đã xóa thành công {deleted_count} document cũ.")
            else:
                print("ℹ️ Không tìm thấy document nào khớp để xóa.")
        except Exception as e:
            print(f"⚠️ Lỗi khi xóa dữ liệu cũ: {str(e)}")
        
        # BƯỚC 2: CHIA CONTENT THÀNH CHUNKS
        print("Step 2: Splitting content into chunks...")
        chunks_data = split_content_into_chunks(content)
        
        if not chunks_data:
            return jsonify({
                'success': False,
                'error': 'No chunks extracted from content',
                'step': 'chunk_content'
            }), 500
        
        print(f"Created {len(chunks_data)} chunks from content")
        
        # BƯỚC 3: MÃ HÓA VÀ INDEX VÀO ELASTICSEARCH
        print("Step 3: Encoding and indexing to Elasticsearch...")
        indexed_count = 0
        es_errors = []
        
        try:
            for i, chunk_text in enumerate(chunks_data):
                try:
                    # Mã hóa chunk thành vector
                    vector = transformer_model.encode(chunk_text).tolist()
                    
                    # Chuẩn bị document để index
                    document = {
                        'url': url,
                        'url_channel': url_channel,
                        'origin_content': chunk_text,
                        'vector': vector,
                        'time': int(time.time()),
                        'chunk_index': i
                    }
                    
                    # Index document vào Elasticsearch
                    response = es_connection.index(index=ES_INDEX_NAME, body=document)
                    indexed_count += 1
                    print(f"   ✔ Chunk {i+1}/{len(chunks_data)} indexed successfully")
                    
                except Exception as e:
                    error_msg = f"Error indexing chunk {i+1}: {str(e)}"
                    print(f"   ❌ {error_msg}")
                    es_errors.append(error_msg)
                    
        except Exception as e:
            print(f"❌ Elasticsearch indexing error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # BƯỚC 4: TRẢ VỀ KẾT QUẢ
        result = {
            'success': True,
            'message': f'Successfully indexed {indexed_count} chunks from content',
            'total_chunks': len(chunks_data),
            'indexed_count': indexed_count,
            'url': url,
            'url_channel': url_channel
        }
        
        if es_errors:
            result['warnings'] = es_errors
            result['message'] += f' (with {len(es_errors)} errors)'
        
        return jsonify(result), 200
        
    except Exception as e:
        log_exception("index_content", e)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def split_content_into_chunks(content, max_chunk_size=500, overlap=50):
    """
    Chia content thành các chunks phù hợp
    """
    if not content or not content.strip():
        return []
    
    # Làm sạch content
    content = content.strip()
    
    # Nếu content ngắn hơn max_chunk_size, trả về 1 chunk
    if len(content) <= max_chunk_size:
        return [content]
    
    chunks = []
    start = 0
    
    while start < len(content):
        # Xác định vị trí kết thúc chunk
        end = start + max_chunk_size
        
        if end >= len(content):
            # Chunk cuối cùng
            chunks.append(content[start:].strip())
            break
        
        # Tìm vị trí tốt để cắt (ưu tiên dấu câu, xuống dòng)
        cut_positions = [
            content.rfind('.', start, end),
            content.rfind('!', start, end),
            content.rfind('?', start, end),
            content.rfind('\n', start, end),
            content.rfind(' ', start, end)
        ]
        
        # Chọn vị trí cắt tốt nhất
        best_cut = max([pos for pos in cut_positions if pos > start + max_chunk_size // 2])
        
        if best_cut > start:
            end = best_cut + 1
        
        chunk = content[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Tính toán vị trí bắt đầu chunk tiếp theo (có overlap)
        start = max(start + 1, end - overlap)
    
    return chunks

@main.route('/api/process-video-srt', methods=['POST'])
def process_video_srt():
    """
    API để xử lý SRT cho một video cụ thể
    """
    try:
        data = request.get_json()
        video_id = data.get('video_id')
        
        if not video_id:
            return jsonify({
                'success': False,
                'error': 'Video ID is required'
            }), 400
        
        mongo = get_mongo()
        
        # Lấy thông tin video
        video = mongo.db.videos.find_one({'_id': ObjectId(video_id)})
        if not video:
            return jsonify({
                'success': False,
                'error': 'Video not found'
            }), 404
        
        # Lấy SRT files của video này
        srt_files = list(mongo.db.srt_files.find({'video_url': video['url'], 'status': 0}))
        
        if not srt_files:
            return jsonify({
                'success': False,
                'error': 'No pending SRT files found for this video'
            }), 404
        
        total_chunks = 0
        processed_files = 0
        
        for srt_file in srt_files:
            srt_file_path = srt_file['srt_file_path']
            
            # Kiểm tra file tồn tại
            if not os.path.exists(srt_file_path):
                continue
            
            # Xử lý file SRT
            chunks_data = process_srt_file(srt_file_path)
            
            if not chunks_data:
                continue
            
            # Lưu chunks vào MongoDB
            chunks_docs = []
            for i, chunk_info in enumerate(chunks_data):
                chunk_doc = {
                    'srt_id': srt_file['_id'],
                    'video_id': ObjectId(video_id),
                    'video_url': video['url'],
                    'chunk_index': i,
                    'text': chunk_info['text'],
                    'time': chunk_info['time'],
                    'created_at': datetime.utcnow()
                }
                chunks_docs.append(chunk_doc)
            
            # Insert tất cả chunks
            if chunks_docs:
                mongo.db.srt_chunks.insert_many(chunks_docs)
                total_chunks += len(chunks_data)
            
            # Cập nhật status của SRT file
            mongo.db.srt_files.update_one(
                {'_id': srt_file['_id']},
                {
                    '$set': {
                        'status': 1,  # 1: processed
                        'chunks_count': len(chunks_data),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            processed_files += 1
        
        # Cập nhật status của video
        mongo.db.videos.update_one(
            {'_id': ObjectId(video_id)},
            {'$set': {'srt_status': 2, 'updated_at': datetime.utcnow()}}  # 2: SRT processed
        )
        
        return jsonify({
            'success': True,
            'message': f'Successfully processed {processed_files} SRT files with {total_chunks} chunks',
            'processed_files': processed_files,
            'chunks_count': total_chunks
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ==============================================================================
# ELASTICSEARCH APIs
# ==============================================================================

@main.route('/api/search', methods=['GET'])
def search_videos():
    """
    API tìm kiếm semantic trong Elasticsearch với vector embeddings
    """
    try:
        # Get search parameters
        query = request.args.get('q', '').strip()
        video_id = request.args.get('video_id', None)
        size = int(request.args.get('size', 10))
        from_ = int(request.args.get('from', 0))
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter "q" is required'
            }), 400
        
        # Perform semantic search
        search_result = elasticsearch_service.search_chunks(
            query=query,
            video_id=video_id,
            size=size,
            from_=from_
        )
        
        if search_result['success']:
            return jsonify({
                'success': True,
                'query': query,
                'results': search_result['results'],
                'total': search_result['total'],
                'took': search_result['took'],
                'message': f"Found {len(search_result['results'])} results"
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': search_result['message']
            }), 500
            
    except Exception as e:
        logging.error(f"Search API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Search failed: {str(e)}'
        }), 500

@main.route('/api/elasticsearch/stats', methods=['GET'])
def get_elasticsearch_stats():
    """
    API lấy thống kê Elasticsearch index
    """
    try:
        stats = elasticsearch_service.get_index_stats()
        
        if stats['success']:
            return jsonify({
                'success': True,
                'stats': stats
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': stats['message']
            }), 500
            
    except Exception as e:
        logging.error(f"Elasticsearch stats API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to get stats: {str(e)}'
        }), 500

@main.route('/api/elasticsearch/health', methods=['GET'])
def get_elasticsearch_health():
    """
    API kiểm tra health của Elasticsearch và model
    """
    try:
        health = elasticsearch_service.health_check()
        
        return jsonify({
            'success': True,
            'health': health
        }), 200
        
    except Exception as e:
        logging.error(f"Elasticsearch health API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Health check failed: {str(e)}'
        }), 500

@main.route('/api/elasticsearch/delete-video', methods=['POST'])
def delete_video_from_elasticsearch():
    """
    API xóa tất cả chunks của một video khỏi Elasticsearch
    """
    try:
        data = request.get_json()
        video_id = data.get('video_id') if data else None
        
        if not video_id:
            return jsonify({
                'success': False,
                'error': 'video_id is required'
            }), 400
        
        # Delete video chunks from Elasticsearch
        delete_result = elasticsearch_service.delete_video_chunks(video_id)
        
        if delete_result['success']:
            return jsonify({
                'success': True,
                'message': delete_result['message'],
                'deleted_count': delete_result.get('deleted_count', 0)
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': delete_result['message']
            }), 500
            
    except Exception as e:
        logging.error(f"Elasticsearch delete API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Delete failed: {str(e)}'
        }), 500

@main.route('/api/cleanup-video-data', methods=['POST'])
def cleanup_video_data():
    """
    API xóa toàn bộ dữ liệu cũ của video: SRT files, chunks, Elasticsearch records
    """
    try:
        data = request.get_json()
        video_id = data.get('video_id') if data else None
        
        if not video_id:
            return jsonify({
                'success': False,
                'error': 'video_id is required'
            }), 400
        
        mongo = get_mongo()
        cleanup_results = {
            'srt_files_deleted': 0,
            'chunks_deleted': 0,
            'elasticsearch_deleted': 0,
            'errors': []
        }
        
        # BƯỚC 1: XÓA SRT FILES
        try:
            print(f"🗑️ Deleting SRT files for video: {video_id}")
            srt_files = mongo.db.srt_files.find({'video_id': ObjectId(video_id)})
            
            for srt_file in srt_files:
                # Xóa file vật lý
                srt_file_path = srt_file.get('file_path')
                if srt_file_path and os.path.exists(srt_file_path):
                    try:
                        os.remove(srt_file_path)
                        print(f"✅ Deleted SRT file: {srt_file_path}")
                    except Exception as e:
                        print(f"⚠️ Failed to delete SRT file {srt_file_path}: {str(e)}")
                        cleanup_results['errors'].append(f"SRT file deletion: {str(e)}")
                
                # Xóa record trong MongoDB
                mongo.db.srt_files.delete_one({'_id': srt_file['_id']})
                cleanup_results['srt_files_deleted'] += 1
                
        except Exception as e:
            print(f"❌ Error deleting SRT files: {str(e)}")
            cleanup_results['errors'].append(f"SRT files: {str(e)}")
        
        # BƯỚC 2: XÓA CHUNKS
        try:
            print(f"🗑️ Deleting chunks for video: {video_id}")
            chunks_result = mongo.db.chunks.delete_many({'video_id': ObjectId(video_id)})
            cleanup_results['chunks_deleted'] = chunks_result.deleted_count
            print(f"✅ Deleted {chunks_result.deleted_count} chunks")
            
        except Exception as e:
            print(f"❌ Error deleting chunks: {str(e)}")
            cleanup_results['errors'].append(f"Chunks: {str(e)}")
        
        # BƯỚC 3: XÓA ELASTICSEARCH RECORDS
        try:
            print(f"🗑️ Deleting Elasticsearch records for video: {video_id}")
            es_delete_result = elasticsearch_service.delete_video_chunks(video_id)
            
            if es_delete_result['success']:
                cleanup_results['elasticsearch_deleted'] = es_delete_result.get('deleted_count', 0)
                print(f"✅ Deleted {cleanup_results['elasticsearch_deleted']} Elasticsearch records")
            else:
                print(f"⚠️ Elasticsearch deletion warning: {es_delete_result['message']}")
                cleanup_results['errors'].append(f"Elasticsearch: {es_delete_result['message']}")
                
        except Exception as e:
            print(f"❌ Error deleting Elasticsearch records: {str(e)}")
            cleanup_results['errors'].append(f"Elasticsearch: {str(e)}")
        
        # BƯỚC 4: RESET VIDEO STATUS
        try:
            print(f"🔄 Resetting video status for: {video_id}")
            mongo.db.videos.update_one(
                {'_id': ObjectId(video_id)},
                {
                    '$set': {
                        'srt_status': 0,  # 0: not processed
                        'status': 0,      # 0: not processed
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            print(f"✅ Reset video status")
            
        except Exception as e:
            print(f"❌ Error resetting video status: {str(e)}")
            cleanup_results['errors'].append(f"Video status: {str(e)}")
        
        # Tổng kết
        total_deleted = (cleanup_results['srt_files_deleted'] + 
                        cleanup_results['chunks_deleted'] + 
                        cleanup_results['elasticsearch_deleted'])
        
        if cleanup_results['errors']:
            return jsonify({
                'success': True,
                'message': f'Cleanup completed with {len(cleanup_results["errors"])} warnings',
                'results': cleanup_results,
                'total_deleted': total_deleted,
                'warnings': cleanup_results['errors']
            }), 200
        else:
            return jsonify({
                'success': True,
                'message': f'Successfully cleaned up all data for video',
                'results': cleanup_results,
                'total_deleted': total_deleted
            }), 200
            
    except Exception as e:
        logging.error(f"Cleanup API error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Cleanup failed: {str(e)}'
        }), 500

# ==============================================================================
# REQUESTS COLLECTION API
# ==============================================================================

@main.route('/api/requests', methods=['POST'])
def save_request():
    """
    API nhận POST raw JSON và lưu vào collection requests
    """
    try:
        # Lấy raw JSON data từ request
        raw_data = request.get_json()
        
        if not raw_data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        mongo = get_mongo()
        
        # Tạo document để lưu vào collection requests
        request_doc = {
            'data': raw_data,  # Lưu toàn bộ JSON data
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
            'content_type': request.content_type,
            'content_length': request.content_length
        }
        
        # Thêm các field metadata nếu có
        if 'timestamp' in raw_data:
            request_doc['client_timestamp'] = raw_data.get('timestamp')
        
        if 'source' in raw_data:
            request_doc['source'] = raw_data.get('source')
        
        if 'type' in raw_data:
            request_doc['request_type'] = raw_data.get('type')
        
        # Lưu vào MongoDB
        result = mongo.db.requests.insert_one(request_doc)
        
        return jsonify({
            'success': True,
            'message': 'Request saved successfully',
            'request_id': str(result.inserted_id),
            'created_at': request_doc['created_at'].isoformat()
        }), 201
        
    except Exception as e:
        log_exception("save_request", e)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/requests', methods=['GET'])
def get_requests():
    """
    API lấy danh sách requests từ collection requests
    """
    try:
        mongo = get_mongo()
        
        # Lấy parameters từ query
        limit = int(request.args.get('limit', 50))
        skip = int(request.args.get('skip', 0))
        source = request.args.get('source')
        request_type = request.args.get('type')
        
        # Build query
        query = {}
        if source:
            query['source'] = source
        if request_type:
            query['request_type'] = request_type
        
        # Query requests, sorted by newest first
        requests = list(mongo.db.requests.find(query)
                       .sort('created_at', -1)
                       .skip(skip)
                       .limit(limit))
        
        # Convert ObjectId to string for JSON serialization
        for req in requests:
            req['_id'] = str(req['_id'])
            if 'created_at' in req:
                req['created_at'] = req['created_at'].isoformat() if hasattr(req['created_at'], 'isoformat') else str(req['created_at'])
            if 'updated_at' in req:
                req['updated_at'] = req['updated_at'].isoformat() if hasattr(req['updated_at'], 'isoformat') else str(req['updated_at'])
        
        # Get total count
        total_count = mongo.db.requests.count_documents(query)
        
        return jsonify({
            'success': True,
            'requests': requests,
            'total_count': total_count,
            'limit': limit,
            'skip': skip
        }), 200
        
    except Exception as e:
        log_exception("get_requests", e)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/requests/<request_id>', methods=['GET'])
def get_request(request_id):
    """
    API lấy chi tiết một request cụ thể
    """
    try:
        mongo = get_mongo()
        
        request_doc = mongo.db.requests.find_one({'_id': ObjectId(request_id)})
        if not request_doc:
            return jsonify({
                'success': False,
                'error': 'Request not found'
            }), 404
        
        # Convert ObjectId to string for JSON serialization
        request_doc = serialize_document(request_doc)
        
        return jsonify({
            'success': True,
            'request': request_doc
        }), 200
        
    except Exception as e:
        log_exception("get_request", e)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@main.route('/api/requests/<request_id>', methods=['DELETE'])
def delete_request(request_id):
    """
    API xóa một request cụ thể
    """
    try:
        mongo = get_mongo()
        
        result = mongo.db.requests.delete_one({'_id': ObjectId(request_id)})
        
        if result.deleted_count == 0:
            return jsonify({
                'success': False,
                'error': 'Request not found'
            }), 404
        
        return jsonify({
            'success': True,
            'message': 'Request deleted successfully'
        }), 200
        
    except Exception as e:
        log_exception("delete_request", e)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
