from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_login import current_user, login_user, logout_user, login_required
from forms.forms import LoginForm, OTPSetupForm, RegisterForm
from models.user import User
import qrcode
import base64
from io import BytesIO

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.go_home'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get(form.username.data)  # get_user를 get으로 변경
        if user and User.verify_password(user, form.password.data):
            if not user.otp_enabled:
                session['pre_auth_username'] = user.username
                return redirect(url_for('auth.setup_mfa'))
                
            if form.otp.data and User.verify_otp(user, form.otp.data):
                login_user(user)
                flash('Successfully logged in!', 'success')
                return redirect(url_for('main.go_home'))
            else:
                flash('Invalid OTP code', 'danger')
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@auth.route('/setup-mfa', methods=['GET', 'POST'])
def setup_mfa():
    if not session.get('pre_auth_username'):
        return redirect(url_for('auth.login'))
        
    form = OTPSetupForm()
    username = session['pre_auth_username']
    
    if request.method == 'GET':
        otp_secret = User.setup_mfa(username)
        qr_url = User.get_otp_qr_url(username, otp_secret)
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_code = base64.b64encode(buffered.getvalue()).decode()
        
        return render_template('setup_mfa.html', form=form, qr_code=qr_code)
        
    if form.validate_on_submit():
        if User.enable_mfa(username, form.otp_code.data):
            session.pop('pre_auth_username')
            flash('MFA setup successful! Please login again.', 'success')
            return redirect(url_for('auth.login'))
        flash('Invalid OTP code', 'danger')
        
    return render_template('setup_mfa.html', form=form)


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('logged_in'):
        return redirect(url_for('main.go_home'))
        
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            User.create_user(form.username.data, form.password.data)
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash('Registration failed. Please try again.', 'danger')
            
    return render_template('register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Successfully logged out', 'success')
    return redirect(url_for('auth.login'))