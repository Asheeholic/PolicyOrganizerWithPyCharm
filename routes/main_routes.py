from flask import Blueprint, render_template, redirect, url_for, current_app
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return redirect(url_for('auth.login'))

@main.route('/home')
@login_required
def go_home():
     # 디버깅을 위한 로그 추가
    current_app.logger.debug(f"User authenticated: {current_user.is_authenticated}")
    current_app.logger.debug(f"Current user: {current_user.username if current_user.is_authenticated else 'Not logged in'}")
    return render_template('index.html')

@main.route('/solution')
@login_required
def go_solution():
    return render_template('solution.html')