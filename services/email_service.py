"""
Email Verification Service
Sends verification emails to users during registration
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
    """Handles email verification and notifications"""
    
    def __init__(self):
        """Initialize email service with SMTP configuration"""
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@verzektrader.com')
        self.from_name = os.getenv('FROM_NAME', 'VerzekAutoTrader')
        
        # Base URL for verification links
        self.base_url = os.getenv('BASE_URL', 'https://verzek-auto-trader.replit.app')
        
        # Token expiration (24 hours)
        self.token_expiration_hours = 24
        
        # Rate limiting: track sent emails
        self.email_cache = {}  # {email: last_sent_timestamp}
        self.min_resend_interval = 60  # 60 seconds between resend
    
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
                    <p>This is an automated email. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        plain_body = f"""
        Welcome to VerzekAutoTrader, {username}!
        
        Please verify your email address by clicking this link:
        {verification_link}
        
        This link expires in {self.token_expiration_hours} hours.
        
        If you didn't create a VerzekAutoTrader account, please ignore this email.
        
        ---
        VerzekAutoTrader - Multi-Exchange DCA Trading Platform
        """
        
        # Send email
        try:
            # Check if SMTP is configured
            if not self.smtp_username or not self.smtp_password:
                print(f"⚠️ SMTP not configured. Verification link (DEV MODE): {verification_link}")
                return {
                    "success": True,
                    "message": "SMTP not configured (dev mode). Check console for verification link.",
                    "verification_link": verification_link,
                    "dev_mode": True
                }
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = email
            
            # Attach both plain and HTML versions
            msg.attach(MIMEText(plain_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Connect and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            # Update rate limiting cache
            self.email_cache[email] = time.time()
            
            return {
                "success": True,
                "message": f"Verification email sent to {email}",
                "verification_link": verification_link
            }
            
        except Exception as e:
            print(f"❌ Email send error: {str(e)}")
            # In dev mode, still return success with link in console
            print(f"📧 DEV MODE - Verification link: {verification_link}")
            return {
                "success": True,
                "message": f"Email service unavailable (dev mode). Check console for verification link.",
                "verification_link": verification_link,
                "dev_mode": True,
                "error": str(e)
            }
    
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
                </div>
            </div>
        </body>
        </html>
        """
        
        try:
            if not self.smtp_username or not self.smtp_password:
                print(f"✅ Welcome email (dev mode) for {username}")
                return {"success": True, "message": "Dev mode - welcome email skipped"}
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = email
            msg.attach(MIMEText(html_body, 'html'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return {"success": True, "message": "Welcome email sent"}
            
        except Exception as e:
            print(f"⚠️ Welcome email error (non-critical): {str(e)}")
            return {"success": False, "message": str(e)}


# Global instance
email_service = EmailService()
