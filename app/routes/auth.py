from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app.models.users import User
from app.extensions import mongo_user

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
    # Kiểm tra xem người dùng đã đăng nhập chưa
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if mongo_user['users'].find_one({"username": username}):
            flash('Tên đăng nhập đã tồn tại!', 'danger')
        else:
            mongo_user['users'].insert_one({
                "username": username,
                "password_hash": generate_password_hash(password)
            })
            flash('Đăng ký thành công! Đăng nhập ngay.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đăng xuất thành công.', 'success')
    return redirect(url_for('auth.login'))
