"""
Email utilities using Resend API
"""
import os
import resend
from utils.logger import api_logger

# Configure Resend
resend.api_key = os.getenv("RESEND_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM", "support@verzekinnovative.com")


def send_password_reset_email(email: str, reset_token: str, user_id: int):
    """Send password reset email with token"""
    try:
        reset_url = f"https://verzek-app://reset-password?token={reset_token}&user_id={user_id}"
        
        params = {
            "from": EMAIL_FROM,
            "to": [email],
            "subject": "Reset Your VerzekAutoTrader Password",
            "html": f"""
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
        }
        
        email_response = resend.Emails.send(params)
        api_logger.info(f"Password reset email sent to {email}: {email_response}")
        return True
        
    except Exception as e:
        api_logger.error(f"Failed to send password reset email to {email}: {e}")
        return False


def send_verification_email(email: str, verification_token: str, user_id: int):
    """Send email verification link"""
    try:
        verification_url = f"https://verzek-app://verify-email?token={verification_token}&user_id={user_id}"
        
        params = {
            "from": EMAIL_FROM,
            "to": [email],
            "subject": "Verify Your VerzekAutoTrader Email",
            "html": f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #0A4A5C;">Welcome to VerzekAutoTrader!</h2>
                <p>Thank you for registering. Please verify your email address to activate your account.</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" style="background-color: #D4AF37; color: #0A4A5C; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">Verify Email</a>
                </div>
                <p style="color: #666;">Or copy this link:</p>
                <p style="background: #f5f5f5; padding: 10px; border-radius: 5px; word-break: break-all;">{verification_url}</p>
                <p style="color: #999; font-size: 12px; margin-top: 30px;">
                    This link expires in 24 hours.
                </p>
                <p style="color: #999; font-size: 12px;">
                    - VerzekAutoTrader Team
                </p>
            </div>
            """
        }
        
        email_response = resend.Emails.send(params)
        api_logger.info(f"Verification email sent to {email}: {email_response}")
        return True
        
    except Exception as e:
        api_logger.error(f"Failed to send verification email to {email}: {e}")
        return False


def send_welcome_email(email: str, full_name: str):
    """Send welcome email after successful registration"""
    try:
        params = {
            "from": EMAIL_FROM,
            "to": [email],
            "subject": "Welcome to VerzekAutoTrader!",
            "html": f"""
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
        }
        
        email_response = resend.Emails.send(params)
        api_logger.info(f"Welcome email sent to {email}: {email_response}")
        return True
        
    except Exception as e:
        api_logger.error(f"Failed to send welcome email to {email}: {e}")
        return False
