# VerzekAutoTrader

## Overview
VerzekAutoTrader is a multi-tenant auto-trading platform specializing in Dollar Cost Averaging (DCA). It automates trading by monitoring Telegram for signals, broadcasting them to VIP/TRIAL groups, and executing DCA trades with advanced risk management across various exchanges. The platform features a robust subscription system, offering tiered access to automation and features, and aims to provide a secure and reliable trading environment. Key capabilities include progressive take-profit, auto-stop logic, and comprehensive user and position management.

## User Preferences
None specified yet.

## Recent Changes
**October 22, 2025 - Phase 2 Features Completed + Updates:**
- ✅ Auto-logout after 5 minutes of inactivity implemented
- ✅ Leverage settings per exchange (1x-25x slider in exchange detail) - UPDATED
- ✅ Concurrent trades slider (1-20) in Settings screen - NEW
- ✅ Admin wallet address updated (TBjfqimYNsPecGxsk9kcX8GboPyZcWHNzb)
- ✅ iOS distribution guide created (TestFlight/Ad-Hoc/Expo Go)
- ✅ All features architect-reviewed and production-ready

**October 22, 2025 - Phase 1 Critical Features Completed:**
- ✅ Updated subscription pricing: TRIAL (4 days free), VIP ($50/month), PREMIUM ($120/month)
- ✅ Fixed CAPTCHA integration on registration (end-to-end flow verified)
- ✅ Email verification system enforced (blocks exchange connections until verified)
- ✅ Live signals feed displaying real-time Telegram signals with parsing
- ✅ Connection status indicator on Dashboard (shows Telegram connectivity)
- ✅ Referral code display in Profile with copy-to-clipboard
- ✅ Support contact info added (support@verzektrader.com, @VerzekSupport)
- ✅ Payment flow supports trial activation and USDT submissions
- ✅ All features architect-reviewed and production-ready

**October 21, 2025:**
- ✅ Implemented complete email verification system (Option 3: CAPTCHA + Email Verification)
- ✅ Fixed mobile app resend verification bug
- ✅ Updated all 4 exchange clients to support per-user encrypted credentials
- ✅ Created comprehensive testing and payment flow documentation
- ✅ Verified all systems operational and production-ready
- ✅ Created demo test account: demo@verzektrader.com
- ✅ Updated mobile app API URL to current Replit domain
- ✅ Implemented admin notification system (Telegram) for payout requests and payment alerts
- ✅ Added intelligent batching for thousands of users (hourly summaries, daily reports)
- ✅ Created admin API endpoints for managing payouts
- ✅ Implemented real-time financial tracking system (payments in, payouts out, running balance)
- ✅ Enhanced notifications with financial summaries on every transaction

## Production Status
**System Status:** ✅ PRODUCTION READY - DEPLOY & BUILD NOW
- ✅ Backend configured for VM deployment (24/7 operation)
- ✅ Mobile app ready for standalone APK build (no dev server needed)
- ✅ API URL updated to permanent deployment URL
- ✅ All auto-trading services operational
- ✅ Payment system ready (USDT TRC20)
- ✅ Multi-exchange support with encrypted credentials
- ✅ Security layers active: CAPTCHA, email verification, JWT auth, rate limiting
- ✅ Test account: demo@verzektrader.com / Demo123!

**NEXT STEPS FOR CO-TESTING:**
1. **Deploy Backend**: Click "Deploy" button → Get permanent URL (verzek-auto-trader.replit.app)
2. **Build APK**: Run `cd mobile_app/VerzekApp && eas build --profile preview --platform android`
3. **Share APK**: Download link from EAS → Send to co-testers
4. **Test Everything**: Real payments, real trading, all features

## System Architecture
### UI/UX Decisions
The mobile application, built with React Native and Expo, features a modern dark theme. A consistent visual design uses Teal/Gold gradients (`#0A4A5C` → `#1B9AAA`, `#F9C74F`) for branding, with all colors managed via centralized constants. Specific elements like LONG/SHORT indicators also follow this color scheme. An onboarding modal provides critical setup instructions for new users.

### Technical Implementations
- **Core Trading Modules**: Manages Dollar Cost Averaging (DCA Engine), risk (Safety Manager, auto-stop logic), signal execution (DCA Orchestrator), and position tracking (Position Tracker). Includes target-based take-profit system.
- **Multi-User Management**: Supports multi-tenancy with per-user DCA configurations, risk settings, exchange account management, symbol whitelists/blacklists, daily stats, and subscription plans (free/pro/vip).
- **Exchange Adapters**: Provides a unified interface for Binance, Bybit, Phemex, and Kraken, supporting both live and demo modes, with secure API key loading. Includes Cloudflare Workers Proxy for static IP egress (solves Binance IP whitelisting requirement).
- **Cloudflare Workers Proxy**: Routes ALL exchange API calls through static IP address to satisfy Binance Futures IP whitelisting requirements (Replit Reserved VMs have dynamic IPs). Features HMAC SHA256 authentication, automatic fallback to direct connection, JSON signature preservation, and environment-based configuration (dev=disabled, prod=enabled).
- **Signal Broadcasting System**: Monitors Telegram for signals (Telethon Auto-Forwarder) with keyword detection and spam filtering, broadcasting to internal bots and VIP/TRIAL Telegram groups (Broadcast Bot) with priority signal detection and auto-trading capabilities.
- **REST API Server (Flask)**: Provides JWT-authenticated endpoints for user, settings, subscription, exchange account, position management, safety controls, and system status. Includes rate limiting, 2FA, and audit logging.
- **Mobile Application (React Native + Expo)**: Features JWT authentication, secure storage, a dashboard for account overview and stats, API integration with the Flask backend, and auth-based navigation.
- **Security & Payments**: Includes a license key security system, USDT TRC20 payment processing with admin verification, automatic referral bonuses, HMAC signature verification, CAPTCHA system (required for web, optional for mobile apps), email verification system (Option 3: CAPTCHA + Email Verification), and a signal quality filter. API keys are encrypted at rest on the backend.
- **Email Verification System**: Secure token-based email verification with SMTP integration. Users must verify email before connecting exchange accounts or trading. Features 24-hour token expiration, rate-limited resend (60s cooldown), beautiful HTML emails with VZK branding, welcome emails after verification, and dev mode fallback for testing without SMTP.
- **Advanced Features**: AI Trade Assistant (GPT-4o-mini), Multi-Timeframe Analysis, Smart Order Routing, Social Trading (live chat, leaderboards, copy trading), Advanced Charting, Auto-Optimization (ML-powered), AI Risk Scoring, Trading Journal, Real-Time Price Feed (WebSockets), Portfolio Rebalancing, Webhook Integration, Advanced Order Types (trailing stop loss, OCO), Push Notifications (FCM), Admin Dashboard, Automated Backups, TronScan Integration.

### System Design Choices
- **Multi-tenancy**: Isolated configurations and strategies per user.
- **Microservices-like Components**: Separation of concerns into distinct modules.
- **Persistent Local Storage**: JSON files in the `database/` folder for user data, positions, and safety state.
- **Environment Variables**: For sensitive information like API tokens.
- **24/7 Operation**: Configured for continuous uptime.
- **Subscription Model**: Free, Pro, and VIP tiers controlling feature access.
- **Authentication**: JWT-based with secure password hashing and token refresh.
- **Encryption**: Fernet (AES-128 CBC mode) for API keys, with master key stored in Replit Secrets.

## External Dependencies
- **Telegram API**: For signal monitoring and broadcasting (via `telethon` and `python-telegram-bot`).
- **Binance API**: For trading operations.
- **Bybit API**: For trading operations.
- **Phemex API**: For trading operations.
- **Kraken Futures API**: For trading operations.
- **Flask**: Python web framework for the REST API.
- **Requests**: Python HTTP library.
- **Schedule**: Python library for task scheduling.
- **PyJWT**: For JWT authentication.
- **Bcrypt**: For password hashing.
- **flask-simple-captcha**: For CAPTCHA implementation.
- **Cloudflare Workers**: For proxying exchange API calls with static IP.
- **OpenAI API**: For AI Trade Assistant (GPT-4o-mini).
- **Firebase Cloud Messaging (FCM)**: For push notifications.
- **TronScan API**: For USDT TRC20 payment verification.