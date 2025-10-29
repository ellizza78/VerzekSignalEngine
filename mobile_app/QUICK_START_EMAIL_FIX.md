# 🚀 Quick Start: Fix Email Service in 5 Steps

**Goal:** Get email verification and password reset working on your Vultr server

---

## ⚡ TL;DR - Fast Track

```bash
# 1. SSH into Vultr
ssh root@80.240.29.142

# 2. Upload diagnostic script
# (Copy tools/test_email_service.py to Vultr)

# 3. Set environment variables
export EMAIL_USER="support@verzekinnovative.com"
export EMAIL_PASS="your-16-char-app-password"

# 4. Run diagnostic
python3 test_email_service.py
```

---

## 📋 Step-by-Step Instructions

### **Step 1: Check if SMTP Ports are Blocked** ⏱️ 2 minutes

SSH into your Vultr server:

```bash
ssh root@80.240.29.142

# Test port connectivity
telnet smtp.office365.com 587
```

**Result:**
- ✅ **"Connected"** → Ports are open, proceed to Step 3
- ❌ **"Connection refused/timeout"** → Ports blocked, do Step 2

---

### **Step 2: Request SMTP Port Access from Vultr** ⏱️ 24-48 hours

Only needed if ports are blocked!

1. **Login:** https://my.vultr.com/
2. **Support → Open Ticket**
3. **Subject:** "Request SMTP Port Access"
4. **Message:**

```
Hello,

I need to send transactional emails (verification, password reset) 
via Microsoft 365 SMTP for my VerzekAutoTrader platform on server 
80.240.29.142.

Please unblock outbound SMTP port 587.

Email provider: Microsoft 365 (smtp.office365.com)
Use case: User verification emails

Thank you!
```

5. **Wait for approval** (usually 24-48 hours)
6. **Return to Step 1** after approval

---

### **Step 3: Create Microsoft 365 App Password** ⏱️ 5 minutes

#### A. Enable MFA (if not enabled)
1. Go to: https://account.microsoft.com/security
2. Turn on **"Two-step verification"**
3. Follow setup wizard

#### B. Create App Password
1. Go to: https://myaccount.microsoft.com/
2. Click: **Security info**
3. Click: **+ Add sign-in method**
4. Select: **App password**
5. Enter name: **"VerzekAutoTrader"**
6. **⚠️ COPY THE PASSWORD** (example: `abcd efgh ijkl mnop`)
7. **Remove spaces:** `abcdefghijklmnop`

**Can't see "App password" option?**
- Enable MFA first
- May need to disable Security Defaults: https://entra.microsoft.com/

---

### **Step 4: Set Environment Variables on Vultr** ⏱️ 3 minutes

SSH into Vultr:

```bash
ssh root@80.240.29.142

# Navigate to your project
cd /root/VerzekAutoTrader  # Or wherever your project is

# Edit .env file
nano .env
```

Add these lines:

```bash
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USER=support@verzekinnovative.com
EMAIL_PASS=abcdefghijklmnop  # Your app password (NO SPACES!)
EMAIL_FROM=support@verzekinnovative.com
APP_NAME=Verzek Auto Trader
```

**Save file:** `Ctrl+X`, then `Y`, then `Enter`

---

### **Step 5: Test Email Service** ⏱️ 2 minutes

#### Method A: Automated Diagnostic (Recommended)

```bash
# Upload the diagnostic script to Vultr
# On your local machine:
scp tools/test_email_service.py root@80.240.29.142:/root/

# On Vultr:
ssh root@80.240.29.142
cd /root
python3 test_email_service.py
```

The script will:
- ✅ Check port connectivity
- ✅ Verify environment variables
- ✅ Test SMTP authentication
- ✅ Send test email
- ✅ Test mail_sender.py module

#### Method B: Manual Test

```bash
ssh root@80.240.29.142
cd /root/VerzekAutoTrader

# Quick Python test
python3 << 'EOF'
from mail_sender import send_email
send_email(
    'YOUR_EMAIL@gmail.com',  # Replace with your email
    'Test',
    '<h1>Success!</h1><p>Email works!</p>'
)
print('✅ Email sent!')
EOF
```

**Check your inbox!** (and spam folder)

---

## ✅ Verification

Test from your mobile app:

1. **Open VerzekAutoTrader app**
2. **Register new test account**
3. **You should receive verification email!**
4. **Try "Forgot Password"**
5. **You should receive reset email!**

---

## 🐛 Common Issues

### "Connection refused" on port 587
→ Vultr is blocking SMTP ports  
→ Open support ticket (Step 2)

### "Authentication unsuccessful (535 5.7.139)"
→ Wrong app password or spaces in password  
→ Regenerate app password and copy without spaces  
→ May need to disable Security Defaults

### "Username and Password not accepted"
→ Using regular password instead of app password  
→ Create app password (Step 3)

### Email not sent but no errors
→ Check spam folder  
→ Verify EMAIL_FROM matches EMAIL_USER  
→ Check Microsoft 365 sending limits (10k/day)

---

## 📞 Need Help?

**Detailed Guide:** See `VULTR_EMAIL_SETUP_GUIDE.md`  
**Diagnostic Tool:** Run `tools/test_email_service.py`  
**Microsoft 365 Admin:** https://admin.microsoft.com/

---

## 🎯 Summary

**Total Time:** ~15 minutes (+ 24-48h for Vultr if ports blocked)

**What You Need:**
1. SSH access to Vultr (80.240.29.142)
2. Microsoft 365 app password
3. 5 minutes of your time

**Expected Result:**
- ✅ Emails sending from Vultr
- ✅ Users can verify email
- ✅ Password reset works
- ✅ All notification emails working

**Let's get it done!** 🚀
