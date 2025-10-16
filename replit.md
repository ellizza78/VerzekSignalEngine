# VerzekAutoTrader

## Overview
VerzekAutoTrader is a multi-tenant auto-trading platform designed for Dollar Cost Averaging (DCA). It monitors Telegram for trading signals, broadcasts them to VIP/TRIAL groups, and executes automated DCA trades with advanced risk management across multiple exchanges. The platform supports a robust subscription system, allowing users to access varying levels of automation and features, and aims to provide a reliable and secure trading environment.

## User Preferences
None specified yet.

## System Architecture

### Core Trading Modules
- **DCA Engine**: Implements Dollar Cost Averaging with configurable levels, multipliers, average entry calculation, automatic and partial take profit, and stop loss. Includes investment caps and position tracking.
- **Multi-User Management**: Supports a multi-tenant architecture with per-user DCA configurations, risk settings (leverage caps, position size, daily limits), exchange account management, symbol whitelist/blacklist, daily stats, and subscription plans (free/pro/vip).
- **Safety Manager**: Incorporates a Kill Switch for emergency stops, a Circuit Breaker that triggers on rapid losses (configurable thresholds), Order Idempotency to prevent duplicate orders, and a Trading Pause feature.
- **DCA Orchestrator**: Coordinates all trading components, manages the signal execution pipeline, handles DCA triggers, and supports a demo mode.
- **Position Tracker**: Manages and persists all open and historical trading positions.

### Exchange Adapters
- **Unified Exchange Interface**: Provides a consistent API for various exchanges.
- **Exchange Implementations**: Supports Binance, Bybit, Phemex, and Coinexx with both live and demo client modes. Securely loads API keys from environment variables.

### Signal Broadcasting System
- **Telethon Auto-Forwarder**: 24/7 monitoring of Telegram sources (chats, channels, groups) for trading signals, featuring keyword detection, spam filtering, and broadcasting to an internal bot. Uses `StringSession` for persistence.
- **Broadcast Bot**: Receives signals, adds a "New Signal Alert" header, and broadcasts to designated VIP and TRIAL Telegram groups, with loop prevention mechanisms.

### REST API Server
- A Flask-based API on port 5000 providing endpoints for:
    - **User Management**: CRUD operations for users, including retrieving statistics.
    - **Settings Management**: Configuration for general mode (live/demo), risk parameters (capital, position sizing, limits), strategy parameters (auto-follow, TP/SL), and DCA settings.
    - **Subscription Management**: Activation and status updates for user subscriptions.
    - **Exchange Account Management**: CRUD operations for user exchange connections.
    - **Position Management**: Retrieval of all or user-specific trading positions.
    - **Safety Controls**: Endpoints to check status and control the kill switch, trading pause, and circuit breaker.

### UI/UX Decisions
- The project is designed with a focus on comprehensive configuration and control through its REST API, implying a potential external mobile app or web interface for user interaction (though not part of this replit).
- Subscription tiers are clearly defined with feature gating, guiding user experience based on their plan.

### System Design Choices
- **Multi-tenancy**: Designed to serve multiple users, each with isolated configurations and trading strategies.
- **Microservices-like Components**: Separation of concerns into distinct modules like DCA Engine, Safety Manager, and Exchange Adapters.
- **Persistent Local Storage**: Utilizes JSON files in the `database/` folder for user data, positions, and safety state.
- **Environment Variable for Secrets**: Sensitive information like API tokens are managed via environment variables for security.
- **24/7 Operation**: Configured for continuous uptime using a Reserved VM deployment.
- **Subscription Model**: Implements Free, Pro, and VIP tiers, controlling access to features like auto-trading, DCA automation, and number of exchange connections. Default safety settings for new users (auto-trade disabled).

## External Dependencies
- **Telegram API**: Used for signal monitoring (via `telethon` library) and broadcasting (via `python-telegram-bot`).
- **Binance API**: Integrated for trading operations.
- **Bybit API**: Integrated for trading operations.
- **Phemex API**: Integrated for trading operations.
- **Coinexx API**: Integrated for trading operations.
- **Flask**: Python web framework for the REST API.
- **Requests**: Python HTTP library for making external API calls.
- **Schedule**: Python library for scheduling tasks.