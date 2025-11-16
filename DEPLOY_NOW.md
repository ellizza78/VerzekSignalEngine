# 🚀 Deploy VerzekSignalEngine - Quick Start

## ✅ Completed on Replit
- [x] Generated API token: `HOUSE_ENGINE_TOKEN`
- [x] Added token to Replit Secrets
- [x] Database migration complete (tables created)
- [x] Backend code ready
- [x] Mobile app code ready

---

## 📋 Next Steps: Deploy to Vultr Server

### Step 1: Upload Files to Vultr

Connect to your Vultr server:
```bash
ssh root@80.240.29.142
```

Upload these directories to Vultr:
```bash
# From your local machine (NOT Replit):
scp -r backend/ root@80.240.29.142:/root/api_server/
scp -r signal_engine/ root@80.240.29.142:/root/
scp deploy_to_vultr.sh root@80.240.29.142:/root/
```

### Step 2: Set Environment Variables

**CRITICAL**: Set secrets as environment variables (never hardcode them):
```bash
ssh root@80.240.29.142

# Set secrets from your Replit Secrets
export HOUSE_ENGINE_TOKEN="<copy from Replit Secrets>"
export TELEGRAM_BOT_TOKEN="<your telegram bot token>"
```

### Step 3: Run Deployment Script

Now run the deployment:
```bash
cd /root
chmod +x deploy_to_vultr.sh
sudo -E bash deploy_to_vultr.sh
```

**Note**: The `-E` flag preserves environment variables when using sudo.

The script will automatically:
- ✅ Update backend code
- ✅ Add HOUSE_ENGINE_TOKEN to backend environment
- ✅ Restart backend API service
- ✅ Test backend endpoint
- ✅ Install signal engine dependencies
- ✅ Configure signal engine environment
- ✅ Setup systemd service
- ✅ Start signal engine
- ✅ Remove old Telethon code

---

## 🔍 Verification (After Deployment)

### 1. Check Services Status
```bash
# Backend status
sudo systemctl status verzek_api

# Signal engine status
sudo systemctl status verzek-signalengine
```

**Expected**: Both services should show `active (running)`

### 2. Monitor Signal Engine Logs
```bash
# Real-time logs
tail -f /root/signal_engine/logs/signal_engine.log

# Check for signals
grep "Generated signal" /root/signal_engine/logs/signal_engine.log

# Check backend communication
grep "Backend accepted" /root/signal_engine/logs/signal_engine.log
```

### 3. Check Backend Received Signals
```bash
# Query database for signals
psql $DATABASE_URL -c "SELECT id, source, symbol, side, confidence, created_at FROM house_signals ORDER BY created_at DESC LIMIT 5;"

# Check positions
psql $DATABASE_URL -c "SELECT * FROM house_signal_positions ORDER BY opened_at DESC LIMIT 5;"
```

### 4. Test Mobile App
1. Open VerzekAutoTrader mobile app
2. Login as VIP or PREMIUM user
3. Navigate to "House Signals" tab (🔥 icon)
4. Pull to refresh
5. Wait 30 seconds - signals should appear

---

## ⏱️ Timeline

**Signal Generation**: Bots generate signals based on market conditions
- **Scalping Bot**: Every 15 seconds (checks for quick momentum)
- **Trend Bot**: Every 5 minutes (checks for trend alignment)
- **QFL Bot**: Every 20 seconds (checks for dip-buy opportunities)
- **AI/ML Bot**: Every 30 seconds (checks for pattern recognition)

**Expected First Signal**: Within 5-15 minutes after deployment (depending on market volatility)

---

## 🆘 Troubleshooting

### Issue: Backend Not Starting
```bash
# Check logs
sudo journalctl -u verzek_api -n 100

# Check environment
cat /root/api_server/.env | grep HOUSE_ENGINE_TOKEN

# Restart manually
sudo systemctl restart verzek_api
```

### Issue: Signal Engine Not Starting
```bash
# Check logs
sudo journalctl -u verzek-signalengine -n 100
tail -f /root/signal_engine/logs/errors.log

# Check dependencies
cd /root/signal_engine
pip3 list | grep -E 'ccxt|python-telegram-bot'

# Restart manually
sudo systemctl restart verzek-signalengine
```

### Issue: No Signals Generated
**Possible reasons**:
- Market is sideways (low volatility = fewer signals)
- Bots just started (wait 5-15 minutes)
- Confidence thresholds too high

**Solution**:
```bash
# Lower confidence thresholds in config
nano /root/signal_engine/config/engine_settings.json

# Change min_confidence from 70 to 60
# Restart service
sudo systemctl restart verzek-signalengine
```

### Issue: Backend Not Receiving Signals
```bash
# Check dispatcher logs
grep "Backend response" /root/signal_engine/logs/signal_engine.log

# Test endpoint manually (use your token from Replit Secrets)
curl -X POST https://api.verzekinnovative.com/api/house-signals/ingest \
  -H "Content-Type: application/json" \
  -H "X-INTERNAL-TOKEN: $HOUSE_ENGINE_TOKEN" \
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

---

## 📊 Success Indicators

✅ **Deployment Successful When**:
- Both services show `active (running)`
- Signal engine logs show "VERZEK SIGNAL ENGINE v1.0" startup message
- Backend endpoint responds to test signal
- Database contains test signal record
- Mobile app displays signals for VIP/PREMIUM users

---

## 🎯 What Happens After Deployment

1. **Signal Engine** continuously monitors 20+ trading pairs
2. **4 Bots** run in parallel, each with different strategies
3. **Signals** are generated when conditions meet confidence thresholds
4. **Backend** receives signals via POST request, stores in database
5. **Push Notifications** sent to VIP/PREMIUM users
6. **Mobile App** displays signals in real-time (30s refresh)
7. **Paper Positions** tracked automatically with P&L calculations

---

## 📞 Need Help?

**Files to Check**:
- Signal Engine: `/root/signal_engine/logs/signal_engine.log`
- Backend: `sudo journalctl -u verzek_api -n 100`
- Database: `psql $DATABASE_URL -c "SELECT * FROM house_signals;"`

**Common Commands**:
```bash
# Restart everything
sudo systemctl restart verzek_api
sudo systemctl restart verzek-signalengine

# View live logs
tail -f /root/signal_engine/logs/signal_engine.log

# Check database
psql $DATABASE_URL -c "SELECT COUNT(*) FROM house_signals;"
```

---

## 🔐 Security Tokens

**IMPORTANT**: Secrets are stored in Replit Secrets and environment variables only.

**Before running deployment script**, set these environment variables on your Vultr server:

```bash
export HOUSE_ENGINE_TOKEN="your-token-from-replit-secrets"
export TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
```

**Never hardcode secrets in files or commit them to Git repositories.**

---

**Ready to deploy? Follow Step 1 above to upload files to Vultr!** 🚀
