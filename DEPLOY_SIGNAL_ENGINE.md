# VerzekSignalEngine v1.0 - Automated Deployment

## 🚀 Quick Deploy to Vultr

This document outlines the automated deployment of VerzekSignalEngine to your Vultr production server.

### Prerequisites
- Vultr server at 80.240.29.142
- Git repository with auto-pull configured
- Environment variables configured in Replit Secrets

### Automated Deployment Process

The deployment happens automatically via:
1. Code pushed to GitHub repository
2. Vultr systemd timer pulls changes every 2 minutes
3. Deployment script detects signal_engine changes
4. Auto-deploys VerzekSignalEngine to `/root/signal_engine`
5. Starts systemd service `verzek-signalengine`

---

## 📋 Manual Deployment (SSH to Vultr)

If you need to deploy manually, SSH to Vultr and run:

```bash
# Navigate to workspace
cd /root/workspace

# Pull latest changes
git pull origin main

# Run deployment
cd signal_engine
chmod +x deploy.sh
sudo ./deploy.sh
```

---

## 🔧 Environment Configuration

The deployment script automatically creates `/root/signal_engine/.env` with:

```bash
BACKEND_API_URL=https://api.verzekinnovative.com
HOUSE_ENGINE_TOKEN=<from Replit Secrets>
TELEGRAM_BOT_TOKEN=<from Replit Secrets>
TELEGRAM_VIP_CHAT_ID=<from Replit Secrets>
TELEGRAM_TRIAL_CHAT_ID=<from Replit Secrets>

# Bot Configuration
ENABLE_SCALPING_BOT=true
ENABLE_TREND_BOT=true
ENABLE_QFL_BOT=true
ENABLE_AI_BOT=true

TRADING_SYMBOLS=BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,XRPUSDT
```

---

## 📊 Service Management

### Check Status
```bash
sudo systemctl status verzek-signalengine
```

### View Live Logs
```bash
# Systemd logs
sudo journalctl -u verzek-signalengine -f

# Application logs
tail -f /root/signal_engine/logs/signal_engine.log
tail -f /root/signal_engine/logs/errors.log
```

### Restart Service
```bash
sudo systemctl restart verzek-signalengine
```

### Stop Service
```bash
sudo systemctl stop verzek-signalengine
```

---

## 🏥 Health Monitoring

Automatic health checks run every 5 minutes:
- Checks if service is running
- Monitors signal generation activity
- Auto-restarts if service crashes
- Sends Telegram alerts to admin

### Manual Health Check
```bash
cd /root/signal_engine
sudo ./health_check.sh
```

---

## 🔄 Signal Flow (After Deployment)

```
VerzekSignalEngine (4 Bots on Vultr)
├── Scalping Bot (15s) ──┐
├── Trend Bot (5m) ──────┤
├── QFL Bot (20s) ───────┤
└── AI/ML Bot (30s) ─────┘
         ↓
CCXT Market Data (Real-time)
         ↓
Signal Generation (Technical Analysis)
         ↓
Backend API (https://api.verzekinnovative.com/api/house-signals/ingest)
         ↓
    PostgreSQL
         ↓
    ┌────┴────┐
    ↓         ↓
Telegram    Mobile App
VIP/TRIAL   Push Notifications
```

---

## 🎯 Verification Steps

After deployment, verify the system is working:

### 1. Check Service is Running
```bash
sudo systemctl status verzek-signalengine
```
Expected: `active (running)`

### 2. Monitor Signal Generation
```bash
tail -f /root/signal_engine/logs/signal_engine.log
```
Expected: See bot startup messages and signal generation activity

### 3. Check Backend API Connectivity
```bash
grep "Signal sent to backend" /root/signal_engine/logs/signal_engine.log | tail -5
```
Expected: See successful API posts

### 4. Verify Telegram Broadcasting
Check your VIP and TRIAL Telegram groups for test messages

### 5. Check Database
```bash
# On Vultr server
psql -U postgres -d verzek_autotrader -c "SELECT id, source, symbol, confidence, created_at FROM house_signals ORDER BY created_at DESC LIMIT 5;"
```
Expected: See recent signals in database

---

## 🚨 Troubleshooting

### Service Won't Start
```bash
# Check logs
sudo journalctl -u verzek-signalengine -n 100

# Verify environment file exists
cat /root/signal_engine/.env

# Check Python dependencies
cd /root/signal_engine
pip3 install -r requirements.txt
```

### No Signals Being Generated
```bash
# Check bot configuration
cat /root/signal_engine/.env | grep ENABLE_

# Check CCXT connectivity
python3 /root/signal_engine/test_bot.py
```

### Signals Not Reaching Backend
```bash
# Test backend API directly
curl -X POST https://api.verzekinnovative.com/api/house-signals/ingest \
  -H "X-INTERNAL-TOKEN: $HOUSE_ENGINE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "TEST",
    "symbol": "BTCUSDT",
    "side": "LONG",
    "entry": 50000,
    "stop_loss": 49500,
    "take_profits": [50500, 51000],
    "timeframe": "M5",
    "confidence": 75
  }'
```

---

## 📈 Performance Monitoring

### View Signal Statistics
```bash
# Count signals by source
psql -U postgres -d verzek_autotrader -c "SELECT source, COUNT(*) FROM house_signals GROUP BY source;"

# Recent signal performance
psql -U postgres -d verzek_autotrader -c "SELECT source, symbol, confidence, status FROM house_signals ORDER BY created_at DESC LIMIT 10;"
```

### Check Resource Usage
```bash
# CPU and memory
ps aux | grep python.*main.py

# Disk space
df -h /root/signal_engine/logs/
```

---

## 🔐 Security Notes

- All API keys stored in environment variables (never in code)
- HOUSE_ENGINE_TOKEN protects backend API endpoint
- Systemd runs service with `NoNewPrivileges=true`
- Logs are rotated to prevent disk filling
- Health checks monitor for anomalies

---

## 📅 Maintenance

### Log Rotation
Logs automatically rotate at 10MB with 5 backups retained

### Backups
Old installations backed up to `/root/backups/signal_engine/` before updates

### Updates
1. Push code changes to GitHub
2. Wait 2 minutes for auto-deployment
3. Service automatically restarts with new code

---

## ✅ Post-Deployment Checklist

- [ ] Service status shows `active (running)`
- [ ] All 4 bots started successfully (check logs)
- [ ] Signals appearing in database
- [ ] Telegram groups receiving signals
- [ ] Mobile app receiving push notifications
- [ ] Health check passing
- [ ] Admin alerts working

---

**Deployment Date:** November 17, 2025  
**Version:** VerzekSignalEngine v1.0  
**Status:** Production Ready 🚀
