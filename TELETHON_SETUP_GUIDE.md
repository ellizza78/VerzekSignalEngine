# Telethon Auto-Forwarder Setup Guide

## Problem: AuthKeyDuplicatedError

If you see this error:
```
AuthKeyDuplicatedError: The authorization key (session file) was used under two different IP addresses simultaneously
```

**Cause:** Your Telethon session is being used from 2 locations at once (development + production).

---

## Solution Options

### Option 1: Run Telethon ONLY in Production (Recommended for 24/7)

**Step 1:** Disable Telethon in Development
- Add this to your Replit Secrets:
  - Key: `DISABLE_TELETHON`
  - Value: `true`

**Step 2:** Authenticate Telethon for Production
1. In your production/deployed environment, run:
   ```bash
   python setup_telethon.py
   ```
2. Enter your phone number with country code
3. Enter the verification code from Telegram
4. Republish your app

**Result:** Telethon will ONLY run in production (24/7), no conflicts!

---

### Option 2: Run Telethon ONLY in Development

**Step 1:** Stop your deployed/published app (or set `DISABLE_TELETHON=true` there)

**Step 2:** Authenticate Telethon in Development
1. Delete old session: `rm -f telethon_session_string.txt`
2. Run: `python setup_telethon.py`
3. Enter phone + verification code

**Result:** Telethon runs only in development

---

## How the Fix Works

The updated `run_all_bots.py` now checks for `DISABLE_TELETHON` environment variable:
- If `DISABLE_TELETHON=true` → Telethon is skipped
- If not set → Telethon runs normally

This prevents dual-IP authentication conflicts!

---

## Quick Reference

### Disable Telethon in Dev (Run in Production Only)
```bash
# In Replit Secrets, add:
DISABLE_TELETHON=true
```

### Enable Telethon Everywhere
```bash
# Remove DISABLE_TELETHON from Secrets
# Or set it to: false
```

### Re-authenticate Telethon
```bash
rm -f telethon_session_string.txt
python setup_telethon.py
```
