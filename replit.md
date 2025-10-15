# VerzekAutoTrader

## Overview
VerzekAutoTrader is an automated cryptocurrency trading bot that listens to Telegram signal channels, parses trade signals, and executes trades automatically. It includes:
- Real-time Telegram signal monitoring
- Automated trade execution (demo/live modes)
- REST API server for monitoring and data access
- Signal broadcasting capabilities
- Trade logging and analytics

## Project Status
**Status**: Ready to run in Replit environment
**Last Updated**: October 14, 2025

## Architecture

### Main Components
1. **Flask API Server** (`api_server.py`) - REST API on port 5000
   - `/api/status` - Bot status and uptime
   - `/api/trades` - All executed trades
   - `/api/latest` - Latest trade
   - `/api/test` - Connection test

2. **Main Bot** (`main.py`) - Telegram signal monitoring bot
   - Listens to configured signal channels
   - Parses trading signals (LONG/SHORT, TP, SL, ENTRY)
   - Executes trades automatically
   - Sends notifications to admin

3. **Broadcast Bot** (`broadcast_bot.py`) - Signal broadcaster
   - Receives signals from admin/Telethon forwarder
   - Adds custom Verzek header: "🔥 New Signal Alert (VerzekSignalBot)"
   - Broadcasts to VIP Group (-1002721581400) and TRIAL Group (-1002726167386)
   - Loop prevention: Never re-broadcasts from VIP/TRIAL groups

4. **Telethon Auto-Forwarder** (`telethon_forwarder.py`) - Universal signal monitor
   - Monitors ALL Telegram sources 24/7: personal chats, channels, groups (even when user is offline)
   - Enhanced signal detection with 24+ keywords: BUY, SELL, LONG, SHORT, ENTRY, TP, SL, STOP LOSS, TARGETS, TARGET, PROFIT, LOSS, LEV, LEVERAGE, SIGNAL, USDT, /USDT, REACHED, CANCELLED, ACHIEVED, CLOSED, TAKE-PROFIT, TAKE PROFIT, GAINED
   - Supports multiple signal formats: entry signals, profit notifications, stop loss alerts, trade closures, cancellations
   - Spam filter blocks promotional messages (HOW TO, GUIDE, CONTACT, JOIN OUR, etc.)
   - Forwards raw signals to @broadnews_bot for cleaning and broadcasting
   - Uses StringSession (no database locking issues)
   - Requires one-time authentication via `setup_telethon.py`

5. **Trade Executor** (`trade_executor.py`) - Trade execution engine
   - Supports Binance, Bybit, Phemex (via API keys)
   - Falls back to simulation mode if no API keys
   - Logs all trades to CSV

### Supporting Files
- `signal_parser.py` - Parses Telegram messages into trade data
- `telegram_listener.py` - Handles Telegram message monitoring
- `utils/logger.py` - Centralized logging
- `utils/user_manager.py` - User/admin management

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
- `trades_log.csv` - All executed trades
- `trades_log.json` - Trade records in JSON format
- `logs.txt` - System logs
- `broadcast_log.txt` - Broadcast history
- `users.json` - User database
- `forward_log.txt` - Signal forwarding log

## Dependencies
All Python dependencies are managed via pip:
- `flask` - Web framework for REST API
- `python-telegram-bot==13.15` - Telegram bot library
- `requests` - HTTP library
- `schedule` - Task scheduling

## Recent Changes
- **2025-10-15**: Enhanced Signal Detection & Spam Filtering
  - Expanded keyword detection to 24+ keywords: Added ACHIEVED, CLOSED, TAKE-PROFIT, TAKE PROFIT, GAINED
  - Now supports all signal formats: entry signals, profit notifications, stop loss alerts, trade closures, cancellations
  - Added spam filter to block promotional messages (HOW TO, GUIDE, CONTACT, JOIN OUR, PARTICIPATE, etc.)
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
