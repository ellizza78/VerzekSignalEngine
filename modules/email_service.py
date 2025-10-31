import os
import smtplib
import ssl
import secrets
from datetime import datetime, timedelta
from email.mime.text import MIMEText

class EmailService:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", os.getenv("EMAIL_HOST", "smtp.gmail.com"))
        self.smtp_port = int(os.getenv("SMTP_PORT", os.getenv("EMAIL_PORT", "587")))
        self.smtp_user = os.getenv("SMTP_USER", os.getenv("EMAIL_USER"))
        self.smtp_pass = os.getenv("SMTP_PASS", os.getenv("EMAIL_PASS"))
        self.from_email = os.getenv("FROM_EMAIL", os.getenv("EMAIL_FROM", self.smtp_user))
        self.from_name = os.getenv("FROM_NAME", "Verzek Auto Trader")
        
        print(f"📧 Email Service Initialized:")
        print(f"   Host: {self.smtp_host}:{self.smtp_port}")
        print(f"   User: {self.smtp_user[:10] + '...' if self.smtp_user else 'NOT SET'}")
        print(f"   From: {self.from_email}")

    def _send(self, to_email, subject, html_body):
        """Send email via Gmail SMTP (TLS on port 587)"""
        msg = MIMEText(html_body, "html")
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = to_email

        if not self.smtp_user or not self.smtp_pass:
            print("⚠️ SMTP credentials missing — running in dev mode.")
            print(f"[DEV MODE EMAIL] Would send to {to_email} — Subject: {subject}")
            print(f"[DEV MODE] Body preview: {html_body[:100]}...")
            return {"success": False, "dev_mode": True, "message": "SMTP credentials not configured"}

        try:
            print(f"📤 Sending email to {to_email}...")
            print(f"   Subject: {subject}")
            print(f"   SMTP: {self.smtp_host}:{self.smtp_port}")
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {to_email}")
            return {"success": True, "dev_mode": False}
        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ SMTP Authentication failed: {e}")
            return {"success": False, "error": f"Authentication failed: {str(e)}"}
        except smtplib.SMTPException as e:
            print(f"❌ SMTP error: {e}")
            return {"success": False, "error": f"SMTP error: {str(e)}"}
        except Exception as e:
            print(f"❌ Email sending failed: {e}")
            return {"success": False, "error": str(e)}

    # === TOKEN MANAGEMENT ===
    def generate_verification_token(self):
        return secrets.token_urlsafe(32)

    def get_token_expiration(self):
        return (datetime.utcnow() + timedelta(hours=24)).isoformat()

    def is_token_valid(self, expires_at):
        try:
            exp = datetime.fromisoformat(expires_at)
            return datetime.utcnow() < exp
        except Exception:
            return False

    # === EMAIL TEMPLATES ===
    def send_verification_email(self, email, username, token):
        verify_url = f"https://verzekautotrader.com/api/auth/verify-email/{token}"
        html = f"""
        <h2>Verify your email</h2>
        <p>Hi {username},</p>
        <p>Click the button below to verify your VerzekAutoTrader account:</p>
        <p><a href="{verify_url}" style="background:#007BFF;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;">Verify Email</a></p>
        <p>This link expires in 24 hours.</p>
        """
        return self._send(email, "Verify your VerzekAutoTrader Account", html)

    def send_welcome_email(self, email, username):
        html = f"""
        <h2>Welcome to VerzekAutoTrader 🎉</h2>
        <p>Hi {username},</p>
        <p>Your account is now verified and active. You can log in and start trading anytime.</p>
        <p>🚀 <a href="https://verzekautotrader.com">Go to Dashboard</a></p>
        """
        return self._send(email, "Welcome to VerzekAutoTrader", html)

    def send_password_reset_email(self, email, username, token):
        reset_url = f"https://verzekautotrader.com/reset-password?token={token}"
        html = f"""
        <h2>Password Reset Request</h2>
        <p>Hi {username},</p>
        <p>We received a request to reset your password.</p>
        <p><a href="{reset_url}" style="background:#FF6600;color:white;padding:10px 20px;text-decoration:none;border-radius:5px;">Reset Password</a></p>
        <p>If you didn’t request this, you can safely ignore it.</p>
        """
        return self._send(email, "Reset your VerzekAutoTrader Password", html)


    def send_password_reset_success_email(self, email, username):
        """Send confirmation email after successful password reset"""
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #28a745;">Password Reset Successful ✅</h2>
            <p>Hi {username},</p>
            <p>Your password has been successfully reset.</p>
            <p>If you did not make this change, please contact support immediately at <a href="mailto:support@verzekautotrader.com">support@verzekautotrader.com</a></p>
            <p style="margin: 30px 0;">
                <a href="https://verzekautotrader.com" style="background:#007BFF;color:white;padding:12px 30px;text-decoration:none;border-radius:5px;display:inline-block;">Log In to Your Account</a>
            </p>
            <hr style="border: 1px solid #eee; margin: 20px 0;">
            <p style="color: #999; font-size: 12px;">VerzekAutoTrader - Automated Trading Platform</p>
        </div>
        """
        return self._send(email, "Password Reset Successful", html)


# Initialize global instance
email_service = EmailService()