# VerzekSignalEngine v1.0 - Setup Guide

## 📋 Overview
VerzekSignalEngine is a multi-bot trading signal generation system featuring:
- **4 Independent Strategy Bots**: Scalping, Trend-Following, QFL, AI/ML
- **Real-time Market Data**: CCXT integration with Binance & Bybit
- **Automated Broadcasting**: Telegram notifications to VIP/TRIAL groups
- **Backend Integration**: Sends signals to VerzekAutoTrader API

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd signal_engine
pip3 install -r requirements.txt
```

### 2. Configure Environment

```bash
cp config/.env.example config/.env
nano config/.env
```

**Required Environment Variables:**
```bash
# Backend API
BACKEND_API_URL=https://api.verzekinnovative.com
BACKEND_API_KEY=your_backend_api_key

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_VIP_GROUP_ID=-1001234567890
TELEGRAM_TRIAL_GROUP_ID=-1009876543210
TELEGRAM_ADMIN_GROUP_ID=-1005555555555
```

### 3. Test Run

```bash
python3 main.py
```

You should see:
```
🔥 VERZEK SIGNAL ENGINE v1.0 🔥
✅ Scalping Bot started (15s interval)
✅ Trend Bot started (5m interval)
✅ QFL Bot started (20s interval)
✅ AI/ML Bot started (30s interval)
```

---

## 🔧 Production Deployment (Systemd)

### 1. Copy Service File

```bash
sudo cp systemd/verzek-signalengine.service /etc/systemd/system/
```

### 2. Update Service File Paths

Edit `/etc/systemd/system/verzek-signalengine.service`:
```bash
sudo nano /etc/systemd/system/verzek-signalengine.service
```

Update `WorkingDirectory` to your installation path.

### 3. Enable and Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable verzek-signalengine
sudo systemctl start verzek-signalengine
```

### 4. Check Status

```bash
sudo systemctl status verzek-signalengine
sudo journalctl -u verzek-signalengine -f
```

### 5. View Logs

```bash
tail -f logs/signal_engine.log
tail -f logs/errors.log
```

---

## 📊 Bot Configuration

### Edit Watchlist

```bash
nano config/watchlist.json
```

Add/remove trading pairs for each bot:
```json
{
  "scalping_whitelist": ["BTC/USDT", "ETH/USDT"],
  "trend_whitelist": ["BTC/USDT", "ETH/USDT", "SOL/USDT"],
  "qfl_whitelist": ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
}
```

### Adjust Bot Settings

```bash
nano config/engine_settings.json
```

Configure parameters:
- Confidence thresholds
- Timeframes
- TP/SL ranges
- Enable/disable individual bots

---

## 🔗 Backend Integration

### Signal API Endpoint

Signals are automatically sent to:
```
POST https://api.verzekinnovative.com/api/signals
```

**Payload Format:**
```json
{
  "symbol": "BTCUSDT",
  "direction": "LONG",
  "entry_price": 51210.50,
  "tp_price": 51800.00,
  "sl_price": 50900.00,
  "strategy": "Scalping Bot v1",
  "timeframe": "5m",
  "confidence": 81.5,
  "version": "SE.v1.0"
}
```

### Backend Requirements

Your backend must:
1. Accept POST requests to `/api/signals`
2. Validate API key in `X-API-Key` header
3. Process and store signal data
4. Distribute to mobile app subscribers

---

## 📱 Telegram Broadcasting

### Setup Telegram Bot

1. Create bot with [@BotFather](https://t.me/BotFather)
2. Get bot token
3. Add bot to your groups
4. Get group IDs using this script:

```python
from telegram import Bot
import asyncio

async def get_updates():
    bot = Bot(token='YOUR_BOT_TOKEN')
    updates = await bot.get_updates()
    for update in updates:
        print(update)

asyncio.run(get_updates())
```

5. Update `.env` with group IDs

### Message Format

Signals are broadcast as:
```
🔥 VERZEK SIGNAL — Scalping Bot v1

PAIR: BTCUSDT
DIRECTION: 🟢 LONG
ENTRY: 51210.5000
TP: 51780.0000 (+1.11%)
SL: 50800.0000 (-0.80%)
TIMEFRAME: 5m
CONFIDENCE: 81%
EXCHANGE: Binance Futures
VERSION: SE.v1.0

⏰ 2025-11-16 12:34:56 UTC
```

---

## 🤖 Bot Strategies

### 1. Scalping Bot (15s interval)
- **Timeframes**: 1m, 5m, 15m
- **Strategy**: RSI oversold/overbought + Stochastic cross + MA bounce
- **TP/SL**: 0.8% / 0.5%
- **Best for**: Quick momentum trades

### 2. Trend Bot (5m interval)
- **Timeframes**: 1h, 4h
- **Strategy**: MA alignment + MACD cross + price structure
- **TP/SL**: 3.0% / 1.5%
- **Best for**: Strong directional moves

### 3. QFL Bot (20s interval)
- **Timeframes**: 15m, 1h
- **Strategy**: Base detection + crash recovery (6-15% drops)
- **TP**: Return to base level
- **Best for**: Catching dip bounces

### 4. AI/ML Bot (30s interval)
- **Timeframes**: 5m
- **Strategy**: ML pattern recognition (15 features)
- **TP/SL**: Adaptive based on confidence
- **Best for**: Complex pattern detection

---

## 📈 Monitoring

### Live Statistics

Stats are logged every 5 minutes:
```
📊 SIGNAL ENGINE STATISTICS
Signals Sent: 47
Signals Failed: 2
Success Rate: 95.9%
Telegram Messages: 141
```

### Health Checks

```bash
# Check if process is running
ps aux | grep main.py

# Check recent signals
tail -20 logs/signals/signals_20251116.log

# Check for errors
grep ERROR logs/signal_engine.log
```

---

## 🛠️ Troubleshooting

### Bot Not Starting
```bash
# Check Python version (requires 3.8+)
python3 --version

# Reinstall dependencies
pip3 install -r requirements.txt --force-reinstall

# Check logs
tail -50 logs/errors.log
```

### No Signals Generated
- Check watchlist symbols are valid
- Verify exchange connectivity
- Lower confidence thresholds in `engine_settings.json`
- Check market volatility (low volatility = fewer signals)

### Telegram Not Working
- Verify bot token is correct
- Ensure bot is added to groups
- Check group IDs are negative integers
- Test bot independently

### Backend Connection Fails
- Verify `BACKEND_API_URL` is accessible
- Check API key is valid
- Ensure `/api/signals` endpoint exists
- Check firewall/network settings

---

## 🔄 Updates and Maintenance

### Update Signal Engine
```bash
cd /root/VerzekSignalEngine
git pull origin main
sudo systemctl restart verzek-signalengine
```

### Backup Configuration
```bash
tar -czf backup_$(date +%Y%m%d).tar.gz config/ logs/
```

### Log Rotation

Logs automatically rotate at 10MB. Manual cleanup:
```bash
# Delete logs older than 30 days
find logs/ -name "*.log" -mtime +30 -delete
```

---

## 📞 Support

For issues or questions:
- **Email**: support@verzekinnovative.com
- **Telegram**: @VerzekSupport

---

## 📄 License

Copyright © 2025 Verzek Innovative. All rights reserved.
