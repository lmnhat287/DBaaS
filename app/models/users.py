from flask_login import UserMixin
from werkzeug.security import check_password_hash
from bson import ObjectId

class User(UserMixin):
    def __init__(self, user_doc):
        self.id = str(user_doc['_id'])
        self.username = user_doc['username']
    
    @staticmethod
    def get_user_by_username(username):
        from app.extensions import mongo_user
        user_doc = mongo_user['users'].find_one({"username": username})
        return User(user_doc) if user_doc else None

    @staticmethod
    def validate_login(username, password):
        from app.extensions import mongo_user
        user_doc = mongo_user['users'].find_one({"username": username})
        if user_doc and check_password_hash(user_doc['password_hash'], password):
            return User(user_doc)
        return None
