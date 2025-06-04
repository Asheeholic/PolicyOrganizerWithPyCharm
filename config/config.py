import logging
import os
from flask import Flask, render_template
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
    DEBUG = ENV == 'development'
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
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_FILE_DIR = os.path.join(BASE_DIR, 'flask_session')
    
    # File upload settings
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB max file size
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'txt-dir')
    XLSX_FOLDER = os.path.join(BASE_DIR, 'xlsx-dir')
    ALLOWED_EXTENSIONS = {'txt'}
    
    # Database
    DB_DIR = os.path.join(BASE_DIR, 'database')
    DB_FILE = os.path.join(DB_DIR, 'auth.json')

    # Mail settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = True
    ## Todo : Need Fix
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'xxxxxxxxxxxxx@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'xxxxxxxxxxxxxxxx')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'test@gtsolution.co.kr')

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
    login_manager.login_message = "Please login to access this page."
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
            error="File Too Large",
            message="The file you tried to upload is too large. Maximum size is 32MB."), 413
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html',
            error="Page Not Found",
            message="The requested page could not be found."), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('error.html',
            error="Internal Server Error",
            message="Something went wrong. Please try again later."), 500
    

    # Setup logging
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/nbupolicy.log', 
                                         maxBytes=10240, 
                                         backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('NBU Policy Analyzer startup')
    
    return app
