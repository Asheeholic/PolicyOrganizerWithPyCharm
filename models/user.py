from flask_login import UserMixin
from database.db_config import users_table
from werkzeug.security import generate_password_hash, check_password_hash
import pyotp
import qrcode
import base64
from io import BytesIO
from tinydb import Query

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data.get('username')
        self.username = user_data.get('username')
        self.password_hash = user_data.get('password')
        self.otp_secret = user_data.get('otp_secret')
        self.otp_enabled = user_data.get('otp_enabled', False)

    @staticmethod
    def get(user_id):
        User_query = Query()
        user_data = users_table.get(User_query.username == user_id)
        return User(user_data) if user_data else None

    @staticmethod
    def create_user(username, password):
        if User.get(username):
            raise ValueError('Username already exists')
            
        user = {
            'username': username,
            'password': generate_password_hash(password),
            'otp_secret': None,
            'otp_enabled': False
        }
        users_table.insert(user)
        return User(user)
    
    @staticmethod
    def verify_password(user, password):
        return check_password_hash(user.password_hash, password)

    @staticmethod
    def verify_otp(user, otp_code):
        if not user.otp_enabled or not user.otp_secret:
            return True
        totp = pyotp.TOTP(user.otp_secret)
        return totp.verify(otp_code)

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
        User = Query()
        user = users_table.get(User.username == username)
        if not user or not user.get('otp_secret'):
            return False
            
        totp = pyotp.TOTP(user['otp_secret'])
        if totp.verify(otp_code):
            users_table.update({'otp_enabled': True}, User.username == username)
            return True
        return False

    @staticmethod
    def get_otp_qr_url(username, otp_secret):
        totp = pyotp.TOTP(otp_secret)
        return totp.provisioning_uri(
            username,
            issuer_name="NBU Policy Analyzer"
        )

    # ... existing methods ...