"""
Email Service Module
--------------------
Reusable email utility with Zoho SMTP integration
Supports verification emails, password reset, notifications, and support emails
"""

import os
import smtplib
import secrets
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict
from datetime import datetime, timedelta


class EmailService:
    """Handles all email operations via Zoho SMTP"""
    
    def __init__(self):
        """Initialize email service with Zoho SMTP configuration"""
        # Zoho SMTP Configuration
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.zoho.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '465'))  # SSL port
        self.smtp_user = os.getenv('SMTP_USER', 'support@vezekinnovative.com')
        self.smtp_pass = os.getenv('SMTP_PASS', '')
        self.from_email = os.getenv('FROM_EMAIL', 'support@vezekinnovative.com')
        self.from_name = os.getenv('FROM_NAME', 'Verzek Innovative Solutions')
        
        # Base URL for verification links
        self.base_url = os.getenv('BASE_URL', 'https://verzek-auto-trader.replit.app')
        
        # Token expiration (24 hours)
        self.token_expiration_hours = 24
        
        # Rate limiting: track sent emails
        self.email_cache = {}  # {email: last_sent_timestamp}
        self.min_resend_interval = 60  # 60 seconds between resend
        
        # Email send logging
        self.log_path = 'logs/email_logs.txt'
        os.makedirs('logs', exist_ok=True)
    
    def _log_email(self, to: str, subject: str, success: bool, error: str = None):
        """Log email send attempt
        
        Args:
            to: Recipient email
            subject: Email subject
            success: Whether send was successful
            error: Error message if failed
        """
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        status = "✅ SUCCESS" if success else "❌ FAILED"
        log_entry = f"[{timestamp}] {status} | TO: {to} | SUBJECT: {subject}"
        if error:
            log_entry += f" | ERROR: {error}"
        
        print(log_entry)
        
        try:
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(log_entry + '\n')
        except Exception as e:
            print(f"⚠️ Failed to write email log: {e}")
    
    def send_email(self, to: str, subject: str, html: str, plain: Optional[str] = None) -> Dict[str, any]:
        """Send email via Zoho SMTP (REUSABLE UTILITY)
        
        Args:
            to: Recipient email address
            subject: Email subject
            html: HTML email body
            plain: Plain text email body (optional, auto-generated from html if not provided)
            
        Returns:
            {
                "success": True/False,
                "message": "Status message",
                "error": "Error details" (if failed)
            }
        """
        try:
            # Check if SMTP is configured
            if not self.smtp_pass:
                dev_msg = f"⚠️ SMTP not configured. Email would be sent to: {to}"
                print(dev_msg)
                self._log_email(to, subject, False, "SMTP_PASS not configured")
                return {
                    "success": False,
                    "message": "SMTP not configured (dev mode)",
                    "dev_mode": True
                }
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to
            
            # Attach plain text (if not provided, use stripped HTML)
            if not plain:
                plain = html.replace('<br>', '\n').replace('</p>', '\n\n')
                # Remove all HTML tags
                import re
                plain = re.sub(r'<[^>]+>', '', plain)
            
            msg.attach(MIMEText(plain, 'plain'))
            msg.attach(MIMEText(html, 'html'))
            
            # Connect and send via SSL (port 465)
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            
            self._log_email(to, subject, True)
            
            return {
                "success": True,
                "message": f"Email sent to {to}"
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Email send error: {error_msg}")
            self._log_email(to, subject, False, error_msg)
            return {
                "success": False,
                "message": "Failed to send email",
                "error": error_msg
            }
    
    def generate_verification_token(self) -> str:
        """Generate secure random verification token"""
        return secrets.token_urlsafe(32)
    
    def get_token_expiration(self) -> str:
        """Get token expiration timestamp (24 hours from now)"""
        expiration = datetime.utcnow() + timedelta(hours=self.token_expiration_hours)
        return expiration.isoformat()
    
    def is_token_valid(self, token_expires: str) -> bool:
        """Check if verification token is still valid
        
        Args:
            token_expires: ISO format timestamp
            
        Returns:
            True if token hasn't expired
        """
        try:
            expiration = datetime.fromisoformat(token_expires)
            return datetime.utcnow() < expiration
        except (ValueError, TypeError):
            return False
    
    def can_resend_email(self, email: str) -> bool:
        """Check if email can be resent (rate limiting)
        
        Args:
            email: User email address
            
        Returns:
            True if enough time has passed since last send
        """
        if email not in self.email_cache:
            return True
        
        last_sent = self.email_cache[email]
        time_elapsed = time.time() - last_sent
        return time_elapsed >= self.min_resend_interval
    
    def send_verification_email(self, email: str, username: str, token: str) -> Dict[str, any]:
        """Send verification email to user
        
        Args:
            email: User email address
            username: Username
            token: Verification token
            
        Returns:
            {
                "success": True/False,
                "message": "Status message",
                "verification_link": "https://..." (only if success)
            }
        """
        # Rate limiting check
        if not self.can_resend_email(email):
            return {
                "success": False,
                "message": f"Please wait {self.min_resend_interval} seconds before requesting another verification email"
            }
        
        # Build verification link
        verification_link = f"{self.base_url}/api/auth/verify-email/{token}"
        
        # Create email content
        subject = "🔐 Verify Your VerzekAutoTrader Account"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #0A4A5C 0%, #1B9AAA 100%);
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #0A4A5C 0%, #1B9AAA 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    color: #F9C74F;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .content h2 {{
                    color: #0A4A5C;
                    margin-top: 0;
                }}
                .verify-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #F9C74F 0%, #F3A712 100%);
                    color: #0A4A5C;
                    padding: 15px 40px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 20px 0;
                    font-size: 16px;
                }}
                .footer {{
                    background: #f5f5f5;
                    padding: 20px 30px;
                    text-align: center;
                    color: #666;
                    font-size: 14px;
                }}
                .warning {{
                    background: #fff3cd;
                    border-left: 4px solid #F9C74F;
                    padding: 15px;
                    margin: 20px 0;
                    color: #856404;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 VerzekAutoTrader</h1>
                </div>
                <div class="content">
                    <h2>Welcome, {username}! 🎉</h2>
                    <p>Thank you for registering with VerzekAutoTrader. To complete your account setup and start auto-trading, please verify your email address.</p>
                    
                    <center>
                        <a href="{verification_link}" class="verify-button">
                            ✅ Verify Email Address
                        </a>
                    </center>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="background: #f5f5f5; padding: 10px; border-radius: 5px; word-break: break-all; font-family: monospace; font-size: 12px;">
                        {verification_link}
                    </p>
                    
                    <div class="warning">
                        <strong>⏱️ This link expires in {self.token_expiration_hours} hours</strong>
                    </div>
                    
                    <p style="margin-top: 30px; color: #666;">
                        If you didn't create a VerzekAutoTrader account, please ignore this email.
                    </p>
                </div>
                <div class="footer">
                    <p>VerzekAutoTrader - Multi-Exchange DCA Trading Platform</p>
                    <p>📧 support@vezekinnovative.com | 💬 @VerzekSupport on Telegram</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send email
        result = self.send_email(email, subject, html_body)
        
        if result['success']:
            # Update rate limiting cache
            self.email_cache[email] = time.time()
            result['verification_link'] = verification_link
        
        return result
    
    def send_welcome_email(self, email: str, username: str) -> Dict[str, any]:
        """Send welcome email after successful verification
        
        Args:
            email: User email address
            username: Username
            
        Returns:
            {"success": True/False, "message": "..."}
        """
        subject = "🎉 Welcome to VerzekAutoTrader!"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #0A4A5C 0%, #1B9AAA 100%);
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #0A4A5C 0%, #1B9AAA 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .footer {{
                    background: #f5f5f5;
                    padding: 20px 30px;
                    text-align: center;
                    color: #666;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="color: #F9C74F;">🎉 Account Verified!</h1>
                </div>
                <div class="content">
                    <h2 style="color: #0A4A5C;">Welcome to VerzekAutoTrader, {username}!</h2>
                    <p>Your email has been successfully verified. You can now:</p>
                    <ul>
                        <li>✅ Connect exchange API keys (Binance, Bybit, Phemex, Kraken)</li>
                        <li>✅ Enable auto-trading on Telegram signals</li>
                        <li>✅ Configure DCA strategies</li>
                        <li>✅ Access VIP/TRIAL Telegram groups</li>
                        <li>✅ Upgrade to Pro/VIP subscription</li>
                    </ul>
                    <p>Get started by connecting your first exchange account in the mobile app!</p>
                </div>
                <div class="footer">
                    <p>VerzekAutoTrader - Multi-Exchange DCA Trading Platform</p>
                    <p>📧 support@vezekinnovative.com | 💬 @VerzekSupport on Telegram</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(email, subject, html_body)
    
    def send_password_reset_email(self, email: str, username: str, reset_token: str) -> Dict[str, any]:
        """Send password reset email
        
        Args:
            email: User email address
            username: Username
            reset_token: Password reset token
            
        Returns:
            {"success": True/False, "message": "..."}
        """
        reset_link = f"{self.base_url}/api/auth/reset-password/{reset_token}"
        
        subject = "🔑 Reset Your VerzekAutoTrader Password"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #0A4A5C 0%, #1B9AAA 100%);
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #0A4A5C 0%, #1B9AAA 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .reset-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #F9C74F 0%, #F3A712 100%);
                    color: #0A4A5C;
                    padding: 15px 40px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    margin: 20px 0;
                    font-size: 16px;
                }}
                .footer {{
                    background: #f5f5f5;
                    padding: 20px 30px;
                    text-align: center;
                    color: #666;
                    font-size: 14px;
                }}
                .warning {{
                    background: #fff3cd;
                    border-left: 4px solid #F9C74F;
                    padding: 15px;
                    margin: 20px 0;
                    color: #856404;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="color: #F9C74F;">🔑 Password Reset</h1>
                </div>
                <div class="content">
                    <h2 style="color: #0A4A5C;">Hello, {username}</h2>
                    <p>We received a request to reset your VerzekAutoTrader password. Click the button below to create a new password:</p>
                    
                    <center>
                        <a href="{reset_link}" class="reset-button">
                            🔑 Reset Password
                        </a>
                    </center>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="background: #f5f5f5; padding: 10px; border-radius: 5px; word-break: break-all; font-family: monospace; font-size: 12px;">
                        {reset_link}
                    </p>
                    
                    <div class="warning">
                        <strong>⏱️ This link expires in 1 hour</strong>
                    </div>
                    
                    <p style="margin-top: 30px; color: #666;">
                        If you didn't request a password reset, please ignore this email and your password will remain unchanged.
                    </p>
                </div>
                <div class="footer">
                    <p>VerzekAutoTrader - Multi-Exchange DCA Trading Platform</p>
                    <p>📧 support@vezekinnovative.com | 💬 @VerzekSupport on Telegram</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(email, subject, html_body)
    
    def send_support_notification(self, from_user: str, message: str, telegram_username: str = None) -> Dict[str, any]:
        """Send support notification email (from Telegram bot)
        
        Args:
            from_user: Telegram user identifier
            message: Support message content
            telegram_username: Telegram username (optional)
            
        Returns:
            {"success": True/False, "message": "..."}
        """
        subject = f"🆘 New Support Message from {from_user}"
        
        username_display = f"@{telegram_username}" if telegram_username else "No username"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #0A4A5C 0%, #1B9AAA 100%);
                    color: white;
                    padding: 20px 30px;
                }}
                .content {{
                    padding: 30px;
                }}
                .message-box {{
                    background: #f9f9f9;
                    border-left: 4px solid #1B9AAA;
                    padding: 15px;
                    margin: 20px 0;
                    font-family: monospace;
                    white-space: pre-wrap;
                }}
                .footer {{
                    background: #f5f5f5;
                    padding: 15px 30px;
                    text-align: center;
                    color: #666;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="margin: 0; color: #F9C74F;">🆘 Support Message Received</h2>
                </div>
                <div class="content">
                    <p><strong>From:</strong> {from_user}</p>
                    <p><strong>Telegram Username:</strong> {username_display}</p>
                    <p><strong>Time:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                    
                    <h3>Message:</h3>
                    <div class="message-box">{message}</div>
                    
                    <p style="color: #666; font-size: 14px; margin-top: 30px;">
                        Reply to this customer via Telegram: {username_display if telegram_username else 'No username available'}
                    </p>
                </div>
                <div class="footer">
                    <p>VerzekAutoTrader Support System</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send to support email
        return self.send_email(self.from_email, subject, html_body)


# Global instance
email_service = EmailService()
