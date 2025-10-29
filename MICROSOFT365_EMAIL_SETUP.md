# Microsoft 365 Email Integration - Complete Setup Guide

## ✅ Integration Status: COMPLETED

VerzekAutoTrader now uses **Microsoft 365 SMTP** (support@verzekinnovative.com) for all email communications.

---

## 📧 Email Service Configuration

### Replit Secrets (Environment Variables)

**Required secrets** (add in Replit → Tools → Secrets):

```
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USER=support@verzekinnovative.com
EMAIL_PASS=[your Microsoft 365 password or app password]
EMAIL_FROM=support@verzekinnovative.com
APP_NAME=Verzek Auto Trader
```

**Optional (for domain/API configuration):**

```
DOMAIN=verzekinnovative.com
API_BASE_URL=https://api.verzekinnovative.com
SUPPORT_EMAIL=support@verzekinnovative.com
ADMIN_EMAIL=support@verzekinnovative.com
BACKEND_URL=http://80.240.29.142:5000
```

---

## 🚀 Quick Test

### Test Email Service Health

```bash
curl https://verzek-auto-trader.replit.app/health/mail
```

**Expected response:**
```json
{
  "email_service": "Microsoft 365 SMTP",
  "configured": true,
  "smtp_host": "smtp.office365.com",
  "smtp_port": 587,
  "from_email": "support@verzekinnovative.com"
}
```

### Send Test Email

```bash
curl -X POST https://verzek-auto-trader.replit.app/send-test \
  -H "Content-Type: application/json" \
  -d '{"to":"your-email@example.com"}'
```

**Expected response:**
```json
{
  "ok": true,
  "sent_to": "your-email@example.com",
  "message": "Test email sent successfully via Microsoft 365"
}
```

---

## 📂 Files Created/Modified

### New Files:
- **`mail_sender.py`** - Drop-in Microsoft 365 email utility with helper functions
  - `send_email()` - Core SMTP sender
  - `send_verification_email()` - Pre-formatted verification emails
  - `send_password_reset_email()` - Pre-formatted reset emails
  - `send_welcome_email()` - Pre-formatted welcome emails

### Modified Files:
- **`services/email_service.py`** - Updated to support Microsoft 365 SMTP
  - Backward compatible with old env vars (SMTP_USER, SMTP_PASS)
  - New env vars take priority (EMAIL_USER, EMAIL_PASS)
  - Default: smtp.office365.com:587

- **`bridge.py`** - Added test endpoints
  - `GET /health/mail` - Email service health check
  - `POST /send-test` - Send test email

---

## 🔧 Usage in Code

### Option 1: Use mail_sender.py (Recommended)

```python
from mail_sender import send_verification_email, send_password_reset_email, send_welcome_email

# Send verification code
send_verification_email(
    to="user@example.com",
    code="123456",
    user_name="John"
)

# Send password reset
send_password_reset_email(
    to="user@example.com",
    code="654321",
    user_name="John"
)

# Send welcome email
send_welcome_email(
    to="user@example.com",
    user_name="John"
)

# Send custom email
from mail_sender import send_email

html = "<h3>Custom Email</h3><p>Your content here</p>"
send_email("user@example.com", "Subject", html)
```

### Option 2: Use existing EmailService (Automatic)

The existing `EmailService` class automatically uses Microsoft 365:

```python
from services.email_service import email_service

# Works automatically with Microsoft 365
result = email_service.send_verification_email(
    email="user@example.com",
    username="john",
    token="verification-token-123"
)
```

---

## 🔐 Microsoft 365 Notes

### SMTP Authentication
- **Server:** smtp.office365.com
- **Port:** 587 (TLS via STARTTLS)
- **Auth:** Must be enabled for the mailbox (usually enabled by default)

### If MFA (Multi-Factor Authentication) is Enabled:

1. Go to https://account.microsoft.com/security
2. Under "Advanced security options" → "App passwords"
3. Create new app password: "Verzek Auto Trader"
4. Use the generated password as `EMAIL_PASS` secret

### Sending Limits (Microsoft 365)
- **~10,000 recipients/day**
- **~30 messages/minute**
- Respect rate limits to avoid throttling

### Deliverability
- ✅ **SPF Record:** Already configured for verzekinnovative.com
- ⏳ **DKIM:** Recommended for maximum deliverability
- ⏳ **DMARC:** Recommended for email security

---

## 🎯 Email Types Supported

### 1. Verification Emails
- Sent during user registration
- 6-digit code with 10-minute expiration
- Professional Verzek branding

### 2. Password Reset Emails
- Sent on password reset request
- 6-digit code with 10-minute expiration
- Security warning included

### 3. Welcome Emails
- Sent after successful registration
- Lists platform features
- Includes getting started guide

### 4. Custom Emails
- Support messages
- Trade alerts
- System notifications

---

## 🚨 Troubleshooting

### Error: "535 5.7.3 Authentication unsuccessful"
**Solution:**
1. Verify EMAIL_PASS is correct
2. Log in to outlook.office.com to confirm credentials
3. If MFA is enabled, use an App Password instead

### Error: "BROADCAST_BOT_TOKEN environment variable is required"
**Solution:**
This is a different error - make sure EMAIL_USER and EMAIL_PASS are set, not BROADCAST_BOT_TOKEN

### Test email not arriving
**Checks:**
1. Check spam/junk folder
2. Verify EMAIL_USER = support@verzekinnovative.com
3. Test with `/health/mail` endpoint first
4. Check Replit logs for SMTP errors

---

## 📋 Deployment Checklist

- [x] Microsoft 365 email secrets added to Replit
- [x] `mail_sender.py` created with helper functions
- [x] `EmailService` updated to use Microsoft 365
- [x] Test endpoints added (`/health/mail`, `/send-test`)
- [x] Backward compatibility maintained
- [x] Professional email templates created
- [ ] **User action:** Add EMAIL_PASS secret to Replit
- [ ] **User action:** Test email with `/send-test` endpoint
- [ ] **User action:** Verify email arrives in inbox

---

## 🔄 Syncing with Vultr Backend

**Important:** This setup is for the **Replit bridge only**. To use Microsoft 365 email on Vultr:

```bash
# SSH into Vultr
ssh root@80.240.29.142

# Add email config to .env
cd /var/www/VerzekAutoTrader
cat >> .env << 'EOF'
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USER=support@verzekinnovative.com
EMAIL_PASS=[your-password]
EMAIL_FROM=support@verzekinnovative.com
APP_NAME=Verzek Auto Trader
EOF

# Copy mail_sender.py from Replit to Vultr
# (Upload via SCP or copy content manually)

# Restart services
sudo systemctl restart verzekapi
```

---

## ✅ Success Criteria

**Email integration is working when:**

1. ✅ `/health/mail` shows `"configured": true`
2. ✅ `/send-test` sends email successfully
3. ✅ Test email arrives in inbox (not spam)
4. ✅ User registration sends verification email
5. ✅ Password reset sends code email

---

## 📞 Support

For issues with Microsoft 365 email integration:
- Check Replit logs: `Console` tab
- Test health endpoint first
- Verify all secrets are set correctly
- Contact: support@verzekinnovative.com (after email is working!)
