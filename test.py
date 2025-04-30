from pymongo import MongoClient
from werkzeug.security import generate_password_hash

# Kết nối MongoDB
client = MongoClient("mongodb+srv://lmnhat148:LMNhat287@mydatabase.5kr4r2f.mongodb.net")  # đổi thành URI thật
db = client['user']
users = db['users']

# Kiểm tra admin đã tồn tại chưa
if not users.find_one({"username": "admin"}):
    users.insert_one({
        "username": "admin",
        "password_hash": generate_password_hash("admin123"),
        "role": "admin"
    })
    print("Admin user created successfully!")
else:
    users.insert_one({
        "username": "admin",
        "password_hash": generate_password_hash("admin123"),
        "role": "admin"
    })
    print("Admin already exists.")