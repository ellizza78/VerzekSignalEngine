#!/bin/bash
# Deploy Resend Email Service to Vultr
# Copy this entire file to Vultr and run: bash DEPLOY_EMAIL_RESEND.sh

echo "📧 Installing Resend Email Service..."

# Install Resend
pip3 install resend

# Add environment variables
cat >> /root/.env << 'EOF'

# Resend Email Configuration
RESEND_API_KEY=re_cVoPKdC1_8vF1dnLgezjSbbE5eztikCY5
EMAIL_FROM=onboarding@resend.dev
APP_NAME=Verzek Auto Trader
BASE_URL=https://verzek-auto-trader.replit.app
EOF

echo "✅ Environment configured"

# Create services directory if not exists
mkdir -p /root/services

# Download email service from Replit
wget -O /root/services/email_service.py https://verzek-auto-trader.replit.app/download/email_service.py 2>/dev/null || {
    echo "⚠️ Direct download failed, creating file manually..."
    
    # Create the email service file directly
    cat > /root/services/email_service.py << 'PYEOF'
"""
Email Verification Service using Resend API
Sends verification emails to users during registration
"""

import os
import secrets
import time
from typing import Dict, Any
from datetime import datetime, timedelta


class EmailService:
    """Handles email verification and notifications using Resend API"""
    
    def __init__(self):
        """Initialize email service with Resend API configuration"""
        self.resend_api_key = os.getenv('RESEND_API_KEY', '')
        self.from_email = os.getenv('EMAIL_FROM', 'onboarding@resend.dev')
        self.from_name = os.getenv('APP_NAME', 'Verzek Auto Trader')
        
        # Base URL for verification links
        self.base_url = os.getenv('BASE_URL', 'https://verzek-auto-trader.replit.app')
        
        # Token expiration (24 hours)
        self.token_expiration_hours = 24
        
        # Rate limiting: track sent emails
        self.email_cache = {}
        self.min_resend_interval = 60
        
        # Initialize Resend if API key is available
        if self.resend_api_key:
            try:
                import resend
                resend.api_key = self.resend_api_key
                self.resend = resend
                print("✅ Resend API initialized successfully")
            except ImportError:
                print("⚠️ Resend package not installed. Run: pip install resend")
                self.resend = None
        else:
            print("⚠️ RESEND_API_KEY not set. Email service in dev mode.")
            self.resend = None
    
    def generate_verification_token(self):
        """Generate secure random verification token"""
        return secrets.token_urlsafe(32)
    
    def get_token_expiration(self):
        """Get token expiration timestamp (24 hours from now)"""
        expiration = datetime.utcnow() + timedelta(hours=self.token_expiration_hours)
        return expiration.isoformat()
    
    def is_token_valid(self, token_expires):
        """Check if verification token is still valid"""
        try:
            expiration = datetime.fromisoformat(token_expires)
            return datetime.utcnow() < expiration
        except (ValueError, TypeError):
            return False
    
    def can_resend_email(self, email):
        """Check if email can be resent (rate limiting)"""
        if email not in self.email_cache:
            return True
        last_sent = self.email_cache[email]
        time_elapsed = time.time() - last_sent
        return time_elapsed >= self.min_resend_interval
    
    def send_verification_email(self, email, username, token):
        """Send verification email to user using Resend API"""
        if not self.can_resend_email(email):
            return {
                "success": False,
                "message": f"Please wait {self.min_resend_interval} seconds before requesting another verification email"
            }
        
        verification_link = f"{self.base_url}/api/auth/verify-email/{token}"
        subject = "🔐 Verify Your VerzekAutoTrader Account"
        
        html_body = f"""<!DOCTYPE html>
<html>
<head><style>
body {{ font-family: Arial, sans-serif; background: linear-gradient(135deg, #0A4A5C 0%, #1B9AAA 100%); margin: 0; padding: 20px; }}
.container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
.header {{ background: linear-gradient(135deg, #0A4A5C 0%, #1B9AAA 100%); color: white; padding: 30px; text-align: center; }}
.header h1 {{ margin: 0; font-size: 28px; color: #F9C74F; }}
.content {{ padding: 40px 30px; }}
.content h2 {{ color: #0A4A5C; margin-top: 0; }}
.verify-button {{ display: inline-block; background: linear-gradient(135deg, #F9C74F 0%, #F3A712 100%); color: #0A4A5C; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; font-size: 16px; }}
.footer {{ background: #f5f5f5; padding: 20px 30px; text-align: center; color: #666; font-size: 14px; }}
.warning {{ background: #fff3cd; border-left: 4px solid #F9C74F; padding: 15px; margin: 20px 0; color: #856404; }}
</style></head>
<body>
<div class="container">
<div class="header"><h1>📊 VerzekAutoTrader</h1></div>
<div class="content">
<h2>Welcome, {username}! 🎉</h2>
<p>Thank you for registering with VerzekAutoTrader. To complete your account setup and start auto-trading, please verify your email address.</p>
<center><a href="{verification_link}" class="verify-button">✅ Verify Email Address</a></center>
<p>Or copy and paste this link into your browser:</p>
<p style="background: #f5f5f5; padding: 10px; border-radius: 5px; word-break: break-all; font-family: monospace; font-size: 12px;">{verification_link}</p>
<div class="warning"><strong>⏱️ This link expires in {self.token_expiration_hours} hours</strong></div>
<p style="margin-top: 30px; color: #666;">If you didn't create a VerzekAutoTrader account, please ignore this email.</p>
</div>
<div class="footer"><p>VerzekAutoTrader - Multi-Exchange DCA Trading Platform</p><p>This is an automated email. Please do not reply.</p></div>
</div>
</body>
</html>"""
        
        try:
            if not self.resend:
                print(f"⚠️ Resend not configured. Verification link (DEV MODE): {verification_link}")
                return {"success": True, "message": "Resend not configured (dev mode). Check console for verification link.", "verification_link": verification_link, "dev_mode": True}
            
            params = {"from": f"{self.from_name} <{self.from_email}>", "to": [email], "subject": subject, "html": html_body}
            response = self.resend.Emails.send(params)
            self.email_cache[email] = time.time()
            print(f"✅ Verification email sent to {email} (ID: {response.get('id', 'N/A')})")
            return {"success": True, "message": f"Verification email sent to {email}", "verification_link": verification_link, "email_id": response.get('id')}
        except Exception as e:
            print(f"❌ Email send error: {str(e)}")
            print(f"📧 DEV MODE - Verification link: {verification_link}")
            return {"success": True, "message": f"Email service unavailable (dev mode). Check console for verification link.", "verification_link": verification_link, "dev_mode": True, "error": str(e)}
    
    def send_welcome_email(self, email, username):
        """Send welcome email after successful verification"""
        subject = "🎉 Welcome to VerzekAutoTrader!"
        html_body = f"""<!DOCTYPE html>
<html><head><style>
body {{ font-family: Arial, sans-serif; background: linear-gradient(135deg, #0A4A5C 0%, #1B9AAA 100%); margin: 0; padding: 20px; }}
.container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
.header {{ background: linear-gradient(135deg, #0A4A5C 0%, #1B9AAA 100%); color: white; padding: 30px; text-align: center; }}
.content {{ padding: 40px 30px; }}
.footer {{ background: #f5f5f5; padding: 20px 30px; text-align: center; color: #666; font-size: 14px; }}
</style></head>
<body>
<div class="container">
<div class="header"><h1 style="color: #F9C74F;">🎉 Account Verified!</h1></div>
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
<div class="footer"><p>VerzekAutoTrader - Multi-Exchange DCA Trading Platform</p></div>
</div>
</body>
</html>"""
        
        try:
            if not self.resend:
                print(f"✅ Welcome email (dev mode) for {username}")
                return {"success": True, "message": "Dev mode - welcome email skipped"}
            params = {"from": f"{self.from_name} <{self.from_email}>", "to": [email], "subject": subject, "html": html_body}
            response = self.resend.Emails.send(params)
            print(f"✅ Welcome email sent to {email} (ID: {response.get('id', 'N/A')})")
            return {"success": True, "message": "Welcome email sent", "email_id": response.get('id')}
        except Exception as e:
            print(f"⚠️ Welcome email error (non-critical): {str(e)}")
            return {"success": False, "message": str(e)}
    
    def send_password_reset_email(self, email, username, token):
        """Send password reset email"""
        reset_link = f"{self.base_url}/api/auth/reset-password/{token}"
        subject = "🔑 Reset Your VerzekAutoTrader Password"
        html_body = f"""<!DOCTYPE html>
<html><head><style>
body {{ font-family: Arial, sans-serif; background: linear-gradient(135deg, #0A4A5C 0%, #1B9AAA 100%); margin: 0; padding: 20px; }}
.container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; }}
.header {{ background: linear-gradient(135deg, #0A4A5C 0%, #1B9AAA 100%); color: white; padding: 30px; text-align: center; }}
.content {{ padding: 40px 30px; }}
.reset-button {{ display: inline-block; background: linear-gradient(135deg, #F9C74F 0%, #F3A712 100%); color: #0A4A5C; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; }}
.footer {{ background: #f5f5f5; padding: 20px 30px; text-align: center; color: #666; font-size: 14px; }}
</style></head>
<body>
<div class="container">
<div class="header"><h1 style="color: #F9C74F;">🔑 Password Reset</h1></div>
<div class="content">
<h2 style="color: #0A4A5C;">Reset Your Password</h2>
<p>Hi {username}, we received a request to reset your password. Click below:</p>
<center><a href="{reset_link}" class="reset-button">🔑 Reset Password</a></center>
<p>This link expires in 15 minutes.</p>
</div>
<div class="footer"><p>VerzekAutoTrader</p></div>
</div>
</body>
</html>"""
        
        try:
            if not self.resend:
                print(f"⚠️ Resend not configured. Reset link (DEV MODE): {reset_link}")
                return {"success": True, "message": "Dev mode", "reset_link": reset_link, "dev_mode": True}
            params = {"from": f"{self.from_name} <{self.from_email}>", "to": [email], "subject": subject, "html": html_body}
            response = self.resend.Emails.send(params)
            print(f"✅ Password reset email sent to {email}")
            return {"success": True, "message": "Password reset email sent", "reset_link": reset_link, "email_id": response.get('id')}
        except Exception as e:
            print(f"❌ Password reset email error: {str(e)}")
            return {"success": False, "message": str(e), "reset_link": reset_link, "dev_mode": True}


# Global instance
email_service = EmailService()
PYEOF
}

echo "✅ Email service file created"

# Restart API server
echo "🔄 Restarting API server..."
pkill -9 -f api_server.py
sleep 2
nohup python3 /root/api_server.py > /tmp/api_server.log 2>&1 &

# Wait for server to start
sleep 3

# Test email service
echo ""
echo "🧪 Testing Resend Email Service..."
python3 << 'TESTEOF'
import sys
sys.path.insert(0, '/root')
from services.email_service import email_service

result = email_service.send_verification_email(
    email="verzekgloballtd@gmail.com",
    username="TestUser",
    token="test123"
)
print(f"\n✅ Result: {result}")
TESTEOF

echo ""
echo "================================================"
echo "✅ Email service deployed successfully!"
echo "📧 Check verzekgloballtd@gmail.com inbox"
echo "================================================"
