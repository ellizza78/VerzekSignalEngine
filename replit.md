# VerzekAutoTrader

## Overview
VerzekAutoTrader is a multi-tenant auto-trading platform designed for Dollar Cost Averaging (DCA) strategies. It automates trading by monitoring Telegram signals, broadcasting them to user groups, and executing DCA trades with advanced risk management across multiple exchanges. The platform includes a comprehensive subscription system with tiered access, progressive take-profit, auto-stop logic, and robust user/position management. The project aims to provide a secure, reliable, and automated trading environment with a strong focus on user experience and to enable users to participate in automated trading with sophisticated strategies.

## User Preferences
- **Production Safety**: Enterprise-grade PostgreSQL database with ACID compliance
- **Security First**: No hard-coded secrets, all environment variables mandatory
- **Trade Capacity**: Default 50 concurrent positions per user (configurable)
- **Build Process**: ALWAYS build Android APK from Replit Shell using `eas build` command (never use automated tools)
- **Dynamic Updates**: Use OTA updates (eas update) for JavaScript changes; remote config for feature flags and settings; only rebuild APK for native changes
- **Email Verification**: REQUIRED - All new users must verify email before login
- **Concurrency**: 4 Gunicorn workers with PostgreSQL for production-scale traffic

## Production URLs
- **Backend API**: https://verzekinnovative.com (Vultr VPS: 80.240.29.142)
- **Email Service**: support@verzekinnovative.com (Resend API verified domain)
- **Legacy Bridge** (deprecated): https://verzek-auto-trader.replit.app (no longer used in production)

## Recent Changes (November 2025)
### Complete Sync & Deployment Solution (COMPLETED - Nov 12, 2025)
**VPS Status:** Currently DOWN (502 Bad Gateway) - awaiting fresh deployment
**GitHub Status:** 392 commits ahead (198 backend + 194 mobile) - unpushed
**Critical Fixes Applied:**
- **requirements.txt**: Added missing resend==2.19.0 package (email verification dependency)
- **Deployment Script**: Production-ready with security hardening:
  - Removed hardcoded secrets (validates all required env vars exist)
  - Fixed pip installation error detection (set -o pipefail + exit code check)
  - Added worker service restart logic
  - Strengthened env var validation (grep -Eq '^KEY=.+' ensures non-empty values)
- **Documentation**: Created COMPLETE_SYNC_DEPLOY.md with:
  - GitHub sync instructions (both repos)
  - Automated VPS deployment script (copy-paste ready)
  - Post-deployment verification checklist
  - Complete rollback procedure
  - Troubleshooting guide
**Architect Approved:** All security checks passed, deployment script production-ready
**Next Action:** User must push to GitHub → Deploy to Vultr → Verify email functionality


### Email Verification & 4-Day Trial System (COMPLETED - Nov 11, 2025)
**Email Verification (PRODUCTION READY):**
- **Database Tokens**: VerificationToken model with persistent storage (production-safe for multi-worker deployment)
- **Registration Flow**: Users created with is_verified=False, verification email sent via Resend API
- **Login Protection**: Unverified users blocked with HTTP 403 + needs_verification flag
- **Mobile App Protection**: loadUser() checks is_verified on app start, auto-logout if false
- **Resend Verification**: Public endpoint (no auth required) accepts email parameter, prevents account enumeration
- **Mobile UI**: EmailVerificationScreen with resend functionality, navigation from login error
- **Backend Responses**: register/login/me endpoints return created_at field for trial tracking
- **Token Management**: 24-hour expiration, one-time use, automatic cleanup function

**4-Day Trial Expiration (PRODUCTION READY):**
- **Auto-Logout**: TRIAL users automatically logged out after 4 days from registration
- **Dual Enforcement**: Checked on app load (loadUser) AND login attempt
- **Token Cleanup**: Immediate removal of access/refresh tokens on expiration
- **Date Calculation**: `Math.floor((currentDate - createdDate) / (1000 * 60 * 60 * 24))` 
- **Trial Warning**: Day 3+ users see console warning about upcoming expiration
- **Error Messaging**: Clear user-facing error with upgrade prompt
- **Telegram Trial Link**: https://t.me/+JObDSp1HOuxmMWQ0 (updated in SubscriptionScreen)
- **Architect Approved**: All security checks passed, ready for OTA deployment
### VPS Deployment - PRODUCTION READY (COMPLETED - Nov 12, 2025)
- **Deployment Location**: /root/VerzekBackend on Vultr VPS (80.240.29.142)
- **SSL Certificate**: Installed via certbot for https://api.verzekinnovative.com
- **Deployment Method**: systemd service (verzek-api.service) - stable and reliable
- **Service Configuration**: 4 workers (production-scale), 120s timeout, auto-restart on failure
- **Environment File**: /root/api_server_env.sh (KEY=value format, no "export" keywords for systemd compatibility)
- **Database**: PostgreSQL 14 (verzek_db) - enterprise-grade, handles concurrent traffic
- **Database Credentials**: verzek_user with secure password, full privileges on verzek_db
- **Logging**: /root/api_server/logs/ directory with rotating file handlers
- **Status**: ✅ FULLY OPERATIONAL - Registration, login, email verification, concurrent requests all working
- **Concurrent Testing**: 5 simultaneous registrations completed successfully
- **Key Fixes Applied**:
  - Removed "export" keywords from environment file (systemd incompatibility)
  - Created /root/api_server/logs directory (logger requirement)
  - Migrated from SQLite to PostgreSQL for production scalability
  - Scaled from 1 to 4 workers after PostgreSQL migration
  - Generated valid Fernet encryption key for API key encryption

### Phase 3 Complete & GitHub Push (COMPLETED - Nov 11, 2025)
- **GitHub Repository**: Successfully pushed to https://github.com/ellizza78/VerzekBackend (8,188 objects, 211 MB)
- **Rate Limiting**: Thread-safe in-memory limiter (1 signal/symbol/minute) prevents spam, returns HTTP 429
- **Watchdog Monitoring**: 5-minute health checks with auto-restart and Telegram admin alerts
- **Enhanced Deployment**: Post-deploy endpoint testing (/api/ping, /api/health) with deployment history logging
- **Signal Detection**: Unified keywords.json schema for BUY/SELL/CLOSE/UPDATE signal parsing
- **API Endpoints**: Separated /api/ping (service info) and /api/health (ok:true with UTC timestamp)
- **Version**: 2.1 - Production Ready for Vultr VPS deployment

### Backend Refactor (COMPLETED - Nov 8, 2025)
- **Complete Backend Rebuild**: Modular architecture with Flask blueprints (auth, users, signals, positions, payments)
- **Database**: SQLAlchemy ORM with SQLite (Postgres-ready), proper relationships and indexing
- **Paper Trading Engine**: Supports 50 concurrent positions per user with real-time price feed
- **Auto-Trader Worker**: Daemon process for automatic trade execution with TP ladder and SL automation
- **Telegram Broadcasting**: Full integration for VIP/Trial groups with signal/event notifications
- **Daily Reports**: Automated 24h performance summaries with cron scheduling
- **Security Hardening**: Required ENCRYPTION_KEY env var, secrets in /root/api_server_env.sh (chmod 600)
- **Deployment Automation**: Complete systemd services and deployment script for Vultr VPS
- **Port Configuration**: API runs on port 8050, proxied through Nginx on port 443
- **Production Deployment**: Ready for deployment to Vultr VPS (80.240.29.142)

## System Architecture
### UI/UX Decisions
The mobile application (React Native + Expo) utilizes a modern dark theme with Teal/Gold gradients. It features an onboarding modal and a compact UI for optimal content visibility.

### Technical Implementations
- **Core Trading Modules**: Includes a DCA Engine, Safety Manager, DCA Orchestrator, and a Position Tracker with target-based take-profit.
- **Multi-User Management**: Supports multi-tenancy with per-user configurations, risk settings, exchange account management, symbol whitelists/blacklists, and subscription plans.
- **Exchange Adapters**: A unified interface supports Binance, Bybit, Phemex, and Kraken, offering both live and demo trading modes with secure API key handling.
- **Static IP Proxy Infrastructure**: A Vultr-based WireGuard VPN mesh with HAProxy and Nginx routes all exchange API calls through a static IP (45.76.90.149) for IP whitelisting, featuring HMAC SHA256 authentication and automatic failover.
- **Signal Broadcasting System**: Monitors Telegram for signals with keyword detection and spam filtering, distributing them to VIP/TRIAL Telegram groups and a protected API endpoint for the mobile app.
- **REST API Server (Flask)**: Provides JWT-authenticated endpoints for managing users, settings, subscriptions, exchange accounts, and positions, incorporating rate limiting, 2FA, and audit logging.
- **Mobile Application (React Native + Expo)**: Features JWT authentication, secure storage, a dashboard for account overview, API integration with the Flask backend, auth-based navigation, and comprehensive help resources.
- **Security & Payments**: Multi-layer security with JWT authentication, server-side subscription validation, USDT TRC20 payment processing, automatic referral bonuses, HMAC signature verification, custom CAPTCHA, and email verification. API keys are encrypted at rest.
- **Email Verification System**: Secure token-based email verification with Resend API (support@verzekinnovative.com), required before users can connect exchange accounts or trade.
- **Advanced Features**: Includes an AI Trade Assistant (GPT-4o-mini), Multi-Timeframe Analysis, Smart Order Routing, Social Trading, Advanced Charting, ML-powered Auto-Optimization, AI Risk Scoring, Trading Journal, Real-Time Price Feed (WebSockets), Portfolio Rebalancing, Webhook Integration, Advanced Order Types, Push Notifications (FCM), Admin Dashboard, Automated Backups, and TronScan Integration.
- **Health Monitoring System**: Deployed with heartbeat monitoring, watchdog auto-restart, and Telegram admin alerts for continuous operation and quick recovery from service interruptions.
- **Dynamic Update Architecture**: Remote config system enables instant updates without APK rebuilds. Features include: remote config endpoint (/api/app-config), feature flags for A/B testing, OTA updates via Expo EAS Update, force update flow for mandatory upgrades, and auto-refresh every 5 minutes. Config stored in SQLite with admin CLI tool for management.

### System Design Choices
- **Multi-tenancy**: Isolated configurations and strategies per user.
- **Microservices-like Components**: Separation of concerns into distinct modules.
- **Production Database**: PostgreSQL 14 with ACID compliance, full concurrency support, and connection pooling.
- **Environment Variables**: All sensitive information is stored in environment variables.
- **24/7 Operation**: Designed for continuous uptime with systemd auto-restart.
- **Subscription Model**: Tiered access (FREE/TRIAL, VIP, PREMIUM) with varying features.
- **Authentication**: JWT-based with secure password hashing and token refresh.
- **Encryption**: Fernet (AES-128 CBC mode) for API keys, with master key stored in Replit Secrets.
- **Scalability**: 4 Gunicorn workers handle concurrent traffic, tested with 5 simultaneous requests.

## External Dependencies
- **Telegram API**: For signal monitoring and broadcasting.
- **Binance API**: For trading operations.
- **Bybit API**: For trading operations.
- **Phemex API**: For trading operations.
- **Kraken Futures API**: For trading operations.
- **Flask**: Python web framework.
- **Requests**: Python HTTP library.
- **Schedule**: Python library for task scheduling.
- **PyJWT**: For JWT authentication.
- **Bcrypt**: For password hashing.
- **OpenAI API**: For AI Trade Assistant (GPT-4o-mini).
- **Firebase Cloud Messaging (FCM)**: For push notifications.
- **TronScan API**: For USDT TRC20 payment verification.
- **Resend API**: For transactional emails (support@verzekinnovative.com verified domain).