# 📦 VerzekAutoTrader Complete Source Code Archive
## Download Package Summary

**Archive File:** `VerzekAutoTrader_Complete_v1.1.5.tar.gz`  
**Size:** 1.4 MB  
**Total Files:** 173  
**Created:** November 3, 2025

---

## 📂 WHAT'S INCLUDED

### ✅ Backend API (Python/Flask)
**Location:** `VerzekAutoTrader_v1.1.5/`

#### Core API Files:
- `api_server.py` - Main Flask REST API server (JWT auth, user management, positions, payments)
- `main.py` - Application entry point
- `requirements.txt` - Python dependencies

#### Trading Modules (`/modules/`):
- `dca_engine.py` - Dollar Cost Averaging engine
- `safety_manager.py` - Risk management & position safety
- `auth.py` - JWT authentication & password hashing
- `encryption_service.py` - Fernet encryption for API keys
- `signal_filter.py` - Signal parsing & validation
- `tronscan_client.py` - USDT TRC20 payment verification
- `ai_trade_assistant.py` - GPT-4o-mini trade analysis
- `advanced_orders.py` - OCO, trailing stop, limit orders
- `portfolio_rebalancer.py` - Auto-rebalancing logic
- `trading_journal.py` - Trade history & analytics
- `ai_risk_scoring.py` - ML-based risk assessment
- `auto_optimization.py` - Strategy parameter tuning
- `social_trading.py` - Copy trading features
- `realtime_price_feed.py` - WebSocket price updates
- `push_notifications.py` - FCM integration
- `webhook_handler.py` - External webhook support
- `backtesting_engine.py` - Historical strategy testing
- `advanced_analytics.py` - Performance metrics
- `custom_indicators.py` - Technical indicators
- `multi_timeframe_analysis.py` - Multi-TF signal analysis
- `smart_order_routing.py` - Optimal exchange routing
- `rate_limiter.py` - API rate limiting
- `two_factor_auth.py` - 2FA support
- `backup_system.py` - Automated backups
- `audit_logger.py` - Security audit logging

#### Services (`/services/`):
- `email_service.py` - Resend API email service (support@verzekinnovative.com)

#### Utilities (`/utils/`):
- `logger.py` - Centralized logging with rotation
- `user_manager.py` - User CRUD operations
- `admin_dashboard.py` - Admin analytics
- `mailer.py` - Email service wrapper
- `email_verification.py` - Token-based verification

#### Exchange Adapters (`/exchanges/`):
- `binance_adapter.py` - Binance Futures integration
- `bybit_adapter.py` - Bybit API
- `phemex_adapter.py` - Phemex API
- `kraken_adapter.py` - Kraken Futures
- `base_adapter.py` - Unified exchange interface

#### Database (`/database/`):
- `verzek.db` - SQLite production database
- `data.json` - JSON data backup
- `users.json.backup_*` - User backups
- `referrals.json` - Referral tracking
- `trades_log.csv` - Trade history

#### Telegram Bots:
- `signal_forwarder.py` - Signal channel monitoring
- `telegram_listener.py` - Keyword-based signal detection
- `broadcast_bot.py` - VIP/TRIAL group broadcasting
- `telethon_forwarder.py` - Telethon-based forwarder

#### Background Services:
- `price_feed_service.py` - Real-time price updates
- `scheduled_tasks.py` - Cron-like scheduler
- `advanced_orders_monitor.py` - Advanced order monitoring
- `recurring_payments_service.py` - Subscription renewals

#### Configuration (`/config/`):
- Various config files for exchanges, settings

#### Deployment (`/vultr_infrastructure/`):
- Nginx configuration
- Systemd service files
- SSL setup scripts
- Environment variable templates

#### Deployment Scripts:
- `deploy_backend_to_vultr.sh` - Automated Vultr deployment
- `FINAL_VULTR_FIX.sh` - Email service migration
- `vultr_deployment.sh` - Production deployment

---

### ✅ Mobile App (React Native/Expo)
**Location:** `VerzekAutoTrader_v1.1.5/mobile_app/VerzekApp/`

#### Root Config:
- `App.js` - Main app entry point
- `app.json` - Expo configuration (v1.1.5, versionCode 15)
- `eas.json` - EAS Build profiles (Android/iOS)
- `package.json` - NPM dependencies

#### Source Code (`/src/`):

**Configuration:**
- `config/api.js` - API base URL: `https://api.verzekinnovative.com`
- `constants/colors.js` - Theme colors (teal/gold)
- `constants/exchangeConfig.js` - Exchange settings

**Services:**
- `services/api.js` - Axios HTTP client with JWT interceptors

**Context Providers:**
- `context/AuthContext.js` - Global auth state & token management
- `context/RemoteConfigContext.js` - Dynamic feature flags & config

**Navigation:**
- `navigation/AppNavigator.js` - React Navigation setup

**Authentication Screens:**
- `screens/RegisterScreen.js` - **USER REGISTRATION LOGIC**
  - Email, password, full name input
  - CAPTCHA integration
  - Referral code support
  - API call: `POST /api/auth/register`
- `screens/LoginScreen.js` - User login with CAPTCHA
- `screens/ForgotPasswordScreen.js` - Password reset
- `screens/EmailVerificationScreen.js` - Email verification status

**Main Screens:**
- `screens/DashboardScreen.js` - Account overview (balance, positions, subscription)
- `screens/SignalsFeedScreen.js` - Live trading signals with real-time prices
- `screens/PositionsScreen.js` - Active positions with PnL
- `screens/SettingsScreen.js` - User preferences (risk, DCA, strategy)
- `screens/ExchangeAccountsScreen.js` - Manage exchange API keys
- `screens/ExchangeDetailScreen.js` - Exchange account details
- `screens/SubscriptionScreen.js` - Subscription plans & USDT payment
- `screens/ProfileScreen.js` - User profile management

**Support & Help:**
- `screens/HelpResourcesScreen.js` - Help hub & guides
- `screens/FAQScreen.js` - Frequently asked questions
- `screens/UserGuideScreen.js` - App usage guide
- `screens/GuideDetailScreen.js` - Detailed guide viewer
- `screens/SupportScreen.js` - Contact support

**Rewards:**
- `screens/ReferralsScreen.js` - Referral dashboard & code
- `screens/RewardsScreen.js` - Rewards tracking

**Components:**
- `components/OnboardingModal.js` - First-time user onboarding
- `components/ForceUpdateModal.js` - Mandatory app updates
- `components/SliderCaptcha.js` - Interactive CAPTCHA

**Hooks:**
- `hooks/useInactivityLogout.js` - Auto-logout timer
- `hooks/useAppUpdates.js` - OTA update checker

**Assets (`/assets/`):**
- `vzk-logo.png` - App icon & splash screen

---

### ✅ Documentation
**Location:** `VerzekAutoTrader_v1.1.5/` and `VerzekAutoTrader_v1.1.5/docs/`

**Essential Docs:**
- `FILE_MANIFEST.md` - **THIS DOCUMENT** - Complete file inventory
- `README.md` - Project overview
- `replit.md` - Technical architecture & user preferences

**Setup Guides:**
- `docs/START_HERE.md` - Getting started
- `docs/BUILD_INSTRUCTIONS.md` - Mobile app build guide
- `docs/REBUILD_CHECKLIST.md` - Pre-build verification

**Deployment:**
- `docs/VULTR_DEPLOYMENT_GUIDE.md` - Vultr VPS setup
- `docs/DEPLOYMENT_COMPLETE.md` - Production deployment summary

**Feature Guides:**
- `docs/EMAIL_SETUP_README.md` - Email service setup (Resend)
- `docs/PAYMENT_FLOW.md` - USDT payment verification
- `docs/REFERRAL_SYSTEM_GUIDE.md` - Referral system
- `docs/SECURITY_ARCHITECTURE.md` - Security implementation
- `docs/TROUBLESHOOTING_GUIDE.md` - Common issues & fixes

---

## 🔑 KEY FILES FOR COMMON TASKS

### 📝 Want to modify registration?
→ `mobile_app/VerzekApp/src/screens/RegisterScreen.js`  
→ `api_server.py` (search for `/api/auth/register`)

### 🔐 Want to change authentication logic?
→ `modules/auth.py` (backend JWT)  
→ `src/context/AuthContext.js` (mobile app)

### 📊 Want to add new API endpoints?
→ `api_server.py` (add Flask route)  
→ `src/services/api.js` (add API function)

### 💰 Want to modify payment flow?
→ `api_server.py` (search for `/api/payments/`)  
→ `src/screens/SubscriptionScreen.js` (mobile UI)

### 📡 Want to update signal logic?
→ `signal_forwarder.py` (Telegram monitoring)  
→ `modules/signal_filter.py` (parsing logic)  
→ `src/screens/SignalsFeedScreen.js` (mobile display)

### 🎨 Want to change app theme?
→ `src/constants/colors.js`

### 🌐 Want to change API URL?
→ `src/config/api.js` (change `API_BASE_URL`)

---

## 📥 HOW TO EXTRACT & USE

### Extract Archive:
```bash
tar -xzf VerzekAutoTrader_Complete_v1.1.5.tar.gz
cd VerzekAutoTrader_v1.1.5
```

### Backend Setup:
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables (create .env file)
# See FILE_MANIFEST.md for required secrets

# Run development server
python api_server.py
```

### Mobile App Setup:
```bash
cd mobile_app/VerzekApp

# Install dependencies
npm install

# Run Expo dev server
npx expo start

# Build Android APK
eas build --platform android --profile preview
```

---

## 🚀 PRODUCTION DEPLOYMENT

### Backend (Vultr VPS):
```bash
# Copy deployment script
scp deploy_backend_to_vultr.sh root@80.240.29.142:/root/

# SSH to server
ssh root@80.240.29.142

# Run deployment
bash deploy_backend_to_vultr.sh
```

### Mobile App:
```bash
# Android APK
cd mobile_app/VerzekApp
eas build --platform android --profile preview --non-interactive

# iOS Build
eas build --platform ios --profile preview --non-interactive

# OTA Update (JavaScript only)
eas update --branch preview --message "Update description"
```

---

## ⚠️ IMPORTANT NOTES

1. **Excluded from Archive:**
   - `node_modules/` - Install via `npm install`
   - `venv/` - Create via `python -m venv venv`
   - `.expo/` - Build cache (recreated automatically)
   - Production secrets & API keys

2. **Required Secrets (Backend):**
   - `ENCRYPTION_MASTER_KEY` - Fernet key for API encryption
   - `RESEND_API_KEY` - Email service API key
   - `TELEGRAM_BOT_TOKEN` - Telegram bot token
   - `ADMIN_CHAT_ID` - Admin Telegram chat ID

3. **Database:**
   - Included: Development database with schema
   - **NOT** included: Production data (backup separately)

4. **Production URLs:**
   - Backend API: `https://api.verzekinnovative.com`
   - Email: `support@verzekinnovative.com`
   - Server IP: `80.240.29.142`

---

## 📞 SUPPORT

**Email:** support@verzekinnovative.com  
**Documentation:** See `FILE_MANIFEST.md` for complete file reference

---

**Archive Version:** 1.1.5  
**Created:** November 3, 2025  
**Platform:** Multi-tenant Auto-Trading System
