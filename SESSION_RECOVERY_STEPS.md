# 🔧 SESSION RECOVERY - QUICK START GUIDE

## Your Current Situation
You're getting **AuthKeyDuplicatedError** because your Telegram session is corrupted from being used on different IPs (development + production).

## ✅ THE FIX IS READY - Just Follow These Steps:

### Step 1: Revoke Session in Telegram (30 seconds)
1. Open **Telegram app** on your phone
2. Go to **Settings** → **Devices** (or **Privacy & Security** → **Active Sessions**)
3. Find session named **"telethon"**
4. Tap it and select **"Terminate Session"**
5. Wait 10 seconds

### Step 2: Create Fresh Production Session (1 minute)
In the Replit Shell, run:
```bash
python recover_telethon_session.py
```

Follow the prompts:
- Confirm you terminated the session (type `yes`)
- Enter your phone number
- Enter the code from Telegram
- Done! Production session created ✅

### Step 3: Deploy to Production (2 minutes)
1. Click **"Deploy"** or **"Deployments"** (left sidebar)
2. Find your **Reserved VM** deployment
3. Click **"Republish"**
4. Wait 1-2 minutes

### Step 4: Verify It Works
Check deployment logs for:
```
[TELETHON] Loading PRODUCTION session: telethon_session_prod.txt
🔄 Starting Telethon Auto-Forwarder (PRODUCTION)...
📡 Monitoring Telegram for trading signals...
```

**No more errors!** 🎉

---

## What Was Fixed

### BEFORE (Broken):
- ❌ Same session used in dev + production
- ❌ Dual-IP conflict → AuthKeyDuplicatedError
- ❌ Session permanently corrupted

### AFTER (Fixed):
- ✅ Separate sessions for dev and production
- ✅ Zero dual-IP conflicts
- ✅ Production auto-uses `telethon_session_prod.txt`
- ✅ Development never runs Telethon (auto-disabled)

---

## Files Created
- **recover_telethon_session.py** - Recovery script (you'll run this once)
- **setup_telethon.py** - Production session setup
- **TELETHON_SESSION_RECOVERY.md** - Complete documentation
- **DEPLOYMENT_GUIDE.md** - Updated deployment guide

---

## Need Help?
See **TELETHON_SESSION_RECOVERY.md** for detailed troubleshooting.

---

**Start with Step 1 above to fix the error!** 🚀
