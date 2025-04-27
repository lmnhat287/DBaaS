# routes/main_routes.py
from flask import Blueprint, render_template
from app.extensions import mongo
main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def home():
    return render_template("index.html")

@main_bp.route("/databases")
def show_databases():
    # Lấy danh sách tất cả database (trừ hệ thống)
    all_dbs = mongo.cx.list_database_names()
    user_dbs = [db for db in all_dbs if db not in ['admin', 'local', 'config', 'user']]
    return render_template("databases.html", databases=user_dbs)

@main_bp.route("/databases/<db_name>/collections")
def view_collections(db_name):
    # Lấy tên các collection trong DB
    collections = mongo.cx[db_name].list_collection_names()
    # Render template collections.html với biến db_name, collections
    return render_template("collections.html",
                           db_name=db_name,
                           collections=collections)


