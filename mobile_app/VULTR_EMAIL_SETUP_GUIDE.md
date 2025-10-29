# 🔧 Vultr Email Service Setup Guide
**VerzekAutoTrader - Microsoft 365 SMTP Configuration**

---

## ⚠️ CRITICAL: Vultr SMTP Port Blocking

**IMPORTANT DISCOVERY:** Vultr **blocks SMTP ports (25, 465, 587) by default** to prevent spam!

### Check if Your Ports Are Blocked

SSH into your Vultr server and test:

```bash
ssh root@80.240.29.142

# Test SMTP port 587 connectivity
telnet smtp.office365.com 587
# Or use nc (netcat)
nc -zv smtp.office365.com 587
```

**If you see "Connection refused" or timeout:**
- ✅ Your ports ARE blocked (most likely)
- ⚠️ You MUST request port access from Vultr

**If you see "Connected":**
- ✅ Ports are open, proceed to configuration!

---

## 🎫 Step 1: Request SMTP Port Access from Vultr

**Requirements:**
- Account must be active for at least 1 month
- Manual review by Vultr staff

**How to Request:**

1. **Login to Vultr Portal:** https://my.vultr.com/
2. **Open Support Ticket:**
   - Click "Support" → "Open Ticket"
   - Subject: "Request SMTP Port Access for VPS"
   - Message template:
   
   ```
   Hello Vultr Support,

   I am running a legitimate auto-trading platform (VerzekAutoTrader) 
   on server 80.240.29.142 and need to send transactional emails 
   (verification codes, password resets) to our users via Microsoft 
   365 SMTP.

   Please unblock outbound SMTP ports (587, 25) for this server.

   Use case: 
   - Email verification for new users
   - Password reset notifications
   - Trading alerts and notifications

   Email provider: Microsoft 365 (smtp.office365.com)
   From address: support@verzekinnovative.com

   Thank you!
   ```

3. **Wait for Response:** Usually 24-48 hours
4. **Test Again:** After approval, retest port connectivity

---

## 🔐 Step 2: Create Microsoft 365 App Password

### Prerequisites
1. ✅ MFA (Multi-Factor Authentication) must be enabled
2. ✅ SMTP AUTH must be enabled for the mailbox

### Enable MFA (if not already enabled)

1. Go to: https://account.microsoft.com/security
2. Click "Advanced security options"
3. Turn on "Two-step verification"
4. Follow setup wizard (use authenticator app or phone)

### Enable SMTP AUTH for Mailbox

**Method A: Via Microsoft 365 Admin Center**

1. Login: https://admin.microsoft.com/
2. Navigate: **Users** → **Active users**
3. Select: `support@verzekinnovative.com`
4. Click: **Mail** tab
5. Click: **Manage email apps**
6. ✅ Check **"Authenticated SMTP"**
7. Click: **Save changes**

**Method B: Via PowerShell (if you have admin access)**

```powershell
Connect-ExchangeOnline
Set-CASMailbox -Identity support@verzekinnovative.com -SmtpClientAuthenticationDisabled $false
```

### Create App Password

1. **Go to:** https://myaccount.microsoft.com/
2. **Click:** "Security info" (left sidebar)
3. **Click:** "+ Add sign-in method"
4. **Select:** "App password"
5. **Enter name:** "VerzekAutoTrader SMTP"
6. **Click:** "Next"
7. **⚠️ COPY PASSWORD IMMEDIATELY** (example: `abcd efgh ijkl mnop`)
8. **Remove spaces:** `abcdefghijklmnop` (use this in environment variable)

**If "App password" option is missing:**
- MFA is not enabled → Enable it first
- Admin disabled app passwords → Contact admin
- Security defaults enabled → May need to disable (see troubleshooting)

---

## 🖥️ Step 3: Configure Environment Variables on Vultr

SSH into your Vultr server:

```bash
ssh root@80.240.29.142
```

### Option A: Add to Project Environment File

```bash
# Navigate to your project directory
cd /root/VerzekAutoTrader  # Or wherever your project is

# Create/edit .env file
nano .env
```

Add these lines (replace with your actual app password):

```bash
# Microsoft 365 SMTP Configuration
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USER=support@verzekinnovative.com
EMAIL_PASS=abcdefghijklmnop  # Your 16-char app password (NO SPACES)
EMAIL_FROM=support@verzekinnovative.com
APP_NAME=Verzek Auto Trader

# Admin notifications
ADMIN_EMAIL=your-admin-email@example.com
SUPPORT_EMAIL=support@verzekinnovative.com
```

**Make sure your Flask app loads .env:**

```python
# In your main Flask app or config file
from dotenv import load_dotenv
load_dotenv()  # This loads .env file
```

### Option B: Export as System Environment Variables

```bash
# Add to bash profile for persistence
nano ~/.bashrc

# Add these lines at the bottom:
export EMAIL_HOST="smtp.office365.com"
export EMAIL_PORT="587"
export EMAIL_USER="support@verzekinnovative.com"
export EMAIL_PASS="abcdefghijklmnop"  # Your app password
export EMAIL_FROM="support@verzekinnovative.com"
export APP_NAME="Verzek Auto Trader"

# Save file, then reload:
source ~/.bashrc
```

### Option C: Set in Systemd Service (if using systemd)

```bash
# Edit your service file
sudo nano /etc/systemd/system/verzek.service

# Add under [Service] section:
[Service]
Environment="EMAIL_HOST=smtp.office365.com"
Environment="EMAIL_PORT=587"
Environment="EMAIL_USER=support@verzekinnovative.com"
Environment="EMAIL_PASS=abcdefghijklmnop"
Environment="EMAIL_FROM=support@verzekinnovative.com"

# Reload systemd
sudo systemctl daemon-reload
sudo systemctl restart verzek
```

---

## 🧪 Step 4: Test Email Service

### Test 1: Python Script Test

SSH into Vultr and run:

```bash
cd /root/VerzekAutoTrader

# Test email sending
python3 << 'EOF'
from mail_sender import send_email

try:
    send_email(
        to='YOUR_PERSONAL_EMAIL@gmail.com',  # Replace with your email
        subject='Test Email from Vultr',
        html_body='<h1>✅ Success!</h1><p>Email service is working!</p>'
    )
    print('✅ Email sent successfully!')
except Exception as e:
    print(f'❌ Error: {str(e)}')
EOF
```

**Expected Results:**
- ✅ Success: "Email sent successfully!"
- ✅ Check your inbox (and spam folder)
- ❌ Error: See troubleshooting section below

### Test 2: Verification Email Test

```bash
python3 << 'EOF'
from mail_sender import send_verification_email

try:
    send_verification_email(
        to='YOUR_EMAIL@gmail.com',
        code='123456',
        user_name='Test User'
    )
    print('✅ Verification email sent!')
except Exception as e:
    print(f'❌ Error: {str(e)}')
EOF
```

### Test 3: API Endpoint Test (if backend is running)

```bash
# Test from command line
curl -X POST http://localhost:5000/api/email/test \
  -H "Content-Type: application/json" \
  -d '{"to": "YOUR_EMAIL@gmail.com"}'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Test email sent successfully via Microsoft 365"
}
```

---

## 🐛 Troubleshooting

### Error: "535 5.7.139 Authentication unsuccessful"

**Solution 1: Disable Security Defaults**

1. Login: https://entra.microsoft.com/
2. Navigate: **Identity** → **Overview** → **Properties**
3. Scroll down: Click **"Manage security defaults"**
4. Toggle: **Disabled**
5. Reason: Select "My organization is using Conditional Access"
6. Click: **Save**

**Solution 2: Verify SMTP AUTH is enabled**

```powershell
# Check current status
Get-CASMailbox -Identity support@verzekinnovative.com | Select SmtpClientAuthenticationDisabled

# Should return: SmtpClientAuthenticationDisabled : False
# If True, run:
Set-CASMailbox -Identity support@verzekinnovative.com -SmtpClientAuthenticationDisabled $false
```

---

### Error: "Connection timed out" or "Network unreachable"

**Cause:** Vultr is blocking SMTP ports

**Solution:**
1. Open Vultr support ticket (see Step 1)
2. Wait for port access approval
3. Retest after approval

**Temporary Workaround:** Use port 25 instead of 587 (less secure)

---

### Error: "SMTPAuthenticationError: Username and Password not accepted"

**Causes:**
1. Wrong app password (has spaces or typos)
2. Using regular password instead of app password
3. Email address is incorrect

**Solution:**
1. Regenerate app password in Microsoft account
2. Copy it carefully (remove all spaces)
3. Verify EMAIL_USER is the full email address
4. Test with curl:

```bash
curl --url 'smtp://smtp.office365.com:587' \
  --ssl-reqd \
  --mail-from 'support@verzekinnovative.com' \
  --mail-rcpt 'test@gmail.com' \
  --user 'support@verzekinnovative.com:YOUR_APP_PASSWORD' \
  --upload-file - << EOF
From: support@verzekinnovative.com
To: test@gmail.com
Subject: Test

Test email body
EOF
```

---

### Error: "SMTPServerDisconnected: Connection unexpectedly closed"

**Cause:** TLS/SSL handshake failure

**Solution:**

```python
# Update mail_sender.py if needed:
import ssl

context = ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE  # Only for testing

server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
server.starttls(context=context)
```

⚠️ **Warning:** Disabling certificate verification reduces security. Only use for testing.

---

### Check Email Service Logs

```bash
# If using systemd
sudo journalctl -u verzek -f

# Check Python application logs
tail -f /var/log/verzek.log

# Or wherever your logs are stored
```

---

## ✅ Verification Checklist

Before going live, verify:

- [ ] Vultr SMTP ports are unblocked (support ticket resolved)
- [ ] MFA is enabled on support@verzekinnovative.com
- [ ] SMTP AUTH is enabled for the mailbox
- [ ] App password created and copied (no spaces)
- [ ] Environment variables set on Vultr server
- [ ] Test email sent successfully
- [ ] Verification email template works
- [ ] Password reset email template works
- [ ] Flask app restarts load environment variables
- [ ] Email service health endpoint returns 200 OK
- [ ] Mobile app can trigger emails

---

## 📊 Final Test from Mobile App

Once everything is configured:

1. **Open VerzekAutoTrader mobile app**
2. **Register new test account**
3. **Check email for verification code**
4. **Try "Forgot Password"**
5. **Check email for reset code**

---

## 🚨 Important Notes

1. **App Password Deprecation:** Microsoft is deprecating basic authentication in September 2025. Plan to migrate to OAuth 2.0 before then.

2. **Sending Limits:**
   - 10,000 recipients per day
   - 30 messages per minute
   - Exceeding limits may block your account

3. **Firewall Rules:**
   ```bash
   # Allow outbound SMTP
   sudo ufw allow out 587/tcp
   sudo ufw allow out 25/tcp
   ```

4. **Backup Option:** If Microsoft 365 fails, consider:
   - SendGrid (15,000 free emails/month)
   - Amazon SES (62,000 free emails/month)
   - Mailgun (5,000 free emails/month)

---

## 🎯 Quick Command Reference

```bash
# SSH into Vultr
ssh root@80.240.29.142

# Check environment variables
echo $EMAIL_USER
echo $EMAIL_PASS

# Test SMTP connectivity
telnet smtp.office365.com 587

# Test Python email
python3 -c "from mail_sender import send_email; send_email('test@gmail.com', 'Test', '<h1>Test</h1>')"

# Restart Flask app
sudo systemctl restart verzek

# Check logs
sudo journalctl -u verzek -f
```

---

## 📞 Support Resources

- **Vultr Support:** https://my.vultr.com/support/
- **Microsoft 365 Admin:** https://admin.microsoft.com/
- **App Password Setup:** https://myaccount.microsoft.com/
- **SMTP Status:** https://www.limilabs.com/blog/office365-app-passwords

---

**Need help? Contact me with error messages and I'll help troubleshoot!** 🚀
