"""
Pyrogram Signal Listener - Hybrid Approach
Listens to signal source channel with user account, broadcasts via Bot API
SAFETY: Read-only mode, random delays, residential proxy recommended
"""
import os
import sys
import time
import random
import requests
import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from utils.logger import api_logger

# ================== CONFIGURATION ==================

# Pyrogram User Session (for listening to source channel)
PYROGRAM_API_ID = int(os.getenv("PYROGRAM_API_ID", "0"))
PYROGRAM_API_HASH = os.getenv("PYROGRAM_API_HASH", "")
PYROGRAM_SESSION_NAME = os.getenv("PYROGRAM_SESSION_NAME", "verzek_listener")

# Signal Source Channel (where you subscribed with new account)
SIGNAL_SOURCE_CHANNEL = os.getenv("SIGNAL_SOURCE_CHANNEL", "")  # e.g., "@channelname" or "-100123456789"

# Bot API (for broadcasting to groups)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TRIAL_GROUP_ID = os.getenv("TELEGRAM_TRIAL_CHAT_ID", "")
VIP_GROUP_ID = os.getenv("TELEGRAM_VIP_CHAT_ID", "")

# Backend API
BACKEND_API_URL = os.getenv("API_BASE_URL", "https://verzekinnovative.com")

# Safety Settings
MIN_DELAY = float(os.getenv("LISTENER_MIN_DELAY", "3.0"))  # Min 3 seconds between actions
MAX_DELAY = float(os.getenv("LISTENER_MAX_DELAY", "8.0"))  # Max 8 seconds
MAX_SIGNALS_PER_HOUR = int(os.getenv("MAX_SIGNALS_PER_HOUR", "10"))  # Rate limit

# ================== VALIDATION ==================

def validate_config():
    """Validate all required environment variables"""
    missing = []
    
    if not PYROGRAM_API_ID or PYROGRAM_API_ID == 0:
        missing.append("PYROGRAM_API_ID")
    if not PYROGRAM_API_HASH:
        missing.append("PYROGRAM_API_HASH")
    if not SIGNAL_SOURCE_CHANNEL:
        missing.append("SIGNAL_SOURCE_CHANNEL")
    if not BOT_TOKEN:
        missing.append("TELEGRAM_BOT_TOKEN")
    if not TRIAL_GROUP_ID:
        missing.append("TELEGRAM_TRIAL_CHAT_ID")
    
    if missing:
        api_logger.error(f"Missing required secrets: {', '.join(missing)}")
        sys.exit(1)
    
    api_logger.info("✅ Configuration validated")


# ================== RATE LIMITING ==================

class RateLimiter:
    """Track signal processing rate to avoid spam"""
    def __init__(self, max_per_hour=10):
        self.max_per_hour = max_per_hour
        self.timestamps = []
    
    def can_process(self):
        """Check if we can process another signal"""
        now = time.time()
        # Remove timestamps older than 1 hour
        self.timestamps = [t for t in self.timestamps if now - t < 3600]
        
        if len(self.timestamps) >= self.max_per_hour:
            api_logger.warning(f"Rate limit hit: {self.max_per_hour} signals/hour")
            return False
        
        return True
    
    def record(self):
        """Record a processed signal"""
        self.timestamps.append(time.time())

rate_limiter = RateLimiter(MAX_SIGNALS_PER_HOUR)


# ================== BOT API BROADCASTING ==================

def send_to_bot(chat_id: str, text: str) -> bool:
    """Send message via Bot API (safe, official method)"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json().get("ok", False)
    except Exception as e:
        api_logger.error(f"Bot broadcast failed to {chat_id}: {e}")
        return False


def broadcast_to_groups(message_text: str) -> dict:
    """Broadcast signal to Trial and VIP groups via Bot API"""
    results = {
        "trial": False,
        "vip": False
    }
    
    # Send to Trial group
    if TRIAL_GROUP_ID:
        results["trial"] = send_to_bot(TRIAL_GROUP_ID, message_text)
        time.sleep(random.uniform(1, 2))  # Small delay between sends
    
    # Send to VIP group (if configured)
    if VIP_GROUP_ID:
        results["vip"] = send_to_bot(VIP_GROUP_ID, message_text)
    
    return results


def send_to_backend(signal_text: str) -> bool:
    """Send signal to backend API for processing"""
    url = f"{BACKEND_API_URL}/api/signals"
    
    payload = {
        "raw_signal": signal_text,
        "source": "telegram_listener",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        return response.status_code in [200, 201]
    except Exception as e:
        api_logger.error(f"Backend API failed: {e}")
        return False


# ================== SIGNAL PROCESSING ==================

def is_valid_signal(text: str) -> bool:
    """Basic validation to filter noise"""
    if not text:
        return False
    
    # Must contain key trading terms
    keywords = ["BTC", "ETH", "LONG", "SHORT", "ENTRY", "TP", "TARGET", "SL", "STOP"]
    text_upper = text.upper()
    
    # At least 2 keywords must match
    matches = sum(1 for keyword in keywords if keyword in text_upper)
    return matches >= 2


async def process_signal(message_text: str):
    """Process and broadcast signal with safety delays"""
    
    # Rate limiting
    if not rate_limiter.can_process():
        api_logger.warning("⚠️ Rate limit exceeded, skipping signal")
        return
    
    # Validation
    if not is_valid_signal(message_text):
        api_logger.info("🚫 Invalid signal format, skipping")
        return
    
    api_logger.info(f"📡 Processing signal: {message_text[:50]}...")
    
    # Human-like random delay before processing
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    api_logger.info(f"⏳ Waiting {delay:.1f}s (human-like delay)...")
    await asyncio.sleep(delay)
    
    # Format message for broadcast
    formatted_message = f"""
🔥 <b>VERZEK SIGNAL</b> 🔥

{message_text}

🤖 <i>Auto-forwarded from signal source</i>
⏰ <i>{datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</i>
    """.strip()
    
    # Broadcast to groups
    broadcast_results = broadcast_to_groups(formatted_message)
    api_logger.info(f"✅ Broadcast: Trial={broadcast_results['trial']}, VIP={broadcast_results['vip']}")
    
    # Send to backend API
    backend_success = send_to_backend(message_text)
    api_logger.info(f"📤 Backend API: {'✅ Success' if backend_success else '❌ Failed'}")
    
    # Record in rate limiter
    rate_limiter.record()


# ================== PYROGRAM CLIENT ==================

# Initialize Pyrogram client (USER SESSION - for listening only)
app = Client(
    name=PYROGRAM_SESSION_NAME,
    api_id=PYROGRAM_API_ID,
    api_hash=PYROGRAM_API_HASH,
    workdir="./sessions"  # Store session files in dedicated folder
)


@app.on_message(filters.chat(SIGNAL_SOURCE_CHANNEL) & filters.text)
async def handle_new_signal(client, message):
    """
    Listen to signal source channel (READ-ONLY)
    This is the SAFEST use of Pyrogram - passive listening only
    """
    try:
        message_text = message.text or message.caption or ""
        
        if not message_text.strip():
            return
        
        api_logger.info(f"🔔 New message from source channel")
        
        # Process signal asynchronously
        await process_signal(message_text)
        
    except FloodWait as e:
        api_logger.warning(f"⚠️ FloodWait: sleeping {e.value}s")
        await asyncio.sleep(e.value)
    except Exception as e:
        api_logger.error(f"❌ Error handling signal: {e}")


# ================== STARTUP & MONITORING ==================

@app.on_disconnect()
async def on_disconnect():
    """Handle disconnection gracefully"""
    api_logger.warning("🔌 Pyrogram disconnected, will auto-reconnect...")


async def startup_check():
    """Verify connection on startup"""
    try:
        me = await app.get_me()
        api_logger.info(f"✅ Logged in as: {me.first_name} (@{me.username or 'no_username'})")
        api_logger.info(f"📱 Phone: {me.phone_number}")
        
        # Verify we're subscribed to source channel
        try:
            chat = await app.get_chat(SIGNAL_SOURCE_CHANNEL)
            api_logger.info(f"✅ Monitoring channel: {chat.title or SIGNAL_SOURCE_CHANNEL}")
        except Exception as e:
            api_logger.error(f"❌ Can't access channel {SIGNAL_SOURCE_CHANNEL}: {e}")
            api_logger.error("Make sure your account is subscribed to the channel!")
    except Exception as e:
        api_logger.error(f"❌ Startup check failed: {e}")


# ================== MAIN ==================

def main():
    """Run the signal listener"""
    
    # Validate configuration
    validate_config()
    
    # Create sessions directory
    os.makedirs("./sessions", exist_ok=True)
    
    api_logger.info("=" * 60)
    api_logger.info("🚀 VERZEK SIGNAL LISTENER STARTING")
    api_logger.info("=" * 60)
    api_logger.info(f"📡 Source Channel: {SIGNAL_SOURCE_CHANNEL}")
    api_logger.info(f"🤖 Trial Group: {TRIAL_GROUP_ID}")
    api_logger.info(f"💎 VIP Group: {VIP_GROUP_ID or 'Not configured'}")
    api_logger.info(f"⏱️  Delay Range: {MIN_DELAY}-{MAX_DELAY}s")
    api_logger.info(f"📊 Rate Limit: {MAX_SIGNALS_PER_HOUR} signals/hour")
    api_logger.info("=" * 60)
    
    # Register startup hook
    @app.on_message(filters.me)
    async def on_ready(client, message):
        """Run startup check on first message"""
        await startup_check()
    
    # Run Pyrogram client
    try:
        app.run()
    except KeyboardInterrupt:
        api_logger.info("\n⏹️  Listener stopped by user")
    except Exception as e:
        api_logger.error(f"❌ Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
