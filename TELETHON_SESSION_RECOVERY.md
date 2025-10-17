# 🔧 Telethon Session Recovery Guide

## Problem: AuthKeyDuplicatedError

When you see this error in production logs:
```
telethon.errors.rpcerrorlist.AuthKeyDuplicatedError: The authorization key (session file) 
was used under two different IP addresses simultaneously
```

**This means:** The Telegram session is corrupted and must be manually recovered.

---

## ⚠️ Why This Happens

Telegram sessions are **IP-locked** for security. When the same session is used from:
- Development workspace (IP: 172.x.x.x)
- Production deployment (IP: 10.x.x.x)

Telegram detects this as suspicious activity and **permanently blocks the session**.

---

## ✅ PERMANENT SOLUTION (Already Implemented)

The system now uses **environment-specific sessions**:

| Environment | Session File | When Active |
|-------------|--------------|-------------|
| **Development** | `telethon_session_dev.txt` | Only in workspace (Telethon is DISABLED) |
| **Production** | `telethon_session_prod.txt` | Only in deployment (auto-enabled) |

This prevents dual-IP conflicts completely!

---

## 🔧 Recovery Steps (One-Time Setup)

### Step 1: Revoke the Corrupted Session

1. Open **Telegram app** on your phone
2. Go to **Settings** → **Devices** (or **Privacy & Security** → **Active Sessions**)
3. Find the session named **"telethon"** or similar
4. Tap on it and select **"Terminate Session"**
5. Wait 10 seconds

### Step 2: Run Recovery Script

In the Replit Shell, run:

```bash
python recover_telethon_session.py
```

This will:
- ✅ Delete corrupted session files
- ✅ Create a fresh PRODUCTION session
- ✅ Save it to `telethon_session_prod.txt`

**You'll need to:**
1. Enter your phone number
2. Enter the code from Telegram app
3. Confirm the setup

### Step 3: Deploy to Production

1. Click **"Republish"** in the Deployments panel
2. Wait 1-2 minutes for deployment to complete
3. Check deployment logs for:
   ```
   [TELETHON] Loading PRODUCTION session: telethon_session_prod.txt
   🔄 Starting Telethon Auto-Forwarder (PRODUCTION)...
   📡 Monitoring Telegram for trading signals...
   ```

---

## 🎯 How It Works Now

### Development (Workspace)
```
⏭️ Telethon disabled in development (prevents dual-IP conflicts)
✅ Telethon will auto-start in production deployment
```
- Telethon is **automatically disabled**
- No session conflicts possible
- Safe to work on code

### Production (Deployment)
```
[TELETHON] Loading PRODUCTION session: telethon_session_prod.txt
🔄 Starting Telethon Auto-Forwarder (PRODUCTION)...
```
- Telethon is **automatically enabled**
- Uses dedicated production session
- 24/7 signal monitoring active

---

## 📋 Quick Commands

### Create Fresh Production Session (First Time)
```bash
python setup_telethon.py
```

### Recover Corrupted Session (After Error)
```bash
python recover_telethon_session.py
```

### Check Which Session is Being Used
```bash
ls -la telethon_session*.txt
```

---

## ⚠️ Important Notes

1. **Never Run Both Environments Simultaneously**: 
   - Development has Telethon disabled by design
   - Production has Telethon enabled automatically
   - They use separate sessions

2. **After Recovery**: 
   - Always republish to production
   - Old session is permanently dead
   - New session only works in production

3. **Session Files**:
   - `telethon_session_prod.txt` = Production (deployed)
   - `telethon_session_dev.txt` = Development (unused)
   - `telethon_session_string.txt` = Old/legacy (can be deleted)

---

## 🆘 Troubleshooting

### Error: "No session file found"
**Solution**: Run `python setup_telethon.py` to create production session

### Error: "Session still corrupted after recovery"
**Solution**: 
1. Ensure you terminated session in Telegram app
2. Wait 30 seconds
3. Run recovery script again

### Error: "Telethon not starting in production"
**Solution**: 
1. Check deployment logs for session file path
2. Verify `telethon_session_prod.txt` exists
3. Republish deployment

---

## ✅ Verification Checklist

After recovery, verify these in production logs:

- ✅ `[TELETHON] Loading PRODUCTION session: telethon_session_prod.txt`
- ✅ `🔄 Starting Telethon Auto-Forwarder (PRODUCTION)...`
- ✅ `📡 Monitoring Telegram for trading signals...`
- ✅ No AuthKeyDuplicatedError

---

**Need help?** Check `DEPLOYMENT_GUIDE.md` for complete deployment instructions.
