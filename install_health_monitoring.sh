#!/bin/bash
################################################################################
# VerzekAutoTrader - One-Click Health Monitoring Installation
# Phase 1 + 2: Heartbeat Monitoring + Auto-Restart + Telegram Alerts
################################################################################

echo "🚀 Installing Forwarder Health Monitoring System..."
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo "❌ Please run as root"
   exit 1
fi

cd /var/www/VerzekAutoTrader || exit 1

echo "📋 Step 1: Stopping current forwarder..."
pkill -f telethon_forwarder.py
sleep 2
echo "  ✅ Stopped"

echo ""
echo "📋 Step 2: Creating telethon_forwarder.py v2.2 (with heartbeat)..."
cat > telethon_forwarder.py << 'FORWARDER_EOF'
"""
VerzekTelethonForwarder v2.2
----------------------------
Monitors your Telegram account for signal-like messages and forwards them
to your Broadcast Bot (which then broadcasts to VIP & TRIAL).
Fixed: Database locking issues with StringSession
Added: Heartbeat monitoring and faster async requests
"""

import hashlib
import os
import json
import asyncio
import requests
from datetime import datetime
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# --- YOUR TELEGRAM CREDENTIALS (REQUIRED from environment variables) ---
api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")

if not api_id or not api_hash:
    print("\n❌ ERROR: Missing Telegram API credentials!")
    print("Please set the following environment variables in Replit Secrets:")
    print("  - TELEGRAM_API_ID")
    print("  - TELEGRAM_API_HASH")
    print("\nGet your credentials from: https://my.telegram.org/apps")
    import sys
    sys.exit(1)

api_id = int(api_id)

# --- BROADCAST BOT USERNAME (change this to your actual bot username) ---
BROADCAST_BOT_USERNAME = "broadnews_bot"  # Replace with your broadcast bot username

# --- MONITORED CHANNELS (signals from these channels will be forwarded) ---
# Add channel usernames or IDs here (without @)
MONITORED_CHANNELS = [
    -1002249790469,  # Ai Golden Crypto (🔱VIP) - PAID VIP CHANNEL - PRIMARY SIGNAL SOURCE (15 subscribers)
    # Add more signal channels below as needed
]

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
# Use ENVIRONMENT-SPECIFIC sessions to prevent dual-IP conflicts
# Production and development use completely separate sessions
is_production = os.getenv("REPLIT_DEPLOYMENT") == "1"
session_file = "telethon_session_prod.txt" if is_production else "telethon_session_dev.txt"

print(f"[TELETHON] Loading {'PRODUCTION' if is_production else 'DEVELOPMENT'} session: {session_file}")

if os.path.exists(session_file):
    with open(session_file, "r") as f:
        session_string = f.read().strip()
    client = TelegramClient(StringSession(session_string), api_id, api_hash)
    print(f"[TELETHON] Using existing session from {session_file}")
else:
    # No environment-specific session found
    print(f"[TELETHON] ERROR: No {session_file} found!")
    print(f"[TELETHON] Run 'python setup_telethon.py' to create production session")
    print(f"[TELETHON] Or run 'python recover_telethon_session.py' if session is corrupted")
    import sys
    sys.exit(1)

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

# --- HEARTBEAT MONITORING ---
HEARTBEAT_FILE = "/tmp/forwarder_heartbeat.json"
last_signal_time = None

async def heartbeat_task():
    """Updates heartbeat file every 30 seconds to prove forwarder is alive"""
    while True:
        try:
            heartbeat_data = {
                "timestamp": datetime.now().isoformat(),
                "status": "running",
                "last_signal": last_signal_time.isoformat() if last_signal_time else None,
                "pid": os.getpid()
            }
            with open(HEARTBEAT_FILE, "w") as f:
                json.dump(heartbeat_data, f)
        except Exception as e:
            print(f"⚠️ Heartbeat write failed: {e}")
        await asyncio.sleep(30)  # Update every 30 seconds

@client.on(events.NewMessage(chats=MONITORED_CHANNELS, incoming=True))
async def auto_forward(event):
    text = (event.message.message or "").strip()
    if not text:
        return

    # DEBUG: Log ALL incoming messages
    print(f"🔔 Received message from chat {event.chat_id}: {text[:50]}...")

    # 1) Do not process messages you SENT (outgoing)
    if event.out:
        print(f"⏭️ Skipped outgoing message")
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

    # 5) Check if message is from a monitored channel (always allow these)
    from_monitored_channel = False
    try:
        chat = await event.get_chat()
        chat_id = getattr(chat, 'id', None)
        chat_username = (getattr(chat, 'username', None) or "").lower()
        
        # Check both username and ID
        for monitored in MONITORED_CHANNELS:
            if isinstance(monitored, int):
                if chat_id == monitored:
                    from_monitored_channel = True
                    print(f"📢 Message from monitored channel ID: {chat_id}")
                    break
            elif isinstance(monitored, str):
                if chat_username and chat_username == monitored.lower():
                    from_monitored_channel = True
                    print(f"📢 Message from monitored channel: @{chat_username}")
                    break
    except Exception as e:
        pass
    
    # 6) Smart filtering for MONITORED CHANNELS - only allow real signals and updates
    if from_monitored_channel:
        # Check if this is a REAL signal (has trading details)
        is_real_signal = any([
            # New signal with entry/targets
            ("ENTRY" in upper and "TARGET" in upper),
            ("ENTRY" in upper and "STOP LOSS" in upper),
            # Trade update notifications
            ("TARGET" in upper and "REACHED" in upper),
            ("PROFIT COLLECTED" in upper),
            ("CLOSED" in upper and "PROFIT" in upper),
            # Trade close/cancel signals (CRITICAL for auto-stop)
            ("CLOSED" in upper and "USDT" in upper),
            ("CANCELLED" in upper and "USDT" in upper),
            ("STOPPED" in upper and "USDT" in upper),
            ("STOP LOSS" in upper and "USDT" in upper),
            ("SL HIT" in upper),
            # Signal format markers
            ("#SIGNAL" in upper and ("/USDT" in upper or "USDT" in upper)),
        ])
        
        # Block promotional content even from monitored channels
        PROMO_KEYWORDS = [
            "SETUP AUTO-TRADE",
            "CLAIM BONUS",
            "EXCLUSIVE BENEFIT",
            "PINNED MESSAGE",
            "INVITE LINK",
            "T.ME/",
            "JOIN",
            "SUBSCRIBE",
            "GUIDE",
            "TUTORIAL",
            "HOW TO",
            "CLICK HERE",
            "TAP HERE",
        ]
        
        is_promotional = any(keyword in upper for keyword in PROMO_KEYWORDS)
        
        if is_promotional and not is_real_signal:
            print(f"🚫 Blocked promotional content from monitored channel")
            return
        
        if not is_real_signal:
            print(f"⏭️ Skipped non-signal message from monitored channel")
            return
    
    # 7) Block spam/promotional messages (for non-monitored channels)
    if not from_monitored_channel:
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
            "GOLDENCRYPTOSIGNALS", "AUTO-DETECTS", "BUILT BY",
            "CLOSED SOURCE", "FREE FOR ALL", "TRADINGVIEW USERS",
            "INVITE LINK", "T.ME/", "BINARYBOSS", "BITNOBLES",
            "AUTOTRADE GOLDEN BOT", "AUTOTRADE BOT", "PORTFOLIO GROWTH",
            "SUPERX SHOWDOWN", "PREDICT BTC", "LUCKY DRAW", "DUAL LEADERBOARDS",
            "TRADING VOLUME", "ROI CONTESTS", "PRIZE POOL"
        )
    
        spam_hits = sum(k in upper for k in SPAM_KEYWORDS)
        if spam_hits >= 2:
            print(f"⛔ Blocked spam/promotional message")
            return
        
        # 7.5) Block obvious invite link spam (single keyword match for these)
        INVITE_SPAM_PATTERNS = ["T.ME/", "INVITE LINK"]
        if any(pattern in upper for pattern in INVITE_SPAM_PATTERNS):
            print(f"🚫 Blocked invite link spam")
            return
    
    # 8) Only act on signal-like content (>= 2 keywords) for non-monitored channels
    # Monitored channels already passed smart filtering above
    if not from_monitored_channel:
        hits = sum(k in upper for k in KEYWORDS)
        if hits < 2:
            return

    # 9) De-duplicate exact same text
    if seen_before(text):
        print(f"⏭️ Skipped duplicate signal")
        return

    # 10) Send RAW signal to broadcast bot via direct HTTP POST (with timeout)
    global last_signal_time
    last_signal_time = datetime.now()
    
    try:
        # Get source info
        try:
            chat = await event.get_chat()
            source_name = getattr(chat, 'title', None) or getattr(chat, 'username', None) or "Unknown"
        except Exception as chat_err:
            source_name = "Unknown"
            print(f"⚠️ Could not get chat info: {chat_err}")
        
        # Send directly to our webhook handler via HTTP
        webhook_url = "http://127.0.0.1:5000/api/broadcast/signal"
        
        payload = {
            "text": text,
            "source": source_name,
            "source_type": "channel" if from_monitored_channel else "personal_chat",
            "chat_id": str(event.chat_id)
        }
        
        print(f"📤 Sending signal to Flask API: {source_name} ({payload['source_type']})")
        
        # Use shorter timeout to prevent blocking
        response = requests.post(webhook_url, json=payload, timeout=3)
        
        if response.status_code == 200:
            source_type = "CHANNEL" if from_monitored_channel else "PERSONAL CHAT"
            print(f"✅ [{source_type}] Sent signal to broadcast bot from chat {event.chat_id}: {text[:90]}...")
        else:
            print(f"⚠️ Failed to send to broadcast bot: HTTP {response.status_code} - {response.text}")
    except requests.exceptions.Timeout:
        print(f"⚠️ HTTP request timed out (3s) - Flask API may be slow, signal processing continues")
    except Exception as e:
        print(f"❌ Failed to send to broadcast bot: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

print("🚀 VerzekTelethonForwarder v2.2 starting...")
print("💓 Heartbeat monitoring enabled (writes to /tmp/forwarder_heartbeat.json)")

channel_list = []
for c in MONITORED_CHANNELS:
    if isinstance(c, str):
        channel_list.append(f'@{c}')
    else:
        channel_list.append(f'ID:{c}')
print(f"📢 Monitored channels: {', '.join(channel_list) if channel_list else 'None'}")
print(f"💬 Also monitoring personal chats for signals...")

# Start client (synchronous)
client.start()

# NOTE: Session is already persisted in environment-specific file (telethon_session_prod.txt or telethon_session_dev.txt)
# No need to save again - this prevents recreating the legacy session file that causes dual-IP conflicts

# Start heartbeat monitoring task in the event loop
client.loop.create_task(heartbeat_task())

print("✅ All systems operational - monitoring for signals...")

# Run until disconnected (synchronous - handles its own event loop)
client.run_until_disconnected()
FORWARDER_EOF
echo "  ✅ Created"

echo ""
echo "📋 Step 3: Creating forwarder_watchdog.py..."
cat > forwarder_watchdog.py << 'WATCHDOG_EOF'
#!/usr/bin/env python3
"""
Telegram Forwarder Watchdog v1.0
---------------------------------
Monitors the telethon_forwarder.py process for freezes/crashes
and automatically restarts it if needed.

Checks:
1. Heartbeat file freshness (<90 seconds old)
2. Process is running (by PID in heartbeat file)
3. Sends Telegram alerts to admin on failures
"""

import os
import sys
import json
import time
import subprocess
import requests
from datetime import datetime, timedelta

# Configuration
HEARTBEAT_FILE = "/tmp/forwarder_heartbeat.json"
FORWARDER_SCRIPT = "/var/www/VerzekAutoTrader/telethon_forwarder.py"
FORWARDER_LOG = "/var/www/VerzekAutoTrader/telethon_forwarder.log"
MAX_HEARTBEAT_AGE_SECONDS = 90  # 90 seconds = heartbeat should update every 30s
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

def send_admin_alert(message):
    """Send Telegram notification to admin"""
    if not TELEGRAM_BOT_TOKEN or not ADMIN_CHAT_ID:
        print(f"⚠️ Cannot send alert (missing credentials): {message}")
        return
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": ADMIN_CHAT_ID,
            "text": f"🚨 **Forwarder Watchdog Alert**\n\n{message}",
            "parse_mode": "Markdown"
        }
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            print(f"✅ Alert sent to admin: {message}")
        else:
            print(f"⚠️ Failed to send alert: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to send admin alert: {e}")

def check_heartbeat():
    """Check if heartbeat file exists and is fresh"""
    if not os.path.exists(HEARTBEAT_FILE):
        return False, "Heartbeat file not found"
    
    try:
        with open(HEARTBEAT_FILE, "r") as f:
            data = json.load(f)
        
        heartbeat_time = datetime.fromisoformat(data["timestamp"])
        age_seconds = (datetime.now() - heartbeat_time).total_seconds()
        pid = data.get("pid")
        
        if age_seconds > MAX_HEARTBEAT_AGE_SECONDS:
            return False, f"Heartbeat stale ({int(age_seconds)}s old, PID: {pid})"
        
        return True, f"Heartbeat healthy ({int(age_seconds)}s old, PID: {pid})"
    except Exception as e:
        return False, f"Heartbeat read error: {e}"

def is_process_running(pid):
    """Check if process is running by PID"""
    try:
        os.kill(pid, 0)  # Signal 0 = check if process exists
        return True
    except (OSError, TypeError):
        return False

def restart_forwarder():
    """Kill old process and start new forwarder"""
    print("🔄 Restarting forwarder...")
    
    # Kill any existing forwarder processes
    try:
        subprocess.run(["pkill", "-f", "telethon_forwarder.py"], check=False)
        time.sleep(2)
    except Exception as e:
        print(f"⚠️ Error killing old process: {e}")
    
    # Start new forwarder process
    try:
        cmd = f"cd /var/www/VerzekAutoTrader && nohup python3 -u telethon_forwarder.py > {FORWARDER_LOG} 2>&1 &"
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Forwarder restarted")
        send_admin_alert("🔄 **Forwarder Restarted**\n\nThe Telegram signal forwarder was automatically restarted by the watchdog.")
        return True
    except Exception as e:
        error_msg = f"Failed to restart: {e}"
        print(f"❌ {error_msg}")
        send_admin_alert(f"❌ **Forwarder Restart Failed**\n\n{error_msg}")
        return False

def main():
    """Main watchdog check"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Forwarder Watchdog Check")
    
    # Check heartbeat
    is_healthy, status_msg = check_heartbeat()
    print(f"  {status_msg}")
    
    if not is_healthy:
        print("  ❌ Forwarder unhealthy - restarting...")
        send_admin_alert(f"⚠️ **Forwarder Frozen Detected**\n\n{status_msg}\n\nAttempting automatic restart...")
        restart_forwarder()
    else:
        print("  ✅ Forwarder healthy")

if __name__ == "__main__":
    main()
WATCHDOG_EOF
chmod +x forwarder_watchdog.py
echo "  ✅ Created"

echo ""
echo "📋 Step 4: Creating systemd service files..."

cat > /etc/systemd/system/telethon-forwarder.service << 'SERVICE_EOF'
[Unit]
Description=VerzekAutoTrader Telegram Signal Forwarder
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/VerzekAutoTrader
EnvironmentFile=/var/www/VerzekAutoTrader/.env
ExecStart=/usr/bin/python3 -u /var/www/VerzekAutoTrader/telethon_forwarder.py
Restart=on-failure
RestartSec=10
StandardOutput=append:/var/www/VerzekAutoTrader/telethon_forwarder.log
StandardError=append:/var/www/VerzekAutoTrader/telethon_forwarder.log

# Restart if crashes
StartLimitInterval=300
StartLimitBurst=5

[Install]
WantedBy=multi-user.target
SERVICE_EOF

cat > /etc/systemd/system/forwarder-watchdog.service << 'WATCHDOG_SERVICE_EOF'
[Unit]
Description=Telegram Forwarder Watchdog Timer
After=telethon-forwarder.service

[Service]
Type=oneshot
User=root
WorkingDirectory=/var/www/VerzekAutoTrader
EnvironmentFile=/var/www/VerzekAutoTrader/.env
ExecStart=/usr/bin/python3 /var/www/VerzekAutoTrader/forwarder_watchdog.py
WATCHDOG_SERVICE_EOF

cat > /etc/systemd/system/forwarder-watchdog.timer << 'TIMER_EOF'
[Unit]
Description=Run Forwarder Watchdog every minute
Requires=forwarder-watchdog.service

[Timer]
OnBootSec=2min
OnUnitActiveSec=1min
AccuracySec=1s

[Install]
WantedBy=timers.target
TIMER_EOF

systemctl daemon-reload
echo "  ✅ Services created"

echo ""
echo "📋 Step 5: Starting forwarder service..."
systemctl enable telethon-forwarder.service
systemctl start telethon-forwarder.service
sleep 3
echo "  ✅ Started"

echo ""
echo "📋 Step 6: Checking forwarder status..."
systemctl status telethon-forwarder.service --no-pager -l | head -15

echo ""
echo "📋 Step 7: Enabling watchdog timer..."
systemctl enable forwarder-watchdog.timer
systemctl start forwarder-watchdog.timer
echo "  ✅ Watchdog enabled"

echo ""
echo "📋 Step 8: Verifying heartbeat (waiting 35 seconds)..."
sleep 35
if [ -f /tmp/forwarder_heartbeat.json ]; then
    echo "  ✅ Heartbeat file detected:"
    cat /tmp/forwarder_heartbeat.json
    echo ""
else
    echo "  ⚠️  Warning: No heartbeat file yet (may take up to 60 seconds)"
fi

echo ""
echo "✅ =========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "✅ =========================================="
echo ""
echo "📊 System Status:"
echo "  - Forwarder: systemctl status telethon-forwarder"
echo "  - Watchdog: systemctl status forwarder-watchdog.timer"
echo "  - Logs: tail -f telethon_forwarder.log"
echo "  - Heartbeat: cat /tmp/forwarder_heartbeat.json"
echo ""
echo "🔔 You will receive Telegram alerts if the forwarder freezes!"
echo ""
