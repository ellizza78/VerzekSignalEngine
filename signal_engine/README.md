# 🔥 VerzekSignalEngine v1.0

**Multi-Bot Trading Signal Generation System**

VerzekSignalEngine is a sophisticated signal generation platform featuring 4 independent trading strategy bots that analyze markets in real-time and distribute high-quality trading signals.

---

## ✨ Features

### 🤖 Four Independent Strategy Bots

1. **Scalping Bot** (15s interval)
   - Fast momentum trades on 1m/5m/15m timeframes
   - RSI + Stochastic + MA bounce detection
   - TP: 0.8% | SL: 0.5%

2. **Trend-Following Bot** (5m interval)
   - Captures strong directional moves on 1h/4h
   - MA alignment + MACD cross + price structure
   - TP: 3.0% | SL: 1.5%

3. **QFL Bot** (20s interval)
   - Catches deep dips and crash recoveries
   - 6-15% drop detection + base level analysis
   - TP: Return to base | SL: 3% below entry

4. **AI/ML Bot** (30s interval)
   - Machine learning pattern recognition
   - 15+ feature analysis with confidence scoring
   - Adaptive TP/SL based on prediction confidence

### 🌐 Key Capabilities

- ✅ Real-time market data via CCXT (Binance & Bybit)
- ✅ 25+ technical indicators (RSI, MACD, Bollinger, ATR, etc.)
- ✅ Telegram broadcasting to VIP/TRIAL groups
- ✅ Backend API integration with VerzekAutoTrader
- ✅ Comprehensive logging and monitoring
- ✅ Production-ready systemd services
- ✅ Async parallel bot execution (uvloop)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip3
- Telegram Bot Token
- VerzekAutoTrader backend deployed

### Installation

```bash
# Clone repository
git clone https://github.com/your-repo/VerzekSignalEngine.git
cd VerzekSignalEngine/signal_engine

# Install dependencies
pip3 install -r requirements.txt

# Configure environment
cp config/.env.example config/.env
nano config/.env
```

### Configuration

Edit `config/.env`:

```bash
BACKEND_API_URL=https://api.verzekinnovative.com
BACKEND_API_KEY=your_api_key_here
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_VIP_GROUP_ID=-1001234567890
TELEGRAM_TRIAL_GROUP_ID=-1009876543210
TELEGRAM_ADMIN_GROUP_ID=-1005555555555
```

### Run

```bash
python3 main.py
```

Expected output:
```
🔥 VERZEK SIGNAL ENGINE v1.0 🔥
✅ Scalping Bot started (15s interval)
✅ Trend Bot started (5m interval)
✅ QFL Bot started (20s interval)
✅ AI/ML Bot started (30s interval)
🔥 All bots running. Press Ctrl+C to stop.
```

---

## 📁 Project Structure

```
signal_engine/
├── bots/
│   ├── scalper/          # Scalping strategy
│   │   └── scalping_bot.py
│   ├── trend/            # Trend-following strategy
│   │   └── trend_bot.py
│   ├── qfl/              # QFL strategy
│   │   └── qfl_bot.py
│   └── ai_ml/            # AI/ML strategy
│       └── ai_bot.py
├── engine/
│   └── base_strategy.py  # Base class for all bots
├── common/
│   └── indicators.py     # Shared technical indicators
├── data_feed/
│   └── live_data.py      # CCXT market data provider
├── services/
│   ├── dispatcher.py     # Backend API dispatcher
│   ├── scheduler.py      # Async bot scheduler
│   └── telegram_broadcaster.py  # Telegram notifications
├── config/
│   ├── .env.example      # Environment template
│   ├── watchlist.json    # Trading pairs
│   └── engine_settings.json  # Bot configurations
├── systemd/
│   └── verzek-signalengine.service  # Systemd service
├── logs/                 # Auto-generated logs
├── models/               # ML models (optional)
├── main.py               # Main entry point
├── requirements.txt      # Python dependencies
├── SETUP.md              # Detailed setup guide
├── INTEGRATION_GUIDE.md  # Backend integration
└── README.md             # This file
```

---

## 🔧 Configuration

### Watchlist (`config/watchlist.json`)

Define which symbols each bot should monitor:

```json
{
  "scalping_whitelist": ["BTC/USDT", "ETH/USDT", "BNB/USDT"],
  "trend_whitelist": ["BTC/USDT", "ETH/USDT", "SOL/USDT"],
  "qfl_whitelist": ["BTC/USDT", "ETH/USDT", "BNB/USDT"]
}
```

### Engine Settings (`config/engine_settings.json`)

Customize bot parameters:

```json
{
  "bots": {
    "scalping": {
      "enabled": true,
      "primary_timeframe": "5m",
      "confidence_threshold": 70
    },
    "trend": {
      "enabled": true,
      "primary_timeframe": "1h",
      "confidence_threshold": 75
    }
  }
}
```

---

## 📊 Signal Format

### API Payload

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
  "version": "SE.v1.0",
  "metadata": {
    "strategy_type": "scalping",
    "tp_pct": 0.8,
    "sl_pct": 0.5
  }
}
```

### Telegram Message

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

## 🔗 Integration

### With VerzekAutoTrader Backend

1. Add signal endpoint to backend
2. Generate API key
3. Configure `BACKEND_API_KEY` in `.env`
4. Deploy signal engine

See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) for detailed instructions.

---

## 📱 Deployment

### Development

```bash
python3 main.py
```

### Production (Systemd)

```bash
# Copy service file
sudo cp systemd/verzek-signalengine.service /etc/systemd/system/

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable verzek-signalengine
sudo systemctl start verzek-signalengine

# Check status
sudo systemctl status verzek-signalengine

# View logs
sudo journalctl -u verzek-signalengine -f
```

---

## 📈 Monitoring

### Statistics

Logged every 5 minutes:

```
📊 SIGNAL ENGINE STATISTICS
Signals Sent: 47
Signals Failed: 2
Success Rate: 95.9%
Telegram Messages: 141
```

### Log Files

- `logs/signal_engine.log` - Main application log
- `logs/errors.log` - Error tracking
- `logs/signals/` - Signal history by date
- `logs/systemd.log` - Systemd output

---

## 🛠️ Troubleshooting

### No Signals Generated

**Possible causes:**
- Low market volatility
- Confidence thresholds too high
- Watchlist symbols invalid

**Solutions:**
```bash
# Lower confidence thresholds
nano config/engine_settings.json

# Check market data connectivity
tail -f logs/signal_engine.log | grep "ERROR"

# Verify watchlist symbols
python3 -c "from data_feed.live_data import get_market_feed; feed = get_market_feed(); print(feed.get_ticker('BTC/USDT'))"
```

### Telegram Not Working

```bash
# Test bot token
python3 -c "from telegram import Bot; import asyncio; asyncio.run(Bot('YOUR_TOKEN').get_me())"

# Check group IDs
grep TELEGRAM config/.env
```

### Backend Connection Failed

```bash
# Test endpoint
curl -X POST https://api.verzekinnovative.com/api/signals \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_key" \
  -d '{"symbol":"BTCUSDT","direction":"LONG","entry_price":50000,"tp_price":51000,"sl_price":49500,"strategy":"Test","confidence":75}'
```

---

## 🔄 Updates

### Update Code

```bash
cd /root/VerzekSignalEngine
git pull origin main
sudo systemctl restart verzek-signalengine
```

### Backup Configuration

```bash
tar -czf backup_$(date +%Y%m%d).tar.gz config/ logs/
```

---

## 📖 Documentation

- [SETUP.md](SETUP.md) - Detailed setup instructions
- [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - Backend integration guide
- [API Documentation](https://api.verzekinnovative.com/docs) - Backend API reference

---

## 🎯 Roadmap

- [ ] Advanced ML model training pipeline
- [ ] Multi-exchange support (Kraken, Phemex)
- [ ] Custom indicator builder
- [ ] Web dashboard for monitoring
- [ ] Backtesting framework
- [ ] Signal performance analytics

---

## 📄 License

Copyright © 2025 Verzek Innovative. All rights reserved.

---

## 📞 Support

- **Email**: support@verzekinnovative.com
- **Telegram**: @VerzekSupport
- **Documentation**: https://docs.verzekinnovative.com

---

## 👨‍💻 Credits

**Developed by**: Verzek Innovative Team  
**Version**: 1.0.0  
**Release Date**: November 2025

---

**Happy Trading! 🚀**
