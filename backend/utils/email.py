"""
Email utilities using SMTP (Gmail)
Switched from Resend due to API outage (Cloudflare 500 errors)
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.logger import api_logger

# SMTP Configuration
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_FROM = os.getenv("EMAIL_FROM", "support@verzekinnovative.com")


def send_email_smtp(to_email: str, subject: str, html_content: str):
    """Send email using SMTP"""
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = subject
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        
        api_logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        api_logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def send_password_reset_email(email: str, reset_token: str, user_id: int):
    """Send password reset email with token"""
    try:
        reset_url = f"https://api.verzekinnovative.com/api/auth/reset-password?token={reset_token}&user_id={user_id}"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #0A4A5C;">Password Reset Request</h2>
            <p>You requested to reset your password for VerzekAutoTrader.</p>
            <p>Click the button below to reset your password:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" style="background-color: #D4AF37; color: #0A4A5C; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">Reset Password</a>
            </div>
            <p style="color: #666;">Or copy this link:</p>
            <p style="background: #f5f5f5; padding: 10px; border-radius: 5px; word-break: break-all;">{reset_url}</p>
            <p style="color: #999; font-size: 12px; margin-top: 30px;">
                This link expires in 15 minutes. If you didn't request this, please ignore this email.
            </p>
            <p style="color: #999; font-size: 12px;">
                - VerzekAutoTrader Team
            </p>
        </div>
        """
        
        success = send_email_smtp(email, "Reset Your VerzekAutoTrader Password", html_content)
        if success:
            api_logger.info(f"Password reset email sent to {email}")
        return success
        
    except Exception as e:
        api_logger.error(f"Failed to send password reset email to {email}: {e}")
        return False


def send_verification_email(email: str, verification_token: str, user_id: int):
    """Send email verification link"""
    try:
        verification_url = f"https://api.verzekinnovative.com/api/auth/verify-email?token={verification_token}&user_id={user_id}"
        
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #0A4A5C;">Welcome to VerzekAutoTrader!</h2>
            <p>Thank you for registering. Please verify your email address to activate your account.</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_url}" style="background-color: #D4AF37; color: #0A4A5C; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">Verify Email</a>
            </div>
            <p style="color: #666;">Or copy this link:</p>
            <p style="background: #f5f5f5; padding: 10px; border-radius: 5px; word-break: break-all;">{verification_url}</p>
            <p style="color: #999; font-size: 12px; margin-top: 30px;">
                This link expires in 15 minutes.
            </p>
            <p style="color: #999; font-size: 12px;">
                - VerzekAutoTrader Team
            </p>
        </div>
        """
        
        success = send_email_smtp(email, "Verify Your VerzekAutoTrader Email", html_content)
        if success:
            api_logger.info(f"Verification email sent to {email}")
        return success
        
    except Exception as e:
        api_logger.error(f"Failed to send verification email to {email}: {e}")
        return False


def send_welcome_email(email: str, full_name: str):
    """Send welcome email after successful registration"""
    try:
        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #0A4A5C;">Welcome aboard, {full_name}!</h2>
            <p>Your VerzekAutoTrader account is now active.</p>
            <h3 style="color: #D4AF37;">Getting Started:</h3>
            <ul style="line-height: 1.8;">
                <li>Connect your exchange accounts (Binance, Bybit, Phemex, or Kraken)</li>
                <li>Configure your trading settings and risk management</li>
                <li>Join our Telegram group for signals</li>
                <li>Upgrade to VIP or PREMIUM for auto-trading</li>
            </ul>
            <p style="margin-top: 30px;">Need help? Contact our support:</p>
            <p>📧 Email: support@verzekinnovative.com</p>
            <p>💬 Telegram: t.me/+7442859456</p>
            <p style="color: #999; font-size: 12px; margin-top: 30px;">
                - VerzekAutoTrader Team
            </p>
        </div>
        """
        
        success = send_email_smtp(email, "Welcome to VerzekAutoTrader!", html_content)
        if success:
            api_logger.info(f"Welcome email sent to {email}")
        return success
        
    except Exception as e:
        api_logger.error(f"Failed to send welcome email to {email}: {e}")
        return False
