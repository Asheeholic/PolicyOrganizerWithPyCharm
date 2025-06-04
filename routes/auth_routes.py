from flask import Blueprint, render_template, redirect, url_for, flash, session, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from flask_wtf.csrf import CSRFError
from forms.forms import LoginForm, OTPSetupForm, RegisterForm, EmailVerificationForm
from models.user import User
from qrcode import make as generate_qr_code
from utils.email import send_verification_email, generate_verification_code
import base64
import qrcode
from io import BytesIO
import pyotp


auth = Blueprint('auth', __name__)

# login route
# This route handles user login, including optional MFA setup if the user has not enabled it yet.
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


# This route handles the setup of Multi-Factor Authentication (MFA) for users who have not yet enabled it.
# It generates a QR code for the user to scan with their authenticator app, 
# and verifies the OTP code entered by the user.
@auth.route('/setup-mfa', methods=['GET', 'POST'])
def setup_mfa():
    if not session.get('pre_auth_username'):
        flash('Please login first', 'warning')
        return redirect(url_for('auth.login'))
        
    form = OTPSetupForm()
    username = session.get('pre_auth_username')
    
    if request.method == 'GET':
        # QR 코드 생성 로직 디버깅
        try:
            otp_secret = User.setup_mfa(username)
            if not otp_secret:
                current_app.logger.error(f"Failed to generate OTP secret for user: {username}")
                flash('Failed to setup MFA', 'danger')
                return redirect(url_for('auth.login'))
            
            # QR 코드 URL 생성
            totp = pyotp.TOTP(otp_secret)
            qr_url = totp.provisioning_uri(username, issuer_name="NBU Policy Analyzer")
            
            # QR 코드 이미지 생성
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 이미지를 base64로 인코딩
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            qr_code = base64.b64encode(buffered.getvalue()).decode()
            
            current_app.logger.debug(f"QR Code generated successfully for user: {username}")
            
            return render_template('setup_mfa.html', form=form, qr_code=qr_code)
            
        except Exception as e:
            current_app.logger.error(f"Error generating QR code: {str(e)}")
            flash('Error setting up MFA', 'danger')
            return redirect(url_for('auth.login'))
        
    # POST request handling
    if form.validate_on_submit():
        try:
            # OTP 코드 검증 및 MFA 활성화
            if User.enable_mfa(username, form.otp_code.data):
                session.pop('pre_auth_username', None)
                flash('MFA setup successful!', 'success')
                return redirect(url_for('main.go_home'))
            else:
                flash('Invalid OTP code', 'danger')
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Error verifying OTP: {str(e)}', 'danger')
        
        return redirect(url_for('auth.setup_mfa'))
    
    # If form validation fails
    return render_template('setup_mfa.html', form=form)


# This route handles user registration, including email verification.
@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            verification_code = generate_verification_code()
            user = User.create_user(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                verification_code=verification_code
            )
            
            send_verification_email(form.email.data, verification_code)
            
            # 이메일 주소를 세션에 저장
            session['verification_email'] = form.email.data
            
            flash('Registration successful! Please check your email for verification code.', 'success')
            return redirect(url_for('auth.verify_email'))
        except Exception as e:
            flash(str(e), 'danger')
    
    return render_template('register.html', form=form)

@auth.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    if 'verification_email' not in session:
        return redirect(url_for('auth.register'))
        
    form = EmailVerificationForm()
    if form.validate_on_submit():
        email = session['verification_email']
        if User.verify_email_code(email, form.code.data):
            session.pop('verification_email', None)
            flash('Email verified successfully! You can now login.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid or expired verification code.', 'danger')
    
    return render_template('verify_email.html', form=form)



# This route handles user logout, clearing the session and redirecting to the login page.
# It also provides a success message upon logout.
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Successfully logged out', 'success')
    return redirect(url_for('auth.login'))


# This error handler catches CSRF errors and redirects the user to the registration page with a flash message.
@auth.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash('The form has expired. Please try again.', 'danger')
    return redirect(url_for('auth.register'))