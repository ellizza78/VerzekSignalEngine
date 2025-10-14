"""
VerzekAutoTrader - Main Bot Application
---------------------------------------
Handles Telegram commands, listens for signals,
parses them, and triggers simulated trades automatically.
Includes auto-cleanup of old signal logs and external signal monitoring.
"""

import json
import os
import time
import schedule
from datetime import datetime, timedelta
from telegram.ext import Updater, CommandHandler
from utils.logger import log_event
from utils.user_manager import load_users
from telegram_listener import register_forwarder, watch_signal_channels
from signal_parser import parse_signal
from trade_executor import execute_trade


# ============================
# LOAD CONFIGURATION
# ============================

CONFIG_PATH = "config/config.json"

def load_config():
    """Load bot configuration from config/config.json"""
    if not os.path.exists(CONFIG_PATH):
        log_event("ERROR", "⚠️ config/config.json not found! Please create it before running.")
        raise FileNotFoundError("config/config.json file missing.")

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()

BOT_TOKEN = config["telegram_bot_token"]
ADMIN_CHAT_ID = int(config["admin_chat_id"])
SIGNAL_GROUP_IDS = [int(gid) for gid in config.get("signal_group_ids", [])]
WATCHED_SIGNAL_SOURCES = [int(cid) for cid in config.get("watched_signal_sources", [])]
SCAN_INTERVAL = config.get("scan_interval", 10)
MODE = config.get("mode", "demo")

LOG_FILE = "database/forward_log.txt"


# ============================
# TELEGRAM COMMANDS
# ============================

def start(update, context):
    """Start command."""
    user_id = update.effective_user.id
    log_event("INFO", f"👋 User {user_id} started the bot.")
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🤖 Welcome to *VerzekSignalBot*!\nYour premium crypto signal assistant.",
        parse_mode="Markdown"
    )


def help_command(update, context):
    """Help command."""
    help_text = (
        "📘 *VerzekSignalBot Commands:*\n"
        "/start - Welcome message\n"
        "/help - Show this help menu\n"
        "/status - Show system status\n"
        "/logs - View last forwarded signals (Admin only)\n"
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=help_text, parse_mode="Markdown")


def status(update, context):
    """Show current bot status."""
    data = load_users()
    admins = data.get("admins", [])
    users = data.get("users", [])

    msg = (
        f"⚙️ *VerzekSignalBot Status*\n"
        f"👑 Admins: {len(admins)}\n"
        f"👥 Users: {len(users)}\n"
        f"📡 Mode: {MODE}\n"
        f"🕐 Scan Interval: {SCAN_INTERVAL} min\n"
        f"📢 Watching: {len(WATCHED_SIGNAL_SOURCES)} external signal channels\n"
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg, parse_mode="Markdown")


def logs(update, context):
    """Show recent forwarded signal logs (admin only)."""
    user_id = update.effective_user.id
    if user_id != ADMIN_CHAT_ID:
        context.bot.send_message(chat_id=update.effective_chat.id, text="❌ You’re not authorized to view logs.")
        return

    if not os.path.exists(LOG_FILE):
        context.bot.send_message(chat_id=update.effective_chat.id, text="📂 No logs found yet.")
        return

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()[-10:]

    if not lines:
        msg = "📂 No forwarded signals logged yet."
    else:
        msg = "🧾 *Recent Forwarded Signals:*\n\n" + "".join(lines[-10:])

    context.bot.send_message(chat_id=update.effective_chat.id, text=f"```{msg}```", parse_mode="Markdown")


# ============================
# AUTO LOG CLEANUP
# ============================

def cleanup_old_logs():
    """Delete log entries older than 30 days."""
    if not os.path.exists(LOG_FILE):
        return

    cutoff_date = datetime.now() - timedelta(days=30)
    retained_lines = []

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                timestamp_str = line.split("]")[0].strip("[")
                entry_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                if entry_time > cutoff_date:
                    retained_lines.append(line)
            except Exception:
                continue  # skip any malformed lines

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.writelines(retained_lines)

    log_event("CLEANUP", "🧹 Old log entries (older than 30 days) have been cleaned.")


# ============================
# SIGNAL MONITORING LOOP
# ============================

def run_signal_monitor():
    """Main loop for listening and parsing new signals."""
    from telegram_listener import get_new_messages
    log_event("INFO", "🔍 Checking for new signals...")

    for group_id in SIGNAL_GROUP_IDS:
        messages = get_new_messages(group_id)
        for msg in messages:
            signal_data = parse_signal(msg)
            if signal_data:
                symbol = signal_data.get("symbol")
                side = signal_data.get("side", "buy")
                tp = signal_data.get("tp")
                sl = signal_data.get("sl")
                amount = signal_data.get("amount", 0.01)

                trade = execute_trade(symbol=symbol, side=side, amount=amount, tp=tp, sl=sl)
                log_event("TRADE", f"💰 Auto-trade executed: {symbol} {side.upper()}")
                notify_admin(trade)


# ============================
# NOTIFICATION FUNCTION
# ============================

def notify_admin(trade):
    """Notify admin via Telegram when a trade is executed."""
    from telegram import Bot
    bot = Bot(token=BOT_TOKEN)
    msg = (
        f"📢 *Source:* Verzek Signal Bot\n\n"
        f"✅ *Trade Executed Successfully!*\n"
        f"💎 *Symbol:* {trade['symbol']}\n"
        f"📊 *Type:* {trade['mode'].capitalize()}\n"
        f"📈 *Side:* {trade['side'].upper()}\n"
        f"💰 *Entry:* {trade['entry_price']:.4f}\n"
        f"🎯 *Take Profit:* {trade['tp'] or '—'}\n"
        f"🛑 *Stop Loss:* {trade['sl'] or '—'}\n"
        f"💵 *Balance:* {trade['balance']} USDT\n"
    )
    bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg, parse_mode="Markdown")


# ============================
# SCHEDULES
# ============================

schedule.every(SCAN_INTERVAL).minutes.do(run_signal_monitor)
schedule.every().day.at("00:00").do(cleanup_old_logs)


# ============================
# MAIN BOT INITIALIZATION
# ============================

def main():
    log_event("START", "🚀 VerzekSignalBot launching...")

    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Register commands
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("status", status))
    dispatcher.add_handler(CommandHandler("logs", logs))

    # Register forwarder and watcher
    register_forwarder(dispatcher)
    watch_signal_channels(dispatcher, WATCHED_SIGNAL_SOURCES, SIGNAL_GROUP_IDS[0])

    # Start the bot
    updater.start_polling()
    log_event("SUCCESS", f"✅ Bot connected successfully! Monitoring {len(SIGNAL_GROUP_IDS)} groups.")
    updater.bot.send_message(chat_id=ADMIN_CHAT_ID, text="✅ VerzekSignalBot is now *LIVE*!", parse_mode="Markdown")

    # Continuous monitoring
    while True:
        schedule.run_pending()
        time.sleep(5)


if __name__ == "__main__":
    main()
