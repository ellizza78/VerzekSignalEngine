# VerzekAutoTrader

## Overview
VerzekAutoTrader is a multi-tenant auto-trading platform focused on Dollar Cost Averaging (DCA) strategies. It automates trading by processing Telegram signals, broadcasting them to user groups, and executing DCA trades with advanced risk management across multiple exchanges. The platform offers a comprehensive subscription system with tiered access, progressive take-profit, auto-stop logic, and robust user/position management. The project aims to provide a secure, reliable, and automated trading environment with a strong emphasis on user experience, enabling sophisticated automated trading strategies.

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
- **Per-User Exchange API Keys**: Premium users connect their own Exchange API keys, encrypted at rest using Fernet (AES-128) and stored in PostgreSQL.
- **Exchange Adapters**: Unified interface for Binance, Bybit, Phemex, and Kraken, supporting live and demo trading. All exchange API calls route through ProxyHelper for static IP support.
- **VerzekSignalEngine v1.0**: Independent 4-bot signal generation system (Scalping, Trend, QFL, AI/ML bots) using CCXT market data, 25+ technical indicators, async parallel execution, and Telegram broadcasting.
- **Signal Broadcasting System**: Uses official Telegram Bot API for distributing signals from external VIP providers to user groups and the backend API, avoiding user account monitoring.
- **REST API Server (Flask)**: Provides JWT-authenticated endpoints for users, settings, subscriptions, exchange accounts, positions, and signal ingestion. Includes rate limiting, 2FA, and audit logging.
- **Mobile Application (React Native + Expo)**: Features JWT authentication, secure storage, account dashboard, API integration, auth-based navigation, live signal feed, and help resources.
- **Security & Payments**: Multi-layer security with JWT, server-side subscription validation, USDT TRC20 payment processing, automatic referral bonuses, HMAC signature verification, custom CAPTCHA, and email verification. API keys are encrypted at rest.
- **Email Verification System**: Secure token-based email verification using Resend API.
- **Signal Auto-Reversal System**: Automatically closes positions upon receiving opposite signals within a configurable time window, with Telegram notifications.
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
- **Telegram API**: For signal broadcasting.
- **Binance API**: For trading operations and market data.
- **Bybit API**: For trading operations and market data.
- **Phemex API**: For trading operations.
- **Kraken Futures API**: For trading operations.
- **CCXT Library**: Unified exchange API for market data feed.
- **Flask**: Python web framework.
- **PyJWT**: For JWT authentication.
- **Bcrypt**: For password hashing.
- **OpenAI API**: For AI Trade Assistant (GPT-4o-mini).
- **Firebase Cloud Messaging (FCM)**: For push notifications.
- **TronScan API**: For USDT TRC20 payment verification.
- **Resend API**: For transactional emails.
### Signal Auto-Reversal System - IMPLEMENTED ✅
- **Smart Position Management**: Automatically detects and closes opposite direction positions when reversal signals arrive
- **Database Schema Updates**: Added `auto_reversal_enabled` (boolean, default: true) and `reversal_window_minutes` (integer, default: 15) columns to user_settings table
- **Reversal Detection Logic**: Implemented in `backend/trading/executor.py` with handle_signal_reversal() function
  - Normalizes BUY/SELL and LONG/SHORT formats for compatibility
  - Checks time window (configurable 1-60 minutes, default 15 minutes)
  - Closes opposite positions at current market price
  - Logs reversal events with detailed metadata
- **Telegram Notifications**: Broadcasts cancellation messages to VIP/TRIAL groups when reversals occur (e.g., "Signal Reversal: LONG → SHORT")
- **API Endpoint**: Created `/users/{id}/reversal` PUT endpoint for managing reversal settings
  - Requires JWT authentication and user ownership validation
  - Validates reversal_window_minutes (1-60 range)
  - Returns reversal settings in GET `/users/{id}` response
- **Example Flow**: 
  - 2:39 PM: BTCUSDT LONG signal arrives → Position opened
  - 2:42 PM: BTCUSDT SHORT signal arrives (3 minutes later, within 15-min window)
  - Auto-reversal: Closes LONG position, sends Telegram notification, opens SHORT position
- **Status**: LIVE - Feature ready for production use, fully tested with architect review
- **Date Implemented**: November 18, 2025
