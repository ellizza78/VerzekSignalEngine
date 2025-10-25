import os, jwt, datetime
from utils.mailer import send_test_email
from email.mime.text import MIMEText
import smtplib

SECRET_KEY = os.getenv("JWT_SECRET", "verzek-secret-key")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.zoho.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)
FROM_NAME = os.getenv("FROM_NAME", "Verzek Innovative Solutions")

def generate_verification_token(email):
    payload = {
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["email"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def send_verification_email(to_email, token):
    verify_url = f"https://verzekautotrader.com/verify?token={token}"
    subject = "Verify your VerzekAutoTrader account"
    body = f"""
    Hello 👋,

    Thank you for registering on VerzekAutoTrader!
    Please verify your email by clicking the link below:

    ✅ {verify_url}

    This link expires in 24 hours.
    If you didn’t create this account, you can safely ignore this email.

    — Verzek Innovative Solutions
    """

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
    print(f"✅ Verification email sent to {to_email}")

def send_password_reset_email(to_email, token):
    reset_url = f"https://verzekautotrader.com/reset-password?token={token}"
    subject = "Reset your VerzekAutoTrader password"
    body = f"""
    Hello,

    You requested to reset your password. Click the link below:

    🔐 {reset_url}

    This link will expire in 1 hour.

    — Verzek Innovative Solutions
    """

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
    print(f"✅ Password reset email sent to {to_email}")