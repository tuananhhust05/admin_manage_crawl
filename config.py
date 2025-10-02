import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-super-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    PORT = int(os.getenv('PORT', 5001))
    
    # MongoDB Configuration
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://admin:password123@localhost:27017/playfantasy365?authSource=admin')
    
    # YouTube API Configuration
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', 'AIzaSyBfvol09E1FSgzoDQgf0c4r5oNj8PC4buY')
    
    # MongoDB Admin Credentials
    MONGO_ROOT_USERNAME = os.getenv('MONGO_ROOT_USERNAME', 'admin')
    MONGO_ROOT_PASSWORD = os.getenv('MONGO_ROOT_PASSWORD', 'password123')
