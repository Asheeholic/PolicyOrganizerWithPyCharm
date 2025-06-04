from flask_mail import Message, Mail
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