from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app.models.users import User
from app.extensions import mongo_user, mongo
from bson import ObjectId
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.validate_login(username, password)
        # Kiểm tra form
        if not username or not password:
            flash('Vui lòng điền đầy đủ thông tin!', 'danger')
            return render_template('auth/login.html')
        else:
            flash('Sai tên đăng nhập hoặc mật khẩu!', 'danger')
        if user:
            login_user(user)
            flash('Đăng nhập thành công!', 'success')
            # Chuyển về trang người dùng định truy cập trước đó
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.home'))
        else:
            flash('Sai tên đăng nhập hoặc mật khẩu!', 'danger')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_collection = mongo.cx["user"]["users"]

        if user_collection.find_one({"username": username}):
            flash('Tên đăng nhập đã tồn tại!', 'danger')
        else:
            result = user_collection.insert_one({
                "username": username,
                "password": generate_password_hash(password),
                "role": "user"  # Mặc định là user
            })

            user_doc = user_collection.find_one({"_id": result.inserted_id})
            login_user(User(user_doc))

            flash('Đăng ký thành công! Chào mừng bạn.', 'success')
            return redirect(url_for('main.home'))

    return render_template('register.html')

@auth_bp.route('/profile', methods=["GET", "POST"])
@login_required
def profile():
    if current_user.role != "admin":
        abort(403)

    users_col = mongo.cx["user"]["users"]

    if request.method == "POST":
        user_id = request.form.get("user_id")
        new_role = request.form.get("new_role")

        if user_id and new_role:
            users_col.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"role": new_role}}
            )
            flash("Cập nhật vai trò thành công!", "success")
        return redirect(url_for("auth.profile"))
    # GET request
    all_users = users_col.find({"_id": {"$ne": ObjectId(current_user.id)}})
    return render_template("index.html", users=all_users)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đăng xuất thành công.', 'success')
    return redirect(url_for('auth.login'))
