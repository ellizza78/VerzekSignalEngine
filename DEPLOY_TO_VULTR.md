# 🚀 Deploy VerzekSignalEngine to Vultr - Quick Guide

## Server Information
- **IP Address**: 80.240.29.142
- **Backend API**: https://api.verzekinnovative.com
- **Target Directory**: /root/

---

## Step 1: Upload Files from Local Machine

From your terminal (where you cloned the project):

```bash
# Upload backend code
scp -r backend/ root@80.240.29.142:/root/api_server/

# Upload signal engine
scp -r signal_engine/ root@80.240.29.142:/root/

# Upload deployment script
scp deploy_to_vultr.sh root@80.240.29.142:/root/
```

---

## Step 2: SSH into Vultr and Set Environment Variables

```bash
ssh root@80.240.29.142

# Set your secrets (get these from Replit Secrets)
export HOUSE_ENGINE_TOKEN="EXEE_TueWz6vSSUlWus3jStZKFM8JCP1mPuUjQ6SX5o"
export TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
```

---

## Step 3: Run Deployment Script

```bash
cd /root
chmod +x deploy_to_vultr.sh
sudo -E bash deploy_to_vultr.sh
```

The script will:
- ✅ Update backend code
- ✅ Add HOUSE_ENGINE_TOKEN to backend .env
- ✅ Restart backend API service
- ✅ Install signal engine dependencies
- ✅ Configure signal engine
- ✅ Setup systemd service
- ✅ Start signal engine
- ✅ Remove old Telethon code

---

## Step 4: Verify Deployment

### Check Services
```bash
# Backend status
sudo systemctl status verzek_api

# Signal engine status
sudo systemctl status verzek-signalengine
```

**Expected**: Both show `active (running)`

### Monitor Signal Engine
```bash
# Real-time logs
tail -f /root/signal_engine/logs/signal_engine.log

# Wait 5-10 minutes for first signal
grep "Generated signal" /root/signal_engine/logs/signal_engine.log
```

### Check Backend Received Signals
```bash
# Count signals in database
psql $DATABASE_URL -c "SELECT COUNT(*) FROM house_signals;"

# View recent signals
psql $DATABASE_URL -c "SELECT id, source, symbol, side, confidence, created_at FROM house_signals ORDER BY created_at DESC LIMIT 5;"
```

---

## Step 5: Test Mobile App

1. Open VerzekAutoTrader app
2. Login as **VIP** or **PREMIUM** user
3. Navigate to **House Signals** tab (🔥 icon)
4. Pull to refresh
5. Signals should appear within 30 seconds

---

## 🎯 Success Indicators

✅ Both services running  
✅ Signal engine logs show bot startup  
✅ Signals generated within 15 minutes  
✅ Database contains signal records  
✅ Mobile app displays signals  
✅ No Telethon processes running  

---

## 🆘 Quick Troubleshooting

**Service won't start:**
```bash
sudo journalctl -u verzek-signalengine -n 50
```

**No signals generated:**
- Market may be low volatility (wait longer)
- Check bot logs: `tail -f /root/signal_engine/logs/signal_engine.log`

**Backend not receiving signals:**
```bash
# Test endpoint
curl -X POST https://api.verzekinnovative.com/api/house-signals/ingest \
  -H "Content-Type: application/json" \
  -H "X-INTERNAL-TOKEN: $HOUSE_ENGINE_TOKEN" \
  -d '{"source":"TEST","symbol":"BTCUSDT","side":"LONG","entry":50000,"stop_loss":49750,"take_profits":[50500],"timeframe":"M5","confidence":75}'
```

---

## 📊 What Happens Next

After successful deployment:
1. **Signal engine** generates 10-25 signals/day
2. **Backend** stores all signals in PostgreSQL
3. **Mobile app** displays signals for VIP/PREMIUM users
4. **Paper positions** tracked automatically
5. **Performance stats** accumulate in database

---

## 🔄 After Deployment: Phase 5 & 6

Once the signal engine is live and stable, we'll build:
- Watchlist API (bots fetch trading pairs)
- Auto-trading trigger (PREMIUM users)
- Position management engine (TP/SL ladder)
- Telegram signal listener (parse external signals)
- Daily performance reports

---

**Ready to deploy? Run the SCP commands from Step 1!** 🚀
