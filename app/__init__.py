from flask import Flask, request, redirect, url_for, flash
from app.extensions import init_extensions
from app.config import Config
from flask_login import current_user

# Import các blueprint

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    init_extensions(app)

    # Require login for all routes except auth
    @app.before_request
    def require_login():
        # List of endpoints that don't require authentication
        public_endpoints = ['auth.login', 'auth.register', 'static']
        
        # Skip auth check for public endpoints
        if request.endpoint in public_endpoints:
            return None
            
        # Skip auth check for static files
        if request.path.startswith('/static/'):
            return None
            
        # Require login for all other routes
        if not current_user.is_authenticated:
            flash('Vui lòng đăng nhập để truy cập!', 'warning')
            return redirect(url_for('auth.login', next=request.url))


    from app.routes.main import main_bp
    from app.routes.backup_restore import backup_bp
    from app.routes.collection import collection_bp
    from app.routes.database import database_bp
    from app.routes.auth import auth_bp
    # Register blueprint
    app.register_blueprint(main_bp)
    app.register_blueprint(backup_bp)
    app.register_blueprint(database_bp, url_prefix="/databases")
    app.register_blueprint(collection_bp, url_prefix="/collections")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    return app
__all__ = ['create_app']

