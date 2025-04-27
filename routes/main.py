# routes/main_routes.py
import os
import tempfile
from flask import Blueprint, request, redirect, url_for, flash, render_template, current_app
from werkzeug.utils import secure_filename
from app.extensions import mongo, s3_client

main_blueprint = Blueprint("main", __name__)


@main_blueprint.route("/databases")
def show_databases():
    # Lấy danh sách tất cả database (trừ hệ thống)
    all_dbs = mongo.cx.list_database_names()
    user_dbs = [db for db in all_dbs if db not in ['admin', 'local', 'config']]
    return render_template("databases.html", databases=user_dbs)

@main_blueprint.route("/create_db", methods=["POST"])
def create_db():
    db_name = request.form.get("db_name")
    if not db_name:
        flash("Vui lòng nhập tên database!", "danger")
        return redirect(url_for("main.show_databases"))

    if db_name in mongo.cx.list_database_names():
        flash(f"Database '{db_name}' đã tồn tại!", "warning")
        return redirect(url_for("main.show_databases"))

    # Tạo 1 collection mẫu trong DB mới
    new_db = mongo.cx[db_name]  # mongo.cx là MongoClient
    new_db["sample_collection"].insert_one({"message": f"Database {db_name} đã tạo thành công!"})

    flash(f"Tạo database '{db_name}' thành công!", "success")
    return redirect(url_for("main.home"))

@main_blueprint.route("/upload", methods=["POST"])
def upload_backup():
    file = request.files.get("backup_file")
    if not file:
        flash("Chưa chọn file!", "warning")
        return redirect(url_for("main.upload_restore"))

    filename = secure_filename(file.filename)
    try:
        s3_client.upload_fileobj(
            file,
            current_app.config["AWS_S3_BUCKET"],
            filename
        )
        flash(f"Upload thành công: {filename}", "success")
    except Exception as e:
        flash(f"Upload thất bại: {str(e)}", "danger")

    return redirect(url_for("main.upload_restore"))

@main_blueprint.route("/upload_restore")
def upload_restore():
    try:
        objects = s3_client.list_objects_v2(Bucket=current_app.config["AWS_S3_BUCKET"])
        files = [obj["Key"] for obj in objects.get("Contents", [])]
    except Exception as e:
        flash(f"Lỗi tải danh sách backup: {str(e)}", "danger")
        files = []

    return render_template("upload_restore.html", backup_files=files)

import json

@main_blueprint.route("/restore", methods=["POST"])
def restore_backup():
    file_name = request.form.get("file_name")
    if not file_name:
        flash("Không có tên file", "warning")
        return redirect(url_for("main.upload_restore"))

    try:
        # Tạo file tạm
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            s3_client.download_fileobj(
                current_app.config["AWS_S3_BUCKET"],
                file_name,
                temp_file
            )
            temp_path = temp_file.name

        # Giả định file backup dạng JSON list: [{...}, {...}]
        with open(temp_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Restore vào MongoDB, dùng tên file làm tên collection
        db = mongo.cx["Restored_DB"]
        collection_name = os.path.splitext(file_name)[0]
        db[collection_name].delete_many({})  # Clear trước
        if isinstance(data, list):
            db[collection_name].insert_many(data)
        else:
            db[collection_name].insert_one(data)

        flash(f"Restore thành công vào collection '{collection_name}'", "success")
    except Exception as e:
        flash(f"Restore thất bại: {str(e)}", "danger")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return redirect(url_for("main.upload_restore"))