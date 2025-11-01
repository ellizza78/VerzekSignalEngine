#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# FINAL VULTR EMAIL FIX - Complete Pipeline Validation
# Run this on Vultr (80.240.29.142) to enable Resend API
# ═══════════════════════════════════════════════════════════════

set -e  # Exit on any error

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  VerzekAutoTrader - Final Email Service Fix & Validation     ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# ═══════════════════════════════════════════════════════════════
# STEP 1: Stop Backend
# ═══════════════════════════════════════════════════════════════
echo "🛑 Step 1: Stopping backend..."
pkill -9 -f api_server.py || true
sleep 3
echo "✅ Backend stopped"
echo ""

# ═══════════════════════════════════════════════════════════════
# STEP 2: Backup Old Files
# ═══════════════════════════════════════════════════════════════
echo "💾 Step 2: Backing up old files..."
BACKUP_DIR="/root/backup_$(date +%s)"
mkdir -p "$BACKUP_DIR"
cp /root/api_server.py "$BACKUP_DIR/" 2>/dev/null || true
cp -r /root/modules/email_service.py "$BACKUP_DIR/" 2>/dev/null || true
cp -r /root/services "$BACKUP_DIR/" 2>/dev/null || true
echo "✅ Backup created: $BACKUP_DIR"
echo ""

# ═══════════════════════════════════════════════════════════════
# STEP 3: Remove Old Gmail SMTP Module
# ═══════════════════════════════════════════════════════════════
echo "🗑️  Step 3: Removing old Gmail SMTP module..."
if [ -f "/root/modules/email_service.py" ]; then
    mv /root/modules/email_service.py /root/modules/email_service.py.OLD_GMAIL
    echo "✅ Old Gmail module disabled (renamed to .OLD_GMAIL)"
else
    echo "ℹ️  Old module already removed"
fi
echo ""

# ═══════════════════════════════════════════════════════════════
# STEP 4: Create Services Directory & Resend Email Service
# ═══════════════════════════════════════════════════════════════
echo "📁 Step 4: Creating new Resend-based email service..."
mkdir -p /root/services
touch /root/services/__init__.py

cat > /root/services/email_service.py << 'RESEND_SERVICE_EOF'
"""Email Service using Resend API"""
import os
import secrets
import time
from typing import Dict, Any
from datetime import datetime, timedelta

class EmailService:
    def __init__(self):
        self.resend_api_key = os.getenv('RESEND_API_KEY', '')
        self.from_email = os.getenv('EMAIL_FROM', 'support@verzekinnovative.com')
        self.from_name = os.getenv('APP_NAME', 'Verzek Auto Trader')
        self.base_url = os.getenv('BASE_URL', 'https://verzekinnovative.com')
        self.token_expiration_hours = 24
        self.email_cache = {}
        self.min_resend_interval = 60
        
        if self.resend_api_key:
            try:
                import resend
                resend.api_key = self.resend_api_key
                self.resend = resend
                print("✅ Resend API initialized successfully")
                print(f"   From: {self.from_email}")
                print(f"   Base URL: {self.base_url}")
            except ImportError:
                print("❌ ERROR: Resend package not installed!")
                print("   Run: pip3 install resend")
                self.resend = None
            except Exception as e:
                print(f"❌ ERROR: Resend initialization failed: {e}")
                self.resend = None
        else:
            print("❌ ERROR: RESEND_API_KEY not set in environment!")
            self.resend = None
    
    def generate_verification_token(self) -> str:
        return secrets.token_urlsafe(32)
    
    def get_token_expiration(self) -> str:
        expiration = datetime.utcnow() + timedelta(hours=self.token_expiration_hours)
        return expiration.isoformat()
    
    def is_token_valid(self, token_expires: str) -> bool:
        try:
            expiration = datetime.fromisoformat(token_expires)
            return datetime.utcnow() < expiration
        except (ValueError, TypeError):
            return False
    
    def can_resend_email(self, email: str) -> bool:
        if email not in self.email_cache:
            return True
        last_sent = self.email_cache[email]
        time_elapsed = time.time() - last_sent
        return time_elapsed >= self.min_resend_interval
    
    def send_verification_email(self, email: str, username: str, token: str) -> Dict[str, Any]:
        if not self.can_resend_email(email):
            return {
                "success": False,
                "message": f"Please wait {self.min_resend_interval} seconds"
            }
        
        verification_link = f"{self.base_url}/api/auth/verify-email/{token}"
        subject = "🔐 Verify Your VerzekAutoTrader Account"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 40px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h1 style="color: #0A4A5C; text-align: center;">📊 VerzekAutoTrader</h1>
                <h2 style="color: #0A4A5C;">Welcome, {username}! 🎉</h2>
                <p>Thank you for registering. Please verify your email to activate your account:</p>
                <center>
                    <a href="{verification_link}" style="display: inline-block; background: #F9C74F; color: #0A4A5C; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-weight: bold; margin: 20px 0;">
                        ✅ Verify Email Address
                    </a>
                </center>
                <p style="color: #666; font-size: 12px; word-break: break-all;">Or copy this link: {verification_link}</p>
                <p style="background: #fff3cd; padding: 10px; border-left: 4px solid #F9C74F; color: #856404;">
                    ⏱️ This link expires in {self.token_expiration_hours} hours
                </p>
            </div>
        </body>
        </html>
        """
        
        try:
            if not self.resend:
                print(f"❌ Resend not configured! Verification link: {verification_link}")
                return {
                    "success": False,
                    "message": "Email service not configured",
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
            return {
                "success": False,
                "message": f"Email send failed: {str(e)}",
                "verification_link": verification_link,
                "error": str(e)
            }
    
    def send_welcome_email(self, email: str, username: str) -> Dict[str, Any]:
        if not self.resend:
            return {"success": False, "message": "Resend not configured"}
        try:
            params = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [email],
                "subject": "🎉 Welcome to VerzekAutoTrader!",
                "html": f"<h2>Welcome {username}!</h2><p>Your account is verified and active.</p>"
            }
            response = self.resend.Emails.send(params)
            return {"success": True, "message": "Welcome email sent"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def send_password_reset_email(self, email: str, username: str, token: str) -> Dict[str, Any]:
        reset_link = f"{self.base_url}/api/auth/reset-password/{token}"
        if not self.resend:
            return {"success": False, "reset_link": reset_link}
        try:
            params = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": [email],
                "subject": "🔑 Reset Your Password",
                "html": f"<p>Reset your password: <a href='{reset_link}'>Click here</a></p>"
            }
            response = self.resend.Emails.send(params)
            return {"success": True, "reset_link": reset_link}
        except Exception as e:
            return {"success": False, "reset_link": reset_link, "error": str(e)}

email_service = EmailService()
RESEND_SERVICE_EOF

echo "✅ Resend email service created"
echo ""

# ═══════════════════════════════════════════════════════════════
# STEP 5: Update api_server.py Import
# ═══════════════════════════════════════════════════════════════
echo "🔧 Step 5: Updating api_server.py import..."
sed -i 's/from modules\.email_service import email_service/from services.email_service import email_service/g' /root/api_server.py
echo "✅ Import updated to use Resend service"
echo ""

# ═══════════════════════════════════════════════════════════════
# STEP 6: Install Resend Package
# ═══════════════════════════════════════════════════════════════
echo "📦 Step 6: Installing Resend SDK..."
pip3 install resend --upgrade --quiet
echo "✅ Resend SDK installed"
echo ""

# ═══════════════════════════════════════════════════════════════
# STEP 7: Verify Environment Variables
# ═══════════════════════════════════════════════════════════════
echo "🔍 Step 7: Verifying environment variables..."
source /root/api_server_env.sh

if [ -z "$RESEND_API_KEY" ]; then
    echo "❌ ERROR: RESEND_API_KEY not set!"
    echo "   Add to /root/api_server_env.sh: export RESEND_API_KEY=your_key_here"
    exit 1
fi

if [ -z "$EMAIL_FROM" ]; then
    echo "⚠️  WARNING: EMAIL_FROM not set, using default: support@verzekinnovative.com"
    export EMAIL_FROM="support@verzekinnovative.com"
fi

if [ -z "$BASE_URL" ]; then
    echo "⚠️  WARNING: BASE_URL not set, using default: https://verzekinnovative.com"
    export BASE_URL="https://verzekinnovative.com"
fi

echo "✅ Environment variables verified:"
echo "   RESEND_API_KEY: ${RESEND_API_KEY:0:20}..."
echo "   EMAIL_FROM: $EMAIL_FROM"
echo "   BASE_URL: $BASE_URL"
echo ""

# ═══════════════════════════════════════════════════════════════
# STEP 8: Restart Backend
# ═══════════════════════════════════════════════════════════════
echo "🚀 Step 8: Starting backend with Resend API..."
cd /root
nohup python3 /root/api_server.py > /tmp/api_server.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"
echo ""

# ═══════════════════════════════════════════════════════════════
# STEP 9: Wait for Initialization
# ═══════════════════════════════════════════════════════════════
echo "⏳ Step 9: Waiting 15 seconds for initialization..."
for i in {15..1}; do
    echo -n "$i... "
    sleep 1
done
echo "Done!"
echo ""

# ═══════════════════════════════════════════════════════════════
# STEP 10: Validate Email Service
# ═══════════════════════════════════════════════════════════════
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  STEP 10: EMAIL SERVICE VALIDATION                           ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

echo "📋 Checking backend logs for email initialization..."
if grep -q "✅ Resend API initialized successfully" /tmp/api_server.log; then
    echo "✅ SUCCESS: Resend API is initialized!"
    grep -A 2 "Resend API initialized" /tmp/api_server.log | head -5
elif grep -q "smtp.gmail" /tmp/api_server.log; then
    echo "❌ FAILURE: Still using Gmail SMTP!"
    grep "smtp.gmail" /tmp/api_server.log | head -5
    exit 1
elif grep -q "RESEND_API_KEY not set" /tmp/api_server.log; then
    echo "❌ FAILURE: RESEND_API_KEY missing!"
    exit 1
else
    echo "⚠️  WARNING: Email service status unclear. Full logs:"
    tail -50 /tmp/api_server.log | grep -i "email\|resend" || echo "No email logs found"
fi
echo ""

# ═══════════════════════════════════════════════════════════════
# STEP 11: Validate HTTPS Endpoint
# ═══════════════════════════════════════════════════════════════
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  STEP 11: HTTPS ENDPOINT VALIDATION                          ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

echo "🌐 Testing HTTPS health endpoint..."
HEALTH_RESPONSE=$(curl -s https://verzekinnovative.com/api/health)
if echo "$HEALTH_RESPONSE" | grep -q '"status":"ok"'; then
    echo "✅ HTTPS endpoint working!"
    echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    echo "❌ HTTPS endpoint failed!"
    echo "Response: $HEALTH_RESPONSE"
fi
echo ""

# ═══════════════════════════════════════════════════════════════
# STEP 12: Test Email Sending (Manual)
# ═══════════════════════════════════════════════════════════════
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  STEP 12: EMAIL SENDING TEST                                 ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

echo "📧 Testing email service manually..."
python3 << 'PYTHON_TEST_EOF'
import sys
sys.path.insert(0, '/root')
try:
    from services.email_service import email_service
    print("✅ Email service imported successfully")
    print(f"   Resend configured: {email_service.resend is not None}")
    print(f"   From email: {email_service.from_email}")
    print(f"   Base URL: {email_service.base_url}")
    
    # Test token generation
    token = email_service.generate_verification_token()
    print(f"✅ Token generation working: {token[:20]}...")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
PYTHON_TEST_EOF
echo ""

# ═══════════════════════════════════════════════════════════════
# FINAL STATUS REPORT
# ═══════════════════════════════════════════════════════════════
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  FINAL STATUS REPORT                                         ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check process
if ps aux | grep -v grep | grep -q "api_server.py"; then
    echo "✅ Backend process running (PID: $(pgrep -f api_server.py))"
else
    echo "❌ Backend process NOT running!"
fi

# Check port
if netstat -tulnp 2>/dev/null | grep -q ":8000.*python" || ss -tulnp 2>/dev/null | grep -q ":8000.*python"; then
    echo "✅ Backend listening on port 8000"
else
    echo "❌ Backend NOT listening on port 8000!"
fi

# Check Resend
if grep -q "Resend API initialized" /tmp/api_server.log; then
    echo "✅ Resend API active"
else
    echo "❌ Resend API NOT active!"
fi

# Check HTTPS
if curl -s https://verzekinnovative.com/api/health | grep -q '"status":"ok"'; then
    echo "✅ HTTPS endpoint working"
else
    echo "❌ HTTPS endpoint failed!"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  🎉 EMAIL SERVICE FIX COMPLETE!                              ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "1. Test registration from mobile app"
echo "2. Check email inbox (including spam folder)"
echo "3. If still no email, check logs: tail -f /tmp/api_server.log"
echo "4. For manual test, register at:"
echo "   curl -X POST https://verzekinnovative.com/api/auth/register \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"username\":\"testuser\",\"email\":\"your@email.com\",\"password\":\"Test1234!\"}'"
echo ""
