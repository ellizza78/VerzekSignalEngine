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
- **Exchange Adapters**: Unified interface for Binance, Bybit, Phemex, and Kraken, supporting live and demo trading with secure API key handling.
- **Static IP Proxy Infrastructure**: Vultr-based WireGuard VPN mesh with HAProxy and Nginx for static IP (80.240.29.142) routing of all exchange API calls, featuring HMAC SHA256 authentication and automatic failover.
- **VerzekSignalEngine v1.0**: Independent 4-bot signal generation system with Scalping Bot (15s interval), Trend Bot (5m interval), QFL Bot (20s interval), and AI/ML Bot (30s interval). Features real-time CCXT market data, 25+ technical indicators, async parallel execution with uvloop, Telegram broadcasting, and backend API integration. Replaces old Telethon-based signal monitoring.
- **Signal Broadcasting System**: Uses python-telegram-bot library for distributing signals to VIP/TRIAL Telegram groups and protected API endpoint for the mobile app.
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
### House Signals System Deployment
- **Fixed critical metadata column bug**: Changed from `metadata = Column()` to `meta_data = Column('metadata', ...)` using SQLAlchemy column mapping to avoid reserved word collision without requiring database migration
- **Added backwards compatibility**: @property decorator allows both `signal.metadata` and `signal.meta_data` access patterns
- **Updated API serializers**: /api/house-signals/live and /api/house-signals/admin/signals now include metadata field in responses
- **Deployment Infrastructure**: Created deploy_all.sh for continuous deployment from Replit to Vultr production server
- **Verified End-to-End Flow**: VerzekSignalEngine (4 bots) → Backend API → PostgreSQL → Mobile App push notifications
- **Production Status**: Architecture approved by code review, ready for deployment