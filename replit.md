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
   - Forwards signals from admin to VIP/TRIAL groups
   - Adds custom Verzek branding

4. **Trade Executor** (`trade_executor.py`) - Trade execution engine
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

### Development (Current Setup)
The Flask API Server workflow is configured to run automatically:
```bash
python api_server.py
```
This serves the REST API on port 5000 (0.0.0.0:5000).

### Running the Main Bot
To start the Telegram signal monitoring bot:
```bash
python main.py
```

### Running the Broadcast Bot
To start the signal broadcaster:
```bash
python broadcast_bot.py
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
