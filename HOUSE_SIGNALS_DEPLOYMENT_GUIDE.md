# 🚀 VerzekSignalEngine v1.0 Backend Integration - Deployment Guide

## 📋 Overview

This guide provides complete step-by-step instructions for deploying the VerzekSignalEngine v1.0 integration with the VerzekAutoTrader backend and mobile app.

---

## ⚙️ Prerequisites

Before deploying, ensure you have:

- ✅ VerzekSignalEngine v1.0 code ready (see `signal_engine/` directory)
- ✅ Backend deployed at `https://api.verzekinnovative.com`
- ✅ PostgreSQL database accessible
- ✅ Access to Vultr VPS server (SSH)
- ✅ Expo mobile app code in `mobile_app/VerzekApp/`

---

## 🔑 Step 1: Generate Internal API Token

On your local machine or Replit shell:

```bash
python3 -c "import secrets; print('HOUSE_ENGINE_TOKEN=' + secrets.token_urlsafe(32))"
```

**Example output:**
```
HOUSE_ENGINE_TOKEN=gK9mP3xR7vZ2nL4wQ8bC5tY6hJ1fS0dA
```

**Save this token securely** - you'll need it for both backend and signal engine configuration.

**IMPORTANT**: Never commit this token to Git or share it publicly. Store it only in:
- Replit Secrets (for backend)
- Vultr server environment variables (for signal engine)

---

## 🗄️ Step 2: Backend Database Migration

### On Replit (or Backend Server)

```bash
cd backend

# Check database connection
python3 -c "from db import engine; print('Database:', engine.url)"

# Run migration SQL
psql $DATABASE_URL -f database/migrations/add_house_signals.sql

# Verify tables created
psql $DATABASE_URL -c "\dt house_*"
```

**Expected output:**
```
                List of relations
 Schema |         Name          | Type  |  Owner  
--------+-----------------------+-------+---------
 public | house_signal_positions| table | user
 public | house_signals         | table | user
```

---

## 🔐 Step 3: Configure Backend Environment

### Add to Replit Secrets (or `.env` file)

```bash
HOUSE_ENGINE_TOKEN=gK9mP3xR7vZ2nL4wQ8bC5tY6hJ1fS0dA
```

### Restart Backend

```bash
# On Replit - just restart the workflow
# On Vultr
cd /root/api_server
sudo systemctl restart verzek_api
sudo systemctl status verzek_api
```

### Test Endpoint

```bash
curl -X POST https://api.verzekinnovative.com/api/house-signals/ingest \
  -H "Content-Type: application/json" \
  -H "X-INTERNAL-TOKEN: gK9mP3xR7vZ2nL4wQ8bC5tY6hJ1fS0dA" \
  -d '{
    "source": "TEST",
    "symbol": "BTCUSDT",
    "side": "LONG",
    "entry": 50000.0,
    "stop_loss": 49750.0,
    "take_profits": [50500],
    "timeframe": "M5",
    "confidence": 75
  }'
```

**Expected response:**
```json
{
  "ok": true,
  "signal_id": 1,
  "message": "Signal ingested and position opened"
}
```

---

## 🤖 Step 4: Deploy Signal Engine to Vultr

### Connect to Vultr VPS

```bash
ssh root@80.240.29.142
```

### Clone or Upload Signal Engine

```bash
cd /root

# Option A: Clone from repository (if using Git)
git clone https://github.com/your-repo/VerzekAutoTrader.git
cd VerzekAutoTrader/signal_engine

# Option B: Upload via SCP (from local machine)
# scp -r signal_engine/ root@80.240.29.142:/root/
```

### Install Dependencies

```bash
cd /root/signal_engine

# Install Python packages
pip3 install -r requirements.txt

# Verify installation
pip3 list | grep -E 'ccxt|python-telegram-bot|aiohttp|uvloop'
```

### Configure Environment

```bash
cp config/.env.example config/.env
nano config/.env
```

**Edit `.env` with these values:**

```bash
# Backend Integration
BACKEND_API_URL=https://api.verzekinnovative.com
HOUSE_ENGINE_TOKEN=gK9mP3xR7vZ2nL4wQ8bC5tY6hJ1fS0dA

# Telegram Bot (use your actual values)
TELEGRAM_BOT_TOKEN=<your-telegram-bot-token>
TELEGRAM_VIP_GROUP_ID=<your-vip-group-id>
TELEGRAM_TRIAL_GROUP_ID=<your-trial-group-id>
TELEGRAM_ADMIN_GROUP_ID=<your-admin-user-id>
```

### Setup Systemd Service

```bash
# Update service file paths
sudo nano systemd/verzek-signalengine.service

# Change WorkingDirectory if needed:
# WorkingDirectory=/root/signal_engine

# Copy to systemd
sudo cp systemd/verzek-signalengine.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable verzek-signalengine
```

---

## 🧪 Step 5: Test Signal Engine

### Manual Test

```bash
cd /root/signal_engine

# Test individual bots
python3 test_bot.py

# Start manually (for testing)
python3 main.py
```

**Expected output:**
```
🔥 VERZEK SIGNAL ENGINE v1.0 🔥
✅ Scalping Bot started (15s interval)
✅ Trend Bot started (5m interval)
✅ QFL Bot started (20s interval)
✅ AI/ML Bot started (30s interval)
🔥 All bots running. Press Ctrl+C to stop.
```

**Wait 1-5 minutes** for a bot to generate a signal, then check:

```bash
# Check signal engine logs
tail -f logs/signal_engine.log

# Check dispatcher logs for backend communication
grep "Backend accepted" logs/signal_engine.log

# Check backend logs
ssh replit-backend "tail -f backend/logs/api.log | grep house_signal"
```

---

## ✅ Step 6: Start Production Service

### Start Signal Engine

```bash
sudo systemctl start verzek-signalengine
sudo systemctl status verzek-signalengine
```

**Expected status:**
```
● verzek-signalengine.service - VerzekSignalEngine
   Loaded: loaded
   Active: active (running)
```

### Monitor Logs

```bash
# Real-time logs
sudo journalctl -u verzek-signalengine -f

# Signal logs
tail -f /root/signal_engine/logs/signal_engine.log

# Error logs
tail -f /root/signal_engine/logs/errors.log
```

---

## 🗑️ Step 7: Remove Old Telethon Code

### On Vultr Server

```bash
# Stop old Telethon service
sudo systemctl stop telethon-forwarder
sudo systemctl disable telethon-forwarder

# Remove service file
sudo rm /etc/systemd/system/telethon-forwarder.service
sudo systemctl daemon-reload

# Remove old code
rm -f /root/telethon_forwarder.py
rm -f /root/setup_telethon.py
rm -f /root/recover_telethon_session.py
rm -f /root/forwarder_watchdog.py

# Remove session files
rm -f /root/telethon_session_*.txt
rm -f /root/*.session

# Clean up old logs
rm -rf /root/telethon_logs/
```

### On Replit/Backend

```bash
# Remove Telethon files
rm -f backend/signal_listener.py
rm -f setup_telethon.py
rm -f recover_telethon_session.py

# Clean up documentation (optional)
rm -f TELETHON_*.md
rm -f SIGNAL_MONITORING_FIX.md
```

### Verify Cleanup

```bash
# Check no Telethon processes
ps aux | grep telethon

# Check no Telethon imports in backend
grep -r "from telethon" backend/

# Should return nothing
```

---

## 📱 Step 8: Update Mobile App

### Add Navigation Entry

Edit `mobile_app/VerzekApp/src/navigation/AppNavigator.js`:

```javascript
import HouseSignalsScreen from '../screens/HouseSignalsScreen';

// Add to tab navigator or drawer
<Tab.Screen 
  name="HouseSignals" 
  component={HouseSignalsScreen}
  options={{
    title: "House Signals",
    tabBarIcon: ({ color, size }) => (
      <Ionicons name="pulse" size={size} color={color} />
    )
  }}
/>
```

### Test Mobile App

```bash
cd mobile_app/VerzekApp

# Install dependencies (if needed)
npm install

# Start Expo
npx expo start
```

**Test in app:**
1. Login as VIP or PREMIUM user
2. Navigate to "House Signals" tab
3. Pull to refresh
4. Verify signals appear within 30 seconds

---

## 🔍 Step 9: Verification Checklist

### Backend Verification

- [ ] Database tables created (`house_signals`, `house_signal_positions`)
- [ ] `/api/house-signals/ingest` endpoint responds to test signal
- [ ] `/api/house-signals/live` endpoint returns signals for VIP users
- [ ] Admin endpoints accessible (`/api/house-signals/admin/signals`, `/admin/positions`, `/admin/performance`)
- [ ] Push notifications sent to VIP/PREMIUM users

### Signal Engine Verification

- [ ] All 4 bots start successfully
- [ ] Bots generate signals (check logs after 5-10 minutes)
- [ ] Signals sent to backend API (check dispatcher logs)
- [ ] Telegram messages broadcast to groups
- [ ] Systemd service auto-restarts on failure

### Mobile App Verification

- [ ] House Signals screen displays correctly
- [ ] Signals load for VIP/PREMIUM users
- [ ] TRIAL users see upgrade message
- [ ] Pull-to-refresh works
- [ ] Signal details displayed properly (entry, TP, SL, confidence)

### Telethon Cleanup Verification

- [ ] No Telethon processes running
- [ ] No Telethon files in codebase
- [ ] No Telethon imports in backend
- [ ] Old systemd services removed

---

## 📊 Step 10: Monitor Performance

### Daily Checks

```bash
# Check signal count
psql $DATABASE_URL -c "SELECT source, COUNT(*) FROM house_signals GROUP BY source;"

# Check position stats
psql $DATABASE_URL -c "SELECT status, COUNT(*) FROM house_signal_positions GROUP BY status;"

# Check bot uptime
sudo systemctl status verzek-signalengine

# Check logs for errors
grep ERROR /root/signal_engine/logs/signal_engine.log
```

### Weekly Checks

```bash
# Performance by bot
curl -X GET https://api.verzekinnovative.com/api/house-signals/admin/performance \
  -H "Authorization: Bearer YOUR_PREMIUM_TOKEN" | jq

# Signal statistics
grep "SIGNAL ENGINE STATISTICS" /root/signal_engine/logs/signal_engine.log | tail -10
```

---

## 🚨 Troubleshooting

### Issue: Backend Not Receiving Signals

**Check:**
```bash
# Signal engine logs
grep "Backend accepted" logs/signal_engine.log

# Backend logs
tail -f backend/logs/api.log | grep house_signal

# Test endpoint manually
curl -X POST https://api.verzekinnovative.com/api/house-signals/ingest \
  -H "X-INTERNAL-TOKEN: $HOUSE_ENGINE_TOKEN" \
  -d '{"source":"TEST","symbol":"BTCUSDT","side":"LONG","entry":50000,"stop_loss":49500,"take_profits":[50500],"timeframe":"M5","confidence":75}'
```

**Solution:**
- Verify `HOUSE_ENGINE_TOKEN` matches in both backend and signal engine
- Check backend is running: `systemctl status verzek_api`
- Verify network connectivity: `ping api.verzekinnovative.com`

### Issue: No Signals Generated

**Check:**
```bash
# Bot status
sudo systemctl status verzek-signalengine

# Market data connectivity
tail -f logs/signal_engine.log | grep "Market data"

# Bot execution
grep "Analyzing" logs/signal_engine.log
```

**Solution:**
- Market may be sideways (low volatility = fewer signals)
- Lower confidence thresholds in `config/engine_settings.json`
- Verify CCXT exchange connectivity
- Check watchlist symbols are valid

### Issue: Mobile App Shows No Signals

**Check:**
- User subscription tier (must be VIP or PREMIUM)
- Backend `/api/house-signals/live` endpoint returns data
- App has valid auth token
- Network connectivity from mobile device

**Solution:**
```bash
# Test endpoint
curl -X GET https://api.verzekinnovative.com/api/house-signals/live \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check user tier
psql $DATABASE_URL -c "SELECT email, subscription_type FROM users WHERE id=YOUR_USER_ID;"
```

---

## 🎉 Success Indicators

### You've successfully deployed when:

✅ Signal engine service shows `active (running)`  
✅ Backend receives and stores signals in database  
✅ Mobile app displays signals for VIP/PREMIUM users  
✅ Telegram groups receive signal broadcasts  
✅ All 4 bots generate signals within 24 hours  
✅ No Telethon code remaining in codebase  
✅ Admin endpoints show performance statistics  

---

## 📞 Support

### Logs to Check First

1. Signal engine: `/root/signal_engine/logs/signal_engine.log`
2. Backend: `backend/logs/api.log`
3. Systemd: `journalctl -u verzek-signalengine -n 100`

### Contact

- **Email**: support@verzekinnovative.com
- **Telegram**: @VerzekSupport

---

## 🔄 Maintenance

### Weekly Tasks

- Review signal performance stats
- Check bot success rates
- Monitor database size
- Review error logs

### Monthly Tasks

- Update bot confidence thresholds based on performance
- Retrain AI/ML model with new data
- Review and adjust watchlists
- Clean up old signal logs (>30 days)

---

**🚀 Deployment Complete!**

VerzekSignalEngine v1.0 is now fully integrated with your VerzekAutoTrader platform.
