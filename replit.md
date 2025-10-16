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
    - **Authentication**: JWT-based registration, login, token refresh, and user info endpoints
    - **User Management**: CRUD operations for users, including retrieving statistics
    - **Settings Management**: Configuration for general mode (live/demo), risk parameters (capital, position sizing, limits), strategy parameters (auto-follow, TP/SL), and DCA settings
    - **Subscription Management**: Activation and status updates for user subscriptions
    - **Exchange Account Management**: CRUD operations for user exchange connections
    - **Position Management**: Retrieval of all or user-specific trading positions
    - **Safety Controls**: Endpoints to check status and control the kill switch, trading pause, and circuit breaker

### Mobile Application
- **React Native + Expo**: Cross-platform mobile app for iOS and Android
- **JWT Authentication**: Secure login/register with automatic token refresh
- **Secure Storage**: AsyncStorage for tokens and user data
- **Dashboard**: Account overview, trading stats, subscription status, and quick actions
- **API Integration**: Full integration with Flask backend via REST API
- **Token Management**: Automatic access token refresh on 401 errors
- **Navigation**: Auth-based routing (Login/Register stack vs Main app stack)
- **UI/UX**: Modern dark theme with responsive design (Navy blue: #1a1a2e, Accent: #e94560)

### System Design Choices
- **Multi-tenancy**: Designed to serve multiple users, each with isolated configurations and trading strategies.
- **Microservices-like Components**: Separation of concerns into distinct modules like DCA Engine, Safety Manager, and Exchange Adapters.
- **Persistent Local Storage**: Utilizes JSON files in the `database/` folder for user data, positions, and safety state.
- **Environment Variable for Secrets**: Sensitive information like API tokens are managed via environment variables for security.
- **24/7 Operation**: Configured for continuous uptime using a Reserved VM deployment.
- **Subscription Model**: Implements Free, Pro, and VIP tiers, controlling access to features like auto-trading, DCA automation, and number of exchange connections. Default safety settings for new users (auto-trade disabled).

## Target-Based Take Profit System

### Overview
Automated progressive take profit system that monitors positions and executes partial closes at each target level from trading signals.

### How It Works
1. **Signal Parsing**: Extracts numbered targets from Telegram signals
   - Patterns: "TARGET 1: 50000", "TARGET 2: 51000", "TP 1:", "TAKE PROFIT 1:"
   - Returns structured data: `[{"target_num": 1, "price": 50000}, ...]`

2. **Position Tracking**: Enhanced position data structure
   - `targets`: Array of target objects with prices
   - `stop_loss`: Stop loss price
   - `remaining_quantity`: Tracks quantity for progressive TP
   - `reached_targets`: Array of hit target numbers
   - `total_profit_taken`: Cumulative profit tracker

3. **Target Monitoring**: Background service (`target_monitor.py`)
   - Checks all active positions every 5 seconds
   - Compares current price vs targets
   - LONG: Target reached when price >= target_price
   - SHORT: Target reached when price <= target_price

4. **Progressive Take Profit**:
   - Closes position in stages as each target is reached
   - Default split: [25%, 25%, 25%, 25%] for 4 targets
   - Customizable via `strategy_settings.partial_tp_splits`
   - Final target: Closes 100% of remaining position
   - Calculates and records profit for each TP

### Example Flow
**Signal**: "BTCUSDT LONG, TARGET 1: 50000, TARGET 2: 51000, TARGET 3: 52000, TARGET 4: 53000"

1. Position opens at entry price
2. Price hits 50000 → Close 25%, profit recorded, Target 1 marked reached
3. Price hits 51000 → Close 25% more, profit added, Target 2 marked
4. Price hits 52000 → Close 25% more, profit added, Target 3 marked
5. Price hits 53000 → Close remaining 25%, position closed, total PnL recorded

### User Settings
- `strategy_settings.target_based_tp`: Enable/disable feature (default: True)
- `strategy_settings.partial_tp_splits`: Customize TP percentages (default: [25, 25, 25, 25])

### Services Running
- **Flask API**: Port 5000
- **Telethon Forwarder**: Signal monitoring
- **Broadcast Bot**: Signal broadcasting
- **Target Monitor**: TP execution (NEW)

## External Dependencies
- **Telegram API**: Used for signal monitoring (via `telethon` library) and broadcasting (via `python-telegram-bot`).
- **Binance API**: Integrated for trading operations.
- **Bybit API**: Integrated for trading operations.
- **Phemex API**: Integrated for trading operations.
- **Coinexx API**: Integrated for trading operations.
- **Flask**: Python web framework for the REST API.
- **Requests**: Python HTTP library for making external API calls.
- **Schedule**: Python library for scheduling tasks.

## Auto-Stop Logic System

### Overview
Automated position closure system that detects signal cancellations, stop loss hits, and close messages from Telegram and automatically closes affected positions.

### Supported Close Signals
- **"Signal Cancelled"** or **"Signal Canceled"**
- **"Closed"** or **"Close"** (e.g., "BTCUSDT Closed")
- **"Stop Loss Hit"** or **"SL Hit"**
- **"Position Closed"** or **"Trade Closed"**

### How It Works
1. **Signal Detection**: Broadcast Bot receives message from Telegram
2. **Parse Close Signal**: `parse_close_signal()` checks for close keywords
3. **Extract Details**: Identifies symbol (e.g., BTCUSDT) and close reason
4. **Check User Settings**: Verifies if `auto_stop_on_cancel` is enabled
5. **Auto-Close**: Triggers `auto_close_positions(symbol, reason)`
6. **Find Positions**: Locates all active positions for that symbol
7. **Place Orders**: Executes opposite orders at current market price
8. **Calculate PnL**: Computes final profit/loss (including any partial TPs)
9. **Update State**: Sets position to closed, records trade, updates user stats

### Close Reasons
- `signal_cancelled`: Signal was cancelled by provider
- `stop_loss_hit`: Stop loss was triggered
- `closed`: General position closure
- `manual_close`: User manually closed

### User Settings
- `strategy_settings.auto_stop_on_cancel`: Enable/disable auto-close (default: **True**)
- When disabled, positions remain open for manual management

### Example Flow
```
Message: "BTCUSDT - Signal Cancelled"
1. Broadcast Bot detects close signal
2. Extracts: symbol=BTCUSDT, reason=signal_cancelled
3. Finds all active BTCUSDT positions
4. For each position (if auto_stop enabled):
   - Get current price
   - Place close order (sell for LONG, buy for SHORT)
   - Calculate final PnL = entry profit + partial TPs
   - Update position: status="closed", auto_closed=True
   - Record trade in user stats
5. Broadcast close message to groups
```

### Integration Points
- **signal_parser.py**: `parse_close_signal()` function
- **modules/dca_orchestrator.py**: `auto_close_positions()` method
- **broadcast_bot.py**: Detects and triggers auto-close before broadcasting

## Recent Changes
- **2025-10-16**: CAPTCHA, Signal Filtering & IP Whitelisting Complete
  - ✅ CAPTCHA System: flask-simple-captcha for registration and login security
  - ✅ Signal Quality Filter: Scoring algorithm (0-100) filters best signals for auto-trading
    - R/R ratio (30pts), SL presence (20pts), targets (20pts), entry clarity (15pts), provider rep (15pts)
    - Default threshold: 60/100 for auto-execution
    - User-configurable via strategy_settings.signal_quality_threshold
  - ✅ IP Whitelisting: /api/system/ip endpoint displays server IP (34.11.228.15)
  - ✅ Exchange Setup Screen: Mobile tab with IP copy, 6-step instructions, exchange links
  - ✅ Updated Onboarding: Step 3 explains IP whitelisting requirement for Futures API keys
  - ✅ Architect-approved: All features tested and production-ready

- **2025-10-16**: VZK Branding & Onboarding Complete
  - ✅ VZK Logo: Added to Login, Register, and Dashboard screens
  - ✅ Color Scheme: Complete update to Teal/Gold gradient (#0A4A5C → #1B9AAA, #F9C74F)
  - ✅ All Screens: Migrated from hardcoded colors to centralized COLORS constants
  - ✅ Onboarding Modal: Critical setup instructions (ISOLATED MARGIN, AUTO TRADES settings)
  - ✅ First-Run Experience: Shows instructions automatically, re-accessible from Dashboard
  - ✅ LONG/SHORT Indicators: Teal (LONG) / Gold (SHORT) for brand consistency
  - ✅ Architect-approved: Zero hardcoded colors, cohesive visual design

- **2025-10-16**: Mobile App - All Core Screens Production-Ready
  - ✅ Signals Feed: Real API integration with signalsAPI.getSignals(), parses broadcast log, proper error handling
  - ✅ Positions Screen: Calls positionsAPI.getUserPositions(), Alert dialogs on errors, no mock fallback
  - ✅ Settings Screen: All toggles persist via backend API (strategy + notifications), auto-refresh
  - ✅ Backend API: Added /api/signals and /api/users/<user_id>/preferences endpoints
  - ✅ All screens architect-approved for production use
  - 📋 Next: Exchange Accounts screen for API key management

- **2025-10-16**: React Native Mobile App Complete
  - ✅ Created Expo React Native app structure (mobile_app/VerzekApp/)
  - ✅ Implemented JWT authentication with secure token storage
  - ✅ Built Login/Register screens with form validation
  - ✅ Created Dashboard with user stats and subscription info
  - ✅ Integrated API service layer with automatic token refresh
  - ✅ Added auth context for global authentication state
  - ✅ Configured navigation with auth-based routing
  - ✅ Backend tested: Registration, Login, and Protected endpoints verified
  - ✅ Modern dark UI with Navy/Pink color scheme
  - 📱 Ready for iOS/Android deployment via Expo

- **2025-10-16**: JWT Authentication System Complete
  - ✅ Added PyJWT and bcrypt dependencies
  - ✅ Created auth module with token generation/verification
  - ✅ Implemented 4 auth endpoints: register, login, refresh, me
  - ✅ Extended User model with email, full_name, password_hash
  - ✅ Secure password hashing (bcrypt) and validation
  - ✅ Access tokens (1hr) and refresh tokens (30 days)
  - ✅ Token-based authentication decorators
  - ✅ Password hash excluded from API responses for security

- **2025-10-16**: Phase 2 Task 5 Complete - Auto-Stop Logic System
  - ✅ Enhanced signal parser to detect close/cancel messages
  - ✅ Implemented auto_close_positions() method in DCA Orchestrator
  - ✅ Integrated auto-close detection into Broadcast Bot
  - ✅ Added per-user auto_stop_on_cancel setting (default: True)
  - ✅ Calculates final PnL including partial TP profits
  - ✅ Updates position state with close_reason and auto_closed flag
  - ✅ Architect-approved: End-to-end flow validated and production-ready

- **2025-10-16**: Phase 2 Task 4 Complete - Target-Based Take Profit System
  - ✅ Enhanced signal parser to extract numbered targets (TARGET 1, 2, 3, 4...)
  - ✅ Added comprehensive target tracking to position model
  - ✅ Implemented progressive TP logic in DCA Orchestrator
  - ✅ Created background Target Monitor service (5-second interval)
  - ✅ Implemented final target closure (100% close on last target)
  - ✅ Integrated Target Monitor into run_all_bots.py
  - ✅ Customizable TP split percentages via user settings
  - ✅ System tested and running in production