from flask import Flask
import os
from datetime import timedelta
from flask_login import LoginManager
from flask_session import Session
from models.user import User

class Config:
    # Base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'csrf-key-please-change'
    
    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # File upload settings
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB max file size
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'txt-dir')
    XLSX_FOLDER = os.path.join(BASE_DIR, 'xlsx-dir')
    ALLOWED_EXTENSIONS = {'txt'}
    
    # Database
    DB_DIR = os.path.join(BASE_DIR, 'database')
    DB_FILE = os.path.join(DB_DIR, 'auth.json')

def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config['JSON_AS_ASCII'] = False
    app.config['SECRET_KEY'] = 'your-secret-key-here'

    # Session configurations
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_FILE_DIR'] = os.path.join(app.root_path, 'flask_session')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    
    # Ensure session directory exists
    if not os.path.exists(app.config['SESSION_FILE_DIR']):
        os.makedirs(app.config['SESSION_FILE_DIR'])
    
    # Load configurations
    app.config.from_object(Config)
    
    # Ensure directories exist
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.XLSX_FOLDER, exist_ok=True)
    os.makedirs(Config.DB_DIR, exist_ok=True)

    # Login manager setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # 로그인되지 않은 사용자는 login 페이지로
    login_manager.login_message = "Please login to access this page."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)
    
    # Setup CSRF protection
    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect(app)
    
    # Setup session interface
    Session(app)
    
    # Register error handlers
    @app.errorhandler(413)
    def too_large(e):
        return {"error": "File is too large"}, 413
    
    @app.errorhandler(404)
    def not_found(e):
        return {"error": "Resource not found"}, 404
    
    return app