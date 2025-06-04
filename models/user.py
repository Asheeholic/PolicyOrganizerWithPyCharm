from flask_login import UserMixin
from database.db_config import users_table
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp
import qrcode
import base64
from io import BytesIO
from tinydb import Query
from datetime import datetime, timedelta, timezone

class User(UserMixin):
    def __init__(self, user_data):
        if user_data is None:
            raise ValueError("User data cannot be None")

        self.id = user_data.get('username')
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.password_hash = user_data.get('password')
        self.otp_secret = user_data.get('otp_secret')
        self.otp_enabled = user_data.get('otp_enabled', False)
        self.email_verified = user_data.get('email_verified', False)
        self.verification_code = user_data.get('verification_code')
        self.verification_code_expires = user_data.get('verification_code_expires')

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @staticmethod
    def get(user_id):
        User_query = Query()
        user_data = users_table.get(User_query.username == user_id)
        return User(user_data) if user_data else None

    @staticmethod
    def create_user(username, email, password,  verification_code):
        if User.get(username):
            raise ValueError('Username already exists')
            
        user = {
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'verification_code': verification_code,
            'verification_code_expires': (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(),
            'email_verified': False,
            'otp_secret': None,
            'otp_enabled': False
        }
        users_table.insert(user)
        return User(user)

    @staticmethod
    def verify_email_code(email, code):
        User_query = Query()
        user = users_table.get(User_query.email == email)
        
        if not user:
            return False
            
        if (user['verification_code'] != code or 
            datetime.fromisoformat(user['verification_code_expires']) < datetime.now(timezone.utc)):
            return False
            
        users_table.update({
            'email_verified': True,
            'verification_code': None,
            'verification_code_expires': None
        }, User_query.email == email)
        
        return True
    
    @staticmethod
    def verify_password(user, password):
        return check_password_hash(user.password_hash, password)

    @staticmethod
    def verify_otp(user, otp_code):
        try:
            if not user.otp_secret:
                return False
            totp = pyotp.TOTP(user.otp_secret)
            return totp.verify(otp_code)
        except Exception as e:
            return False

    @staticmethod
    def setup_mfa(username):
        User = Query()
        user = users_table.get(User.username == username)
        if not user:
            return None
        
        otp_secret = pyotp.random_base32()
        users_table.update({
            'otp_secret': otp_secret,
            'otp_enabled': False
        }, User.username == username)
        
        return otp_secret

    @staticmethod
    def enable_mfa(username, otp_code):
        User_query = Query()
        user = users_table.get(User_query.username == username)
        
        if not user:
            raise ValueError("User not found")
            
        if not User.verify_otp(User(user), otp_code):
            raise ValueError("Invalid OTP code")
            
        users_table.update({'otp_enabled': True}, User_query.username == username)
        return True

    @staticmethod
    def get_otp_qr_url(username, otp_secret):
        totp = pyotp.TOTP(otp_secret)
        return totp.provisioning_uri(
            username,
            issuer_name="NBU Policy Analyzer"
        )