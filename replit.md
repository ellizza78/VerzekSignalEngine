# VerzekAutoTrader

## Overview
VerzekAutoTrader is a multi-tenant auto-trading platform specializing in Dollar Cost Averaging (DCA) strategies. It automates trading by monitoring Telegram signals, broadcasting them to user groups, and executing DCA trades with advanced risk management across multiple exchanges. The platform includes a comprehensive subscription system with tiered access, progressive take-profit, auto-stop logic, and robust user/position management. The project aims to deliver a secure, reliable, and automated trading environment with a focus on user experience, enabling sophisticated automated trading strategies.

## User Preferences
- **Production Safety**: Enterprise-grade PostgreSQL database with ACID compliance
- **Security First**: No hard-coded secrets, all environment variables mandatory
- **Trade Capacity**: Default 50 concurrent positions per user (configurable)
- **Build Process**: ALWAYS build Android APK from Replit Shell using `eas build` command (never use automated tools)
- **Dynamic Updates**: Use OTA updates (eas update) for JavaScript changes; remote config for feature flags and settings; only rebuild APK for native changes
- **Email Verification**: REQUIRED - All new users must verify email before login
- **Concurrency**: 4 Gunicorn workers with PostgreSQL for production-scale traffic

## System Architecture
### UI/UX Decisions
The mobile application (React Native + Expo) features a modern dark theme with Teal/Gold gradients, an onboarding modal, and a compact UI for optimal content visibility.

### Technical Implementations
- **Core Trading Modules**: DCA Engine, Safety Manager, DCA Orchestrator, and Position Tracker with target-based take-profit.
- **Multi-User Management**: Supports multi-tenancy with per-user configurations, risk settings, exchange account management, symbol whitelists/blacklists, and subscription plans.
- **Per-User Exchange API Keys**: Premium users connect their own Exchange API keys inside the mobile app. Keys are encrypted at rest using Fernet (AES-128) and stored in PostgreSQL. DCA Engine retrieves and decrypts keys per-user for trading.
- **Exchange Adapters**: Unified interface for Binance, Bybit, Phemex, and Kraken, supporting live and demo trading. All exchange API calls route through ProxyHelper for static IP support.
- **Static IP Proxy Infrastructure (Code Ready, Not Deployed)**: ProxyHelper routes all users' exchange API calls through shared static IP proxy. Two deployment options: (1) Vultr WireGuard VPN mesh with HAProxy/Nginx (80.240.29.142), or (2) Cloudflare Workers proxy. Features HMAC SHA256 authentication and automatic failover to direct connection.
- **VerzekSignalEngine v1.0**: Independent 4-bot signal generation system with Scalping Bot (15s interval), Trend Bot (5m interval), QFL Bot (20s interval), and AI/ML Bot (30s interval). Features real-time CCXT market data, 25+ technical indicators, async parallel execution with uvloop, Telegram broadcasting, and backend API integration.
- **Signal Broadcasting System - Bot-to-Bot Architecture**: Uses official Telegram Bot API (@VerzekSignalBridgeBot) for distributing signals. External VIP signal providers connect their bots to user's VIP group, broadcast bot listens and forwards to VIP/TRIAL groups and backend API. NO Telethon/Pyrogram user account monitoring (account ban risk eliminated).
- **REST API Server (Flask)**: Provides JWT-authenticated endpoints for managing users, settings, subscriptions, exchange accounts, positions, and receiving signals from VerzekSignalEngine. Includes rate limiting, 2FA, and audit logging.
- **Mobile Application (React Native + Expo)**: Features JWT authentication, secure storage, account dashboard, API integration, auth-based navigation, live signal feed, and help resources.
- **Security & Payments**: Multi-layer security with JWT authentication, server-side subscription validation, USDT TRC20 payment processing, automatic referral bonuses, HMAC signature verification, custom CAPTCHA, and email verification. API keys are encrypted at rest.
- **Email Verification System**: Secure token-based email verification using Resend API (support@verzekinnovative.com).
- **Advanced Features**: AI Trade Assistant (GPT-4o-mini), Multi-Timeframe Analysis, Smart Order Routing, Social Trading, Advanced Charting, ML-powered Auto-Optimization, AI Risk Scoring, Trading Journal, Real-Time Price Feed (WebSockets), Portfolio Rebalancing, Webhook Integration, Advanced Order Types, Push Notifications (FCM), Admin Dashboard, Automated Backups, and TronScan Integration.
- **Health Monitoring System**: Heartbeat monitoring, watchdog auto-restart, and Telegram admin alerts.
- **Dynamic Update Architecture**: Remote config system for instant updates, including feature flags, OTA updates via Expo EAS Update, force update flows, and auto-refresh.

### System Design Choices
- **Multi-tenancy**: Isolated configurations and strategies per user.
- **Microservices-like Components**: Separation of concerns into distinct modules.
- **Production Database**: PostgreSQL 14 with ACID compliance, full concurrency support, and connection pooling.
- **Environment Variables**: All sensitive information is stored in environment variables.
- **24/7 Operation**: Designed for continuous uptime with systemd auto-restart.
- **Subscription Model**: Tiered access (FREE/TRIAL, VIP, PREMIUM) with varying features.
- **Authentication**: JWT-based with secure password hashing and token refresh.
- **Encryption**: Fernet (AES-128 CBC mode) for API keys, with master key stored in Replit Secrets.
- **Scalability**: 4 Gunicorn workers handle concurrent traffic.

## External Dependencies
- **Telegram API**: For signal broadcasting via python-telegram-bot library.
- **Binance API**: For trading operations and market data (VerzekSignalEngine uses CCXT).
- **Bybit API**: For trading operations and market data (VerzekSignalEngine uses CCXT).
- **Phemex API**: For trading operations.
- **Kraken Futures API**: For trading operations.
- **CCXT Library**: Unified exchange API for VerzekSignalEngine market data feed.
- **Flask**: Python web framework.
- **Requests**: Python HTTP library.
- **Schedule**: Python library for task scheduling.
- **PyJWT**: For JWT authentication.
- **Bcrypt**: For password hashing.
- **OpenAI API**: For AI Trade Assistant (GPT-4o-mini).
- **Firebase Cloud Messaging (FCM)**: For push notifications.
- **TronScan API**: For USDT TRC20 payment verification.
- **Resend API**: For transactional emails.

## Project Structure
### VerzekSignalEngine (signal_engine/)
Independent signal generation system with 4 trading bots:
- **Scalping Bot**: RSI + Stochastic + MA bounce detection (0.8% TP, 0.5% SL)
- **Trend Bot**: MA alignment + MACD + price structure (3.0% TP, 1.5% SL)
- **QFL Bot**: Deep dip detection with base level analysis (return to base TP)
- **AI/ML Bot**: 15+ feature pattern recognition with adaptive TP/SL

Features: Real-time CCXT data, shared indicators library, async parallel execution, Telegram broadcasting, systemd services, comprehensive logging.

Integration: Sends signals to backend `/api/house-signals/ingest` endpoint with HOUSE_ENGINE_TOKEN authentication.

## Recent Changes (November 2025)
### Architecture Cleanup - Telethon/Pyrogram Removed ✅
- **Removed ALL Telethon/Pyrogram Files**: User's Telegram account was banned for using Telethon. Completely removed telethon_forwarder.py, signal_listener.py, setup_telethon.py, and all related files.
- **Bot-to-Bot Architecture Verified**: External VIP signal providers connect their bots directly to user's VIP group. Broadcast bot (ID: 8401236648) uses official Bot API only - NO user account monitoring.
- **Per-User Exchange API Keys Confirmed**: Mobile app allows premium users to connect their own exchange API keys. Backend encrypts keys using Fernet AES-128 and stores in PostgreSQL. DCA Engine decrypts per-user for trading.
- **Static IP Proxy READY FOR DEPLOYMENT**: ProxyHelper integrated in all 4 exchange clients (Binance, Bybit, Phemex, Kraken). Deployment options ready: (1) Cloudflare Workers (5min, FREE), (2) Vultr VPN (30min, dedicated IP 80.240.29.142). Run `./deploy_cloudflare_proxy.sh` or see `documentation/DEPLOY_STATIC_IP_PROXY.md`. System works without proxy (automatic fallback to direct connection).
- **APK Build Ready**: Mobile app configured for production. Command: `cd mobile_app/VerzekApp && eas build --platform android --profile production`
- **Date Updated**: November 17, 2025

### House Signals System - PRODUCTION DEPLOYED ✅
- **Fixed critical metadata column bug**: Changed from `metadata = Column()` to `meta_data = Column('metadata', JSON)` using SQLAlchemy column mapping to avoid reserved word collision
- **Resolved import path issues**: Fixed `from backend.models` to `from models` in utils/notifications.py for proper module resolution
- **Fixed systemd service**: Configured verzek_api.service to run Gunicorn with 4 workers (was running Python directly)
- **Deployment Infrastructure**: Auto-deployment via systemd timer checks GitHub every 2 minutes and deploys automatically
- **Production Server**: Vultr 80.240.29.142, port 8050, PostgreSQL database, 4 Gunicorn workers
- **Verified End-to-End Flow**: VerzekSignalEngine (4 bots) → /api/house-signals/ingest → PostgreSQL → Mobile App push notifications
- **Production Status**: LIVE - Successfully ingesting signals (signal_id=2 confirmed), ready for VerzekSignalEngine v1.0 integration
- **Date Deployed**: November 17, 2025

### Telegram Broadcasting Integration - DEPLOYED ✅
- **Integrated Telegram Broadcasting**: Added `broadcast_signal()` to `/api/house-signals/ingest` endpoint for automatic Telegram distribution
- **Bot Configuration**: Using @VerzekSignalBridgeBot (ID: 7516420499) for signal broadcasting
- **Target Groups**: VIP Group (VERZEK SUBSCRIBERS) + TRIAL Group (VERZEK TRIAL SIGNALS)
- **Tested End-to-End**: Successfully sent test signals to both Telegram groups
- **Signal Format**: Formatted messages with HTML markup for professional presentation
- **Date Deployed**: November 17, 2025

### VerzekSignalEngine v1.0 - DEPLOYMENT READY ✅
- **Created Auto-Deployment Scripts**: `signal_engine/deploy.sh`, `vultr_infrastructure/auto_deploy.sh`, `signal_engine/health_check.sh`
- **Systemd Services**: verzek-signalengine.service with health monitoring timer (5-minute checks)
- **Environment Configuration**: Production environment file with all required secrets from Replit
- **Health Monitoring**: Auto-restart on failure, Telegram admin alerts, comprehensive logging
- **Deployment Method**: Auto-deploys when changes pushed to GitHub (systemd timer polls every 2 minutes)
- **Status**: All deployment files created, ready for automatic deployment to Vultr
- **Date Prepared**: November 17, 2025

### Email Verification & Security Updates - DEPLOYED ✅
- **Token Expiration Fixed**: Changed verification and password reset tokens from 24 hours to 15 minutes for improved security
- **Email Link Format**: Updated email templates to show correct expiration time (15 minutes)
- **GET Endpoint Support**: Added GET handlers to `/api/auth/verify-email` and `/api/auth/reset-password` for email link clicks
- **Deep Link Redirects**: Email links redirect to app via `verzek-app://` custom URL scheme after token verification
- **Login Protection**: Email verification required before login (returns 403 if not verified)
- **Status**: LIVE - All authentication flows secured with shorter token expiration
- **Date Deployed**: November 17, 2025