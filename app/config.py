# config.py
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "Nhat@20872400")
    ENV = os.environ.get("FLASK_ENV", "development")
    # MongoDB Atlas URI (cập nhật theo URI thật của bạn)
    MONGO_URI = os.environ.get("MONGO_URI")
    # MongoDB database name
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")