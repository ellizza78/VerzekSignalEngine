"""
VerzekTelethonForwarder v2.1
----------------------------
Monitors your Telegram account for signal-like messages and forwards them
to your Broadcast Bot (which then broadcasts to VIP & TRIAL).
Fixed: Database locking issues with StringSession
"""

import hashlib
import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- YOUR TELEGRAM CREDENTIALS ---
api_id = 26395582
api_hash = "a32cb77b68ad84fb0dd60531d83698dc"

# --- BROADCAST BOT USERNAME (change this to your actual bot username) ---
BROADCAST_BOT_USERNAME = "broadnews_bot"  # Replace with your broadcast bot username

# --- TARGET GROUPS (for loop prevention only) ---
VIP_GROUP_ID = -1002721581400
TRIAL_GROUP_ID = -1002726167386
TARGET_IDS = {VIP_GROUP_ID, TRIAL_GROUP_ID}

# --- SIGNAL KEYWORDS ---
KEYWORDS = (
    "BUY", "SELL", "LONG", "SHORT", "ENTRY", "TP", "SL", 
    "STOP LOSS", "TARGETS", "TARGET", "PROFIT", "LOSS",
    "LEV", "LEVERAGE", "SIGNAL", "USDT", "/USDT",
    "ACHIEVED", "CLOSED", "TAKE-PROFIT", "TAKE PROFIT", "GAINED",
    "GAINED PROFIT", "ALL TAKE-PROFIT TARGETS ACHIEVED"
)

# --- Init client with StringSession (no DB locks) ---
# Load session string from environment or file
session_file = "telethon_session_string.txt"
if os.path.exists(session_file):
    with open(session_file, "r") as f:
        session_string = f.read().strip()
    client = TelegramClient(StringSession(session_string), api_id, api_hash)
else:
    # First time: create new session
    client = TelegramClient(StringSession(), api_id, api_hash)

# simple rolling de-dupe cache
_recent = []
_recent_set = set()
def seen_before(text: str) -> bool:
    h = hashlib.sha1(text.strip().encode("utf-8", errors="ignore")).hexdigest()
    if h in _recent_set:
        return True
    _recent.append(h)
    _recent_set.add(h)
    if len(_recent) > 300:  # keep last 300 messages
        old = _recent.pop(0)
        _recent_set.discard(old)
    return False

@client.on(events.NewMessage(incoming=True))
async def auto_forward(event):
    text = (event.message.message or "").strip()
    if not text:
        return

    # 1) Do not process messages you SENT (outgoing)
    if event.out:
        return

    # 2) Do not process messages already in VIP/TRIAL groups (loop prevention)
    if event.chat_id in TARGET_IDS:
        return

    # 3) Block known spammers by username
    BLOCKED_USERS = ["powellnolan", "sanjay_message_bot", "officialroyalqbot"]  # Add spammer usernames here (lowercase)
    
    try:
        sender = await event.get_sender()
        username = (sender.username or "").lower()
        
        # Block broadcast bot to prevent loops
        if username == BROADCAST_BOT_USERNAME.lower():
            return
        
        # Block known spammers
        if username in BLOCKED_USERS:
            print(f"🚫 Blocked message from spammer: @{username}")
            return
    except Exception:
        pass

    # 4) Prevent loops by header text check
    upper = text.upper()
    if "VERZEKSIGNALBOT" in upper or "NEW SIGNAL ALERT" in upper:
        return

    # 5) Block spam/promotional messages (common spam keywords)
    SPAM_KEYWORDS = (
        "HOW TO", "GUIDE", "MANUAL", "TUTORIAL", "INSTRUCTIONS",
        "WRITE ME", "CONTACT", "DM ME", "DIRECT MESSAGE", "REACH OUT",
        "JOIN OUR", "JOIN US", "PARTICIPATE", "PUMP GROUP", "VIP GROUP",
        "SUBSCRIBE", "CHANNEL", "VIDEO GUIDE", "TEXT MANUAL",
        "CRYPTO PUMP", "PUMP AND", "YESTERDAY", "REVEALED", 
        "PROVEN SYSTEM", "BUILD TRUST", "FULL STORY", "NO LUCK",
        "DISCIPLINE", "BE PART", "NEXT BIG", "MAKE PROFIT",
        "WHAT IS A", "HOW IT WORKS", "WHY IT", "EXAMPLE",
        "PICK A COIN", "BUY TOGETHER", "ATTRACTS", "COORDINATED",
        "HYPERLIQUID", "NO KYC", "NO RESTRICTIONS", "INSTANT SIGNUP",
        "GLOBAL ACCESS", "BREAK FREE", "TRADE WITHOUT",
        "GN, TRADERS", "GOOD NIGHT", "REST UP", "PRODUCTIVE DAY",
        "GROWING OUR", "FINE-TUNING", "STEP BY STEP",
        "GOLDENCRYPTOSIGNALS", "AI GOLDEN", "AUTO-DETECTS", "BUILT BY",
        "CLOSED SOURCE", "FREE FOR ALL", "TRADINGVIEW USERS",
        "INVITE LINK", "T.ME/", "BINARYBOSS", "BITNOBLES"
    )
    
    spam_hits = sum(k in upper for k in SPAM_KEYWORDS)
    if spam_hits >= 2:
        print(f"⛔ Blocked spam/promotional message")
        return
    
    # 5.5) Block obvious invite link spam (single keyword match for these)
    INVITE_SPAM_PATTERNS = ["T.ME/", "INVITE LINK"]
    if any(pattern in upper for pattern in INVITE_SPAM_PATTERNS):
        print(f"🚫 Blocked invite link spam")
        return
    
    # 6) Only act on signal-like content (>= 2 keywords)
    hits = sum(k in upper for k in KEYWORDS)
    if hits < 2:
        return

    # 7) De-duplicate exact same text
    if seen_before(text):
        print(f"⏭️ Skipped duplicate signal")
        return

    # 8) Send RAW signal to broadcast bot (bot will add header)
    try:
        await client.send_message(BROADCAST_BOT_USERNAME, text)
        print(f"✅ Sent signal to broadcast bot from chat {event.chat_id}: {text[:90]}...")
    except Exception as e:
        print(f"⚠️ Failed to send to broadcast bot: {e}")

print("🚀 VerzekTelethonForwarder is now monitoring your messages...")
client.start()

# Save session string for future use (no DB needed)
session_file = "telethon_session_string.txt"
if not os.path.exists(session_file):
    session_string = client.session.save()
    with open(session_file, "w") as f:
        f.write(session_string)
    print(f"✅ Session saved to {session_file}")

client.run_until_disconnected()