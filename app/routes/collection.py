from flask import Blueprint, render_template, redirect, url_for, flash, send_file, request
from app.extensions import mongo
import datetime, os, json
from bson.regex import Regex

collection_bp = Blueprint("collection", __name__)
#Chức năng CRUD cho collection trong MongoDB
@collection_bp.route("/<db_name>/<collection_name>/documents")
def view_documents(db_name, collection_name):
    try:
        page = int(request.args.get('page', 1))  # Lấy trang hiện tại, mặc định 1
        per_page = 8  # Documents mỗi trang

        collection = mongo.cx[db_name][collection_name]
        total_docs = collection.count_documents({})
        documents = list(collection.find().skip((page - 1) * per_page).limit(per_page))
        for doc in documents:
            doc['_id'] = str(doc['_id'])

        first_doc = collection.find_one()
        if first_doc:
            field_names = list(first_doc.keys())
        else:
            field_names = []
    
    except Exception as e:
        flash(f"Lỗi khi tải documents: {e}", "danger")
        documents = []
        field_names = []
        total_docs = 0

    total_pages = (total_docs + per_page - 1) // per_page  # Làm tròn lên
    start_page = max(1, page - 2)
    end_page = min(total_pages, page + 2)

    return render_template("collections.html",
                           db_name=db_name,
                           collection_name=collection_name,
                           collections=mongo.cx[db_name].list_collection_names(),
                           documents=documents,
                           field_names=field_names,
                           page=page,
                           total_pages=total_pages,
                           start_page=start_page,
                           end_page=end_page
)

@collection_bp.route("/<db_name>/<collection_name>/delete", methods=["POST"])
def delete_collection(db_name, collection_name):
    try:
        mongo.cx[db_name].drop_collection(collection_name)
        flash(f"Đã xoá collection {collection_name}", "success")
    except Exception as e:
        flash(f"Lỗi khi xoá collection: {e}", "danger")
    return redirect(url_for("main.view_collections", db_name=db_name))

@collection_bp.route("/<db_name>/<collection_name>/export", methods=["POST"])
def export_collection(db_name, collection_name):
    try:
        collection = mongo.cx[db_name][collection_name]
        docs = list(collection.find({}))  
        for doc in docs:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{collection_name}_{timestamp}.json"
        path = os.path.join("app", "static", "backups", filename)

        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(docs, f, ensure_ascii=False, indent=2)

        return send_file(path, as_attachment=True)
    except Exception as e:
        flash(f"Lỗi khi export collection: {e}", "danger")
        return redirect(url_for("main.view_collections", db_name=db_name))

@collection_bp.route("/<db_name>/create_collection", methods=["POST"])
def create_collection(db_name):
    collection_name = request.form.get("collection_name")
    
    if not collection_name:
        flash("Vui lòng nhập tên Collection!", "danger")
        return redirect(url_for('main.view_collections', db_name=db_name))
    
    db = mongo.cx[db_name]
    
    if collection_name in db.list_collection_names():
        flash(f"Collection '{collection_name}' đã tồn tại!", "warning")
    else:
        try:
            db.create_collection(collection_name)
            flash(f"Tạo Collection '{collection_name}' thành công!", "success")
        except Exception as e:
            flash(f"Lỗi khi tạo Collection: {e}", "danger")

    return redirect(url_for('main.view_collections', db_name=db_name))

@collection_bp.route("/<db_name>/<old_name>/rename", methods=["POST"])
def rename_collection(db_name, old_name):
    new_name = request.form.get("new_name")
    if not new_name:
        flash("Vui lòng nhập tên mới cho collection.", "warning")
        return redirect(url_for("main.view_collections", db_name=db_name))

    try:
        db = mongo.cx[db_name]
        # Kiểm tra tên collection mới đã tồn tại chưa
        if new_name in db.list_collection_names():
            flash(f"Collection '{new_name}' đã tồn tại trong database!", "danger")
        else:
            db[old_name].aggregate([{"$out": new_name}])  # copy sang tên mới
            db.drop_collection(old_name)
            flash(f"Đã đổi tên collection từ '{old_name}' thành '{new_name}'", "success")
    except Exception as e:
        flash(f"Lỗi khi đổi tên collection: {e}", "danger")

    return redirect(url_for("main.view_collections", db_name=db_name))


#Cac chuc nang CRUD cho document trong collection MongoDB
@collection_bp.route("/<db_name>/<collection_name>/add", methods=["POST"])
def add_document(db_name, collection_name):
    try:
        json_data = request.form.get("json_data")
        if not json_data:
            flash("Chưa nhập nội dung JSON.", "warning")
            return redirect(url_for('collection.view_documents', db_name=db_name, collection_name=collection_name))

        doc = json.loads(json_data)
        mongo.cx[db_name][collection_name].insert_one(doc)
        flash("Thêm document thành công!", "success")
    except Exception as e:
        flash(f"Lỗi khi thêm document: {e}", "danger")

    return redirect(url_for('collection.view_documents', db_name=db_name, collection_name=collection_name))

@collection_bp.route("/<db_name>/<collection_name>/delete/<doc_id>", methods=["POST"])
def delete_document(db_name, collection_name, doc_id):
    try:
        mongo.cx[db_name][collection_name].delete_one({"_id": doc_id})
        flash("Đã xoá document thành công!", "success")
    except Exception as e:
        flash(f"Lỗi khi xoá document: {e}", "danger")

    return redirect(url_for('collection.view_documents', db_name=db_name, collection_name=collection_name))

@collection_bp.route("/<db_name>/<collection_name>/update/<doc_id>", methods=["POST"])
def update_document(db_name, collection_name, doc_id):
    try:
        json_data = request.form.get("json_data")
        if not json_data:
            flash("Chưa nhập nội dung JSON mới.", "warning")
            return redirect(url_for('collection.view_documents', db_name=db_name, collection_name=collection_name))

        new_data = json.loads(json_data)
        mongo.cx[db_name][collection_name].update_one(
            {"_id": doc_id},
            {"$set": new_data}
        )
        flash("Cập nhật document thành công!", "success")
    except Exception as e:
        flash(f"Lỗi khi cập nhật document: {e}", "danger")

    return redirect(url_for('collection.view_documents', db_name=db_name, collection_name=collection_name))

from bson.regex import Regex

@collection_bp.route("/<db_name>/<collection_name>/search", methods=["GET", "POST"])
def search_documents(db_name, collection_name):
    try:
        field = request.form.get("field")
        value = request.form.get("value")
        page = int(request.args.get('page', 1))
        per_page = 1

        collection = mongo.cx[db_name][collection_name]

        # Build search query
        if field and value:
            if field == "_id":
                # Exact match for _id
                filter_query = {"_id": value}
            else:
                # Case-insensitive partial match for other fields
                filter_query = {
                    field: {
                        "$regex": value,
                        "$options": "i"  # i for case-insensitive
                    }
                }
                
                # Handle number fields
                try:
                    num_value = float(value)
                    # Add numeric search condition
                    filter_query = {
                        "$or": [
                            {field: num_value},  # Exact number match
                            filter_query  # Text partial match
                        ]
                    }
                except ValueError:
                    pass  # Not a number, keep text search only
        else:
            filter_query = {}

        # Get total matching documents
        total_docs = collection.count_documents(filter_query)

        # Get paginated results
        documents = list(
            collection.find(filter_query)
            .sort([("_id", 1)])  # Sort by _id
            .skip((page - 1) * per_page)
            .limit(per_page)
        )

        # Convert ObjectId to string
        for doc in documents:
            doc['_id'] = str(doc['_id'])

        total_pages = (total_docs + per_page - 1) // per_page
        start_page = max(1, page - 2)
        end_page = min(total_pages, page + 2)

        return render_template(
            "collections.html",
            db_name=db_name,
            collection_name=collection_name,
            collections=mongo.cx[db_name].list_collection_names(),
            documents=documents,
            field_names=[],
            page=page,
            total_pages=total_pages,
            start_page=start_page,
            end_page=end_page,
            search_field=field,
            search_value=value
        )

    except Exception as e:
        flash(f"Lỗi khi tìm documents: {e}", "danger")
        return render_template(
            "collections.html",
            db_name=db_name,
            collection_name=collection_name,
            collections=mongo.cx[db_name].list_collection_names(),
            documents=[],
            field_names=[],
            page=1,
            total_pages=1,
            start_page=1,
            end_page=1
        )