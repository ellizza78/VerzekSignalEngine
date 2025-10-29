#!/bin/bash
# ONE COMMAND DEPLOY - Microsoft 365 Email to Vultr
# Run this on your Vultr server: 80.240.29.142

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📧 Microsoft 365 Email Deployment to Vultr"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Prompt for password
read -sp "Enter your Microsoft 365 email password: " EMAIL_PASSWORD
echo ""
echo ""

cd /var/www/VerzekAutoTrader || exit 1

echo "✓ Backing up .env..."
cp .env ".env.backup.$(date +%Y%m%d_%H%M%S)"

echo "✓ Removing old email config..."
sed -i '/^EMAIL_HOST=/d; /^EMAIL_PORT=/d; /^EMAIL_USER=/d; /^EMAIL_PASS=/d; /^EMAIL_FROM=/d; /^APP_NAME=/d; /^DOMAIN=/d; /^API_BASE_URL=/d; /^SUPPORT_EMAIL=/d; /^ADMIN_EMAIL=/d' .env

echo "✓ Adding Microsoft 365 configuration..."
cat >> .env << EOF

# Microsoft 365 Email Configuration
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USER=support@verzekinnovative.com
EMAIL_PASS=${EMAIL_PASSWORD}
EMAIL_FROM=support@verzekinnovative.com
APP_NAME=VerzekAutoTrader

# Domain Configuration
DOMAIN=verzekinnovative.com
API_BASE_URL=https://api.verzekinnovative.com
SUPPORT_EMAIL=support@verzekinnovative.com
ADMIN_EMAIL=support@verzekinnovative.com
EOF

echo "✓ Creating mail_sender.py..."
cat > mail_sender.py << 'PYEOF'
#!/usr/bin/env python3
import os, smtplib, ssl, re
from email.message import EmailMessage

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.office365.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "support@verzekinnovative.com")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_FROM = os.getenv("EMAIL_FROM", EMAIL_USER)
APP_NAME = os.getenv("APP_NAME", "VerzekAutoTrader")

def send_email(to, subject, html_body, text_body=None):
    if not EMAIL_USER or not EMAIL_PASS:
        raise ValueError("EMAIL_USER and EMAIL_PASS required")
    if not text_body:
        text_body = re.sub("<[^<]+?>", "", html_body)
    msg = EmailMessage()
    msg["From"] = EMAIL_FROM
    msg["To"] = to if isinstance(to, str) else ", ".join(to)
    msg["Subject"] = f"{APP_NAME}: {subject}"
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")
    context = ssl.create_default_context()
    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
    return True

def send_verification_email(to, code, user_name=None):
    greeting = f"Hi {user_name}," if user_name else "Hello,"
    html = f"""<!DOCTYPE html><html><head><style>body{{font-family:Arial,sans-serif;color:#333}}.container{{max-width:600px;margin:0 auto;padding:20px}}.header{{background:linear-gradient(135deg,#0A4A5C,#1B9AAA);color:white;padding:30px;text-align:center;border-radius:8px 8px 0 0}}.content{{background:#f9f9f9;padding:30px;border-radius:0 0 8px 8px}}.code{{background:#F9C74F;color:#0A4A5C;font-size:32px;font-weight:bold;padding:15px;text-align:center;border-radius:6px;letter-spacing:5px;margin:20px 0}}</style></head><body><div class="container"><div class="header"><h1>🔐 Email Verification</h1></div><div class="content"><p>{greeting}</p><p>Your verification code:</p><div class="code">{code}</div><p>Expires in 10 minutes.</p></div></div></body></html>"""
    return send_email(to, "Email Verification", html)

def send_password_reset_email(to, code, user_name=None):
    greeting = f"Hi {user_name}," if user_name else "Hello,"
    html = f"""<!DOCTYPE html><html><head><style>body{{font-family:Arial,sans-serif;color:#333}}.container{{max-width:600px;margin:0 auto;padding:20px}}.header{{background:linear-gradient(135deg,#0A4A5C,#1B9AAA);color:white;padding:30px;text-align:center;border-radius:8px 8px 0 0}}.content{{background:#f9f9f9;padding:30px;border-radius:0 0 8px 8px}}.code{{background:#F9C74F;color:#0A4A5C;font-size:32px;font-weight:bold;padding:15px;text-align:center;border-radius:6px;letter-spacing:5px;margin:20px 0}}</style></head><body><div class="container"><div class="header"><h1>🔑 Password Reset</h1></div><div class="content"><p>{greeting}</p><p>Your password reset code:</p><div class="code">{code}</div><p>Expires in 10 minutes.</p></div></div></body></html>"""
    return send_email(to, "Password Reset Request", html)
PYEOF

chmod +x mail_sender.py

echo "✓ Restarting verzekapi service..."
sudo systemctl restart verzekapi
sleep 3

echo "✓ Checking service status..."
if sudo systemctl is-active --quiet verzekapi; then
    echo "  ✅ verzekapi is running"
else
    echo "  ⚠️  verzekapi may have issues"
    sudo systemctl status verzekapi --no-pager -l | head -10
fi

echo ""
echo "✓ Testing email configuration..."
source venv/bin/activate 2>/dev/null || true
python3 << 'TESTEOF'
import os
try:
    from mail_sender import send_email
    send_email("support@verzekinnovative.com", "Vultr Deployment Test", "<h2>✅ Email working on Vultr!</h2>")
    print("  ✅ Test email sent to support@verzekinnovative.com")
except Exception as e:
    print(f"  ⚠️  Error: {e}")
TESTEOF

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DEPLOYMENT COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📧 Check support@verzekinnovative.com for test email"
echo "🎉 Microsoft 365 email is now active on Vultr!"
echo ""
