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
from signal_parser import parse_close_signal
from modules.dca_orchestrator import DCAOrchestrator

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

# Initialize DCA Orchestrator for auto-close functionality
orchestrator = DCAOrchestrator()

KEYWORDS = (
    "BUY", "SELL", "LONG", "SHORT", "ENTRY", "TP", "SL", 
    "STOP LOSS", "TARGETS", "TARGET", "PROFIT", "LOSS",
    "LEV", "LEVERAGE", "SIGNAL", "USDT", "/USDT", "REACHED", "CANCELLED",
    "ACHIEVED", "CLOSED", "TAKE-PROFIT", "TAKE PROFIT", "GAINED"
)

def clean_signal(text):
    """Remove unwanted formatting from signals"""
    import re
    
    # Process line by line to preserve structure
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Remove only # symbol but keep the word (e.g., #BTCUSDT -> BTCUSDT)
        line = re.sub(r'#', '', line)
        
        # Remove leverage indicators (Lev x26, Lev: x10, etc.)
        line = re.sub(r'Lev\s*:?\s*x?\d+', '', line, flags=re.IGNORECASE)
        
        # Remove extra emojis (optional cleanup)
        line = re.sub(r'🩸', '', line)
        
        # Clean up multiple spaces on the same line
        line = re.sub(r' {2,}', ' ', line)
        
        # Strip leading/trailing whitespace
        line = line.strip()
        
        # Keep non-empty lines
        if line:
            cleaned_lines.append(line)
    
    # Join lines and clean up excessive blank lines
    result = '\n'.join(cleaned_lines)
    result = re.sub(r'\n{3,}', '\n\n', result)
    
    return result.strip()

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

    # Prevent re-broadcasting if message already has our header
    if "VERZEK TRADING SIGNALS" in text.upper() or "SIGNAL ALERT" in text.upper():
        logger.info("Ignored message - already has Verzek header")
        return
    
    # Check for signal keywords
    if not any(k in text.upper() for k in KEYWORDS):
        logger.info("Ignored non-trading message.")
        return
    
    # Check if this is a close/cancel signal
    close_signal = parse_close_signal(text)
    if close_signal and close_signal.get("symbol"):
        symbol = close_signal["symbol"]
        reason = close_signal["reason"]
        
        logger.info(f"🛑 Detected close signal for {symbol}: {reason}")
        
        # Trigger auto-close for all active positions of this symbol
        try:
            result = orchestrator.auto_close_positions(symbol, reason)
            if result.get("success"):
                logger.info(f"✅ Auto-closed {result.get('closed_count', 0)} positions for {symbol}")
            else:
                logger.info(f"ℹ️ {result.get('message', 'No positions to close')}")
        except Exception as e:
            logger.error(f"⚠️ Error auto-closing positions for {symbol}: {e}")

    # Clean the signal (remove hashtags, leverage indicators, etc.)
    cleaned_text = clean_signal(text)
    
    # Compose broadcast message with Verzek header
    header = "🔥 Signal Alert (Verzek Trading Signals)\n━━━━━━━━━━━━━━━━━━\n"
    msg = header + cleaned_text

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
    
    # CRITICAL: Prevent loop - ignore if message already has our header
    if "VERZEK TRADING SIGNALS" in text.upper() or "SIGNAL ALERT" in text.upper():
        logger.info("Ignored message from group - already has Verzek header")
        return
    
    # Check if message contains trading keywords
    if not any(k in text.upper() for k in KEYWORDS):
        return
    
    # Get source info
    source_chat = message.chat.title or message.chat.username or "Signal Source"
    
    # Clean the signal (remove hashtags, leverage indicators, etc.)
    cleaned_text = clean_signal(text)
    
    # Format message with Verzek branding
    header = "🔥 Signal Alert (Verzek Trading Signals)\n━━━━━━━━━━━━━━━━━━\n"
    formatted_msg = header + cleaned_text
    
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
