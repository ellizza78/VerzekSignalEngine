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
- **Mobile Application (React Native + Expo)**: Features JWT authentication, secure storage, a dashboard for account overview and stats, API integration with the Flask backend, auth-based navigation, in-app FAQ, and auto-polling for signal delivery.
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