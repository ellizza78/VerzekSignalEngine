# VerzekAutoTrader

## Overview
VerzekAutoTrader is a multi-tenant auto-trading platform specializing in Dollar Cost Averaging (DCA). It automates trading by monitoring Telegram for signals, broadcasting them to VIP/TRIAL groups, and executing DCA trades with advanced risk management across various exchanges. The platform features a robust subscription system, offering tiered access to automation and features. Key capabilities include progressive take-profit, auto-stop logic, and comprehensive user and position management. The project aims to provide a secure and reliable trading environment, with a strong focus on automation and user experience.

## User Preferences
None specified yet.

## Recent Changes
**October 25, 2025 - Production Readiness & Security Hardening:**
- ✅ **JWT_SECRET_KEY secured** - Moved from hard-coded default to Replit Secrets (environment variable)
- ✅ **Production WSGI server** - Configured Gunicorn with gevent workers for production deployment
- ✅ **Telegram credentials secured** - Migrated hard-coded API credentials to environment variables in 3 files
- ✅ **Support bot conflict fixed** - Automatic webhook deletion before polling to prevent conflicts
- ✅ **Requirements cleaned** - Removed duplicates, added gunicorn and gevent dependencies
- ✅ **Health check endpoint** - Added /health for monitoring and load balancer health checks
- ✅ **Deployment configured** - VM deployment with proper build and run commands
- ✅ **Production documentation** - Created PRODUCTION_READINESS.md with comprehensive deployment guide
- ✅ **Environment template** - Created .env.template with all required and optional variables
- ✅ **Security audit passed** - All critical security issues resolved, production-ready

**October 25, 2025 - Vultr Infrastructure for Static IP Proxy:**
- ✅ **Automated deployment orchestrator** - Python script to deploy entire infrastructure across Vultr nodes
- ✅ **FastAPI mesh service** - HMAC-authenticated proxy with exchange whitelist enforcement
- ✅ **WireGuard VPN mesh** - Encrypted network connecting all nodes (10.10.0.0/24)
- ✅ **HAProxy load balancer** - Round-robin distribution with health checks and automatic failover
- ✅ **Nginx + Let's Encrypt SSL** - HTTPS reverse proxy with automatic certificate renewal
- ✅ **Static IP solution** - Frankfurt hub (45.76.90.149) for Binance API key whitelisting
- ✅ **Shell scripts** - Automated setup for WireGuard, HAProxy, Nginx, and FastAPI deployment
- ✅ **Comprehensive documentation** - README, deployment guide, quick start, and Replit configuration
- ✅ **No code changes needed** - Existing ProxyHelper already compatible with Vultr infrastructure
- ✅ **Security hardened** - HMAC signatures, HTTPS, UFW firewall, VPN encryption, exchange whitelist

**October 25, 2025 - SQLite Migration & Production Database (CRITICAL):**
- ✅ **SQLite database** - Migrated from JSON files to SQLite for ACID compliance and data integrity
- ✅ **Concurrent write safety** - Implemented BEGIN IMMEDIATE transactions with exponential backoff retry (5 attempts)
- ✅ **WAL mode** - Enabled Write-Ahead Logging for better concurrent read/write performance
- ✅ **Busy timeout** - 30-second timeout prevents database lock errors under production load
- ✅ **Error handling** - All write operations catch and handle OperationalError gracefully
- ✅ **Data migration** - Successfully migrated 2 existing users from users_v2.json to SQLite
- ✅ **Thread-safe connections** - Per-thread database connections for multi-threaded bot architecture
- ✅ **Production-safe** - Architect-verified: No data corruption or race condition risks
- ✅ **Support updated** - Changed to @VerzekSupport on Telegram for human support (bot removed)
- ✅ **Security hardened** - SUBSCRIPTION_SECRET_KEY and CAPTCHA_SECRET_KEY now required (no fallbacks)
- ⚠️ **BREAKING**: App will not start without SUBSCRIPTION_SECRET_KEY and CAPTCHA_SECRET_KEY in environment variables

## System Architecture
### UI/UX Decisions
The mobile application, built with React Native and Expo, features a modern dark theme with a consistent visual design using Teal/Gold gradients (`#0A4A5C` → `#1B9AAA`, `#F9C74F`) for branding. Colors are managed via centralized constants, and an onboarding modal provides critical setup instructions. The UI is designed to be compact, with reduced padding and margins across all screens for better content visibility.

### Technical Implementations
- **Core Trading Modules**: Manages Dollar Cost Averaging (DCA Engine), risk (Safety Manager, auto-stop logic), signal execution (DCA Orchestrator), and position tracking (Position Tracker) with a target-based take-profit system.
- **Multi-User Management**: Supports multi-tenancy with per-user DCA configurations, risk settings, exchange account management, symbol whitelists/blacklists, daily stats, and subscription plans (free/pro/vip).
- **Exchange Adapters**: Provides a unified interface for Binance, Bybit, Phemex, and Kraken, supporting both live and demo modes, with secure API key loading.
- **Static IP Proxy Infrastructure**: Vultr-based WireGuard VPN mesh with HAProxy load balancing and Nginx SSL termination. Routes all exchange API calls through a static IP (45.76.90.149) to satisfy Binance Futures IP whitelisting requirements. Features HMAC SHA256 authentication, automatic failover, and health monitoring. Alternative to Cloudflare Workers with greater control and reliability.
- **Signal Broadcasting System**: Monitors Telegram for signals (Telethon Auto-Forwarder) with keyword detection and spam filtering. Signals are distributed via dual-channel: VIP/TRIAL Telegram groups and `broadcast_log.txt` for mobile app access via a protected `/api/signals` endpoint. Priority signal detection triggers auto-trading for PREMIUM users.
- **REST API Server (Flask)**: Provides JWT-authenticated endpoints for user, settings, subscription, exchange account, position management, safety controls, and system status. Includes rate limiting, 2FA, and audit logging.
- **Mobile Application (React Native + Expo)**: Features JWT authentication, secure storage, a dashboard for account overview and stats, API integration with the Flask backend, and auth-based navigation. It includes an in-app FAQ, auto-polling for near-instant signal delivery, and a compact UI.
- **Security & Payments**: Multi-layer security with JWT authentication, server-side subscription validation, USDT TRC20 payment processing with admin verification, automatic referral bonuses, HMAC signature verification, custom sliding puzzle CAPTCHA, and email verification. All premium endpoints block expired/unauthorized users, and API keys are encrypted at rest.
- **Email Verification System**: Secure token-based email verification with SMTP integration, requiring users to verify their email before connecting exchange accounts or trading. Features 24-hour token expiration, rate-limited resend, and HTML emails with VZK branding.
- **Advanced Features**: Includes an AI Trade Assistant (GPT-4o-mini), Multi-Timeframe Analysis, Smart Order Routing, Social Trading, Advanced Charting, Auto-Optimization (ML-powered), AI Risk Scoring, Trading Journal, Real-Time Price Feed (WebSockets), Portfolio Rebalancing, Webhook Integration, Advanced Order Types, Push Notifications (FCM), Admin Dashboard, Automated Backups, and TronScan Integration.

### System Design Choices
- **Multi-tenancy**: Isolated configurations and strategies per user.
- **Microservices-like Components**: Separation of concerns into distinct modules.
- **Production Database**: SQLite with ACID compliance, WAL mode, and concurrent write safety (replaces JSON files).
- **Environment Variables**: For sensitive information like API tokens and secret keys (all required, no hard-coded fallbacks).
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
- **Cloudflare Workers**: For proxying exchange API calls with static IP.
- **OpenAI API**: For AI Trade Assistant (GPT-4o-mini).
- **Firebase Cloud Messaging (FCM)**: For push notifications.
- **TronScan API**: For USDT TRC20 payment verification.
- **Zoho Mail SMTP**: For sending emails (support@vezekinnovative.com).