from flask import Blueprint, render_template, redirect, url_for, flash, session, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from flask_wtf.csrf import CSRFError
from forms.forms import LoginForm, OTPSetupForm, RegisterForm, EmailVerificationForm, ForgotPasswordForm, ResetCodeVerificationForm, ResetPasswordForm
from models.user import User
from qrcode import make as generate_qr_code
from utils.email import send_verification_email, generate_verification_code, send_reset_email
import base64
import qrcode
from io import BytesIO
import pyotp

auth = Blueprint('auth', __name__)

# Authentication routes for the application
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.go_home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.get(form.username.data)
            if user and User.verify_password(user, form.password.data):
                if not user.otp_enabled:
                    session['pre_auth_username'] = user.username
                    return redirect(url_for('auth.setup_mfa'))
                
                if form.otp.data and User.verify_otp(user, form.otp.data):
                    login_user(user)
                    return redirect(url_for('main.go_home'))
                else:
                    flash('잘못된 인증번호입니다.', 'danger')
            else:
                flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'danger')
        except Exception as e:
            flash('로그인에 실패했습니다. 다시 시도해 주세요.', 'danger')
    
    return render_template('login.html', form=form)

# Authentication route for setting up Multi-Factor Authentication (MFA)
@auth.route('/setup-mfa', methods=['GET', 'POST'])
def setup_mfa():
    if not session.get('pre_auth_username'):
        flash('Please login first', 'warning')
        return redirect(url_for('auth.login'))
        
    form = OTPSetupForm()
    username = session.get('pre_auth_username')
    
    if request.method == 'GET':
        try:
            otp_secret = User.setup_mfa(username)
            if not otp_secret:
                flash('2단계 인증 설정에 실패했습니다.', 'danger')
                return redirect(url_for('auth.login'))
            
            totp = pyotp.TOTP(otp_secret)
            qr_url = totp.provisioning_uri(username, issuer_name="NBU Policy Analyzer")
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            qr_code = base64.b64encode(buffered.getvalue()).decode()
            
            return render_template('setup_mfa.html', form=form, qr_code=qr_code)
            
        except Exception as e:            
            flash('2단계 인증 설정 중 오류가 발생했습니다.', 'danger')
            return redirect(url_for('auth.login'))
    
    if form.validate_on_submit():
        try:
            if User.enable_mfa(username, form.otp_code.data):
                session.pop('pre_auth_username', None)
                flash('2단계 인증이 성공적으로 설정되었습니다!', 'success')
                return redirect(url_for('main.go_home'))
            else:
                flash('잘못된 인증번호입니다.', 'danger')
        except Exception as e:
            print(f"Error during MFA setup: {e}")
            flash('인증번호 확인 중 오류가 발생했습니다.', 'danger')
        
        return redirect(url_for('auth.setup_mfa'))
    
    return render_template('setup_mfa.html', form=form)

# Authentication route for user registration
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('이미 로그인되어 있습니다.', 'warning')
        return redirect(url_for('main.go_home'))

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
            session['verification_email'] = form.email.data
            
            flash('회원가입이 완료되었습니다! 이메일로 전송된 인증 코드를 확인해주세요.', 'success')
            return redirect(url_for('auth.verify_email'))
        except Exception as e:
            flash(str(e), 'danger')
    
    return render_template('register.html', form=form)

# Authentication route for email verification
@auth.route('/verify-email', methods=['GET', 'POST'])
def verify_email():    
    if 'verification_email' not in session:
        return redirect(url_for('auth.register'))
        
    form = EmailVerificationForm()
    if form.validate_on_submit():
        email = session['verification_email']
        if User.verify_email_code(email, form.code.data):
            session.pop('verification_email', None)
            flash('이메일 인증이 완료되었습니다! 이제 로그인하실 수 있습니다.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('잘못되었거나 만료된 인증 코드입니다.', 'danger')
    
    return render_template('verify_email.html', form=form)



@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.go_home'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        try:
            user = User.get_by_email(email)
            if user:
                verification_code = generate_verification_code()  # 6자리 코드 생성
                User.set_reset_code(email, verification_code)
                send_reset_email(email, verification_code)
                session['reset_email'] = email
                flash('비밀번호 재설정 코드가 이메일로 전송되었습니다.', 'info')
                return redirect(url_for('auth.verify_reset_code'))
            flash('등록되지 않은 이메일입니다.', 'danger')
        except Exception as e:
            flash('인증 코드 전송에 실패했습니다. 다시 시도해주세요.', 'danger')
    
    return render_template('forgot_password.html', form=form)

@auth.route('/verify-reset-code', methods=['GET', 'POST'])
def verify_reset_code():
    if 'reset_email' not in session:
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetCodeVerificationForm()
    if form.validate_on_submit():
        email = session['reset_email']
        if User.verify_reset_code(email, form.code.data):            
            session['reset_verified'] = True
            flash('인증되었습니다. 새로운 비밀번호를 설정해주세요.', 'success')
            return redirect(url_for('auth.reset_password'))
        flash('잘못되었거나 만료된 인증 코드입니다.', 'danger')
    
    return render_template('verify_reset_code.html', form=form)

@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if not session.get('reset_verified'):
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        email = session['reset_email']
        if User.reset_password(email, form.password.data):
            # Clear all reset-related session data
            session.pop('reset_email', None)
            session.pop('reset_verified', None)
            flash('비밀번호가 성공적으로 재설정되었습니다!', 'success')
            return redirect(url_for('auth.login'))
        flash('비밀번호 재설정에 실패했습니다. 다시 시도해주세요.', 'danger')
    
    return render_template('reset_password.html', form=form)


# Authentication route for password reset
@auth.route('/logout')
@login_required
def logout():    
    logout_user()
    flash('로그아웃 되었습니다.', 'success')
    return redirect(url_for('auth.login'))

# Error handler for CSRF errors
@auth.errorhandler(CSRFError)
def handle_csrf_error(e):
    flash('The form has expired. Please try again.', 'danger')
    return redirect(url_for('auth.register'))