"""
VerzekBroadcastBot v1.1
------------------------
Listens to admin (personal chat) for Cornix-style signals and broadcasts
them with Verzek-branded header to VIP and TRIAL groups.
"""

import os
import time
import logging
import json
from telegram import Bot
from telegram.ext import Updater, MessageHandler, Filters

# Load config
CONFIG_PATH = "config/config.json"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

BROADCAST_BOT_TOKEN = config.get("broadcast_bot_token")
ADMIN_CHAT_ID = int(config.get("admin_chat_id"))

# Group IDs (set your actual ones)
VIP_GROUP_ID = -1002721581400
TRIAL_GROUP_ID = -1002726167386

LOG_FILE = "database/broadcast_log.txt"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("VerzekBroadcastBot")

bot = Bot(token=BROADCAST_BOT_TOKEN)

KEYWORDS = ("BUY", "SELL", "LONG", "SHORT", "ENTRY", "TP", "SL", "STOP LOSS")

def broadcast_message(update, context):
    user_id = update.effective_user.id
    text = (update.message.text or "").strip()

    # Only accept from admin
    if user_id != ADMIN_CHAT_ID:
        return

    # Check for signal keywords
    if not any(k in text.upper() for k in KEYWORDS):
        logger.info("Ignored non-trading message.")
        return

    # Compose broadcast message with Verzek header
    header = "🔥 New Signal Alert (VerzekSignalBot)\n━━━━━━━━━━━━━━━━━━\n"
    msg = header + text

    try:
        bot.send_message(chat_id=VIP_GROUP_ID, text=msg)
        bot.send_message(chat_id=TRIAL_GROUP_ID, text=msg)
    except Exception as e:
        logger.error(f"⚠️ Broadcast send failed: {e}")

    # Log it to file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {text}\n")

    # Confirmation to admin
    try:
        bot.send_message(chat_id=ADMIN_CHAT_ID, text="✅ Broadcast sent to VIP & TRIAL.")
    except Exception:
        pass

def main():
    updater = Updater(BROADCAST_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, broadcast_message))

    logger.info("🚀 VerzekBroadcastBot is now listening for admin signals...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
