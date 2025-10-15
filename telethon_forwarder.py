"""
VerzekTelethonForwarder v1.2
----------------------------
Monitors your Telegram account for signal-like messages and forwards them
to VIP & TRIAL, with loop-prevention and de-duplication.
"""

import hashlib
from telethon import TelegramClient, events

# --- YOUR TELEGRAM CREDENTIALS ---
api_id = 26395582
api_hash = "a32cb77b68ad84fb0dd60531d83698dc"

# --- TARGET GROUPS ---
VIP_GROUP_ID = -1002721581400
TRIAL_GROUP_ID = -1002726167386
TARGET_IDS = {VIP_GROUP_ID, TRIAL_GROUP_ID}

# --- OPTIONAL: ignore messages sent by these usernames (bots, helpers) ---
IGNORE_USERNAMES = {"broadnews_bot"}  # your broadcaster username

# --- SIGNAL KEYWORDS ---
KEYWORDS = ("BUY", "SELL", "LONG", "SHORT", "ENTRY", "TP", "SL", "STOP LOSS")

# --- Init client ---
client = TelegramClient("verzek_forwarder_session", api_id, api_hash)

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

    # 2) Do not process messages already in our TARGET groups
    if event.chat_id in TARGET_IDS:
        return

    # 3) Ignore messages from our own broadcast bot (or other usernames)
    try:
        sender = await event.get_sender()
        username = (sender.username or "").lower()
        if username in IGNORE_USERNAMES:
            return
    except Exception:
        pass  # if we can't fetch sender, continue with other guards

    # 4) Prevent loops by header text check
    upper = text.upper()
    if "VERZEKSIGNALBOT" in upper or "AUTOFORWARD" in upper:
        return

    # 5) Only act on signal-like content (>= 2 keywords)
    hits = sum(k in upper for k in KEYWORDS)
    if hits < 2:
        return

    # 6) De-duplicate exact same text
    if seen_before(text):
        return

    # 7) Compose clean message and send once to each target
    header = "🔥 Auto-Detected Signal (Verzek AutoForward)\n━━━━━━━━━━━━━━━━━━\n"
    msg = header + text

    try:
        await client.send_message(VIP_GROUP_ID, msg)
        await client.send_message(TRIAL_GROUP_ID, msg)
        print(f"✅ Forwarded clean signal from chat {event.chat_id}: {text[:90]}...")
    except Exception as e:
        print(f"⚠️ Forward failed: {e}")

print("🚀 VerzekTelethonForwarder is now monitoring your messages...")
client.start()
client.run_until_disconnected()