from flask_mail import Message, Mail
from flask import current_app
import random
import string

mail = Mail()

def generate_verification_code():
    """6자리 인증 코드 생성"""
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(email, verification_code):
    """인증 코드를 이메일로 전송"""
    subject = "NBU Policy Analyzer - Email Verification"
    body = f"""
    Welcome to NBU Policy Analyzer!
    
    Your verification code is: {verification_code}
    
    This code will expire in 10 minutes.
    If you did not request this code, please ignore this email.
    """
    
    msg = Message(subject=subject,
                 recipients=[email],
                 body=body)
    mail.send(msg)

def send_reset_email(email, verification_code):
    """비밀번호 재설정 인증 코드 전송"""
    subject = "NBU Policy Analyzer - 비밀번호 재설정"
    body = f"""
    비밀번호 재설정을 요청하셨습니다.
    
    인증 코드: {verification_code}
    
    이 코드는 10분 후에 만료됩니다.
    비밀번호 재설정을 요청하지 않으셨다면 이 이메일을 무시하시기 바랍니다.
    """
    
    try:
        msg = Message(subject=subject,
                     recipients=[email],
                     body=body)
        mail.send(msg)
        current_app.logger.info(f"Reset email sent to {email}")
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send reset email to {email}: {str(e)}")
        return False