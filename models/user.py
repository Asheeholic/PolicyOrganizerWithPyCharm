import pyotp
import qrcode
import base64
import os
import json
from flask_login import UserMixin
from database.db_config import users_table
from werkzeug.security import generate_password_hash, check_password_hash
from io import BytesIO
from tinydb import TinyDB, Query
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, Union
from flask import current_app


class User(UserMixin):
    def __init__(self, user_data: Dict[str, Any]):
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
    def get(user_id: str) -> Optional['User']:
        try:
            # DB 파일이 존재하는지 확인
            if not os.path.exists(current_app.config['DB_FILE']):
                current_app.logger.error(f"Database file not found: {current_app.config['DB_FILE']}")
                return None

            # DB 연결
            users_table = TinyDB(current_app.config['DB_FILE']).table('users')
            User_query = Query()
            
            # 사용자 조회
            user_data = users_table.get(User_query.username == user_id)

            if user_data:
                return User(user_data)
            current_app.logger.warning(f"User not found: {user_id}")
            return None

        except json.decoder.JSONDecodeError as e:
            current_app.logger.error(f"JSON decode error in database: {str(e)}")
            return None
        except Exception as e:
            current_app.logger.error(f"Error getting user {user_id}: {str(e)}")
            return None    
    
    @staticmethod
    def create_user(username: str, email: str, password: str, verification_code: str) -> 'User':
        """Create a new user
        
        Args:
            username: Username for the new user
            email: Email address for the new user  
            password: Password for the new user
            verification_code: Email verification code
            
        Returns:
            User object for the new user
            
        Raises:
            ValueError: If username already exists
            RuntimeError: If database operation fails
        """
        try:
             # Check if username or email already exists
            User_query = Query()
            if users_table.get(User_query.username == username):
                raise ValueError("이미 존재하는 사용자명입니다.")
            if users_table.get(User_query.email == email):
                raise ValueError("이미 등록된 이메일입니다.")

                
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
            current_app.logger.info(f"New user created: {username}")
            return User(user)
        except Exception as e:
            current_app.logger.error(f"Error creating user {username}: {str(e)}")
            raise RuntimeError(f"Failed to create user: {str(e)}") from e    
        
    @staticmethod
    def verify_email_code(email: str, code: str) -> bool:
        """Verify email verification code
        
        Args:
            email: User's email address
            code: Verification code to check
            
        Returns:
            bool: True if verification successful, False otherwise
            
        Raises:
            RuntimeError: If database operation fails
        """
        try:
            User_query = Query()
            user = users_table.get(User_query.email == email)
            
            if not user:
                current_app.logger.warning(f"Verification attempt for non-existent email: {email}")
                return False
                
            if (user['verification_code'] != code or 
                datetime.fromisoformat(user['verification_code_expires']) < datetime.now(timezone.utc)):
                current_app.logger.warning(f"Invalid or expired verification code for email: {email}")
                current_app.logger.debug(f"Input code: {code}")
                current_app.logger.debug(f"Stored code: {user['verification_code']}")
                current_app.logger.debug(f"Stored expiry: {datetime.fromisoformat(user['verification_code_expires'])}")
                current_app.logger.debug(f"Current time (UTC): {datetime.now(timezone.utc)}")
                return False
                
            users_table.update({
                'email_verified': True,
                'verification_code': None,
                'verification_code_expires': None
            }, User_query.email == email)
            
            current_app.logger.info(f"Email verified successfully for: {email}")
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error verifying email {email}: {str(e)}")
            raise RuntimeError(f"Failed to verify email: {str(e)}") from e
    
    @staticmethod
    def verify_password(user, password):
        return check_password_hash(user.password_hash, password)

    @staticmethod
    def verify_otp(user, otp_code):
        """Verify OTP code for user"""
        try:
            current_app.logger.debug(f"Verifying OTP for user {user.username}")
            current_app.logger.debug(f"Input OTP code: {otp_code}")
            current_app.logger.debug(f"User OTP secret: {user.otp_secret}")
            
            if not user.otp_secret:
                current_app.logger.warning(f"No OTP secret set for user {user.username}")
                return False
                
            totp = pyotp.TOTP(user.otp_secret)
            # 현재 시간과 허용 시간 윈도우 확인
            current_time = datetime.now()
            current_app.logger.debug(f"Current time: {current_time}")
            current_app.logger.debug(f"Valid window: {totp.interval} seconds")
            
            # 생성된 OTP 코드 확인
            valid_codes = [
                totp.at(current_time - timedelta(seconds=30)),  # 이전 코드
                totp.now(),  # 현재 코드
                totp.at(current_time + timedelta(seconds=30))   # 다음 코드
            ]
            current_app.logger.debug(f"Valid OTP codes for current window: {valid_codes}")
            
            result = totp.verify(otp_code)
            current_app.logger.debug(f"OTP verification result: {result}")
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error verifying OTP for user {user.username}: {str(e)}")
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
    
    
    @staticmethod
    def get_by_email(email):
        """Get user by email"""
        try:
            User_query = Query()
            user_data = users_table.get(User_query.email == email)
            return User(user_data) if user_data else None
        except Exception as e:
            current_app.logger.error(f"Error getting user by email: {str(e)}")
            return None

    @staticmethod
    def set_reset_code(email, code):
        """Set password reset code"""
        try:
            User_query = Query()
            users_table.update({
                'reset_code': code,
                'reset_code_expires': (datetime.utcnow() + timedelta(minutes=10)).isoformat()
            }, User_query.email == email)
            return True
        except Exception as e:
            current_app.logger.error(f"Error setting reset code: {str(e)}")
            return False

    @staticmethod
    def verify_reset_code(email, code):
        """Verify password reset code"""
        try:
            User_query = Query()
            user_data = users_table.get(User_query.email == email)
            if not user_data:
                return False
            
            if (user_data.get('reset_code') == code and 
                datetime.fromisoformat(user_data.get('reset_code_expires')) > datetime.utcnow()):
                return True
            return False
        except Exception as e:
            current_app.logger.error(f"Error verifying reset code: {str(e)}")
            return False

    @staticmethod
    def reset_password(email, new_password):
        """Reset user password"""
        try:
            User_query = Query()
            users_table.update({
                'password': generate_password_hash(new_password),
                'reset_code': None,
                'reset_code_expires': None
            }, User_query.email == email)
            return True
        except Exception as e:
            current_app.logger.error(f"Error resetting password: {str(e)}")
            return False