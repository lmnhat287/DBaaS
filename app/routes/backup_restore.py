# app/routes/backup_restore.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from app.extensions import mongo
import os, json, datetime

backup_bp = Blueprint("backup", __name__)

# Thư mục lưu backup local
BACKUP_FOLDER = os.path.join("app", "static", "backups")
os.makedirs(BACKUP_FOLDER, exist_ok=True)

@backup_bp.route("/upload_restore", methods=["GET"])
def upload_restore():
    try:
        # Get backup files
        files = os.listdir(BACKUP_FOLDER)
        files = [f for f in files if f.endswith(".json")]
        
        # Get available databases
        all_dbs = mongo.cx.list_database_names()
        databases = [db for db in all_dbs if db not in ['admin', 'local', 'config']]
        
    except FileNotFoundError:
        files = []
        databases = []
    return render_template("upload_restore.html", backup_files=files, databases=databases)

@backup_bp.route("/upload", methods=["POST"])
def upload_backup():
    file = request.files.get("backup_file")
    if not file:
        flash("Chưa chọn file!", "warning")
        return redirect(url_for("backup.upload_restore"))

    filename = secure_filename(file.filename)
    save_path = os.path.join(BACKUP_FOLDER, filename)

    try:
        file.save(save_path)
        flash(f"Upload thành công: {filename}", "success")
    except Exception as e:
        flash(f"Lỗi khi lưu file: {e}", "danger")

    return redirect(url_for("backup.upload_restore"))

@backup_bp.route("/restore", methods=["POST"])
def restore_backup():
    file_name = request.form.get("file_name")
    target_db = request.form.get("target_db")
    new_db_name = request.form.get("new_db_name")
    
    if not file_name:
        flash("Không tìm thấy file backup!", "danger")
        return redirect(url_for("backup.upload_restore"))
        
    if not target_db:
        flash("Vui lòng chọn database!", "danger")
        return redirect(url_for("backup.upload_restore"))

    file_path = os.path.join(BACKUP_FOLDER, file_name)
    if not os.path.exists(file_path):
        flash("File không tồn tại!", "danger")
        return redirect(url_for("backup.upload_restore"))

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Get database name based on selection
        db_name = new_db_name if target_db == "new" else target_db
        if not db_name:
            flash("Tên database không hợp lệ!", "danger")
            return redirect(url_for("backup.upload_restore"))

        # Get collection name from filename (without timestamp)
        collection_name = os.path.splitext(file_name)[0].split('_')[0]
        
        # Restore to selected/new database
        db = mongo.cx[db_name]
        db[collection_name].delete_many({})
        if isinstance(data, list):
            db[collection_name].insert_many(data)
        else:
            db[collection_name].insert_one(data)

        flash(f"Restore thành công vào {db_name}.{collection_name}", "success")
    except Exception as e:
        flash(f"Restore thất bại: {e}", "danger")

    return redirect(url_for("backup.upload_restore"))
@backup_bp.route("/backup_collection", methods=["POST"])
def backup_collection():
    db_name = request.form.get("db_name")
    collection_name = request.form.get("collection_name")

    if not db_name or not collection_name:
        flash("Thiếu thông tin DB hoặc collection", "danger")
        return redirect(url_for("backup.upload_restore"))

    try:
        collection = mongo.cx[db_name][collection_name]
        data = list(collection.find({}))
        for doc in data:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{collection_name}_{timestamp}.json"
        save_path = os.path.join(BACKUP_FOLDER, filename)

        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        flash(f"Backup thành công: {filename}", "success")
    except Exception as e:
        flash(f"Lỗi khi backup: {e}", "danger")

    return redirect(url_for("backup.upload_restore"))

@backup_bp.route("/delete", methods=["POST"])
def delete_backup():
    file_name = request.form.get("file_name")
    if not file_name:
        flash("Không tìm thấy tên file!", "danger")
        return redirect(url_for("backup.upload_restore"))

    file_path = os.path.join(BACKUP_FOLDER, file_name)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            flash(f"Đã xóa file {file_name}", "success")
        else:
            flash("File không tồn tại!", "warning")
    except Exception as e:
        flash(f"Lỗi khi xóa file: {str(e)}", "danger")

    return redirect(url_for("backup.upload_restore"))