# VerzekAutoTrader

## Overview
VerzekAutoTrader is a multi-tenant auto-trading platform specializing in Dollar Cost Averaging (DCA). It automates trading by monitoring Telegram for signals, broadcasting them to VIP/TRIAL groups, and executing DCA trades with advanced risk management across various exchanges. The platform features a robust subscription system, offering tiered access to automation and features, and aims to provide a secure and reliable trading environment. Key capabilities include progressive take-profit, auto-stop logic, and comprehensive user and position management.

## User Preferences
None specified yet.

## System Architecture

### UI/UX Decisions
The mobile application, built with React Native and Expo, features a modern dark theme. A consistent visual design uses Teal/Gold gradients (`#0A4A5C` → `#1B9AAA`, `#F9C74F`) for branding, with all colors managed via centralized constants. Specific elements like LONG/SHORT indicators also follow this color scheme. An onboarding modal provides critical setup instructions for new users.

### Technical Implementations
- **Core Trading Modules**:
    - **DCA Engine**: Manages Dollar Cost Averaging with configurable levels, multipliers, average entry, auto/partial take profit, stop loss, investment caps, and position tracking.
    - **Safety Manager**: Includes a Kill Switch, Circuit Breaker (configurable thresholds), Order Idempotency, and Trading Pause.
    - **DCA Orchestrator**: Coordinates trading, manages signal execution, and handles DCA triggers, supporting a demo mode.
    - **Position Tracker**: Persists and manages all trading positions.
- **Multi-User Management**: Supports multi-tenancy with per-user DCA configurations, risk settings, exchange account management, symbol whitelists/blacklists, daily stats, and subscription plans (free/pro/vip).
- **Exchange Adapters**: Provides a unified interface for Binance, Bybit, Phemex, and Coinexx, supporting both live and demo modes, with secure API key loading.
- **Signal Broadcasting System**:
    - **Telethon Auto-Forwarder**: Monitors Telegram for signals, with keyword detection and spam filtering, broadcasting to an internal bot.
    - **Broadcast Bot**: Receives and broadcasts signals to VIP/TRIAL Telegram groups, adding "New Signal Alert" headers.
- **REST API Server (Flask)**: Provides endpoints for authentication (JWT), user management, settings configuration (general mode, risk, strategy, DCA), subscription management, exchange account management, position retrieval, and safety controls (kill switch, pause, circuit breaker).
- **Mobile Application (React Native + Expo)**: Features JWT authentication, secure storage, a dashboard for account overview and stats, API integration with the Flask backend, and auth-based navigation.
- **Target-Based Take Profit System**: Parses numbered targets from Telegram signals, tracks positions, and executes progressive partial closes at each target level based on customizable split percentages. A background service (`target_monitor.py`) continuously monitors active positions.
- **Auto-Stop Logic System**: Detects "signal cancelled," "closed," or "stop loss hit" messages from Telegram, parses them, and automatically closes affected positions based on user settings (`auto_stop_on_cancel`). It calculates final PnL and updates position states.
- **Security & Payments**: Includes a license key security system, USDT TRC20 payment processing with admin verification, automatic referral bonuses, HMAC signature verification, and a CAPTCHA system for registration/login. A signal quality filter scores incoming signals for auto-trading based on risk/reward, SL presence, targets, and clarity. IP whitelisting instructions are provided for exchange API keys.

### System Design Choices
- **Multi-tenancy**: Isolated configurations and strategies per user.
- **Microservices-like Components**: Separation of concerns into distinct modules.
- **Persistent Local Storage**: JSON files in the `database/` folder for user data, positions, and safety state.
- **Environment Variables**: For sensitive information like API tokens.
- **24/7 Operation**: Configured for continuous uptime.
- **Subscription Model**: Free, Pro, and VIP tiers controlling feature access.
- **Authentication**: JWT-based with secure password hashing and token refresh.

## External Dependencies
- **Telegram API**: For signal monitoring and broadcasting (via `telethon` and `python-telegram-bot`).
- **Binance API**: For trading operations.
- **Bybit API**: For trading operations.
- **Phemex API**: For trading operations.
- **Coinexx API**: For trading operations.
- **Flask**: Python web framework for the REST API.
- **Requests**: Python HTTP library.
- **Schedule**: Python library for task scheduling.
- **PyJWT**: For JWT authentication.
- **Bcrypt**: For password hashing.
- **flask-simple-captcha**: For CAPTCHA implementation.

## Security Architecture

### API Key Protection
**CRITICAL**: API keys are NEVER stored in the mobile app. Here's how it works:

1. **Backend-Only Storage**: User API keys are stored ONLY on the backend server, encrypted at rest using AES-128 (Fernet)
2. **Mobile App**: Stores only account metadata (account_id, exchange name) - NO sensitive credentials
3. **Trade Execution**: Mobile app sends trade instructions with account_id → Backend retrieves encrypted keys → Decrypts in-memory → Executes trade → Discards keys
4. **Transport Security**: All communication via HTTPS/TLS with JWT authentication
5. **Access Control**: User isolation, token validation, role-based permissions

See `SECURITY_ARCHITECTURE.md` for complete details.

### Encryption System
- **Algorithm**: Fernet (AES-128 CBC mode)
- **Key Derivation**: PBKDF2 with 100,000 iterations
- **Master Key**: Stored in Replit Secrets (environment variables)
- **Storage**: `database/user_exchange_accounts.json` contains only encrypted credentials

## Recent Changes
- **2025-10-16**: Phase 4 Intelligent Trading & Social Copy Trading COMPLETE ✅
  - ✅ **Real-Time Price Feed**: WebSocket integration with Binance/Bybit, auto position updates
  - ✅ **Portfolio Rebalancing**: Auto-allocation management, drift detection, dry-run mode
  - ✅ **Advanced Analytics**: ML pattern detection, price prediction, win probability, sentiment analysis
  - ✅ **Social Trading**: Master/follower system, copy trading, automated replication
  - ✅ **Custom Strategies**: User-defined indicators, multi-condition strategies, backtesting
  - ✅ **API Endpoints**: 20 new endpoints for Phase 4 features

- **2025-10-16**: Phase 3 Advanced Trading Features & Risk Management COMPLETE ✅
  - ✅ **Advanced Order Types**: Trailing stop loss, OCO orders, automated execution
  - ✅ **Webhook Integration**: TradingView alerts, custom API signals, HMAC security
  - ✅ **Position Management**: Bulk close, emergency exit, position limits
  - ✅ **Advanced Orders Monitor**: Background service for real-time order tracking
  - ✅ **API Endpoints**: 13 new endpoints for advanced trading features

- **2025-10-16**: Phase 2 Admin Dashboard & Enhanced Features COMPLETE ✅
  - ✅ **Admin Dashboard**: Web interface + comprehensive backend API for monitoring
  - ✅ **Push Notifications**: Firebase Cloud Messaging with 10+ notification types
  - ✅ **Advanced Analytics**: Performance metrics, win/loss ratios, risk analysis, daily PnL
  - ✅ **API Endpoints**: 7 admin endpoints, 3 notification endpoints, 3 analytics endpoints

- **2025-10-16**: Phase 1 Security & Infrastructure COMPLETE ✅
  - ✅ **Rate Limiting**: Flask-Limiter with per-IP/user quotas (5/min auth, 100/min global)
  - ✅ **2FA/MFA System**: TOTP-based auth with QR codes, backup codes, mobile support
  - ✅ **Automated Backups**: Nightly snapshots with 30-day retention, encrypted archives
  - ✅ **TronScan Integration**: Automatic USDT TRC20 payment verification via blockchain API
  - ✅ **Audit Logging**: Comprehensive security event tracking (JSONL format)
  - ✅ **Security Alerts**: Real-time suspicious activity detection and alerting
  - ✅ **Encryption Service**: AES-128 (Fernet) for API keys and sensitive data at rest
  - ✅ **API Endpoints Added**: 2FA enrollment/verification, backup management, audit logs

- **2025-10-16**: Complete Referral & In-App Wallet System
  - ✅ **10% Recurring Commission**: Monthly referral bonuses for lifetime of subscription
  - ✅ **In-App Wallet**: Each user gets generated wallet for referral earnings
  - ✅ **Withdrawal System**: $10 minimum, $1 fee (credited to system wallet)
  - ✅ **Recurring Payments Service**: Background task processes monthly commissions daily
  - ✅ **Wallet Balance API**: GET /api/wallet/balance endpoint
  - ✅ **Updated Referral Stats**: Now includes wallet_balance and recurring_subscriptions count

- **2025-10-16**: Secure Payment & Subscription System
  - ✅ License Key Security: URL-safe base64 encoding with embedded expiry (survives restarts)
  - ✅ USDT TRC20 Payments: Manual admin verification workflow with fraud detection
  - ✅ Payment Flow: User→Admin Verification→Subscription Activation→License Generation
  - ✅ HMAC Signature Verification: MANDATORY X-Payment-Signature & X-Admin-Signature headers
  - ✅ Plan Pricing: PRO $29.99/mo, VIP $99.99/mo (USDT TRC20)
  - ✅ Persistent Storage: licenses.json, payments.json, referrals.json
  - ✅ Fraud Protection: Multi-layer validation, tamper-proof checksums