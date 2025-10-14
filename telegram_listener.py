"""
telegram_listener.py
--------------------
Handles Telegram message listening and forwarding.
Includes:
- register_forwarder(): forwards incoming messages to VIP groups
- watch_signal_channels(): monitors external signal groups
- get_new_messages(): pulls latest messages for signal parsing
"""

import os
import time
from datetime import datetime
from telegram.ext import MessageHandler, Filters
from utils.logger import log_event

LOG_FILE = "database/forward_log.txt"


# ============================================================
# REGISTER FORWARDER FUNCTION
# ============================================================

def register_forwarder(dispatcher):
    """Forward messages from source channels to target VIP groups with source labeling."""
    def forward_message(update, context):
        message = update.message
        text = message.text or message.caption or ""

        if not text:
            return

        source_chat = message.chat.title or message.chat.username or "Unknown Source"
        formatted_msg = (
            f"📢 *Source:* Verzek Signal Bot\n"
            f"🗣 *Origin:* {source_chat}\n\n"
            f"{text}"
        )

        for group_id in context.bot_data.get("target_groups", []):
            try:
                context.bot.send_message(
                    chat_id=group_id,
                    text=formatted_msg,
                    parse_mode="Markdown"
                )
                save_to_log(source_chat, text)
                log_event("FORWARD", f"📤 Message forwarded from {source_chat} to {group_id}")
            except Exception as e:
                log_event("ERROR", f"❌ Failed to forward message: {e}")

    handler = MessageHandler(Filters.text & (~Filters.command), forward_message)
    dispatcher.add_handler(handler)
    log_event("INFO", "🔁 Forwarder registered successfully.")


# ============================================================
# WATCH SIGNAL CHANNELS
# ============================================================

def watch_signal_channels(dispatcher, source_ids, target_id):
    """Monitor multiple signal source groups and forward new messages to target."""
    from telegram import Bot
    import threading

    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN") or load_token_from_config())

    def watcher():
        last_msg_id = {}
        log_event("WATCH", f"📡 Watching {len(source_ids)} signal sources for updates...")

        while True:
            for src_id in source_ids:
                try:
                    updates = bot.get_chat(src_id)
                    messages = bot.get_updates(timeout=5)
                    for m in messages:
                        if not m.message or not hasattr(m.message, "text"):
                            continue
                        msg_id = m.message.message_id
                        if last_msg_id.get(src_id) == msg_id:
                            continue
                        last_msg_id[src_id] = msg_id

                        msg_text = m.message.text or m.message.caption
                        formatted = (
                            f"📢 *Source:* Verzek Signal Bot\n"
                            f"🗣 *Origin:* {updates.title}\n\n"
                            f"{msg_text}"
                        )
                        bot.send_message(chat_id=target_id, text=formatted, parse_mode="Markdown")
                        save_to_log(updates.title, msg_text)
                        log_event("WATCH", f"📡 Forwarded signal from {updates.title}")
                except Exception as e:
                    log_event("ERROR", f"⚠️ Watcher error: {e}")
            time.sleep(10)  # delay between checks

    threading.Thread(target=watcher, daemon=True).start()


# ============================================================
# MESSAGE FETCHER (USED BY SIGNAL MONITOR)
# ============================================================

def get_new_messages(group_id):
    """Fetch recent messages from a group for signal parsing."""
    from telegram import Bot
    bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN") or load_token_from_config())

    try:
        updates = bot.get_updates(timeout=5)
        messages = []
        for m in updates:
            if m.message and m.message.chat and m.message.chat.id == group_id:
                text = m.message.text or m.message.caption
                if text:
                    messages.append(text)
        return messages[-5:]  # return latest few messages only
    except Exception as e:
        log_event("ERROR", f"⚠️ Failed to fetch messages from {group_id}: {e}")
        return []


# ============================================================
# UTILITIES
# ============================================================

def save_to_log(source, text):
    """Save forwarded signal message to logs."""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {source}: {text}\n")


def load_token_from_config():
    """Fallback: load Telegram bot token from config.json"""
    try:
        import json
        with open("config/config.json", "r", encoding="utf-8") as f:
            cfg = json.load(f)
        return cfg["telegram_bot_token"]
    except Exception:
        raise RuntimeError("⚠️ Telegram bot token not found in environment or config.json!")

