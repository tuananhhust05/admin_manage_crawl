from flask import Flask
from flask_pymongo import PyMongo
import os

# Khởi tạo mongo instance toàn cục
mongo = None

def create_app():
    global mongo
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    # Cấu hình MongoDB
    app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://mongodb:27017/playfantasy365')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # Khởi tạo MongoDB
    mongo = PyMongo(app)
    
    # Đăng ký blueprint
    from app.routes import main
    app.register_blueprint(main)
    
    return app, mongo

def get_mongo():
    return mongo
