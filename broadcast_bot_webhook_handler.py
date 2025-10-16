"""
Broadcast Bot Webhook Handler
------------------------------
Processes Telegram webhook updates for the broadcast bot.
Imported by Flask API to handle incoming messages.
"""

import os
import time
import logging
import json
import re
from telegram import Bot, Update
from signal_parser import parse_close_signal
from modules.dca_orchestrator import DCAOrchestrator

# Load sensitive values from environment variables
BROADCAST_BOT_TOKEN = os.getenv("BROADCAST_BOT_TOKEN")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))

# Group IDs
VIP_GROUP_ID = -1002721581400
TRIAL_GROUP_ID = -1002726167386

LOG_FILE = "database/broadcast_log.txt"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("BroadcastWebhookHandler")

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

def is_spam_or_profit_alert(text):
    """Check if message is a profit alert or spam"""
    text_upper = text.upper()
    
    # Profit alert indicators
    profit_indicators = [
        "PROFIT COLLECTED",
        "TARGET REACHED",
        "GAIN:",
        "GAINED",
        "% PROFIT",
        "ACHIEVED",
        "POSTED:"
    ]
    
    # Spam indicators
    spam_indicators = [
        "JOIN OUR",
        "CLICK HERE",
        "HTTP://",
        "HTTPS://",
        "T.ME/",
        "TELEGRAM.ME/",
        "@"
    ]
    
    # Check for profit alerts
    if any(indicator in text_upper for indicator in profit_indicators):
        # If it also has a percentage and "Posted:" it's definitely a profit alert
        if "%" in text and "POSTED:" in text_upper:
            return True
    
    # Check for spam
    if any(indicator in text_upper for indicator in spam_indicators):
        return True
    
    return False

def broadcast_admin_message(message, text):
    """Broadcast message from admin"""
    # Check if it's spam/profit alert
    if is_spam_or_profit_alert(text):
        logger.info("📛 Ignored profit alert or spam message")
        try:
            bot.send_message(
                chat_id=ADMIN_CHAT_ID, 
                text="📛 Message ignored: Detected as profit alert or spam"
            )
        except:
            pass
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

def auto_forward_signal(message, text):
    """Auto-forward signals from monitored channels to VIP and TRIAL groups"""
    # Check if it's spam/profit alert
    if is_spam_or_profit_alert(text):
        logger.info("📛 Ignored profit alert or spam message from group")
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

def handle_webhook_update(update_data):
    """Process incoming webhook update from Telegram"""
    try:
        # Create Update object from webhook data
        update = Update.de_json(update_data, bot)
        
        if not update or not update.message:
            logger.info("Webhook: No message in update")
            return
        
        message = update.message
        user_id = message.from_user.id if message.from_user else None
        chat_id = message.chat_id
        
        # Get text from message or forwarded message
        text = (message.text or message.caption or "").strip()
        
        if not text:
            return
        
        logger.info(f"📥 Webhook received message from chat_id={chat_id}, user_id={user_id}")
        
        # CRITICAL: Prevent loop - NEVER forward from VIP/TRIAL groups
        if chat_id == VIP_GROUP_ID or chat_id == TRIAL_GROUP_ID:
            logger.info("Ignored message from VIP/TRIAL group")
            return
        
        # CRITICAL: Prevent loop - ignore if message already has our header
        if "VERZEK TRADING SIGNALS" in text.upper() or "SIGNAL ALERT" in text.upper():
            logger.info("Ignored message - already has Verzek header")
            return
        
        # Check for signal keywords
        if not any(k in text.upper() for k in KEYWORDS):
            logger.info("Ignored non-trading message")
            return
        
        # Handle private messages from admin (manual broadcast)
        if message.chat.type == 'private' and user_id == ADMIN_CHAT_ID:
            logger.info("Processing admin broadcast")
            broadcast_admin_message(message, text)
        
        # Handle group messages (auto-forward)
        elif message.chat.type in ['group', 'supergroup']:
            logger.info("Processing auto-forward from group")
            auto_forward_signal(message, text)
        
    except Exception as e:
        logger.error(f"❌ Error handling webhook update: {e}")
        import traceback
        traceback.print_exc()
