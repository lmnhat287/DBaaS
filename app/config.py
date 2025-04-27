# config.py
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    ENV = os.environ.get("FLASK_ENV", "development")
    DEBUG = ENV == "development"
    # MongoDB Atlas URI (cập nhật theo URI thật của bạn)
    MONGO_URI = os.environ.get("MONGO_URI")
    # MongoDB database name
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
    APP_NAME = "DBaaS"
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
