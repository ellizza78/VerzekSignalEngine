# signal_forwarder.py
from utils.logger import log_event

def format_signal_message(signal_data):
    """Create a beautiful message for Telegram alerts."""
    direction_emoji = "🟢" if signal_data["direction"] == "LONG" else "🔴"

    text = (
        f"{direction_emoji} *{signal_data['direction']} SIGNAL*\n"
        f"💰 *Pair:* {signal_data['symbol']}\n"
        f"🎯 *Entry:* {signal_data.get('entry', 'Market')}\n"
        f"🎯 *TP:* {', '.join(map(str, signal_data.get('tp', [])))}\n"
        f"🛑 *SL:* {signal_data.get('sl', 'Not specified')}\n"
    )
    return text

def forward_signal(bot, chat_id, signal_data):
    """Send parsed signal to a Telegram chat."""
    if not signal_data:
        log_event("INFO", "⚠️ No valid signal to forward.")
        return

    try:
        msg = format_signal_message(signal_data)
        bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown")
        log_event("SUCCESS", f"📤 Signal forwarded to chat {chat_id}")
    except Exception as e:
        log_event("ERROR", f"Failed to forward signal: {e}")


