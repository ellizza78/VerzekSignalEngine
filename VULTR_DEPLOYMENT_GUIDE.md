# 🚀 Deploy Microsoft 365 Email to Vultr Backend - Step by Step

## ✅ Status: Replit Email Working - Ready to Deploy!

---

## 📋 What You Need

- SSH access to your Vultr server: **80.240.29.142**
- The deployment script: **DEPLOY_EMAIL_TO_VULTR.sh**
- Your Microsoft 365 email password

---

## 🔧 Step 1: SSH into Your Vultr Server

```bash
ssh root@80.240.29.142
```

*(Or use your usual method to connect to Vultr)*

---

## 🔧 Step 2: Navigate to Project Directory

```bash
cd /var/www/VerzekAutoTrader
```

---

## 🔧 Step 3: Create the Deployment Script

Copy and paste this entire script:

```bash
cat > DEPLOY_EMAIL_TO_VULTR.sh << 'EOF'
#!/bin/bash
# DEPLOY_EMAIL_TO_VULTR.sh - Deploy Microsoft 365 email configuration to Vultr backend

echo "📧 Deploying Microsoft 365 Email to Vultr Backend"
echo "=================================================="
echo ""

cd /var/www/VerzekAutoTrader

echo "1️⃣ Backing up current .env..."
cp .env .env.backup.email.$(date +%Y%m%d_%H%M%S)

echo "2️⃣ Adding Microsoft 365 email configuration to .env..."

# Check if email config already exists
if grep -q "EMAIL_HOST" .env; then
    echo "   Email config already exists, updating..."
    sed -i '/^EMAIL_HOST=/d' .env
    sed -i '/^EMAIL_PORT=/d' .env
    sed -i '/^EMAIL_USER=/d' .env
    sed -i '/^EMAIL_PASS=/d' .env
    sed -i '/^EMAIL_FROM=/d' .env
    sed -i '/^APP_NAME=/d' .env
    sed -i '/^DOMAIN=/d' .env
    sed -i '/^API_BASE_URL=/d' .env
    sed -i '/^SUPPORT_EMAIL=/d' .env
    sed -i '/^ADMIN_EMAIL=/d' .env
fi

cat >> .env << 'ENVEOF'

# Microsoft 365 Email Configuration
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USER=support@verzekinnovative.com
EMAIL_PASS=YOUR_PASSWORD_HERE
EMAIL_FROM=support@verzekinnovative.com
APP_NAME=VerzekAutoTrader

# Domain Configuration
DOMAIN=verzekinnovative.com
API_BASE_URL=https://api.verzekinnovative.com
SUPPORT_EMAIL=support@verzekinnovative.com
ADMIN_EMAIL=support@verzekinnovative.com
ENVEOF

echo ""
echo "⚠️  IMPORTANT: Edit .env and replace YOUR_PASSWORD_HERE with actual password"
echo ""
read -p "Press ENTER after you've updated EMAIL_PASS in .env (use: nano .env)..."

echo ""
echo "3️⃣ Creating mail_sender.py utility..."
cat > mail_sender.py << 'PYEOF'
#!/usr/bin/env python3
"""
Microsoft 365 Email Sender - Drop-in Utility
"""
import os
import smtplib
import ssl
import re
from email.message import EmailMessage

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.office365.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER", "support@verzekinnovative.com")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_FROM = os.getenv("EMAIL_FROM", EMAIL_USER)
APP_NAME = os.getenv("APP_NAME", "VerzekAutoTrader")

def send_email(to, subject, html_body, text_body=None):
    if not EMAIL_USER or not EMAIL_PASS:
        raise ValueError("EMAIL_USER and EMAIL_PASS environment variables are required")
    
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
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #0A4A5C, #1B9AAA); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
            .code {{ background: #F9C74F; color: #0A4A5C; font-size: 32px; font-weight: bold; padding: 15px; text-align: center; border-radius: 6px; letter-spacing: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Email Verification</h1>
            </div>
            <div class="content">
                <p>{greeting}</p>
                <p>Thank you for signing up with <strong>Verzek Auto Trader</strong>!</p>
                <p>Your verification code is:</p>
                <div class="code">{code}</div>
                <p>This code will expire in <strong>10 minutes</strong>.</p>
            </div>
            <div class="footer">
                <p>© 2025 Verzek Innovative. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(to, "Email Verification", html)

def send_password_reset_email(to, code, user_name=None):
    greeting = f"Hi {user_name}," if user_name else "Hello,"
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #0A4A5C, #1B9AAA); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 8px 8px; }}
            .code {{ background: #F9C74F; color: #0A4A5C; font-size: 32px; font-weight: bold; padding: 15px; text-align: center; border-radius: 6px; letter-spacing: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔑 Password Reset</h1>
            </div>
            <div class="content">
                <p>{greeting}</p>
                <p>Your password reset code is:</p>
                <div class="code">{code}</div>
                <p>This code will expire in <strong>10 minutes</strong>.</p>
            </div>
            <div class="footer">
                <p>© 2025 Verzek Innovative. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(to, "Password Reset Request", html)
PYEOF

chmod +x mail_sender.py
echo "✅ mail_sender.py created"

echo ""
echo "4️⃣ Restarting verzekapi service..."
sudo systemctl restart verzekapi

echo ""
echo "5️⃣ Waiting for service to start..."
sleep 3

echo ""
echo "6️⃣ Checking service status..."
sudo systemctl status verzekapi --no-pager | head -15

echo ""
echo "7️⃣ Testing email configuration..."
python3 -c "import os; print(f'EMAIL_USER: {os.getenv(\"EMAIL_USER\")}'); print(f'EMAIL_HOST: {os.getenv(\"EMAIL_HOST\")}'); print(f'EMAIL_PASS: {\"SET\" if os.getenv(\"EMAIL_PASS\") else \"NOT SET\"}')"

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo ""
echo "🧪 To test email, run:"
echo "   python3 -c 'from mail_sender import send_email; send_email(\"support@verzekinnovative.com\", \"Test\", \"<h3>Test from Vultr!</h3>\")'"
EOF

chmod +x DEPLOY_EMAIL_TO_VULTR.sh
echo "✅ Deployment script created!"
```

---

## 🔧 Step 4: Run the Deployment Script

```bash
./DEPLOY_EMAIL_TO_VULTR.sh
```

---

## 🔧 Step 5: Edit the .env File

When prompted, edit the .env file to add your actual password:

```bash
nano .env
```

Find this line:
```
EMAIL_PASS=YOUR_PASSWORD_HERE
```

Replace with your actual Microsoft 365 password, then:
- Press `Ctrl + X`
- Press `Y` to confirm
- Press `Enter` to save

---

## 🔧 Step 6: Continue the Script

Press `ENTER` to continue the deployment script.

It will:
- ✅ Create mail_sender.py
- ✅ Restart verzekapi service
- ✅ Test the configuration

---

## 🧪 Step 7: Test Email from Vultr

```bash
python3 << 'EOF'
from mail_sender import send_email
result = send_email(
    "support@verzekinnovative.com",
    "Test from Vultr",
    "<h3>✅ Microsoft 365 email working on Vultr!</h3>"
)
print("✅ Email sent successfully!" if result else "❌ Failed")
EOF
```

---

## ✅ Expected Results

You should see:
```
✅ DEPLOYMENT COMPLETE!
✅ Email sent successfully!
```

And receive an email at support@verzekinnovative.com

---

## 🎊 After Successful Deployment

Your Vultr backend will now have:
- ✅ Microsoft 365 email integration
- ✅ Professional email templates
- ✅ Email verification system
- ✅ Password reset functionality
- ✅ All email features operational

---

## 📞 Troubleshooting

### Issue: Service won't restart
```bash
sudo systemctl status verzekapi
sudo journalctl -u verzekapi -n 50
```

### Issue: Email not sending
```bash
# Check environment variables
cat .env | grep EMAIL
```

### Issue: Permission denied
```bash
sudo chown -R www-data:www-data /var/www/VerzekAutoTrader
```

---

**You're all set!** Just SSH into Vultr and follow these steps! 🚀
