# VerzekAutoTrader

## Overview
VerzekAutoTrader is a multi-tenant auto-trading platform specializing in Dollar Cost Averaging (DCA). It automates trading by monitoring Telegram for signals, broadcasting them to VIP/TRIAL groups, and executing DCA trades with advanced risk management across various exchanges. The platform features a robust subscription system, offering tiered access to automation and features, and aims to provide a secure and reliable trading environment. Key capabilities include progressive take-profit, auto-stop logic, and comprehensive user and position management.

## User Preferences
None specified yet.

## Recent Changes
**October 23, 2025 - Real-Time Signal Delivery Implementation:**
- ✅ **Auto-polling system** - Mobile app automatically checks for new signals every 10 seconds (near-instant delivery)
- ✅ **Smart screen refresh** - Signals reload when navigating to screen or returning from background
- ✅ **AppState monitoring** - Automatically fetches latest signals when app comes to foreground
- ✅ **Memory leak prevention** - Polling intervals properly cleaned up on unmount/navigation
- ✅ **Silent updates** - Background refresh doesn't disrupt user experience (no loading spinners)
- ✅ **Critical UX fix** - Users no longer miss time-sensitive trading signals due to manual refresh requirement
- ✅ **Screen height optimization** - Reduced excessive padding across all mobile screens for better content visibility
- ✅ All changes architect-reviewed and production-ready

**October 23, 2025 - Dual-Channel Signal Distribution & Security Hardening:**
- ✅ **Dual-channel signal distribution** - Signals broadcast to BOTH VIP/TRIAL Telegram groups AND mobile app
- ✅ **Secured /api/signals endpoint** with JWT auth + subscription validation (blocks expired/unauthorized users)
- ✅ **Protected premium features** - DCA/auto-trade and exchange connections require active PREMIUM subscription
- ✅ **Server-side fraud protection** - Direct subscription activation blocked, payment verification required
- ✅ **Expired user handling** - Users can login but are auto-blocked from premium features with clear upgrade messages
- ✅ All signals logged to broadcast_log.txt for mobile app consumption via protected API
- ✅ Subscription tiers enforced: TRIAL (free/4 days) signals only, VIP ($50) signals only, PREMIUM ($120) signals + auto-trade
- ✅ Telegram groups active until end of month (then app-only)
- ✅ Production-ready security implementation

**October 23, 2025 - In-App FAQ & Auto-Logout Update:**
- ✅ In-app FAQ screen created with 5 sections (Getting Started, Subscription, Exchange Integration, Auto-Trading, Security)
- ✅ Interactive features: tap-to-copy wallet address & IP whitelist, deep links to email/Telegram support
- ✅ Accessible from Profile menu with ❓ FAQ icon
- ✅ Auto-logout timeout reduced from 5 minutes to 3 minutes max inactivity
- ✅ All changes production-ready

**October 23, 2025 - Customer Support FAQ PDF:**
- ✅ Comprehensive FAQ PDF generator created (generate_faq_pdf.py)
- ✅ 61 Q&A pairs across 10 sections covering all platform features
- ✅ Professional formatting with VZK teal/gold branding
- ✅ Sections: Getting Started, Account, Subscription, Payment, Exchange Integration, Auto-Trading, Security, Support, Referrals, Terms & Policies
- ✅ Includes contact info, table of contents, legal disclaimer
- ✅ Production-ready 19KB PDF for customer support distribution

**October 23, 2025 - Sliding Puzzle CAPTCHA Implementation:**
- ✅ Custom sliding puzzle CAPTCHA created with VZK logo (SliderCaptcha component)
- ✅ Drag-to-verify mechanism requiring 90% slider completion
- ✅ Integrated into both registration and login screens
- ✅ Automatic reset on failed attempts (key-based remount pattern)
- ✅ Visual feedback with teal/green branding and "✓ Verified!" confirmation
- ✅ All changes architect-reviewed and production-ready

**October 23, 2025 - User Feedback Implementation:**
- ✅ Concurrent trades: Text input instead of slider (user preference)
- ✅ Leverage settings: Moved to Settings > Capital Allocation (1-125x range)
- ✅ Auto-logout: Already implemented (5 min inactivity, works app-wide)
- ✅ Referral codes: Now auto-generated and displayed (VZK format)
- ✅ All changes architect-reviewed and production-ready

**October 22, 2025 - Phase 2 Features Completed:**
- ✅ Auto-logout after 5 minutes of inactivity implemented
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
- **Signal Broadcasting System**: Monitors Telegram for signals (Telethon Auto-Forwarder) with keyword detection and spam filtering. Signals are distributed via dual-channel: (1) VIP/TRIAL Telegram groups with Verzek-branded headers, and (2) broadcast_log.txt for mobile app access via protected /api/signals endpoint. Priority signal detection triggers auto-trading for PREMIUM users only.
- **REST API Server (Flask)**: Provides JWT-authenticated endpoints for user, settings, subscription, exchange account, position management, safety controls, and system status. Includes rate limiting, 2FA, and audit logging.
- **Mobile Application (React Native + Expo)**: Features JWT authentication, secure storage, a dashboard for account overview and stats, API integration with the Flask backend, and auth-based navigation.
- **Security & Payments**: Multi-layer security with JWT authentication, server-side subscription validation (prevents fraud/manipulation), USDT TRC20 payment processing with admin verification, automatic referral bonuses, HMAC signature verification, custom sliding puzzle CAPTCHA with VZK logo (drag-to-verify on mobile registration/login), email verification system (blocks trading until verified), and signal quality filter. All premium endpoints (@token_required + subscription checks) block expired/unauthorized users. API keys encrypted at rest. Direct subscription activation blocked - payment verification required.
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