# Phase 4 Environment Configuration

Complete environment variables required for VerzekAutoTrader production deployment.

## 🔧 Backend Environment Variables

Add these to `/root/api_server_env.sh` on Vultr VPS:

```bash
###############################################################################
# PHASE 4 - Production Environment Configuration
# VerzekAutoTrader Backend (Vultr VPS: 80.240.29.142)
###############################################################################

# ============================================================================
# SAFETY & TRADING MODE (CRITICAL)
# ============================================================================
LIVE_TRADING_ENABLED=false          # Set to 'true' to enable real trading
EXCHANGE_MODE=paper                  # 'paper' or 'live'
USE_TESTNET=true                     # Use exchange testnets (recommended)
EMERGENCY_STOP=false                 # Emergency kill switch

# ============================================================================
# DATABASE
# ============================================================================
DATABASE_URL=postgresql://user:password@localhost:5432/verzek_autotrader
PGHOST=localhost
PGPORT=5432
PGUSER=your_db_user
PGPASSWORD=your_db_password
PGDATABASE=verzek_autotrader

# ============================================================================
# JWT & SECURITY
# ============================================================================
JWT_SECRET=your_jwt_secret_key_here_change_this
ENCRYPTION_MASTER_KEY=your_fernet_encryption_key_here

# ============================================================================
# API & DOMAIN
# ============================================================================
DOMAIN=api.verzekinnovative.com
API_BASE_URL=https://api.verzekinnovative.com
SERVER_IP=80.240.29.142
DEEP_LINK_SCHEME=verzek-app://

# ============================================================================
# EMAIL (Resend API)
# ============================================================================
RESEND_API_KEY=your_resend_api_key_here
EMAIL_FROM=support@verzekinnovative.com
SUPPORT_EMAIL=support@verzekinnovative.com

# ============================================================================
# TELEGRAM BOT (Phase 3 & 4)
# ============================================================================
TELEGRAM_BOT_TOKEN=7516420499:AAHkf1VIt-uYZQ33eJLQRcF6Vnw-IJ8OLWE
ADMIN_CHAT_ID=572038606

# ============================================================================
# TELEGRAM GROUPS (Phase 4 - Signal Bridge)
# ============================================================================
# Configure these after creating your Telegram groups:
TELEGRAM_TRIAL_GROUP_ID=            # Trial group chat ID (use @username_to_id_bot)
TELEGRAM_VIP_GROUP_ID=               # VIP group chat ID
TELEGRAM_ADMIN_DEBUG_GROUP_ID=       # Admin debug group chat ID (optional)

# ============================================================================
# AUTHORIZED SIGNAL SOURCES (Phase 4)
# ============================================================================
# Comma-separated list of bot usernames that can send signals
AUTHORIZED_SIGNAL_BOT_USERNAMES=source_signal_bot,verzek_internal_bot

# Comma-separated list of admin user IDs that can send signals
AUTHORIZED_ADMIN_USER_IDS=572038606

# ============================================================================
# EXCHANGE API KEYS (OPTIONAL - Users provide their own)
# ============================================================================
# These are only for platform-level testing
# Real users provide their own exchange API keys via mobile app

# ============================================================================
# PAYMENT (TronScan API)
# ============================================================================
# USDT TRC20 payment verification
TRON_API_KEY=your_tronscan_api_key_here
TRON_WALLET_ADDRESS=your_tron_wallet_address_here

# ============================================================================
# REFERRAL SYSTEM
# ============================================================================
REFERRAL_BONUS_AMOUNT=10.0           # USDT bonus for referrals
MIN_REFERRAL_DEPOSIT=50.0            # Minimum deposit to qualify

# ============================================================================
# LOGGING
# ============================================================================
LOG_DIR=/root/api_server/logs
LOG_LEVEL=INFO

# ============================================================================
# APP METADATA
# ============================================================================
APP_NAME=VerzekAutoTrader
APP_VERSION=2.1.1

```

---

## 📱 Mobile App Environment (Optional)

For Expo development builds, create `.env` file in `mobile_app/VerzekApp/`:

```bash
# API Configuration (hardcoded in production, this is for dev builds only)
API_BASE_URL=https://api.verzekinnovative.com

# Deep linking
DEEP_LINK_SCHEME=verzek-app://

# Expo Project ID (already in app.json)
EXPO_PROJECT_ID=1874d70a-7769-4b99-a5c0-c9af8d5962ad

# Node environment
NODE_ENV=production
```

**Note:** Production APK builds use hardcoded values from `src/config/api.js`, not environment variables.

---

## 🤖 Telegram Bot Service

The bot reads from `/root/api_server_env.sh` automatically via systemd service.

Service file location: `/etc/systemd/system/verzek-signal-bot.service`

```ini
[Unit]
Description=VerzekAutoTrader Telegram Signal Bridge Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/VerzekBackend/backend
EnvironmentFile=/root/api_server_env.sh
ExecStart=/usr/bin/python3 /root/VerzekBackend/backend/telegram_signal_bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

---

## 🔐 Security Best Practices

### 1. Generate Secure Keys

```bash
# Generate JWT secret
openssl rand -hex 32

# Generate Fernet encryption key (for API key storage)
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 2. File Permissions

```bash
# Secure environment file
chmod 600 /root/api_server_env.sh
chown root:root /root/api_server_env.sh
```

### 3. Never Commit Secrets

Add to `.gitignore`:
```
api_server_env.sh
.env
*.key
*.pem
```

---

## 🚀 Deployment Checklist

### Backend (Vultr VPS)

```bash
# 1. Update environment file
nano /root/api_server_env.sh

# 2. Restart API service
systemctl restart verzek-api.service

# 3. Restart Telegram bot
systemctl restart verzek-signal-bot.service

# 4. Verify services
systemctl status verzek-api.service
systemctl status verzek-signal-bot.service

# 5. Test API
curl https://api.verzekinnovative.com/api/health
curl https://api.verzekinnovative.com/api/safety/status
```

### Mobile App

```bash
# 1. Navigate to app directory
cd mobile_app/VerzekApp

# 2. Build production APK
eas build -p android --profile production --clear-cache

# 3. Wait for build completion (~5-10 minutes)

# 4. Download APK
# EAS will provide download link

# 5. Test APK on device
# Install APK and test all features
```

---

## 📊 Verify Configuration

### Check Backend Safety Mode

```bash
curl https://api.verzekinnovative.com/api/safety/status
```

**Expected Response:**
```json
{
  "ok": true,
  "active_workers": 1,
  "mode": "paper",
  "status": "operational"
}
```

### Check Telegram Bot Status

```bash
journalctl -u verzek-signal-bot.service -n 50 --no-pager
```

**Expected Output:**
```
🤖 VerzekAutoTrader Signal Bridge Bot - Starting...
Mode: DRY-RUN
Bot Token: ✅ Set
Trial Group: Not configured (or group ID)
VIP Group: Not configured (or group ID)
Authorized Bots: source_signal_bot, verzek_internal_bot
Authorized Users: 572038606
Signal bridge bot started (python-telegram-bot)
```

---

## 🔄 Updating Configuration

### Add New Environment Variable

```bash
# 1. Edit environment file
nano /root/api_server_env.sh

# 2. Add new variable
NEW_VARIABLE=value

# 3. Restart services
systemctl restart verzek-api.service
systemctl restart verzek-signal-bot.service
```

### Update Telegram Group IDs

```bash
# 1. Create Telegram group
# 2. Add bot to group
# 3. Get group chat ID using @username_to_id_bot or @getidsbot
# 4. Update environment file
nano /root/api_server_env.sh
# Add: TELEGRAM_TRIAL_GROUP_ID=-1001234567890
# 5. Restart bot
systemctl restart verzek-signal-bot.service
```

---

## ⚠️ Safety Flags Explained

| Variable | Values | Default | Purpose |
|----------|--------|---------|---------|
| `LIVE_TRADING_ENABLED` | true/false | false | Master switch for live trading |
| `EXCHANGE_MODE` | paper/live | paper | Exchange API mode |
| `USE_TESTNET` | true/false | true | Use exchange testnets |
| `EMERGENCY_STOP` | true/false | false | Emergency kill switch |

**To enable live trading, ALL of these must be true:**
- `LIVE_TRADING_ENABLED=true`
- `EXCHANGE_MODE=live`
- `USE_TESTNET=false`
- `EMERGENCY_STOP=false`

**Current Recommended Setting (Phase 4):**
```bash
LIVE_TRADING_ENABLED=false
EXCHANGE_MODE=paper
USE_TESTNET=true
EMERGENCY_STOP=false
```

This keeps everything in **DRY-RUN mode** for safe testing.

---

## 📞 Support

For configuration issues:
1. Check service logs: `journalctl -u verzek-api.service -f`
2. Verify environment file: `cat /root/api_server_env.sh`
3. Test connectivity: `curl https://api.verzekinnovative.com/api/ping`

---

**Last Updated:** November 15, 2025  
**Version:** Phase 4 Configuration
