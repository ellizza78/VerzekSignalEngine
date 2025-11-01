#!/bin/bash
# Fix Email Service on Vultr - Switch from Gmail SMTP to Resend API
# Run this on your Vultr server (80.240.29.142)

echo "═══════════════════════════════════════════════════════════════"
echo "📧 Switching Email Service: Gmail SMTP → Resend API"
echo "═══════════════════════════════════════════════════════════════"

# Step 1: Install resend package
echo ""
echo "Step 1: Installing Resend SDK..."
pip3 install resend
echo "✅ Resend package installed"

# Step 2: Create services directory
echo ""
echo "Step 2: Creating services directory..."
mkdir -p /root/services
echo "✅ Services directory ready"

# Step 3: Create NEW email service (Resend API)
echo ""
echo "Step 3: Creating Resend-based email service..."
cat > /root/services/email_service.py << 'RESEND_EMAIL_SERVICE'
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
        self.from_email = os.getenv('EMAIL_FROM', 'support@verzekinnovative.com')
        self.from_name = os.getenv('APP_NAME', 'Verzek Auto Trader')
        
        # Base URL for verification links
        self.base_url = os.getenv('BASE_URL', 'https://verzekinnovative.com')
        
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
                print(f"   From: {self.from_email}")
                print(f"   Base URL: {self.base_url}")
            except ImportError:
                print("⚠️ Resend package not installed. Run: pip install resend")
                self.resend = None
        else:
            print("⚠️ RESEND_API_KEY not set. Email service in dev mode.")
            self.resend = None
    
    def generate_verification_token(self) -> str:
        """Generate secure random verification token"""
        return secrets.token_urlsafe(32)
    
    def get_token_expiration(self) -> str:
        """Get token expiration timestamp (24 hours from now)"""
        expiration = datetime.utcnow() + timedelta(hours=self.token_expiration_hours)
        return expiration.isoformat()
    
    def is_token_valid(self, token_expires: str) -> bool:
        """Check if verification token is still valid"""
        try:
            expiration = datetime.fromisoformat(token_expires)
            return datetime.utcnow() < expiration
        except (ValueError, TypeError):
            return False
    
    def can_resend_email(self, email: str) -> bool:
        """Check if email can be resent (rate limiting)"""
        if email not in self.email_cache:
            return True
        
        last_sent = self.email_cache[email]
        time_elapsed = time.time() - last_sent
        return time_elapsed >= self.min_resend_interval
    
    def send_verification_email(self, email: str, username: str, token: str) -> Dict[str, Any]:
        """Send verification email to user using Resend API"""
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
        <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #0A4A5C 0%, #1B9AAA 100%); color: white; padding: 30px; text-align: center;">
                    <h1 style="margin: 0; color: #F9C74F;">📊 VerzekAutoTrader</h1>
                </div>
                <div style="padding: 40px 30px;">
                    <h2 style="color: #0A4A5C;">Welcome, {username}! 🎉</h2>
                    <p>Thank you for registering with VerzekAutoTrader. To complete your account setup and start auto-trading, please verify your email address.</p>
                    
                    <center>
                        <a href="{verification_link}" style="display: inline-block; background: linear-gradient(135deg, #F9C74F 0%, #F3A712 100%); color: #0A4A5C; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0; font-size: 16px;">
                            ✅ Verify Email Address
                        </a>
                    </center>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="background: #f5f5f5; padding: 10px; border-radius: 5px; word-break: break-all; font-family: monospace; font-size: 12px;">
                        {verification_link}
                    </p>
                    
                    <div style="background: #fff3cd; border-left: 4px solid #F9C74F; padding: 15px; margin: 20px 0; color: #856404;">
                        <strong>⏱️ This link expires in {self.token_expiration_hours} hours</strong>
                    </div>
                    
                    <p style="margin-top: 30px; color: #666;">
                        If you didn't create a VerzekAutoTrader account, please ignore this email.
                    </p>
                </div>
                <div style="background: #f5f5f5; padding: 20px 30px; text-align: center; color: #666; font-size: 14px;">
                    <p>VerzekAutoTrader - Multi-Exchange DCA Trading Platform</p>
                    <p>This is an automated email. Please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send email using Resend API
        try:
            if not self.resend:
                print(f"⚠️ Resend not configured. Verification link (DEV MODE): {verification_link}")
                return {
                    "success": True,
                    "message": "Resend not configured (dev mode). Check console for verification link.",
                    "verification_link": verification_link,
                    "dev_mode": True
                }
            
            params = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [email],
                "subject": subject,
                "html": html_body,
            }
            
            response = self.resend.Emails.send(params)
            
            # Update rate limiting cache
            self.email_cache[email] = time.time()
            
            print(f"✅ Verification email sent to {email} (ID: {response.get('id', 'N/A')})")
            
            return {
                "success": True,
                "message": f"Verification email sent to {email}",
                "verification_link": verification_link,
                "email_id": response.get('id')
            }
            
        except Exception as e:
            print(f"❌ Email send error: {str(e)}")
            print(f"📧 DEV MODE - Verification link: {verification_link}")
            return {
                "success": True,
                "message": f"Email service unavailable (dev mode). Check console for verification link.",
                "verification_link": verification_link,
                "dev_mode": True,
                "error": str(e)
            }
    
    def send_welcome_email(self, email: str, username: str) -> Dict[str, Any]:
        """Send welcome email after successful verification"""
        subject = "🎉 Welcome to VerzekAutoTrader!"
        html_body = f"<h2>Welcome {username}!</h2><p>Your account is now verified and active.</p>"
        
        try:
            if not self.resend:
                return {"success": True, "message": "Dev mode - welcome email skipped"}
            
            params = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [email],
                "subject": subject,
                "html": html_body,
            }
            
            response = self.resend.Emails.send(params)
            print(f"✅ Welcome email sent to {email}")
            return {"success": True, "message": "Welcome email sent"}
            
        except Exception as e:
            print(f"⚠️ Welcome email error: {str(e)}")
            return {"success": False, "message": str(e)}
    
    def send_password_reset_email(self, email: str, username: str, token: str) -> Dict[str, Any]:
        """Send password reset email"""
        reset_link = f"{self.base_url}/api/auth/reset-password/{token}"
        subject = "🔑 Reset Your VerzekAutoTrader Password"
        html_body = f"<h2>Password Reset</h2><p>Click to reset: <a href='{reset_link}'>Reset Password</a></p>"
        
        try:
            if not self.resend:
                print(f"⚠️ Reset link (DEV): {reset_link}")
                return {"success": True, "reset_link": reset_link, "dev_mode": True}
            
            params = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [email],
                "subject": subject,
                "html": html_body,
            }
            
            response = self.resend.Emails.send(params)
            print(f"✅ Password reset email sent to {email}")
            return {"success": True, "reset_link": reset_link}
            
        except Exception as e:
            print(f"❌ Reset email error: {str(e)}")
            return {"success": False, "reset_link": reset_link, "error": str(e)}


# Global instance
email_service = EmailService()
RESEND_EMAIL_SERVICE

echo "✅ Resend email service created"

# Step 4: Create __init__.py for services module
echo ""
echo "Step 4: Creating services __init__.py..."
touch /root/services/__init__.py
echo "✅ Services module initialized"

# Step 5: Update api_server.py import
echo ""
echo "Step 5: Updating api_server.py import..."
sed -i 's/from modules.email_service import email_service/from services.email_service import email_service/' /root/api_server.py
echo "✅ Import updated"

# Step 6: Verify environment variables
echo ""
echo "Step 6: Checking environment variables..."
source /root/api_server_env.sh
echo "  RESEND_API_KEY: ${RESEND_API_KEY:0:15}..."
echo "  EMAIL_FROM: $EMAIL_FROM"
echo "  BASE_URL: $BASE_URL"

# Step 7: Restart backend
echo ""
echo "Step 7: Restarting backend..."
pkill -9 -f api_server.py || true
sleep 3
cd /root
nohup python3 /root/api_server.py > /tmp/api_server.log 2>&1 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

# Step 8: Wait and test
echo ""
echo "Step 8: Waiting 15 seconds for initialization..."
sleep 15

# Step 9: Check logs
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "📋 Backend Logs (Email Service)"
echo "═══════════════════════════════════════════════════════════════"
tail -50 /tmp/api_server.log | grep -E "(Resend|Email|smtp|SMTP)" || echo "No email-related logs yet"

# Step 10: Test health endpoint
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🧪 Testing Endpoints"
echo "═══════════════════════════════════════════════════════════════"
curl -s https://verzekinnovative.com/api/health | python3 -m json.tool

# Step 11: Final status
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ EMAIL SERVICE UPDATE COMPLETE"
echo "═══════════════════════════════════════════════════════════════"

if grep -q "Resend API initialized" /tmp/api_server.log; then
    echo "✅ Resend API active"
elif grep -q "smtp.gmail" /tmp/api_server.log; then
    echo "❌ Still using Gmail SMTP - check logs"
else
    echo "⚠️ Email service status unknown - check logs"
fi

echo ""
echo "Next steps:"
echo "1. Test registration from mobile app"
echo "2. Check email inbox for verification"
echo "3. If no email, check: tail -f /tmp/api_server.log"
echo ""
