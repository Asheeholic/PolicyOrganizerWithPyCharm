from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
import json
import os

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    otp = StringField('OTP Code')  # Optional during first login

class OTPSetupForm(FlaskForm):
    otp_code = StringField('OTP Code', validators=[DataRequired(), Length(min=6, max=6)])


def allowed_email(form, field):
    email_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'email.json')
    try:
        with open(email_file, 'r') as f:
            data = json.load(f)
            allowed_emails = [email.lower() for email in data.get('allowed_emails', [])]
            if field.data.lower() not in allowed_emails:
                raise ValidationError('This email is not authorized for registration. Please contact administrator.')
    except FileNotFoundError:
        raise ValidationError('Email verification system is currently unavailable. Please contact administrator.')
    except json.JSONDecodeError:
        raise ValidationError('Email verification system error. Please contact administrator.')


class RegisterForm(FlaskForm):

    class Meta:
        csrf = True  # Enable CSRF protection

    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Invalid email address'),
        allowed_email
    ])
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=20, message="Username must be between 4 and 20 characters")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=4, message="Password must be at least 4 characters")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])

class EmailVerificationForm(FlaskForm):
    code = StringField('Verification Code', validators=[
        DataRequired(),
        Length(min=6, max=6, message="Verification code must be 6 digits")
    ])
    submit = SubmitField('Verify Email')