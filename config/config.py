import logging
import os
import json
from flask import Flask, render_template, current_app
from datetime import timedelta
from flask_login import LoginManager
from flask_session import Session
from models.user import User
from logging.handlers import RotatingFileHandler
from flask_wtf.csrf import CSRFProtect
from utils.email import mail

class Config:

    """
    Flask application configuration class.
    This class contains all the necessary configurations for the Flask application,
    including environment settings, security keys, session management, file upload settings,
    database configurations, and logging setup.
    """
    # Environment settings
    ENV = os.environ.get('FLASK_ENV', 'development')
    # DEBUG = ENV == 'development'
    TESTING = False

    # Base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
   # Security - production에서는 반드시 환경변수로 설정
    if ENV == 'production':
        SECRET_KEY = os.environ['SECRET_KEY']  # 환경변수 없으면 에러 발생
        WTF_CSRF_SECRET_KEY = os.environ['WTF_CSRF_SECRET_KEY']
    else:
        SECRET_KEY = 'dev-key-please-change-in-production'
        WTF_CSRF_SECRET_KEY = 'csrf-key-please-change'
    WTF_CSRF_ENABLED = True  # Enable CSRF protection

    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    SESSION_FILE_DIR = os.path.join(BASE_DIR, 'flask_session')
    
    if ENV == 'production':
        SESSION_COOKIE_SECURE = True
        SESSION_COOKIE_HTTPONLY = True
        SESSION_COOKIE_SAMESITE = 'Strict'
        SESSION_COOKIE_DOMAIN = os.environ.get('SESSION_COOKIE_DOMAIN', None)  # 도메인 설정
    else:
        SESSION_COOKIE_SECURE = False
        SESSION_COOKIE_HTTPONLY = True  # 개발환경에서도 보안을 위해 유지
        SESSION_COOKIE_SAMESITE = 'Lax'
        SESSION_COOKIE_DOMAIN = None  # 개발환경에서는 도메인 설정하지 않음
    
    # File upload settings
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB max file size
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'txt-dir')
    XLSX_FOLDER = os.path.join(BASE_DIR, 'xlsx-dir')
    ALLOWED_EXTENSIONS = {'txt'}
    
    # Database
    DB_DIR = os.path.join(BASE_DIR, 'database')
    DB_FILE = os.path.join(DB_DIR, 'auth.json')


    # Util directories
    UTIL_DIR = os.path.join(BASE_DIR, 'utils')

    # Mail configuration
    MAIL_FILE = os.path.join(UTIL_DIR, 'mail-info.json')
    try:
        with open(MAIL_FILE, 'r') as f:
            mail_config = json.load(f)
            MAIL_SERVER = mail_config.get('MAIL_SERVER', os.environ.get('MAIL_SERVER'))
            MAIL_PORT = int(mail_config.get('MAIL_PORT', os.environ.get('MAIL_PORT', '587')))
            MAIL_USE_TLS = mail_config.get('MAIL_USE_TLS', True)
            MAIL_USERNAME = mail_config.get('MAIL_USERNAME', os.environ.get('MAIL_USERNAME'))
            MAIL_PASSWORD = mail_config.get('MAIL_PASSWORD', os.environ.get('MAIL_PASSWORD'))
            MAIL_DEFAULT_SENDER = mail_config.get('MAIL_DEFAULT_SENDER', os.environ.get('MAIL_DEFAULT_SENDER'))
    except FileNotFoundError:
        current_app.logger.warning(f"Mail config file not found: {MAIL_FILE}. Using environment variables.")
        MAIL_SERVER = os.environ.get('MAIL_SERVER')
        MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
        MAIL_USE_TLS = True
        MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
        MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
        MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')


    #   Logging configuration
    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    LOG_FILE = os.path.join(LOG_DIR, 'nbupolicy.log')
    LOG_LEVEL = logging.DEBUG  # Set to DEBUG for development, INFO or WARNING for production
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

def create_app():
    app = Flask(__name__, 
                template_folder='../templates', 
                static_folder='../static')

    # Load configurations
    app.config.from_object(Config)

    # Initialize Flask-Mail
    mail.init_app(app)
    
    # Ensure required directories exist
    os.makedirs(Config.SESSION_FILE_DIR, exist_ok=True)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.XLSX_FOLDER, exist_ok=True)
    os.makedirs(Config.DB_DIR, exist_ok=True)

    # Login manager setup
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "로그인이 필요한 페이지입니다."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)
    
    # Setup CSRF protection
    csrf = CSRFProtect(app)
    
    # Setup session interface
    Session(app)
    
     # Register error handlers
    @app.errorhandler(413)
    def too_large(e):
        return render_template('error.html',
            error="파일 크기 초과",
            message="업로드하려는 파일이 너무 큽니다. 최대 크기는 32MB입니다."), 413
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html',
            error="페이지를 찾을 수 없음",
            message="요청하신 페이지를 찾을 수 없습니다."), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('error.html',
            error="서버 오류",
            message="서버에 문제가 발생했습니다. 잠시 후 다시 시도해주세요."), 500
       # Setup logging
    if not os.path.exists(Config.LOG_DIR):
        os.makedirs(Config.LOG_DIR)
    
    # Configure logging
    formatter = logging.Formatter(
        fmt=Config.LOG_FORMAT,
        datefmt='%Y-%m-%d %H:%M:%S %z'
    )
    
    # File handler for all logs
    file_handler = RotatingFileHandler(
        Config.LOG_FILE,
        maxBytes=10240000,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(Config.LOG_LEVEL)
    
    # Console handler for development
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if Config.ENV == 'development' else logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    root_logger.setLevel(Config.LOG_LEVEL)
    
    # Configure Flask logger
    app.logger.setLevel(Config.LOG_LEVEL)
    
    # Remove default Flask console handler to avoid duplicate logs
    for handler in app.logger.handlers:
        app.logger.removeHandler(handler)
    
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    
    app.logger.info('Application startup')
    app.logger.info(f'Environment: {Config.ENV}')
    app.logger.info(f'Debug mode: {app.debug}')
    
    return app
