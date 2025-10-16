# VerzekAutoTrader

## Overview
VerzekAutoTrader is a multi-tenant auto-trading platform specializing in Dollar Cost Averaging (DCA). It automates trading by monitoring Telegram for signals, broadcasting them to VIP/TRIAL groups, and executing DCA trades with advanced risk management across various exchanges. The platform features a robust subscription system, offering tiered access to automation and features, and aims to provide a secure and reliable trading environment. Key capabilities include progressive take-profit, auto-stop logic, and comprehensive user and position management.

## User Preferences
None specified yet.

## System Architecture

### UI/UX Decisions
The mobile application, built with React Native and Expo, features a modern dark theme. A consistent visual design uses Teal/Gold gradients (`#0A4A5C` → `#1B9AAA`, `#F9C74F`) for branding, with all colors managed via centralized constants. Specific elements like LONG/SHORT indicators also follow this color scheme. An onboarding modal provides critical setup instructions for new users.

### Technical Implementations
- **Core Trading Modules**:
    - **DCA Engine**: Manages Dollar Cost Averaging with configurable levels, multipliers, average entry, auto/partial take profit, stop loss, investment caps, and position tracking.
    - **Safety Manager**: Includes a Kill Switch, Circuit Breaker (configurable thresholds), Order Idempotency, and Trading Pause.
    - **DCA Orchestrator**: Coordinates trading, manages signal execution, and handles DCA triggers, supporting a demo mode.
    - **Position Tracker**: Persists and manages all trading positions.
- **Multi-User Management**: Supports multi-tenancy with per-user DCA configurations, risk settings, exchange account management, symbol whitelists/blacklists, daily stats, and subscription plans (free/pro/vip).
- **Exchange Adapters**: Provides a unified interface for Binance, Bybit, Phemex, and Coinexx, supporting both live and demo modes, with secure API key loading.
- **Signal Broadcasting System**:
    - **Telethon Auto-Forwarder**: Monitors Telegram for signals, with keyword detection and spam filtering, broadcasting to an internal bot.
    - **Broadcast Bot**: Receives and broadcasts signals to VIP/TRIAL Telegram groups, adding "New Signal Alert" headers.
- **REST API Server (Flask)**: Provides endpoints for authentication (JWT), user management, settings configuration (general mode, risk, strategy, DCA), subscription management, exchange account management, position retrieval, and safety controls (kill switch, pause, circuit breaker).
- **Mobile Application (React Native + Expo)**: Features JWT authentication, secure storage, a dashboard for account overview and stats, API integration with the Flask backend, and auth-based navigation.
- **Target-Based Take Profit System**: Parses numbered targets from Telegram signals, tracks positions, and executes progressive partial closes at each target level based on customizable split percentages. A background service (`target_monitor.py`) continuously monitors active positions.
- **Auto-Stop Logic System**: Detects "signal cancelled," "closed," or "stop loss hit" messages from Telegram, parses them, and automatically closes affected positions based on user settings (`auto_stop_on_cancel`). It calculates final PnL and updates position states.
- **Security & Payments**: Includes a license key security system, USDT TRC20 payment processing with admin verification, automatic referral bonuses, HMAC signature verification, and a CAPTCHA system for registration/login. A signal quality filter scores incoming signals for auto-trading based on risk/reward, SL presence, targets, and clarity. IP whitelisting instructions are provided for exchange API keys.

### System Design Choices
- **Multi-tenancy**: Isolated configurations and strategies per user.
- **Microservices-like Components**: Separation of concerns into distinct modules.
- **Persistent Local Storage**: JSON files in the `database/` folder for user data, positions, and safety state.
- **Environment Variables**: For sensitive information like API tokens.
- **24/7 Operation**: Configured for continuous uptime.
- **Subscription Model**: Free, Pro, and VIP tiers controlling feature access.
- **Authentication**: JWT-based with secure password hashing and token refresh.

## External Dependencies
- **Telegram API**: For signal monitoring and broadcasting (via `telethon` and `python-telegram-bot`).
- **Binance API**: For trading operations.
- **Bybit API**: For trading operations.
- **Phemex API**: For trading operations.
- **Coinexx API**: For trading operations.
- **Flask**: Python web framework for the REST API.
- **Requests**: Python HTTP library.
- **Schedule**: Python library for task scheduling.
- **PyJWT**: For JWT authentication.
- **Bcrypt**: For password hashing.
- **flask-simple-captcha**: For CAPTCHA implementation.

## Recent Changes
- **2025-10-16**: Complete Referral & In-App Wallet System
  - ✅ **10% Recurring Commission**: Monthly referral bonuses for lifetime of subscription
  - ✅ **In-App Wallet**: Each user gets generated wallet for referral earnings
  - ✅ **Withdrawal System**: $10 minimum, $1 fee (credited to system wallet)
  - ✅ **Recurring Payments Service**: Background task processes monthly commissions daily
  - ✅ **Wallet Balance API**: GET /api/wallet/balance endpoint
  - ✅ **Updated Referral Stats**: Now includes wallet_balance and recurring_subscriptions count

- **2025-10-16**: Secure Payment & Subscription System
  - ✅ License Key Security: URL-safe base64 encoding with embedded expiry (survives restarts)
  - ✅ USDT TRC20 Payments: Manual admin verification workflow with fraud detection
  - ✅ Payment Flow: User→Admin Verification→Subscription Activation→License Generation
  - ✅ HMAC Signature Verification: MANDATORY X-Payment-Signature & X-Admin-Signature headers
  - ✅ Plan Pricing: PRO $29.99/mo, VIP $99.99/mo (USDT TRC20)
  - ✅ Persistent Storage: licenses.json, payments.json, referrals.json
  - ✅ Fraud Protection: Multi-layer validation, tamper-proof checksums