from tinydb import TinyDB
import os

# 현재 스크립트의 디렉토리를 기준으로 절대 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, 'database')
DB_FILE = os.path.join(DB_DIR, 'auth.json')

# 데이터베이스 디렉토리가 없으면 생성
if not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR)

# TinyDB 초기화
db = TinyDB(DB_FILE)
users_table = db.table('users')