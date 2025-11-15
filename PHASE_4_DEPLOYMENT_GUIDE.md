# Phase 4 Complete Deployment Guide

**VerzekAutoTrader - Production-Ready Deployment**

This guide covers deploying Phase 4 changes: deep linking, Telegram group monitoring, safety flags, and production APK build.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Backend Deployment](#backend-deployment)
3. [Mobile App Build](#mobile-app-build)
4. [Telegram Bot Configuration](#telegram-bot-configuration)
5. [Testing & Verification](#testing--verification)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### ✅ Required Before Starting

- [x] Vultr VPS access (80.240.29.142)
- [x] GitHub repos synced (VerzekBackend + VerzekAutoTrader)
- [x] Expo account with EAS CLI configured
- [x] Telegram bot created (@BotFather)
- [x] Resend API key (for emails)
- [x] Domain configured (api.verzekinnovative.com)

---

## Backend Deployment

### Step 1: Update Environment Configuration

SSH into Vultr VPS:

```bash
ssh root@80.240.29.142
```

Edit environment file:

```bash
nano /root/api_server_env.sh
```

Add/update these variables:

```bash
# Phase 4 Safety Flags
LIVE_TRADING_ENABLED=false
EXCHANGE_MODE=paper
USE_TESTNET=true
EMERGENCY_STOP=false

# Deep Linking
DEEP_LINK_SCHEME=verzek-app://

# Telegram Groups (get IDs from @getidsbot)
TELEGRAM_TRIAL_GROUP_ID=
TELEGRAM_VIP_GROUP_ID=
TELEGRAM_ADMIN_DEBUG_GROUP_ID=

# Authorized Sources
AUTHORIZED_SIGNAL_BOT_USERNAMES=your_signal_source_bot
AUTHORIZED_ADMIN_USER_IDS=572038606
```

Save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`).

### Step 2: Pull Latest Code

```bash
cd /root/VerzekBackend
git pull origin main
```

### Step 3: Restart Services

```bash
# Restart API server
systemctl restart verzek-api.service

# Restart Telegram bot
systemctl restart verzek-signal-bot.service

# Verify both services are running
systemctl status verzek-api.service
systemctl status verzek-signal-bot.service
```

### Step 4: Verify Backend

```bash
# Check API health
curl https://api.verzekinnovative.com/api/health

# Check safety status
curl https://api.verzekinnovative.com/api/safety/status

# View bot logs
journalctl -u verzek-signal-bot.service -n 50 --no-pager
```

**Expected Responses:**

API Health:
```json
{
  "ok": true,
  "status": "healthy",
  "timestamp": "2025-11-15T14:30:00.000Z"
}
```

Safety Status:
```json
{
  "ok": true,
  "active_workers": 1,
  "mode": "paper",
  "status": "operational"
}
```

Bot Logs:
```
🤖 VerzekAutoTrader Signal Bridge Bot - Starting...
Mode: DRY-RUN
Bot Token: ✅ Set
Signal bridge bot started
```

---

## Mobile App Build

### Step 1: Prepare Local Environment

```bash
cd mobile_app/VerzekApp

# Install/update dependencies
npm install

# Login to Expo (if not already logged in)
npx expo login
```

### Step 2: Update App Version

Edit `app.json`:

```json
{
  "expo": {
    "version": "2.2.0",
    "android": {
      "versionCode": 21
    }
  }
}
```

### Step 3: Build Production APK

```bash
# Clear cache and build
eas build -p android --profile production --clear-cache
```

**Build Process:**
1. EAS will upload your code
2. Build on Expo servers (~5-10 minutes)
3. You'll get a download link when complete

### Step 4: Download & Test APK

```bash
# EAS will provide a download link like:
# https://expo.dev/accounts/addeyemi12/projects/verzek-app/builds/...

# Download to your computer, then:
# 1. Transfer APK to Android device
# 2. Enable "Install from Unknown Sources"
# 3. Install APK
# 4. Test all features
```

### Alternative: Build Locally (Optional)

If EAS fails, build locally:

```bash
# Install Android SDK first
# Then:
npx expo prebuild --platform android
cd android
./gradlew assembleRelease

# APK location:
# android/app/build/outputs/apk/release/app-release.apk
```

---

## Telegram Bot Configuration

### Step 1: Create Telegram Groups

1. **Create TRIAL Group:**
   - Open Telegram
   - Create new group: "Verzek TRIAL Signals"
   - Add your signal bot to group
   - Make bot admin

2. **Create VIP Group:**
   - Create new group: "Verzek VIP Signals"
   - Add your signal bot to group
   - Make bot admin

3. **Create DEBUG Group (Optional):**
   - Create new group: "Verzek Admin Debug"
   - Add your signal bot to group

### Step 2: Get Group Chat IDs

Use @getidsbot or @username_to_id_bot:

1. Add bot to each group
2. Send a message in the group
3. Bot will reply with chat ID (e.g., `-1001234567890`)
4. Note down each group's chat ID

### Step 3: Configure Bot

Edit environment file on Vultr:

```bash
nano /root/api_server_env.sh
```

Add group IDs:

```bash
TELEGRAM_TRIAL_GROUP_ID=-1001234567890
TELEGRAM_VIP_GROUP_ID=-1009876543210
TELEGRAM_ADMIN_DEBUG_GROUP_ID=-1005555555555
```

Restart bot:

```bash
systemctl restart verzek-signal-bot.service
journalctl -u verzek-signal-bot.service -f
```

### Step 4: Test Signal Parsing

Send test signal in one of your groups:

```
BUY BTCUSDT @ 50000
```

Bot should:
- React with ✅ emoji (if possible)
- Save signal to `/root/VerzekBackend/backend/telegram_signals/`
- Log the signal

Check logs:

```bash
ls -la /root/VerzekBackend/backend/telegram_signals/
cat /root/VerzekBackend/backend/telegram_signals/signal_*.json
```

---

## Testing & Verification

### End-to-End Testing Checklist

#### 1. Registration & Email Verification ✅

- [ ] Register new user via mobile app
- [ ] Receive verification email
- [ ] Tap "Verify Email" button
- [ ] App opens with deep link (verzek-app://verify-email?token=...)
- [ ] Email verified successfully
- [ ] Redirected to login screen

#### 2. Password Reset ✅

- [ ] Tap "Forgot Password" on login screen
- [ ] Enter email address
- [ ] Receive password reset email
- [ ] Tap "Reset Password" button
- [ ] App opens with deep link (verzek-app://reset-password?token=...)
- [ ] Enter new password
- [ ] Password reset successfully
- [ ] Login with new password

#### 3. Dashboard & Features ✅

- [ ] Login successful
- [ ] Dashboard loads
- [ ] Signals feed displays
- [ ] Positions page works
- [ ] Settings sync with backend
- [ ] Exchange accounts page loads
- [ ] Subscription page works
- [ ] Profile page displays correctly

#### 4. Telegram Bot ✅

- [ ] Bot responds to /start in private chat
- [ ] Bot responds to /status in private chat
- [ ] Bot parses signals from groups
- [ ] Bot only accepts authorized senders
- [ ] Bot saves signals to file
- [ ] Bot logs activity correctly

#### 5. Backend Safety ✅

- [ ] `/api/safety/status` returns "paper" mode
- [ ] Exchange connectors in DRY-RUN mode
- [ ] No real orders possible
- [ ] All trades are simulated

---

## Troubleshooting

### Issue 1: Deep Links Not Opening App

**Symptoms:** Email links open in browser instead of app

**Solution:**

1. Check app.json has correct scheme:
   ```json
   "scheme": "verzek-app"
   ```

2. Rebuild APK with updated configuration

3. On Android, clear app defaults:
   - Settings → Apps → Verzek AutoTrader → Set as Default → Clear defaults
   - Click verification link again

### Issue 2: Telegram Bot Not Responding in Groups

**Symptoms:** Bot doesn't parse signals from groups

**Checklist:**

```bash
# 1. Check bot is running
systemctl status verzek-signal-bot.service

# 2. Check group IDs are correct
grep TELEGRAM_.*_GROUP_ID /root/api_server_env.sh

# 3. Check bot is admin in groups
# (Check Telegram group settings)

# 4. Check authorized senders
grep AUTHORIZED /root/api_server_env.sh

# 5. View live logs
journalctl -u verzek-signal-bot.service -f
```

### Issue 3: APK Build Fails

**Symptoms:** EAS build fails with errors

**Solutions:**

1. **Clear cache:**
   ```bash
   eas build -p android --profile production --clear-cache
   ```

2. **Check credentials:**
   ```bash
   eas credentials
   ```

3. **Build locally (fallback):**
   ```bash
   npx expo prebuild --platform android
   cd android
   ./gradlew clean
   ./gradlew assembleRelease
   ```

### Issue 4: Email Verification Not Working

**Symptoms:** Verification emails not received

**Checklist:**

```bash
# 1. Check Resend API key is set
grep RESEND_API_KEY /root/api_server_env.sh

# 2. Check email configuration
curl -X POST https://api.verzekinnovative.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123456","username":"testuser"}'

# 3. Check API logs
journalctl -u verzek-api.service -f
```

### Issue 5: Safety Mode Not Enforcing

**Symptoms:** Worried about accidental live trading

**Verify Safety:**

```bash
# Check all safety flags
grep -E "LIVE_TRADING|EXCHANGE_MODE|TESTNET|EMERGENCY" /root/api_server_env.sh

# Should show:
# LIVE_TRADING_ENABLED=false
# EXCHANGE_MODE=paper
# USE_TESTNET=true
# EMERGENCY_STOP=false

# Check backend safety config
curl https://api.verzekinnovative.com/api/safety/status

# Restart to ensure settings loaded
systemctl restart verzek-api.service
```

---

## Quick Reference Commands

### Backend Management

```bash
# View API logs
journalctl -u verzek-api.service -f

# View bot logs
journalctl -u verzek-signal-bot.service -f

# Restart API
systemctl restart verzek-api.service

# Restart bot
systemctl restart verzek-signal-bot.service

# Check status
systemctl status verzek-api.service
systemctl status verzek-signal-bot.service
```

### Mobile App

```bash
# Install dependencies
npm install

# Build APK
eas build -p android --profile production

# Run dev build
npx expo start --tunnel --go
```

### Useful API Endpoints

```bash
# Health check
curl https://api.verzekinnovative.com/api/health

# Safety status
curl https://api.verzekinnovative.com/api/safety/status

# Ping
curl https://api.verzekinnovative.com/api/ping
```

---

## Next Steps After Deployment

1. **Monitor Logs:** Watch for any errors in first 24 hours
2. **Test with Real Users:** Invite beta testers
3. **Collect Feedback:** Note any issues or feature requests
4. **Optimize Performance:** Monitor API response times
5. **Plan Phase 5:** Prepare for live trading activation (when ready)

---

## Support

**For Deployment Issues:**
- Check service logs
- Verify environment variables
- Ensure all services are running
- Test API endpoints

**For Feature Questions:**
- Review Phase 2 & 3 completion reports
- Check `LIVE_TRADING_PRECHECK_REPORT.md`
- Review `PHASE_4_ENVIRONMENT_CONFIG.md`

---

**Deployed By:** Replit AI Agent  
**Date:** November 15, 2025  
**Phase:** 4 - Production Ready (DRY-RUN Mode)  
**Status:** ✅ Complete

---

🎉 **Congratulations!** Your VerzekAutoTrader platform is now production-ready with deep linking, group signal monitoring, and safety guardrails in place!
