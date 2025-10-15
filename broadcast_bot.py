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

# Load sensitive values from environment variables
BROADCAST_BOT_TOKEN = os.getenv("BROADCAST_BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

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
    message = update.message
    
    # Get text from message or forwarded message
    text = (message.text or message.caption or "").strip()
    
    # If it's a forwarded message, get the original text
    if message.forward_from or message.forward_from_chat:
        logger.info(f"📥 Received forwarded message from admin")

    # Only accept from admin
    if user_id != ADMIN_CHAT_ID:
        return

    # Check for signal keywords
    if not any(k in text.upper() for k in KEYWORDS):
        logger.info("Ignored non-trading message.")
        return

    # Compose broadcast message with Verzek header
    header = "🔥 Signal Alert (Verzek Trading Signals)\n━━━━━━━━━━━━━━━━━━\n"
    msg = header + text

    try:
        bot.send_message(chat_id=VIP_GROUP_ID, text=msg)
        bot.send_message(chat_id=TRIAL_GROUP_ID, text=msg)
        logger.info(f"✅ Broadcast successful to VIP & TRIAL groups")
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

def auto_forward_signals(update, context):
    """Auto-forward signals from monitored channels to VIP and TRIAL groups"""
    message = update.message
    text = (message.text or message.caption or "").strip()
    
    if not text:
        return
    
    # CRITICAL: Prevent loop - NEVER forward from VIP/TRIAL groups
    chat_id = message.chat_id
    if chat_id == VIP_GROUP_ID or chat_id == TRIAL_GROUP_ID:
        return  # Ignore messages from our own broadcast targets
    
    # Prevent loop - ignore if message already has our header
    if "VERZEKSIGNALBOT" in text.upper() or "NEW SIGNAL ALERT" in text.upper():
        return
    
    # Check if message contains trading keywords
    if not any(k in text.upper() for k in KEYWORDS):
        return
    
    # Get source info
    source_chat = message.chat.title or message.chat.username or "Signal Source"
    
    # Format message with Verzek branding
    header = "🔥 Signal Alert (Verzek Trading Signals)\n━━━━━━━━━━━━━━━━━━\n"
    formatted_msg = header + text
    
    # Broadcast to VIP and TRIAL groups
    try:
        bot.send_message(chat_id=VIP_GROUP_ID, text=formatted_msg)
        bot.send_message(chat_id=TRIAL_GROUP_ID, text=formatted_msg)
        logger.info(f"📡 Auto-forwarded signal from {source_chat}")
        
        # Log it
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] AUTO-FORWARD from {source_chat}: {text}\n")
    except Exception as e:
        logger.error(f"⚠️ Auto-forward failed: {e}")


def main():
    updater = Updater(BROADCAST_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Handler for admin personal messages (manual broadcast)
    dp.add_handler(MessageHandler(
        Filters.text & ~Filters.command & Filters.private, 
        broadcast_message
    ))
    
    # Handler for signal source channels (auto-forward)
    dp.add_handler(MessageHandler(
        Filters.text & ~Filters.command & Filters.group,
        auto_forward_signals
    ))

    logger.info("🚀 VerzekBroadcastBot is now listening for admin signals and monitoring signal sources...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
