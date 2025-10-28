#!/bin/bash
# DIAGNOSE_SIGNAL_ISSUE.sh - Comprehensive diagnostic for signal monitoring
# Run this on your Vultr server to identify why signals aren't being received

echo "🔍 VerzekAutoTrader Signal Monitoring Diagnostic"
echo "================================================"
echo ""

# 1. Check verzekbot service status
echo "1️⃣ Checking verzekbot service status..."
echo "----------------------------------------"
systemctl status verzekbot --no-pager | head -20
echo ""

# 2. Check if Telethon is connected
echo "2️⃣ Checking Telethon connection status..."
echo "----------------------------------------"
echo "Last 30 lines of verzekbot logs:"
journalctl -u verzekbot -n 30 --no-pager
echo ""

# 3. Check session file
echo "3️⃣ Checking Telethon session file..."
echo "----------------------------------------"
cd /var/www/VerzekAutoTrader
if [ -f "telethon_session_prod.txt" ]; then
    echo "✅ telethon_session_prod.txt exists"
    ls -lh telethon_session_prod.txt
else
    echo "❌ telethon_session_prod.txt NOT FOUND"
fi

if [ -f "telethon_session_dev.txt" ]; then
    echo "✅ telethon_session_dev.txt exists"
    ls -lh telethon_session_dev.txt
else
    echo "❌ telethon_session_dev.txt NOT FOUND"
fi
echo ""

# 4. Check environment variables
echo "4️⃣ Checking environment variables..."
echo "----------------------------------------"
source venv/bin/activate
cd /var/www/VerzekAutoTrader
source .env

echo "REPLIT_DEPLOYMENT=${REPLIT_DEPLOYMENT:-NOT SET}"
echo "TELEGRAM_API_ID=${TELEGRAM_API_ID:-NOT SET}"
echo "TELEGRAM_API_HASH=$([ -n "$TELEGRAM_API_HASH" ] && echo "SET (${#TELEGRAM_API_HASH} chars)" || echo "NOT SET")"
echo ""

# 5. Test Telethon connection
echo "5️⃣ Testing Telethon connection..."
echo "----------------------------------------"
cat > /tmp/test_telethon_connection.py << 'PYTHON_EOF'
import os
import sys
from telethon import TelegramClient
from telethon.sessions import StringSession

# Load environment
sys.path.insert(0, '/var/www/VerzekAutoTrader')
os.chdir('/var/www/VerzekAutoTrader')

# Load .env manually
with open('.env', 'r') as f:
    for line in f:
        if '=' in line and not line.strip().startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
is_production = os.getenv("REPLIT_DEPLOYMENT") == "1"
session_file = "telethon_session_prod.txt" if is_production else "telethon_session_dev.txt"

print(f"📂 Using session file: {session_file}")
print(f"🌍 Mode: {'PRODUCTION' if is_production else 'DEVELOPMENT'}")

if not os.path.exists(session_file):
    print(f"❌ ERROR: {session_file} not found!")
    sys.exit(1)

with open(session_file, 'r') as f:
    session_string = f.read().strip()

print(f"📝 Session string length: {len(session_string)} characters")

client = TelegramClient(StringSession(session_string), api_id, api_hash)

async def check_connection():
    try:
        await client.connect()
        if await client.is_user_authorized():
            print("✅ Telethon is CONNECTED and AUTHORIZED")
            
            # Get account info
            me = await client.get_me()
            print(f"👤 Logged in as: {me.first_name} (@{me.username})")
            print(f"📱 Phone: {me.phone}")
            
            # Check access to monitored channel
            MONITORED_CHANNEL_ID = 2249790469
            print(f"\n🔍 Checking access to channel {MONITORED_CHANNEL_ID}...")
            
            try:
                channel = await client.get_entity(MONITORED_CHANNEL_ID)
                print(f"✅ Can access channel: {channel.title}")
                print(f"   - Channel ID: {channel.id}")
                print(f"   - Username: @{channel.username if hasattr(channel, 'username') and channel.username else 'N/A'}")
                print(f"   - Participants: {getattr(channel, 'participants_count', 'Unknown')}")
            except Exception as e:
                print(f"❌ CANNOT access channel {MONITORED_CHANNEL_ID}: {e}")
                print("   This is likely why signals aren't being received!")
            
            # List all dialogs to see what the bot can access
            print(f"\n📋 Listing all accessible chats/channels (first 20)...")
            async for dialog in client.iter_dialogs(limit=20):
                print(f"   - {dialog.name} (ID: {dialog.id})")
            
        else:
            print("❌ Telethon is NOT AUTHORIZED")
            print("   Session is invalid or expired!")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.disconnect()

with client:
    client.loop.run_until_complete(check_connection())
PYTHON_EOF

python /tmp/test_telethon_connection.py
echo ""

# 6. Check verzekapi connectivity
echo "6️⃣ Checking verzekapi connectivity..."
echo "----------------------------------------"
curl -s http://localhost:5000/ping | python -m json.tool 2>/dev/null || echo "❌ verzekapi not responding"
echo ""

echo "================================================"
echo "✅ Diagnostic complete!"
echo ""
echo "NEXT STEPS:"
echo "1. Review the output above"
echo "2. Look for any ❌ errors or warnings"
echo "3. Key things to check:"
echo "   - Is Telethon CONNECTED and AUTHORIZED?"
echo "   - Can Telethon access channel 2249790469?"
echo "   - Which session file is being used (prod vs dev)?"
echo "   - Are there any connection errors in the logs?"
