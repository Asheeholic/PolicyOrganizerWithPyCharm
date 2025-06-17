from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp
import json
import os

# This file contains form classes for user authentication and registration in a Flask application.
class LoginForm(FlaskForm):
    username = StringField('아이디', validators=[
        DataRequired(message='아이디를 입력해주세요.'), 
        Length(min=4, max=20, message='아이디는 4~20자 사이여야 합니다.')
    ])
    password = PasswordField('비밀번호', validators=[
        DataRequired(message='비밀번호를 입력해주세요.'), 
        Length(min=6, message='비밀번호는 최소 6자 이상이어야 합니다.')
    ])
    otp = StringField('인증번호')  # Optional during first login

class OTPSetupForm(FlaskForm):
    otp_code = StringField('인증번호', validators=[
        DataRequired(message='인증번호를 입력해주세요.'),
        Length(min=6, max=6, message='인증번호는 6자리여야 합니다.')
    ])


def allowed_email(form, field):
    email_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'email.json')
    try:
        with open(email_file, 'r') as f:
            data = json.load(f)
            allowed_emails = [email.lower() for email in data.get('allowed_emails', [])]
            if field.data.lower() not in allowed_emails:
                raise ValidationError('등록이 허용되지 않은 이메일입니다. 관리자에게 문의하세요.')
    except FileNotFoundError:
        raise ValidationError('이메일 인증 시스템을 사용할 수 없습니다. 관리자에게 문의하세요.')
    except json.JSONDecodeError:
        raise ValidationError('이메일 인증 시스템 오류가 발생했습니다. 관리자에게 문의하세요.')


# This form is used for user registration
class RegisterForm(FlaskForm):

    class Meta:
        csrf = True  # Enable CSRF protection 

    email = StringField('이메일', validators=[
        DataRequired(message='이메일을 입력해주세요.'),
        Email(message='올바른 이메일 주소를 입력해주세요.'),
        allowed_email
    ])

    username = StringField('아이디', validators=[
        DataRequired(message='아이디를 입력해주세요.'),
        Length(min=4, max=20, message="아이디는 4~20자 사이여야 합니다.")
    ])

    password = PasswordField('비밀번호', validators=[
        DataRequired(message='비밀번호를 입력해주세요.'),
        Length(min=4, message="비밀번호는 최소 4자 이상이어야 합니다.")
    ])
    
    confirm_password = PasswordField('비밀번호 확인', validators=[
        DataRequired(message='비밀번호 확인을 입력해주세요.'),
        EqualTo('password', message='비밀번호가 일치하지 않습니다.')
    ])

class EmailVerificationForm(FlaskForm):
    code = StringField('Verification Code', validators=[
        DataRequired(),
        Length(min=6, max=6, message="Verification code must be 6 digits")
    ])
    submit = SubmitField('Verify Email')

# This form is used for password reset requests
class ForgotPasswordForm(FlaskForm):
    email = EmailField('Email', validators=[
        DataRequired(),
        Email(),
        allowed_email
    ])
    submit = SubmitField('Send Reset Code')

class ResetCodeVerificationForm(FlaskForm):
    code = StringField('Verification Code', validators=[
        DataRequired(),
        Length(min=6, max=6, message='Verification code must be 6 digits')
    ])
    submit = SubmitField('Verify Code')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters'),
        Regexp(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])', 
               message='Password must contain at least one uppercase letter, one lowercase letter, and one number')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')