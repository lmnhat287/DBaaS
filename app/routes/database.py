from flask import Blueprint, request, redirect, url_for, flash, render_template, abort
from app.extensions import mongo
from flask_login import current_user
database_bp = Blueprint("database", __name__)

@database_bp.route("/create_db", methods=["POST"])
def create_db():
    db_name = request.form.get("db_name")
    if not db_name:
        flash("Vui lòng nhập tên database!", "danger")
        return redirect(url_for("main.show_databases"))

    if db_name in mongo.cx.list_database_names():
        flash(f"Database '{db_name}' đã tồn tại!", "warning")
        return redirect(url_for("main.show_databases"))
    new_db = mongo.cx[db_name]
    new_db["sample_collection"].insert_one({"info": f"{db_name} created"})
    flash(f"Tạo database '{db_name}' thành công!", "success")
    return redirect(url_for("main.show_databases"))

@database_bp.route("/delete_db/<db_name>", methods=["POST"])
def delete_db(db_name):
    if current_user.role != "admin":
        abort(403) # Không có quyền
    try:
        mongo.cx.drop_database(db_name)
        flash(f"Đã xoá database {db_name}", "success")
    except Exception as e:
        flash(f"Lỗi khi xoá DB: {e}", "danger")
    return redirect(url_for("main.show_databases"))

@database_bp.route("/rename_db/<old_name>", methods=["POST"])
def rename_database(old_name):
    new_name = request.form.get("new_name")
    if not new_name:
        flash("Vui lòng nhập tên mới cho database!", "warning")
        return redirect(url_for("main.show_databases"))

    try:
        # Kiểm tra tên database mới đã tồn tại chưa
        if new_name in mongo.cx.list_database_names():
            flash(f"Database '{new_name}' đã tồn tại!", "danger")
        else:
            # Copy toàn bộ collections sang DB mới
            for collection_name in mongo.cx[old_name].list_collection_names():
                mongo.cx[old_name][collection_name].aggregate([
                    {"$match": {}},
                    {"$out": {"db": new_name, "coll": collection_name}}
                ])
            
            # Xóa database cũ
            mongo.cx.drop_database(old_name)
            flash(f"Đã đổi tên database từ '{old_name}' thành '{new_name}'", "success")
    except Exception as e:
        flash(f"Lỗi khi đổi tên database: {e}", "danger")

    return redirect(url_for("main.show_databases"))