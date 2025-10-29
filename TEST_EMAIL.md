# Microsoft 365 Email Integration - Testing Guide

## Quick Test Commands

### 1. Check Email Service Health

```bash
curl https://verzek-auto-trader.replit.app/health/mail
```

**Expected Response:**
```json
{
  "email_service": "Microsoft 365 SMTP",
  "configured": true,
  "smtp_host": "smtp.office365.com",
  "smtp_port": 587,
  "from_email": "support@verzekinnovative.com"
}
```

---

### 2. Send Test Email

**Replace `your-email@example.com` with your actual email:**

```bash
curl -X POST https://verzek-auto-trader.replit.app/send-test \
  -H "Content-Type: application/json" \
  -d '{"to":"your-email@example.com"}'
```

**Expected Response:**
```json
{
  "ok": true,
  "sent_to": "your-email@example.com",
  "message": "Test email sent successfully via Microsoft 365"
}
```

---

### 3. Test from Python (Replit Shell)

```python
from mail_sender import send_email, send_verification_email

# Test basic email
send_email(
    to="your-email@example.com",
    subject="Test from Replit",
    html_body="<h3>Test successful!</h3><p>Email is working.</p>"
)

# Test verification email
send_verification_email(
    to="your-email@example.com",
    code="123456",
    user_name="John"
)
```

---

## Troubleshooting

### If health check shows "configured": false

**Check secrets:**
```bash
# In Replit Shell
python3 << 'EOF'
import os
print(f"EMAIL_USER: {bool(os.getenv('EMAIL_USER'))}")
print(f"EMAIL_PASS: {bool(os.getenv('EMAIL_PASS'))}")
print(f"EMAIL_HOST: {os.getenv('EMAIL_HOST', 'not set')}")
EOF
```

### If test email fails

1. **Check logs:**
   - View VerzekBridge logs in Console tab
   - Look for SMTP errors

2. **Verify credentials:**
   - EMAIL_USER = support@verzekinnovative.com
   - EMAIL_PASS = (correct password or app password)

3. **Test SMTP connection manually:**
```python
import smtplib, os, ssl

EMAIL_HOST = "smtp.office365.com"
EMAIL_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

try:
    context = ssl.create_default_context()
    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls(context=context)
        server.login(EMAIL_USER, EMAIL_PASS)
    print("✅ SMTP authentication successful!")
except Exception as e:
    print(f"❌ SMTP authentication failed: {e}")
```

---

## What to Check in Received Email

When you receive the test email, verify:

1. ✅ **From address:** support@verzekinnovative.com
2. ✅ **Subject:** Verzek Auto Trader: Replit SMTP Test
3. ✅ **Branding:** Verzek gradient colors (teal/gold)
4. ✅ **Inbox placement:** Not in spam/junk folder
5. ✅ **Professional formatting:** HTML renders correctly

---

## Next Steps After Successful Test

1. ✅ Verify test email arrives
2. ✅ Test user registration flow
3. ✅ Test password reset flow
4. ✅ Deploy to Vultr backend (optional)

---

## Production Checklist

- [x] EMAIL_PASS secret added to Replit
- [ ] Test email sent and received successfully
- [ ] User registration sends verification email
- [ ] Password reset sends code email
- [ ] Emails arrive in inbox (not spam)
- [ ] Email branding matches Verzek design
- [ ] Rate limiting works (60 second cooldown)
- [ ] Microsoft 365 sending limits respected
