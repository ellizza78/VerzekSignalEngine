# VerzekAutoTrader

## Overview
VerzekAutoTrader is a multi-tenant auto-trading platform specializing in Dollar Cost Averaging (DCA). It automates trading by monitoring Telegram for signals, broadcasting them to VIP/TRIAL groups, and executing DCA trades with advanced risk management across various exchanges. The platform features a robust subscription system with tiered access, progressive take-profit, auto-stop logic, and comprehensive user/position management. The project's ambition is to provide a secure, reliable, and automated trading environment with a strong focus on user experience.

## User Preferences
- **Production Safety**: Enterprise-grade database with ACID compliance required
- **Security First**: No hard-coded secrets, all environment variables mandatory
- **Trade Capacity**: Default 50 concurrent positions per user (configurable)

## System Architecture
### UI/UX Decisions
The mobile application (React Native + Expo) uses a modern dark theme with Teal/Gold gradients (`#0A4A5C` → `#1B9AAA`, `#F9C74F`) for branding, managed via centralized constants. It features an onboarding modal and a compact UI with reduced padding for improved content visibility.

### Technical Implementations
- **Core Trading Modules**: Includes a DCA Engine, Safety Manager (auto-stop logic), DCA Orchestrator for signal execution, and a Position Tracker with target-based take-profit.
- **Multi-User Management**: Supports multi-tenancy with per-user DCA configurations, risk settings, exchange account management, symbol whitelists/blacklists, daily stats, and subscription plans (free/pro/vip).
- **Exchange Adapters**: Unified interface for Binance, Bybit, Phemex, and Kraken, supporting live and demo modes with secure API key loading.
- **Static IP Proxy Infrastructure**: Vultr-based WireGuard VPN mesh with HAProxy load balancing and Nginx SSL termination. All exchange API calls are routed through a static IP (45.76.90.149) for IP whitelisting, featuring HMAC SHA256 authentication and automatic failover.
- **Signal Broadcasting System**: Monitors Telegram for signals (Telethon Auto-Forwarder) with keyword detection and spam filtering. Signals are distributed to VIP/TRIAL Telegram groups and a protected `/api/signals` endpoint for the mobile app, with priority signals triggering auto-trading for PREMIUM users.
- **REST API Server (Flask)**: Provides JWT-authenticated endpoints for user, settings, subscription, exchange account, and position management. Includes rate limiting, 2FA, and audit logging.
- **Mobile Application (React Native + Expo)**: Features JWT authentication, secure storage, a dashboard for account overview and stats, API integration with the Flask backend, auth-based navigation, in-app FAQ, auto-polling for signal delivery, and comprehensive Help & Resources screen with links to exchange setup guides, video tutorials, security best practices, and support contact.
- **Security & Payments**: Multi-layer security with JWT authentication, server-side subscription validation, USDT TRC20 payment processing, automatic referral bonuses, HMAC signature verification, custom sliding puzzle CAPTCHA, and email verification. API keys are encrypted at rest.
- **Email Verification System**: Secure token-based email verification with SMTP integration, requiring users to verify email before connecting exchange accounts or trading.
- **Advanced Features**: Includes an AI Trade Assistant (GPT-4o-mini), Multi-Timeframe Analysis, Smart Order Routing, Social Trading, Advanced Charting, Auto-Optimization (ML-powered), AI Risk Scoring, Trading Journal, Real-Time Price Feed (WebSockets), Portfolio Rebalancing, Webhook Integration, Advanced Order Types, Push Notifications (FCM), Admin Dashboard, Automated Backups, and TronScan Integration.

### System Design Choices
- **Multi-tenancy**: Isolated configurations and strategies per user.
- **Microservices-like Components**: Separation of concerns into distinct modules.
- **Production Database**: SQLite with ACID compliance, WAL mode, and concurrent write safety.
- **Environment Variables**: All sensitive information is stored in environment variables; no hard-coded fallbacks.
- **24/7 Operation**: Designed for continuous uptime.
- **Subscription Model**: Free, Pro, and VIP tiers controlling feature access.
- **Authentication**: JWT-based with secure password hashing and token refresh.
- **Encryption**: Fernet (AES-128 CBC mode) for API keys, with master key stored in Replit Secrets.

### Recent Additions (October 2025)
- **Exchange Connection Documentation**: Complete user-facing guides for connecting Binance, Bybit, Phemex, and Kraken with step-by-step API key creation instructions, security best practices, IP whitelisting setup (45.76.90.149), troubleshooting guides, and video tutorial scripts. Deployed to Vultr at `/guides/exchange-setup.html`.
- **Help & Resources Screen**: In-app screen accessible from Settings providing users with 8 quick links to exchange setup guides, security documentation, FAQ, video tutorials (coming soon), troubleshooting help, and support contact. Features beautiful card-based UI matching app theme.
- **Connection Test Tool**: Python script (`tools/test_binance_connection.py`) for validating user API keys, testing Spot/Futures access, verifying permissions, and troubleshooting connection issues.

### Mobile App Version History
- **v1.0.0-1.0.2**: Early versions had OTA updates enabled, causing backend connection issues (app downloaded stale code from Expo servers)
- **v1.0.3**: Fixed backend connection by removing OTA updates (`updates.url`) and hardcoding API_BASE_URL to Replit bridge; confirmed working (duplicate registration detection functional)
- **v1.0.4**: Updated IP whitelisting display to show all 4 redundant IPs (45.76.90.149, 209.222.24.189, 45.76.158.152, 207.148.80.196); added Telegram support link (@VerzekSupport) for trial users; implemented secure "Remember Me" feature (stores only email in SecureStore, never passwords)

### Security & UX Features
- **Auto-Logout**: 3-minute inactivity timeout (INACTIVITY_TIMEOUT) for security, managed by useInactivityLogout hook
- **IP Whitelisting**: 4 whitelisted IPs for redundancy (primary: 45.76.90.149); supported by Binance, Bybit, Phemex; Kraken uses alternative security (master key + trading key model)
- **Subscription Tiers**: TRIAL (free, 4 days, contact @VerzekSupport for activation) → VIP ($50/month, signals only) → PREMIUM ($120/month, full auto-trading with DCA, progressive TP, multi-exchange)
- **Architecture**: Mobile App → Replit HTTPS Bridge (https://verzek-auto-trader.replit.app) → Vultr Backend (80.240.29.142:5000)

### Known Issues & Limitations
- **Email Service**: Email verification and password reset emails not sending (Vultr backend configuration issue, not mobile app)
- **Remember Me**: Not yet implemented (planned for future release)
- **Kraken IP Whitelisting**: Kraken Futures doesn't support IP whitelisting but uses master key + trading key security model instead

## External Dependencies
- **Telegram API**: For signal monitoring and broadcasting (`telethon` and `python-telegram-bot`).
- **Binance API**: For trading operations.
- **Bybit API**: For trading operations.
- **Phemex API**: For trading operations.
- **Kraken Futures API**: For trading operations.
- **Flask**: Python web framework for the REST API.
- **Requests**: Python HTTP library.
- **Schedule**: Python library for task scheduling.
- **PyJWT**: For JWT authentication.
- **Bcrypt**: For password hashing.
- **OpenAI API**: For AI Trade Assistant (GPT-4o-mini).
- **Firebase Cloud Messaging (FCM)**: For push notifications.
- **TronScan API**: For USDT TRC20 payment verification.
- **Microsoft 365 SMTP**: For sending emails (support@verzekinnovative.com).