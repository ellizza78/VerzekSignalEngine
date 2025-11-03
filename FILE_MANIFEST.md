# 📦 VERZEK AUTO TRADER - COMPLETE SOURCE CODE MANIFEST
## Master Archive - Backend API + Mobile App

**Version:** 1.1.5  
**Build Date:** November 3, 2025  
**Production Backend:** https://api.verzekinnovative.com  
**Archive Purpose:** Complete source backup for development, deployment, and maintenance

---

## 📂 PROJECT STRUCTURE OVERVIEW

```
VerzekAutoTrader/
├── Backend API (Python/Flask)          → Production trading engine
├── Mobile App (React Native/Expo)      → User-facing mobile application
├── Services & Modules                  → Core trading logic
├── Infrastructure                      → Deployment scripts & configs
└── Documentation                       → Setup guides & references
```

---

## 🔧 BACKEND API (Python/Flask)

### Core API Server
- **`api_server.py`** - Main Flask REST API server (port 8000)
  - JWT authentication endpoints
  - User management (CRUD operations)
  - Position tracking
  - Subscription management
  - Exchange account integration
  - Payment verification (USDT TRC20)
  - Referral system
  - CAPTCHA generation/validation
  - Health monitoring endpoint

### Authentication & Security
- **`modules/auth.py`** - JWT token generation, password hashing (bcrypt)
- **`modules/captcha.py`** - Custom CAPTCHA generation and verification
- **`utils/email_verification.py`** - Token-based email verification system
- **`services/email_service.py`** - Resend API email service (support@verzekinnovative.com)

### Database & Models
- **`database/db.py`** - SQLite database manager with ACID compliance
- **`database/models.py`** - SQLAlchemy ORM models (Users, Positions, Payments, etc.)
- **`database/migrations/`** - Database schema migration scripts

### Trading Core Modules
- **`modules/dca_engine.py`** - Dollar Cost Averaging trading engine
- **`modules/safety_manager.py`** - Risk management & position safety
- **`modules/dca_orchestrator.py`** - Coordinates DCA execution across exchanges
- **`modules/position_tracker.py`** - Real-time position monitoring & PnL tracking
- **`modules/signal_parser.py`** - Telegram signal parsing & validation
- **`modules/trade_executor.py`** - Order execution & exchange interface

### Exchange Adapters
- **`exchanges/binance_adapter.py`** - Binance Futures API integration
- **`exchanges/bybit_adapter.py`** - Bybit API integration
- **`exchanges/phemex_adapter.py`** - Phemex API integration
- **`exchanges/kraken_adapter.py`** - Kraken Futures API integration
- **`exchanges/base_adapter.py`** - Unified exchange interface

### Telegram Integration
- **`signal_forwarder.py`** - Monitors source channels, forwards to user groups
- **`telegram_listener.py`** - Listens for signals with keyword detection
- **`broadcast_bot.py`** - Broadcasts signals to VIP/TRIAL groups
- **`telethon_forwarder.py`** - Telethon-based message forwarder (alternative)

### Background Services
- **`price_feed_service.py`** - Real-time price updates via WebSocket
- **`scheduled_tasks.py`** - Cron-like task scheduler (position checks, etc.)
- **`advanced_orders_monitor.py`** - Monitors advanced order types (OCO, trailing stop)
- **`recurring_payments_service.py`** - Handles subscription renewals

### Utilities
- **`utils/logger.py`** - Centralized logging with rotation
- **`utils/user_manager.py`** - User CRUD operations
- **`utils/admin_dashboard.py`** - Admin analytics & monitoring
- **`utils/mailer.py`** - Email service wrapper

### Configuration
- **`requirements.txt`** - Python dependencies (Flask, SQLAlchemy, PyJWT, etc.)
- **`config/settings.py`** - Application settings & environment variables
- **`config/exchanges.json`** - Exchange API endpoints & configurations

### Deployment Files
- **`deploy_backend_to_vultr.sh`** - Automated Vultr VPS deployment script
- **`FINAL_VULTR_FIX.sh`** - Email service migration to Resend API
- **`vultr_infrastructure/nginx.conf`** - Nginx reverse proxy configuration
- **`vultr_infrastructure/api-server.service`** - Systemd service file for PM2
- **`vultr_infrastructure/ssl-setup.sh`** - Let's Encrypt SSL certificate setup

---

## 📱 MOBILE APP (React Native / Expo)

### Root Configuration
- **`mobile_app/VerzekApp/app.json`** - Expo app configuration (version, bundle ID, etc.)
- **`mobile_app/VerzekApp/eas.json`** - EAS Build configuration (Android/iOS profiles)
- **`mobile_app/VerzekApp/package.json`** - NPM dependencies
- **`mobile_app/VerzekApp/.gitignore`** - Git ignore rules

### Application Entry Point
- **`mobile_app/VerzekApp/App.js`** - Main app component with providers

### API Configuration
- **`src/config/api.js`** - API base URL and endpoint definitions
  ```javascript
  API_BASE_URL: 'https://api.verzekinnovative.com'
  ```

### Services & API Integration
- **`src/services/api.js`** - Axios HTTP client with interceptors
  - JWT token injection
  - Auto token refresh on 401
  - Request/response logging
  - Error handling

### Authentication Context
- **`src/context/AuthContext.js`** - Global authentication state
  - Login/logout functions
  - Token management (AsyncStorage)
  - User session persistence
  - Auto-logout on token expiry

### Remote Configuration
- **`src/context/RemoteConfigContext.js`** - Dynamic app configuration
  - Feature flags (A/B testing)
  - Service endpoint URLs
  - Force update control
  - Trading limits & UI messages

### Navigation
- **`src/navigation/AppNavigator.js`** - React Navigation setup
  - Auth stack (Login, Register, ForgotPassword)
  - Main tab navigator (Dashboard, Signals, Settings, Help)
  - Conditional rendering based on auth state

### Authentication Screens
- **`src/screens/RegisterScreen.js`** - User registration
  - Email, password, full name input
  - CAPTCHA integration
  - Referral code support
  - Email verification flow
- **`src/screens/LoginScreen.js`** - User login
  - Email/password authentication
  - CAPTCHA verification
  - Remember me functionality
  - Forgot password link
- **`src/screens/ForgotPasswordScreen.js`** - Password reset
- **`src/screens/EmailVerificationScreen.js`** - Email verification status

### Main Application Screens
- **`src/screens/DashboardScreen.js`** - Account overview
  - Wallet balance
  - Active positions count
  - Subscription status
  - Quick actions (add exchange, view signals)
  
- **`src/screens/SignalsFeedScreen.js`** - Live trading signals
  - Real-time signal updates (10s polling)
  - Signal parsing (symbol, direction, entry, targets, SL)
  - Live price feed from Binance
  - Signal details modal
  
- **`src/screens/PositionsScreen.js`** - Active positions
  - Position list with PnL
  - Open/close position actions
  - Position details
  
- **`src/screens/SettingsScreen.js`** - User preferences
  - Risk settings (max positions, leverage)
  - DCA settings (order count, safety orders)
  - Strategy settings (take profit, stop loss)
  - Exchange accounts management
  
- **`src/screens/ExchangeAccountsScreen.js`** - Exchange management
  - Add/remove exchange accounts
  - API key encryption
  - Balance display
  - Leverage configuration
  
- **`src/screens/SubscriptionScreen.js`** - Subscription plans
  - FREE, TRIAL, VIP, PREMIUM tiers
  - USDT TRC20 payment flow
  - Transaction hash verification
  - Referral code application

### Support & Help Screens
- **`src/screens/HelpResourcesScreen.js`** - Help resources hub
  - Exchange setup guides
  - Video tutorials (YouTube)
  - Security best practices
  - FAQ, troubleshooting, contact support
  
- **`src/screens/FAQScreen.js`** - Frequently asked questions
- **`src/screens/UserGuideScreen.js`** - App usage guide
- **`src/screens/SupportScreen.js`** - Contact support form

### Referral & Rewards
- **`src/screens/ReferralsScreen.js`** - Referral dashboard
  - Referral code display
  - Referral count & earnings
  - Payout request
  
- **`src/screens/RewardsScreen.js`** - Rewards & bonuses

### Profile
- **`src/screens/ProfileScreen.js`** - User profile management
  - Edit profile information
  - Change password
  - Account settings

### Components
- **`src/components/OnboardingModal.js`** - First-time user onboarding
- **`src/components/ForceUpdateModal.js`** - App update enforcement
- **`src/components/SliderCaptcha.js`** - Interactive CAPTCHA widget

### Hooks
- **`src/hooks/useInactivityLogout.js`** - Auto-logout on inactivity
- **`src/hooks/useAppUpdates.js`** - OTA update checking (Expo EAS Update)

### Constants
- **`src/constants/colors.js`** - Theme colors (teal/gold gradient)
- **`src/constants/exchangeConfig.js`** - Exchange-specific configurations

### Assets
- **`assets/vzk-logo.png`** - App icon & splash screen
- **`assets/adaptive-icon.png`** - Android adaptive icon

---

## 🔐 CONFIGURATION FILES

### Environment Variables (Backend)
**File:** `/root/api_server_env.sh` (on Vultr VPS)

**Required secrets:**
```bash
ENCRYPTION_MASTER_KEY=<Fernet key for API key encryption>
RESEND_API_KEY=<Resend API key for emails>
TELEGRAM_BOT_TOKEN=<Bot token for signal broadcasting>
BROADCAST_BOT_TOKEN=<Secondary bot token>
ADMIN_CHAT_ID=<Telegram admin chat ID>
API_BASE_URL=https://api.verzekinnovative.com
DOMAIN=api.verzekinnovative.com
APP_NAME="Verzek AutoTrader"
ADMIN_EMAIL=admin@verzekinnovative.com
SUPPORT_EMAIL=support@verzekinnovative.com
EMAIL_FROM=support@verzekinnovative.com
```

### Nginx Configuration (Vultr)
**File:** `vultr_infrastructure/nginx.conf`
- Reverse proxy from port 443 → 8000
- SSL certificate from Let's Encrypt
- CORS headers for mobile app
- Static file serving

### Systemd Service (Vultr)
**File:** `vultr_infrastructure/api-server.service`
- Auto-start on boot
- PM2 process manager
- Log rotation
- Restart on failure

---

## 🗄️ DATABASE SCHEMA

**Database:** SQLite with WAL mode (ACID compliant)  
**Location:** `database/verzek_trader.db`

### Tables:
1. **users** - User accounts
   - id, email, password_hash, full_name, email_verified
   - subscription_plan, subscription_expires_at
   - created_at, last_login
   
2. **exchange_accounts** - User exchange API keys (encrypted)
   - id, user_id, exchange_name, api_key_encrypted, api_secret_encrypted
   - is_demo, created_at
   
3. **positions** - Active trading positions
   - id, user_id, exchange, symbol, direction
   - entry_price, quantity, leverage
   - take_profit_levels, stop_loss
   - pnl, status, opened_at, closed_at
   
4. **payments** - Subscription payments
   - id, user_id, plan, amount, tx_hash
   - status, verified_at, created_at
   
5. **referrals** - Referral relationships
   - id, referrer_id, referred_user_id, bonus_amount
   - paid, created_at

6. **signals** - Trading signals archive
   - id, symbol, direction, entry, targets, stop_loss
   - leverage, timestamp, source_channel

7. **app_config** - Remote configuration
   - id, config_key, config_value, updated_at

---

## 📡 API ENDPOINTS

**Base URL:** `https://api.verzekinnovative.com`

### Authentication
- `POST /api/auth/register` - Create new account
- `POST /api/auth/login` - User login (returns JWT)
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user
- `GET /api/auth/check-verification` - Check email verification status
- `POST /api/auth/resend-verification` - Resend verification email
- `POST /api/auth/forgot-password` - Request password reset

### Users
- `GET /api/users/{userId}` - Get user details
- `PUT /api/users/{userId}/general` - Update general settings
- `PUT /api/users/{userId}/risk` - Update risk settings
- `PUT /api/users/{userId}/strategy` - Update strategy settings
- `PUT /api/users/{userId}/dca` - Update DCA settings
- `GET /api/users/{userId}/subscription` - Get subscription
- `POST /api/users/{userId}/subscription` - Activate subscription

### Exchange Accounts
- `POST /api/users/{userId}/exchanges` - Add exchange account
- `DELETE /api/users/{userId}/exchanges` - Remove exchange account
- `GET /api/users/{userId}/balance/{exchange}` - Get exchange balance
- `GET /api/users/{userId}/exchanges/{exchange}/leverage` - Get leverage
- `PUT /api/users/{userId}/exchanges/{exchange}/leverage` - Update leverage

### Positions
- `GET /api/positions` - Get all positions (admin)
- `GET /api/positions/{userId}` - Get user positions

### Signals
- `GET /api/signals` - Get recent trading signals

### Payments
- `POST /api/payments/create` - Create payment request
- `POST /api/payments/verify` - Verify USDT payment
- `GET /api/payments/{paymentId}` - Get payment status
- `GET /api/payments/my-payments` - Get user payment history

### Referrals
- `GET /api/referral/code` - Get user referral code
- `GET /api/referral/stats` - Get referral statistics
- `POST /api/referral/payout` - Request referral payout

### CAPTCHA
- `GET /api/captcha/generate` - Generate CAPTCHA challenge
- `POST /api/captcha/verify` - Verify CAPTCHA response

### System
- `GET /api/health` - Health check endpoint
- `GET /api/app-config` - Get remote configuration
- `GET /api/system/ip` - Get server IP address

---

## 🚀 DEPLOYMENT SCRIPTS

### Backend Deployment
- **`deploy_backend_to_vultr.sh`** - Complete backend deployment
  - Installs Python, PM2, Nginx
  - Configures SSL with Let's Encrypt
  - Sets up systemd service
  - Deploys API server to production
  
- **`FINAL_VULTR_FIX.sh`** - Email service migration
  - Removes old Gmail SMTP module
  - Installs Resend API service
  - Updates environment variables
  - Restarts API server

### Mobile App Deployment
- **EAS Build Commands:**
  ```bash
  # Android APK
  eas build --platform android --profile preview --non-interactive
  
  # iOS Build
  eas build --platform ios --profile preview --non-interactive
  
  # OTA Update (JavaScript only)
  eas update --branch preview --message "Update description"
  ```

---

## 📚 DOCUMENTATION FILES

### Setup Guides
- **`README.md`** - Project overview & quickstart
- **`replit.md`** - Technical architecture & user preferences
- **`START_HERE.md`** - Getting started guide
- **`QUICK_START_TESTING.md`** - Testing instructions
- **`MOBILE_APP_SETUP.md`** - Mobile app setup guide
- **`EXPO_QUICK_START.md`** - Expo development guide

### Deployment Guides
- **`VULTR_DEPLOYMENT_GUIDE.md`** - Vultr VPS deployment
- **`DEPLOYMENT_COMPLETE.md`** - Production deployment summary
- **`BUILD_INSTRUCTIONS.md`** - Mobile app build guide
- **`REBUILD_CHECKLIST.md`** - Pre-build verification checklist

### Feature Guides
- **`EMAIL_SETUP_README.md`** - Email service configuration
- **`PAYMENT_FLOW.md`** - Payment verification flow
- **`REFERRAL_SYSTEM_GUIDE.md`** - Referral system documentation
- **`TRADE_CAPACITY_GUIDE.md`** - Position capacity management
- **`IP_WHITELISTING_GUIDE.md`** - Static IP proxy setup

### Technical Documentation
- **`SECURITY_ARCHITECTURE.md`** - Security implementation
- **`DATABASE_TRANSACTION_CONTRACT.md`** - Database safety rules
- **`EXCHANGE_API_BINDING_GUIDE.md`** - Exchange integration guide
- **`TROUBLESHOOTING_GUIDE.md`** - Common issues & solutions

---

## 🔑 KEY TECHNOLOGIES

### Backend Stack
- **Python 3.10+** - Core programming language
- **Flask 2.x** - REST API framework
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Production database (WAL mode)
- **PyJWT** - JWT authentication
- **Bcrypt** - Password hashing
- **Cryptography (Fernet)** - API key encryption
- **Requests** - HTTP client for exchange APIs
- **Telethon / python-telegram-bot** - Telegram integration
- **APScheduler** - Background task scheduling
- **Gunicorn** - WSGI HTTP server
- **Nginx** - Reverse proxy & SSL termination

### Mobile App Stack
- **React Native** - Cross-platform mobile framework
- **Expo SDK** - React Native toolchain
- **React Navigation** - App navigation
- **Axios** - HTTP client
- **AsyncStorage** - Persistent storage
- **Expo Secure Store** - Encrypted storage for tokens
- **EAS Build** - Cloud build service
- **EAS Update** - Over-the-air updates

### Infrastructure
- **Vultr VPS** - Production server (Ubuntu 22.04)
  - IP: 80.240.29.142
  - Domain: api.verzekinnovative.com
- **Let's Encrypt** - Free SSL certificates
- **PM2** - Node.js process manager
- **Cloudflare DNS** - Domain management
- **Resend API** - Transactional email service

---

## 📋 FILES EXCLUDED FROM ZIP

The following files are excluded to keep the archive size manageable:

❌ **Development Dependencies:**
- `node_modules/` - NPM packages (install via `npm install`)
- `venv/` - Python virtual environment (create with `python -m venv venv`)
- `.expo/` - Expo build cache
- `__pycache__/` - Python bytecode cache
- `*.pyc` - Compiled Python files

❌ **Build Artifacts:**
- `android/` - Android build outputs
- `ios/` - iOS build outputs
- `.gradle/` - Gradle cache

❌ **Sensitive Data:**
- `.env` files with actual secrets
- `*.session` - Telethon session files
- `database/verzek_trader.db` - Production database (backup separately)

❌ **Logs & Temp Files:**
- `logs/*.log` - Application logs
- `*.tmp` - Temporary files
- `.DS_Store` - macOS system files

---

## 📥 INSTALLATION INSTRUCTIONS

### Backend Setup (Local Development)

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   - Copy `config/sample.env` to `.env`
   - Fill in all required secrets

3. **Initialize database:**
   ```bash
   python database/init_db.py
   ```

4. **Run development server:**
   ```bash
   python api_server.py
   ```

### Mobile App Setup

1. **Install dependencies:**
   ```bash
   cd mobile_app/VerzekApp
   npm install
   ```

2. **Update API URL (if needed):**
   - Edit `src/config/api.js`
   - Set `API_BASE_URL` to your backend

3. **Run Expo development server:**
   ```bash
   npx expo start
   ```

4. **Build APK:**
   ```bash
   eas build --platform android --profile preview
   ```

---

## 🎯 IMPORTANT NOTES

1. **API Base URL:** Always use `https://api.verzekinnovative.com` in production
2. **Secrets Management:** Never commit actual secrets to Git
3. **Database Backups:** Regularly backup `verzek_trader.db` from Vultr
4. **Email Service:** Uses Resend API (support@verzekinnovative.com)
5. **Payment Verification:** Manual USDT TRC20 verification via TronScan
6. **Mobile Updates:** Use EAS Update for JavaScript changes, rebuild APK for native changes

---

## 📞 SUPPORT & CONTACT

- **Production Backend:** https://api.verzekinnovative.com
- **Support Email:** support@verzekinnovative.com
- **Admin Email:** admin@verzekinnovative.com
- **Documentation:** See `/docs` folder in archive

---

**Archive Created:** November 3, 2025  
**Project:** VerzekAutoTrader v1.1.5  
**License:** Proprietary - All Rights Reserved
