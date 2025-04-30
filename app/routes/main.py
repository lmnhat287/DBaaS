# routes/main_routes.py
from flask import Blueprint, render_template
from app.extensions import mongo
from flask_login import current_user
from flask_login import login_required
from bson import ObjectId
main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    users = None
    if current_user.is_authenticated and current_user.role == "admin":
        users_col = mongo.cx["user"]["users"]
        users = list(users_col.find({"_id": {"$ne": ObjectId(current_user.id)}}))
    return render_template("index.html", users=users)

@main_bp.route("/databases")
@login_required
def show_databases():
    # Lấy danh sách tất cả database (trừ hệ thống)
    all_dbs = mongo.cx.list_database_names()
    system_dbs = ['admin', 'local', 'config', 'user']
    user_dbs = [db for db in all_dbs if db not in system_dbs]
    return render_template("databases.html", databases=user_dbs)

@main_bp.route("/databases/<db_name>/collections")
def view_collections(db_name):
    # Lấy tên các collection trong DB
    collections = mongo.cx[db_name].list_collection_names()
    # Render template collections.html với biến db_name, collections
    return render_template("collections.html",
                           db_name=db_name,
                           collections=collections)


