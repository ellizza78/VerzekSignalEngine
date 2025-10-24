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
from modules.signal_auto_trader import signal_auto_trader

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

def is_priority_signal(text):
    """Check if signal is marked as high priority for auto-trading"""
    text_upper = text.upper()
    
    # Priority indicators from signal providers
    priority_keywords = [
        "SETUP AUTO-TRADE",
        "SETUP AUTOTRADE",
        "AUTO-TRADE SETUP",
        "AUTOTRADE SETUP",
        "PRIORITY SIGNAL",
        "HIGH PRIORITY"
    ]
    
    return any(keyword in text_upper for keyword in priority_keywords)

def is_spam(text):
    """Check if message is spam (invite links, URLs, etc.)"""
    text_upper = text.upper()
    
    # Spam indicators - ONLY block actual spam, not profit alerts
    spam_indicators = [
        "JOIN OUR",
        "CLICK HERE",
        "HTTP://",
        "HTTPS://",
        "T.ME/",
        "TELEGRAM.ME/"
    ]
    
    # Check for spam indicators
    if any(indicator in text_upper for indicator in spam_indicators):
        return True
    
    # Block messages that are ONLY an @ mention (invite spam)
    # But allow @ symbols in regular messages
    if text.strip().startswith("@") and len(text.strip().split()) == 1:
        return True
    
    return False

def broadcast_admin_message(message, text):
    """Broadcast message from admin"""
    # Check if it's spam
    if is_spam(text):
        logger.info("📛 Ignored spam message")
        try:
            bot.send_message(
                chat_id=ADMIN_CHAT_ID, 
                text="📛 Message ignored: Detected as spam (invite link/URL)"
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

    # Check if this is a priority signal
    is_priority = is_priority_signal(text)
    
    # Clean the signal (remove hashtags, leverage indicators, etc.)
    cleaned_text = clean_signal(text)
    
    # Log priority status
    if is_priority:
        logger.info("⚡ Processing PRIORITY signal (dual-channel: app + Telegram groups)")
    else:
        logger.info("📡 Processing signal (dual-channel: app + Telegram groups)")

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

    # 4. Trigger auto-trading for eligible users (PREMIUM plan only)
    try:
        auto_trade_result = signal_auto_trader.process_signal_for_auto_trading(text, provider="admin")
        if auto_trade_result.get("users_traded", 0) > 0:
            priority_tag = "⚡ PRIORITY " if is_priority else ""
            logger.info(f"✅ {priority_tag}Auto-traded for {auto_trade_result['users_traded']} PREMIUM users")
    except Exception as e:
        logger.error(f"⚠️ Auto-trade processing failed: {e}")

    # Confirmation to admin
    try:
        bot.send_message(chat_id=ADMIN_CHAT_ID, text="✅ Signal broadcast to VIP + TRIAL groups, mobile app, AND auto-traded!")
    except Exception:
        pass

def auto_forward_signal(message, text):
    """Process signals from monitored channels and distribute to both mobile app AND Telegram groups"""
    # Check if it's spam
    if is_spam(text):
        logger.info("📛 Ignored spam message from group")
        return
    
    # Get source info
    source_chat = message.chat.title or message.chat.username or "Signal Source"
    
    # Check if this is a priority signal
    is_priority = is_priority_signal(text)
    
    # Clean the signal
    cleaned_text = clean_signal(text)
    
    # Log priority status
    if is_priority:
        logger.info(f"⚡ Processing PRIORITY signal from {source_chat} (dual-channel: app + Telegram groups)")
    else:
        logger.info(f"📡 Processing signal from {source_chat} (dual-channel: app + Telegram groups)")
    
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
    
    # 4. Trigger auto-trading for eligible users (PREMIUM plan only)
    try:
        auto_trade_result = signal_auto_trader.process_signal_for_auto_trading(text, provider=source_chat)
        if auto_trade_result.get("users_traded", 0) > 0:
            priority_tag = "⚡ PRIORITY " if is_priority else ""
            logger.info(f"✅ {priority_tag}Auto-traded for {auto_trade_result['users_traded']} PREMIUM users from {source_chat}")
    except Exception as e:
        logger.error(f"⚠️ Auto-trade processing failed: {e}")

def handle_webhook_update(update_data):
    """Process incoming webhook update from Telegram"""
    try:
        # Parse webhook data directly (avoid Telegram library parsing issues)
        if not update_data or 'message' not in update_data:
            logger.info("Webhook: No message in update")
            return
        
        message_data = update_data['message']
        
        # Extract key fields directly from JSON
        user_id = message_data.get('from', {}).get('id')
        chat_id = message_data.get('chat', {}).get('id')
        chat_type = message_data.get('chat', {}).get('type', 'private')
        text = (message_data.get('text') or message_data.get('caption', '')).strip()
        
        if not text:
            logger.info("Webhook: Empty message text")
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
        
        # Create a minimal message-like object for compatibility
        class SimpleMessage:
            def __init__(self, data):
                self.text = text
                self.chat_id = chat_id
                self.chat = type('obj', (object,), {
                    'type': chat_type,
                    'title': data.get('chat', {}).get('title'),
                    'username': data.get('chat', {}).get('username')
                })()
                self.from_user = type('obj', (object,), {'id': user_id})() if user_id else None
        
        simple_message = SimpleMessage(message_data)
        
        # Handle private messages from admin (manual broadcast)
        if chat_type == 'private' and user_id == ADMIN_CHAT_ID:
            logger.info("Processing admin broadcast")
            broadcast_admin_message(simple_message, text)
        
        # Handle group messages (auto-forward)
        elif chat_type in ['group', 'supergroup']:
            logger.info("Processing auto-forward from group")
            auto_forward_signal(simple_message, text)
        
    except Exception as e:
        logger.error(f"❌ Error handling webhook update: {e}")
        import traceback
        traceback.print_exc()
