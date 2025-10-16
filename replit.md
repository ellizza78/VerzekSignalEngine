# VerzekAutoTrader

## Overview
VerzekAutoTrader has evolved into a comprehensive multi-tenant auto-trading platform with DCA (Dollar Cost Averaging) capabilities. The system monitors Telegram for trading signals, broadcasts them to VIP/TRIAL groups, and executes automated DCA trades with advanced risk management.

**Core Features:**
- 24/7 Telegram signal monitoring & broadcasting
- DCA Engine with margin call strategy
- Multi-exchange support (Binance, Bybit, Phemex, Coinexx)
- Multi-user/multi-tenant architecture
- Advanced safety rails (kill switch, circuit breaker, idempotency)
- REST API for mobile app integration
- Demo mode for testing without API keys

## Project Status
**Status**: Phase 1 Complete - DCA Engine Production-Ready
**Last Updated**: October 16, 2025

## Architecture

### Core Trading Modules (`modules/`)

1. **DCA Engine** (`dca_engine.py`)
   - Dollar Cost Averaging strategy with margin calls
   - Configurable DCA levels with multipliers (1x, 1.5x, 2x, etc.)
   - Average entry price calculation across all fills
   - Automatic take profit when price rebounds
   - Partial TP support (30%/30%/40% splits)
   - Stop loss protection with trailing option
   - Investment cap per symbol ($100 default)
   - Position tracking with PnL calculation

2. **Multi-User Management** (`user_manager_v2.py`)
   - Multi-tenant architecture (each user has own settings)
   - Per-user DCA configurations
   - Risk settings: leverage caps, position size, daily limits
   - Exchange account management (CRUD operations)
   - Symbol whitelist/blacklist enforcement
   - Daily stats tracking with auto-reset
   - Subscription plans (free/pro/vip)
   - Trading statistics (wins/losses/PnL)

3. **Safety Manager** (`safety_manager.py`)
   - **Kill Switch**: Emergency stop for all trading
   - **Circuit Breaker**: Auto-triggers on rapid losses
     - 10% max loss threshold (configurable)
     - 5 consecutive losses limit (configurable)
     - 60-minute lookback window
   - **Order Idempotency**: Prevents duplicate orders via stable hashing
   - **Trading Pause**: Time-based trading halt (auto-resume)
   - **Validation**: Symbol, leverage, and order size checks
   - Persistent state across restarts

4. **DCA Orchestrator** (`dca_orchestrator.py`)
   - Master coordinator integrating all components
   - Full signal execution pipeline with safety checks
   - DCA trigger monitoring and execution
   - Position closure with PnL tracking
   - Demo mode support (works without API keys)
   - Comprehensive logging of all operations

5. **Position Tracker** (`position_tracker.py`)
   - Tracks all open positions across users
   - Persistent storage in JSON format
   - Position status management
   - Historical position records

### Exchange Adapters (`exchanges/`)

6. **Exchange Interface** (`exchange_interface.py`)
   - Unified API across all exchanges
   - Methods: balance, ticker, orders, cancellation
   - Demo clients for offline testing

7. **Exchange Implementations**
   - **Binance** (`binance_client.py`) - Live + Demo
   - **Bybit** (`bybit_client.py`) - Live + Demo
   - **Phemex** (`phemex_client.py`) - Live + Demo
   - **Coinexx** (`coinexx_client.py`) - Live + Demo
   - **ExchangeFactory**: Client instantiation and management
   - Secure API key loading from environment variables
   - Demo mode with deterministic offline pricing

### Signal Broadcasting System

8. **Telethon Auto-Forwarder** (`telethon_forwarder.py`)
   - Monitors ALL Telegram sources 24/7 (personal chats, channels, groups)
   - 24+ signal keywords detection
   - Spam filter (60+ promotional keywords blocked)
   - Username blocklist (@PowellNolan, @Sanjay_Message_Bot, @OfficialRoyalQBot)
   - Forwards to @broadnews_bot for broadcasting
   - StringSession (no database locking)

9. **Broadcast Bot** (`broadcast_bot.py`)
   - Receives signals from Telethon forwarder
   - Adds Verzek header: "🔥 New Signal Alert"
   - Broadcasts to VIP Group (-1002721581400) & TRIAL Group (-1002726167386)
   - Loop prevention (never re-broadcasts from VIP/TRIAL)

10. **Legacy Components**
    - `main.py` - Original signal monitoring bot
    - `signal_parser.py` - Message parsing
    - `trade_executor.py` - Trade execution with demo fallback

### REST API Server

11. **Flask API** (`api_server.py`) - Port 5000
    - **User Management:**
      - `GET/POST /api/users` - List/create users
      - `GET/PUT/DELETE /api/users/<id>` - User CRUD
      - `GET /api/users/<id>/stats` - User statistics
    
    - **Settings:**
      - `GET/PUT /api/users/<id>/risk` - Risk settings
      - `GET/PUT /api/users/<id>/dca` - DCA settings
      - `GET/POST/DELETE /api/users/<id>/exchanges` - Exchange accounts
    
    - **Positions:**
      - `GET /api/positions` - All positions
      - `GET /api/positions/<id>` - User positions
    
    - **Safety Controls:**
      - `GET /api/safety/status` - Safety system status
      - `POST /api/safety/killswitch` - Kill switch control
      - `POST /api/safety/pause` - Pause trading
      - `POST /api/safety/resume` - Resume trading
      - `POST /api/safety/circuit-breaker` - Circuit breaker control
    
    - **Legacy:**
      - `GET /api/trades` - All trades
      - `GET /api/latest` - Latest trade

## Configuration

### Environment Variables (Secrets)
The following secrets are required and configured in Replit Secrets:
- `TELEGRAM_BOT_TOKEN` - Main bot token from @BotFather
- `BROADCAST_BOT_TOKEN` - Broadcast bot token
- `ADMIN_CHAT_ID` - Admin Telegram user ID

### Config File
`config/config.json` contains:
- Signal group IDs to monitor
- Trading parameters (risk, position size, max trades)
- Exchange settings
- Strategy settings (TP/SL percentages, timeframes)
- Logging preferences

**Security Note**: Sensitive tokens have been moved to environment variables and removed from the config file.

## Running the Project

### Automatic (Recommended)
The VerzekAutoTrader workflow runs all services automatically:
- Flask API Server (port 5000)
- Broadcast Bot (@broadnews_bot)
- Telethon Auto-Forwarder (if authenticated)

### First-Time Telethon Setup
Before the auto-forwarder can work, run this ONCE in the Replit Shell:
```bash
python setup_telethon.py
```
This authenticates your Telegram account. You'll receive a code on Telegram.
After authentication, the auto-forwarder will work automatically 24/7.

### Manual Execution
You can also run individual components:
```bash
python api_server.py      # Flask API
python broadcast_bot.py   # Broadcast bot only
python telethon_forwarder.py  # Auto-forwarder only (after setup)
python main.py            # Main signal bot
```

## Deployment
- **Deployment Target**: Reserved VM (24/7 Always-On)
- **Run Command**: `python api_server.py`
- The project is configured for continuous 24/7 operation using a Reserved VM deployment
- This ensures the bot stays online continuously to monitor Telegram channels and execute trades

## Database/Storage
All data is stored locally in the `database/` folder:
- `users_v2.json` - Multi-user database (DCA settings, risk controls)
- `positions.json` - All open/closed positions
- `safety_state.json` - Safety system state (kill switch, circuit breaker)
- `trades_log.csv` - Legacy trade log
- `trades_log.json` - Trade records in JSON
- `logs.txt` - System logs
- `broadcast_log.txt` - Broadcast history
- `forward_log.txt` - Signal forwarding log

## Dependencies
All Python dependencies are managed via pip:
- `flask` - Web framework for REST API
- `python-telegram-bot==13.15` - Telegram bot library
- `requests` - HTTP library
- `schedule` - Task scheduling

## DCA Strategy

### How It Works
1. **Base Order**: Opens initial position (default $10)
2. **Margin Calls**: Triggers DCA orders when price drops
   - Level 1: -1.5% drop, 1.0x multiplier ($10)
   - Level 2: -2.0% drop, 1.2x multiplier ($12)
   - Level 3: -3.0% drop, 1.5x multiplier ($15)
3. **Average Entry**: Calculates weighted average across all fills
4. **Take Profit**: Closes position when price rebounds to target
5. **Stop Loss**: Hard stop at -3% (configurable)

### Risk Management
- **Leverage Caps**: Per-user maximum leverage (default 10x)
- **Position Limits**: Max concurrent positions (default 3)
- **Daily Trade Limit**: Max trades per day (default 20)
- **Daily Loss Limit**: Max loss % per day (default 5%)
- **Investment Cap**: Max USD per symbol (default $100)
- **Symbol Control**: Whitelist/blacklist enforcement

### Safety Rails
- **Kill Switch**: Emergency stop for all trading
- **Circuit Breaker**: Auto-triggers on:
  - 10% total loss in 60 minutes
  - 5 consecutive losing trades
- **Order Idempotency**: MD5 hash of signal context prevents duplicates
- **Trading Pause**: Temporary halt with auto-resume

## Recent Changes
- **2025-10-16**: Phase 1 Complete - DCA System Production-Ready
  - ✅ DCA Engine with margin call strategy
  - ✅ Multi-user management system with per-user DCA settings
  - ✅ 4 exchange adapters (Binance, Bybit, Phemex, Coinexx) with demo modes
  - ✅ Safety Manager with kill switch, auto circuit breaker, order idempotency
  - ✅ Comprehensive Flask API with 20+ endpoints
  - ✅ DCA Orchestrator integrating all components
  - ✅ Demo mode support (works without exchange API keys)
  - ✅ Automatic circuit breaker triggers on rapid losses
  - ✅ Idempotent order IDs prevent duplicate trades
  - ✅ Daily risk limits (trade count, loss %, position count)
  - Added @OfficialRoyalQBot to spam blocker

- **2025-10-15**: Enhanced Signal Detection & Spam Filtering
  - Expanded keyword detection to 24+ keywords: Added ACHIEVED, CLOSED, TAKE-PROFIT, TAKE PROFIT, GAINED
  - Now supports all signal formats: entry signals, profit notifications, stop loss alerts, trade closures, cancellations
  - Added spam filter to block promotional messages (HOW TO, GUIDE, CONTACT, JOIN OUR, PARTICIPATE, HYPERLIQUID, NO KYC, GOLDENCRYPTOSIGNALS, AI GOLDEN, etc.)
  - Username blocklist blocks known spammers (@PowellNolan, @Sanjay_Message_Bot) by username before keyword analysis
  - Fixed signal cleaning: Preserves coin pair names (e.g., BTCUSDT, ORDI/USDT) while removing hashtags
  - Telethon forwarder monitors ALL Telegram sources (personal chats, channels, groups) 24/7
  - Signal cleaning removes only # symbols and leverage indicators (Lev x26) but keeps essential data
  - System works 24/7 even when user is completely offline

- **2025-10-15**: Telethon Auto-Forwarder & Loop Prevention
  - Added Telethon auto-forwarder to monitor personal chats 24/7
  - Fixed infinite broadcast loop with VIP/TRIAL group exclusion
  - Changed from SQLite to StringSession (fixes database locking issues)
  - Created one-time setup script for Telethon authentication
  - Broadcast bot now prevents re-broadcasting its own messages
  - Updated workflow to run Flask API + Broadcast Bot + Telethon Forwarder

- **2025-10-14**: Initial Replit setup
  - Moved sensitive tokens to environment variables
  - Created .gitignore for Python artifacts and sensitive data
  - Installed Python 3.11 and all dependencies
  - Added `get_all_trades()` function to trade_executor.py for API compatibility
  - Configured Flask API workflow on port 5000
  - Set up Reserved VM deployment for 24/7 continuous operation
  - All API endpoints tested and working

## User Preferences
None specified yet.

## Notes
- The bot runs in "demo" mode by default (simulation)
- To enable live trading, add exchange API keys to config.json and set `api_mode: "enabled"`
- The mobile app folder contains a React Native app (not configured in this setup)
