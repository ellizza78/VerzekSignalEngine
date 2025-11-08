# 🚀 Verzek AutoTrader Backend

Production-ready auto-trading backend API with JWT authentication, paper trading engine, and Telegram broadcasting.

## 📋 Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Setup](#setup)
- [Deployment](#deployment)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)

---

## 🎯 Overview

VerzekAutoTrader is a multi-tenant auto-trading platform with:
- **Flask REST API** with JWT authentication
- **Paper trading engine** supporting 50 concurrent positions per user
- **Auto-trader worker** with TP ladder, SL, and risk management
- **Telegram broadcasting** to VIP/Trial groups
- **Daily reports** with performance analytics

**Production URL**: https://api.verzekinnovative.com

---

## ✨ Features

### Authentication & User Management
- JWT-based authentication (access + refresh tokens)
- Email verification system
- User settings (risk, strategy, DCA, preferences)
- Exchange account management (encrypted API keys)
- Subscription tiers (TRIAL, VIP, PREMIUM)

### Trading System
- **Paper Trading**: Default mode, supports 50 concurrent positions per user
- **Signal Management**: Create, broadcast, and track trading signals
- **Position Tracking**: Real-time PnL, TP ladder, SL automation
- **Auto-Trader Worker**: Executes trades for users with `auto_trade_enabled=true`

### Broadcasting & Reporting
- **Telegram Integration**: VIP + Trial group notifications
- **Daily Reports**: Automated 24h performance summaries
- **Real-time Events**: TP hits, SL triggers, signal cancellations

### Payment System
- USDT TRC-20 payment processing
- Subscription upgrades (VIP $50, PREMIUM $100)
- Transaction verification (admin-approved)

---

## 🏗️ Architecture

```
/backend
├── api_server.py           # Flask app entry point
├── worker.py               # Auto-trader worker daemon
├── db.py                   # Database configuration
├── models.py               # SQLAlchemy ORM models
├── broadcast.py            # Telegram broadcasting
├── auth_routes.py          # /api/auth/* endpoints
├── users_routes.py         # /api/users/* endpoints
├── signals_routes.py       # /api/signals endpoints
├── positions_routes.py     # /api/positions endpoints
├── payments_routes.py      # /api/payments/* endpoints
├── trading/
│   ├── paper_client.py     # Paper trading engine
│   └── executor.py         # Trade execution logic
├── reports/
│   └── daily_report.py     # Daily analytics
├── utils/
│   ├── security.py         # Password hashing, encryption
│   ├── logger.py           # Logging configuration
│   └── price_feed.py       # Real-time price fetching
└── deploy/
    ├── verzek_api.service  # Systemd service (API)
    ├── verzek_worker.service # Systemd service (Worker)
    └── deploy_to_vultr.sh  # Deployment automation
```

---

## 🛠️ Setup

### Local Development

1. **Clone repository**:
```bash
git clone https://github.com/ellizza78/VerzekBackend.git
cd VerzekBackend
```

2. **Install dependencies**:
```bash
pip3 install -r requirements.txt
```

3. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Run API server**:
```bash
python3 api_server.py
```

5. **Run worker** (in separate terminal):
```bash
python3 worker.py
```

---

## 🚀 Deployment (Vultr VPS)

### Prerequisites
- Vultr VPS (80.240.29.142)
- Domain: api.verzekinnovative.com
- Ubuntu 22.04 LTS
- Root SSH access

### Automated Deployment

SSH into Vultr VPS and run:

```bash
cd /root
git clone https://github.com/ellizza78/VerzekBackend.git api_server
cd api_server
chmod +x deploy/deploy_to_vultr.sh
./deploy/deploy_to_vultr.sh
```

This script will:
1. ✅ Install system dependencies
2. ✅ Clone/update repository
3. ✅ Install Python packages
4. ✅ Configure environment variables
5. ✅ Install systemd services
6. ✅ Setup Nginx reverse proxy + SSL
7. ✅ Configure daily report cron
8. ✅ Start API + Worker services

### Manual Deployment Steps

If you prefer manual deployment:

1. **Install dependencies**:
```bash
apt-get update
apt-get install -y python3-pip python3-venv nginx certbot python3-certbot-nginx
pip3 install -r requirements.txt
```

2. **Configure environment** in `/etc/environment`:
```bash
JWT_SECRET="VerzekAutoTraderKey2025"
DATABASE_URL="sqlite:////root/api_server/database/verzek.db"
TELEGRAM_BOT_TOKEN="YOUR_BOT_TOKEN"
# ... (see .env.example for all variables)
```

3. **Install systemd services**:
```bash
cp deploy/verzek_api.service /etc/systemd/system/
cp deploy/verzek_worker.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable verzek_api verzek_worker
systemctl start verzek_api verzek_worker
```

4. **Configure Nginx**:
```nginx
server {
    listen 80;
    server_name api.verzekinnovative.com;
    
    location / {
        proxy_pass http://127.0.0.1:8050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

5. **Setup SSL**:
```bash
certbot --nginx -d api.verzekinnovative.com
```

---

## 📡 API Endpoints

### Authentication
```
POST   /api/auth/register           - Register new user
POST   /api/auth/login              - User login
POST   /api/auth/refresh            - Refresh access token
GET    /api/auth/me                 - Get current user
POST   /api/auth/resend-verification - Resend email verification
POST   /api/auth/forgot-password    - Password reset request
```

### Users
```
GET    /api/users/<id>              - Get user details
PUT    /api/users/<id>/general      - Update general settings
PUT    /api/users/<id>/risk         - Update risk settings
PUT    /api/users/<id>/strategy     - Update strategy
PUT    /api/users/<id>/dca          - Update DCA settings
PUT    /api/users/<id>/preferences  - Update preferences
GET    /api/users/<id>/exchanges    - List exchanges
POST   /api/users/<id>/exchanges    - Add exchange
DELETE /api/users/<id>/exchanges    - Remove exchange
GET    /api/users/<id>/subscription - Get subscription
PUT    /api/users/<id>/subscription - Update subscription
```

### Signals
```
GET    /api/signals                 - List signals
POST   /api/signals                 - Create signal (broadcasts to Telegram)
POST   /api/signals/target-reached  - Mark TP target hit
POST   /api/signals/stop-loss       - Trigger stop loss
POST   /api/signals/cancel          - Cancel signal
```

### Positions
```
GET    /api/positions               - Get my positions
GET    /api/positions/<user_id>     - Get user positions
POST   /api/positions/close         - Manually close position
```

### Payments
```
POST   /api/payments/create         - Create payment request
POST   /api/payments/verify         - Verify payment
GET    /api/payments/<payment_id>   - Get payment status
GET    /api/payments/my-payments    - List my payments
POST   /api/payments/admin/verify/<id> - Admin verify payment
```

### System
```
GET    /api/health                  - Health check
GET    /api/ping                    - Ping endpoint
GET    /api/system/ip               - Get server IP
GET    /api/safety/status           - System status
GET    /api/reports/daily           - Daily trading report
```

---

## 🧪 Testing

### 1. Register & Login
```bash
# Register
ACCESS=$(curl -s -X POST https://api.verzekinnovative.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@vzk.com","password":"1234","full_name":"Test User"}' \
  | jq -r .access_token)

echo $ACCESS
```

### 2. Enable Auto-Trading
```bash
curl -s -X PUT https://api.verzekinnovative.com/api/users/1/general \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d '{"auto_trade_enabled": true}' | jq
```

### 3. Configure Risk Settings
```bash
curl -s -X PUT https://api.verzekinnovative.com/api/users/1/risk \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d '{"max_concurrent_trades": 50, "leverage": 10, "per_trade_usdt": 5}' | jq
```

### 4. Create a Signal
```bash
curl -s -X POST https://api.verzekinnovative.com/api/signals \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "side": "LONG",
    "entry": 70000,
    "tp": [70500, 71000, 72000],
    "sl": 69500,
    "confidence": 90,
    "trade_type": "FUTURES",
    "duration": "SHORT",
    "leverage": 10
  }' | jq
```

### 5. View Positions
```bash
curl -s -H "Authorization: Bearer $ACCESS" \
  https://api.verzekinnovative.com/api/positions | jq
```

### 6. Trigger Events
```bash
# Target Hit
curl -s -X POST https://api.verzekinnovative.com/api/signals/target-reached \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d '{"signal_id": 1, "target_index": 1}' | jq

# Stop Loss
curl -s -X POST https://api.verzekinnovative.com/api/signals/stop-loss \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d '{"signal_id": 1}' | jq

# Cancel
curl -s -X POST https://api.verzekinnovative.com/api/signals/cancel \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -d '{"signal_id": 1}' | jq
```

### 7. View Daily Report
```bash
curl -s -H "Authorization: Bearer $ACCESS" \
  https://api.verzekinnovative.com/api/reports/daily | jq
```

---

## 📊 Service Management

### Check Service Status
```bash
systemctl status verzek_api.service
systemctl status verzek_worker.service
```

### View Logs
```bash
# Real-time API logs
journalctl -u verzek_api.service -f

# Real-time Worker logs
journalctl -u verzek_worker.service -f

# View last 100 lines
journalctl -u verzek_api.service -n 100
```

### Restart Services
```bash
systemctl restart verzek_api.service
systemctl restart verzek_worker.service
```

---

## 🔐 Security

- All passwords hashed with bcrypt
- API keys encrypted with Fernet (AES-128 CBC)
- JWT tokens with expiration
- CORS configured for production domains
- Environment variables for sensitive data
- SSL/TLS via Let's Encrypt

---

## 📝 Environment Variables

Required variables in `/etc/environment`:

```bash
# Security
JWT_SECRET="VerzekAutoTraderKey2025"
API_KEY="Verzek2025AutoTrader"

# Database
DATABASE_URL="sqlite:////root/api_server/database/verzek.db"

# Exchange Mode
EXCHANGE_MODE="paper"  # paper | binance_testnet | binance_mainnet

# Telegram
TELEGRAM_BOT_TOKEN="8351047055:AAEqBFx5g0NJpEvUOCP_DCPD0VsGpEAjvRE"
TELEGRAM_VIP_CHAT_ID="-1002721581400"
TELEGRAM_TRIAL_CHAT_ID="-1002726167386"

# Worker
WORKER_POLL_SECONDS="10"

# Server
PORT="8050"
SERVER_IP="80.240.29.142"
FLASK_ENV="production"
```

---

## 🎯 Success Criteria

Backend is operational when:

1. ✅ `curl https://api.verzekinnovative.com/api/health` returns `ok: true`
2. ✅ Registration and login return JWT tokens
3. ✅ Signals broadcast to Telegram groups
4. ✅ Worker auto-executes trades for `auto_trade_enabled=true` users
5. ✅ Positions tracked with real-time PnL
6. ✅ Daily reports posted to Trial group at 23:00 UTC

---

## 📞 Support

- **Backend Repo**: https://github.com/ellizza78/VerzekBackend
- **Frontend Repo**: https://github.com/ellizza78/VerzekAutoTrader
- **Production API**: https://api.verzekinnovative.com
- **Email**: support@verzekinnovative.com

---

## 📜 License

Proprietary - © 2025 Verzek Innovative
