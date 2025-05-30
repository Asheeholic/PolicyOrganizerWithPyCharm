from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return redirect(url_for('auth.login'))

@main.route('/home')
@login_required
def go_home():
    return render_template('index.html')

@main.route('/solution')
@login_required
def go_solution():
    return render_template('solution.html')