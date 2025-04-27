# extensions.py
from flask_login import LoginManager
from flask_pymongo import PyMongo

# Khởi tạo MongoDB
mongo = PyMongo()
login_manager = LoginManager()
mongo_user = None  # ✅ Sẽ gán sau


def init_extensions(app):
    global mongo_user
    # Khởi tạo MongoDB
    mongo.init_app(app)

    # Khởi tạo Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    from pymongo import MongoClient
    from app.models.users import User

    # Kết nối đến MongoDB    
    client = MongoClient(app.config['MONGO_URI'])
    mongo_user = client['user']  # ✅ DB tên "user"

    @login_manager.user_loader
    def load_user(user_id):
        from bson import ObjectId
        from app.extensions import mongo_user
        try:
            object_id = ObjectId(user_id)
            user_doc = mongo_user['users'].find_one({"_id": object_id})
        except Exception:
        # Nếu không phải ObjectId, thử tìm bằng username
            user_doc = mongo_user['users'].find_one({"username": user_id})

        return User(user_doc) if user_doc else None