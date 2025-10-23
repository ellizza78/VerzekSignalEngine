"""
VerzekBroadcastBot v2.0 - Webhook Edition
------------------------------------------
Uses webhooks instead of polling to eliminate conflicts.
Listens to admin (personal chat) for Cornix-style signals and broadcasts
them with Verzek-branded header to VIP and TRIAL groups.
"""

import os
import time
import logging
import json
import requests
from telegram import Bot, Update
from signal_parser import parse_close_signal
from modules.dca_orchestrator import DCAOrchestrator

# Load config
CONFIG_PATH = "config/config.json"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

# Load sensitive values from environment variables
BROADCAST_BOT_TOKEN = os.getenv("BROADCAST_BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

# Webhook URL (Replit provides HTTPS)
WEBHOOK_URL = "https://verzek-auto-trader.replit.app/webhook/broadcast"

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

def process_message(update, context):
    """Process incoming messages (called by webhook)"""
    message = update.message
    if not message:
        return
    
    user_id = message.from_user.id if message.from_user else None
    chat_id = message.chat_id
    
    # Get text from message or forwarded message
    text = (message.text or message.caption or "").strip()
    
    if not text:
        return
    
    # If it's a forwarded message, get the original text
    if message.forward_from or message.forward_from_chat:
        logger.info(f"📥 Received forwarded message")
    
    # CRITICAL: Prevent loop - NEVER forward from VIP/TRIAL groups
    if chat_id == VIP_GROUP_ID or chat_id == TRIAL_GROUP_ID:
        return  # Ignore messages from our own broadcast targets
    
    # CRITICAL: Prevent loop - ignore if message already has our header
    if "VERZEK TRADING SIGNALS" in text.upper() or "SIGNAL ALERT" in text.upper():
        logger.info("Ignored message - already has Verzek header")
        return
    
    # Check for signal keywords
    if not any(k in text.upper() for k in KEYWORDS):
        logger.info("Ignored non-trading message.")
        return
    
    # Handle private messages from admin (manual broadcast)
    if message.chat.type == 'private' and user_id == ADMIN_CHAT_ID:
        broadcast_admin_message(message, text)
    
    # Handle group messages (auto-forward)
    elif message.chat.type in ['group', 'supergroup']:
        auto_forward_signal(message, text)

def broadcast_admin_message(message, text):
    """Process admin signal and distribute to both mobile app AND Telegram groups"""
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

    logger.info("📡 Processing admin signal (dual-channel: app + Telegram groups)")

    # Clean the signal
    cleaned_text = clean_signal(text)
    
    # Create branded header
    header = "🔥 VERZEK TRADING SIGNALS 🔥\n\n"
    formatted_message = header + cleaned_text

    # 1. Broadcast to VIP Group
    try:
        bot.send_message(chat_id=VIP_GROUP_ID, text=formatted_message)
        logger.info("✅ Broadcast to VIP group successful")
    except Exception as e:
        logger.error(f"Failed to send to VIP group: {e}")

    # 2. Broadcast to TRIAL Group
    try:
        bot.send_message(chat_id=TRIAL_GROUP_ID, text=formatted_message)
        logger.info("✅ Broadcast to TRIAL group successful")
    except Exception as e:
        logger.error(f"Failed to send to TRIAL group: {e}")

    # 3. Log signal to file (this feeds the mobile app via /api/signals)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {text}\n")
    
    logger.info(f"✅ Signal logged to broadcast_log.txt for mobile app access")

    # Confirmation to admin
    try:
        bot.send_message(chat_id=ADMIN_CHAT_ID, text="✅ Signal broadcast to VIP + TRIAL groups AND mobile app!")
    except Exception:
        pass

def auto_forward_signal(message, text):
    """Process signals from monitored channels and distribute to both mobile app AND Telegram groups"""
    # Get source info
    source_chat = message.chat.title or message.chat.username or "Signal Source"
    
    logger.info(f"📡 Processing signal from {source_chat} (dual-channel: app + Telegram groups)")
    
    # Clean the signal
    cleaned_text = clean_signal(text)
    
    # Create branded header
    header = f"🔥 VERZEK TRADING SIGNALS 🔥\n📡 Source: {source_chat}\n\n"
    formatted_message = header + cleaned_text

    # 1. Broadcast to VIP Group
    try:
        bot.send_message(chat_id=VIP_GROUP_ID, text=formatted_message)
        logger.info(f"✅ Auto-forwarded to VIP group from {source_chat}")
    except Exception as e:
        logger.error(f"Failed to send to VIP group: {e}")

    # 2. Broadcast to TRIAL Group
    try:
        bot.send_message(chat_id=TRIAL_GROUP_ID, text=formatted_message)
        logger.info(f"✅ Auto-forwarded to TRIAL group from {source_chat}")
    except Exception as e:
        logger.error(f"Failed to send to TRIAL group: {e}")

    # 3. Log signal to file (this feeds the mobile app via /api/signals)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] AUTO-FORWARD from {source_chat}: {text}\n")
    
    logger.info(f"✅ Signal from {source_chat} logged to broadcast_log.txt for mobile app access")

def setup_webhook():
    """Set up webhook with Telegram"""
    try:
        # Delete any existing webhook first
        bot.delete_webhook()
        logger.info("🗑️ Deleted existing webhook")
        
        # Set new webhook
        success = bot.set_webhook(
            url=WEBHOOK_URL,
            drop_pending_updates=True  # Clear any pending updates
        )
        
        if success:
            logger.info(f"✅ Webhook set successfully: {WEBHOOK_URL}")
            
            # Verify webhook info
            webhook_info = bot.get_webhook_info()
            logger.info(f"📡 Webhook URL: {webhook_info.url}")
            logger.info(f"📡 Pending updates: {webhook_info.pending_update_count}")
            return True
        else:
            logger.error("❌ Failed to set webhook")
            return False
    except Exception as e:
        logger.error(f"❌ Error setting up webhook: {e}")
        return False

def main():
    """Initialize webhook-based bot"""
    logger.info("🚀 VerzekBroadcastBot v2.0 (Webhook Edition) starting...")
    
    # Set up webhook with Telegram
    if setup_webhook():
        logger.info("✅ Webhook mode activated - no polling conflicts!")
        logger.info("📡 Listening for admin signals and monitoring signal sources...")
        logger.info("🔗 Webhook endpoint: /webhook/broadcast")
        
        # Register handlers with Flask app (if running in same process)
        try:
            from api_server import set_telegram_webhook_handler
            set_telegram_webhook_handler(bot, process_message)
            logger.info("✅ Handlers registered with Flask API")
        except ImportError:
            logger.warning("⚠️ Could not register handlers - Flask API not running in same process")
    else:
        logger.error("❌ Failed to set up webhook - bot will not receive messages")

if __name__ == "__main__":
    main()
