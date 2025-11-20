# VerzekAutoTrader

## Overview
VerzekAutoTrader is a multi-tenant auto-trading platform designed for Dollar Cost Averaging (DCA) strategies. It automates trading based on Telegram signals, broadcasting them to user groups, and executing DCA trades with advanced risk management across various exchanges. The platform includes a comprehensive subscription system with tiered access, progressive take-profit, auto-stop logic, and robust user/position management. The project aims to deliver a secure, reliable, and automated trading environment with a focus on user experience and sophisticated automated trading capabilities.

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
- **Exchange Adapters**: Unified interface for Binance, Bybit, Phemex, and Kraken, supporting live and demo trading, with all API calls routed through ProxyHelper for static IP support.
- **VerzekSignalEngine v2.0 - Master Fusion Engine**: An intelligent 4-bot signal generation system (Scalping, Trend, QFL, AI/ML) using CCXT market data and 25+ technical indicators. It includes a Fusion Engine for centralized signal filtering, cooldown management, trend bias filtering, rate limiting, opposite signal blocking, and bot priority weighting. Performance is tracked via SQLite, with daily reports sent to Telegram.
- **Signal Broadcasting System**: Uses the official Telegram Bot API for distributing signals from external VIP providers to user groups and the backend API.
- **REST API Server (Flask)**: Provides JWT-authenticated endpoints for users, settings, subscriptions, exchange accounts, positions, and signal ingestion, featuring rate limiting, 2FA, and audit logging.
- **Mobile Application (React Native + Expo)**: Features JWT authentication, secure storage, account dashboard, API integration, auth-based navigation, a live signal feed, and help resources. Includes a TrialBanner component for subscription countdown and an Exchange Balance Display.
- **Security & Payments**: Multi-layer security with JWT, server-side subscription validation, USDT TRC20 payment processing, automatic referral bonuses, HMAC signature verification, custom CAPTCHA, and email verification. API keys are encrypted at rest.
- **Email Verification System**: Secure token-based email verification using Resend API.
- **Signal Auto-Reversal System**: Automatically closes positions upon receiving opposite signals with Telegram notifications. Supports instant market-based reversal logic and position stacking.
- **Multi-TP System**: Implements a 5-level progressive take-profit system where bots generate TP1-TP5 with dynamic scaling for TP5 based on confidence. The system enforces sequential validation of TP hits and provides separate Telegram notifications for partial and final targets.
- **Advanced Features**: AI Trade Assistant (GPT-4o-mini), Multi-Timeframe Analysis, Smart Order Routing, Social Trading, Advanced Charting, ML-powered Auto-Optimization, AI Risk Scoring, Trading Journal, Real-Time Price Feed (WebSockets), Portfolio Rebalancing, Webhook Integration, Advanced Order Types, Push Notifications (FCM), Admin Dashboard, Automated Backups, and TronScan Integration.
- **Health Monitoring System**: Includes heartbeat monitoring, watchdog auto-restart, and Telegram admin alerts.
- **Dynamic Update Architecture**: Remote config system for instant updates, feature flags, OTA updates via Expo EAS Update, force update flows, and auto-refresh.

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
- **Telegram API**: For signal broadcasting and notifications.
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