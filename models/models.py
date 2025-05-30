from tinydb import TinyDB, Query
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from pathlib import Path

# TinyDB 데이터베이스 파일 경로 지정
DB_PATH = Path(__file__).resolve().parent.parent / 'data' / 'tinydb.json'
# 데이터 디렉터리 생성
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
# TinyDB 인스턴스
_db = TinyDB(DB_PATH)
_UserQuery = Query()

class User(UserMixin):
    """
    TinyDB를 백엔드로 사용하는 User 모델.
    username, password_hash, mfa_enabled, mfa_secret 필드를 관리합니다.
    """
    def __init__(self, username, password_hash, mfa_enabled=False, mfa_secret=None):
        self.id = username
        self.username = username
        self.password_hash = password_hash
        self.mfa_enabled = mfa_enabled
        self.mfa_secret = mfa_secret

    @classmethod
    def get(cls, username):
        """
        사용자명을 기준으로 TinyDB에서 레코드 검색.
        없으면 None 반환.
        """
        result = _db.search(_UserQuery.username == username)
        if not result:
            return None
        data = result[0]
        return cls(
            username=data['username'],
            password_hash=data['password_hash'],
            mfa_enabled=data.get('mfa_enabled', False),
            mfa_secret=data.get('mfa_secret')
        )

    @classmethod
    def create(cls, username, password):
        """
        신규 사용자 생성. 비밀번호 해시화 후 TinyDB에 저장.
        """
        pw_hash = generate_password_hash(password)
        _db.insert({
            'username': username,
            'password_hash': pw_hash,
            'mfa_enabled': False,
            'mfa_secret': None
        })
        return cls(username, pw_hash)

    def save(self):
        """
        현재 인스턴스 상태를 TinyDB에 업데이트.
        """
        _db.update({
            'password_hash': self.password_hash,
            'mfa_enabled': self.mfa_enabled,
            'mfa_secret': self.mfa_secret
        }, _UserQuery.username == self.username)

    def set_password(self, password):
        """
        비밀번호 재설정 후 저장.
        """
        self.password_hash = generate_password_hash(password)
        self.save()

    def check_password(self, password):
        """
        입력된 비밀번호를 저장된 해시와 비교.
        """
        return check_password_hash(self.password_hash, password)
