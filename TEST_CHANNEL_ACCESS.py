#!/usr/bin/env python3
"""
TEST_CHANNEL_ACCESS.py - Test if Telethon session can read messages from channel
Run this on Vultr to diagnose channel access issues
"""

import os
import sys
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import ChannelPrivateError, ChatAdminRequiredError

# Load environment variables
with open('.env', 'r') as f:
    for line in f:
        if '=' in line and not line.strip().startswith('#'):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value

api_id = int(os.getenv("TELEGRAM_API_ID"))
api_hash = os.getenv("TELEGRAM_API_HASH")
is_production = os.getenv("REPLIT_DEPLOYMENT") == "1"
session_file = "telethon_session_prod.txt" if is_production else "telethon_session_dev.txt"

CHANNEL_ID = -1002249790469

print("=" * 60)
print("🔍 TELETHON CHANNEL ACCESS TEST")
print("=" * 60)
print(f"\n📂 Session file: {session_file}")
print(f"🎯 Target channel: {CHANNEL_ID}")
print(f"🌍 Mode: {'PRODUCTION' if is_production else 'DEVELOPMENT'}\n")

# Load session
with open(session_file, 'r') as f:
    session_string = f.read().strip()

client = TelegramClient(StringSession(session_string), api_id, api_hash)

async def test_channel_access():
    """Test comprehensive channel access"""
    
    print("1️⃣ Connecting to Telegram...")
    await client.connect()
    
    if not await client.is_user_authorized():
        print("❌ Session is NOT authorized!")
        return
    
    me = await client.get_me()
    print(f"✅ Connected as: {me.first_name} (Phone: {me.phone})\n")
    
    # Test 1: Can we get the channel entity?
    print("2️⃣ Testing channel entity access...")
    try:
        channel = await client.get_entity(CHANNEL_ID)
        print(f"✅ Can access channel: {channel.title}")
        print(f"   - Channel ID: {channel.id}")
        print(f"   - Username: @{channel.username if hasattr(channel, 'username') and channel.username else 'N/A'}")
        print(f"   - Broadcast: {getattr(channel, 'broadcast', False)}")
        print(f"   - Megagroup: {getattr(channel, 'megagroup', False)}")
        print(f"   - Restricted: {getattr(channel, 'restricted', False)}")
    except ChannelPrivateError:
        print("❌ CRITICAL: Channel is private and session has NO ACCESS!")
        print("   You need to rejoin the channel or recreate the session.")
        await client.disconnect()
        return
    except Exception as e:
        print(f"❌ Cannot access channel: {type(e).__name__}: {e}")
        await client.disconnect()
        return
    
    # Test 2: Can we get channel participants info?
    print("\n3️⃣ Testing channel information access...")
    try:
        full_channel = await client.get_entity(CHANNEL_ID)
        print(f"✅ Channel details accessible")
    except Exception as e:
        print(f"⚠️ Limited info access: {type(e).__name__}: {e}")
    
    # Test 3: Can we read recent messages?
    print("\n4️⃣ Testing message read access (last 10 messages)...")
    message_count = 0
    try:
        async for message in client.iter_messages(CHANNEL_ID, limit=10):
            message_count += 1
            if message.message:
                preview = message.message[:50].replace('\n', ' ')
                print(f"   ✅ Message {message_count}: {preview}...")
            else:
                print(f"   ℹ️ Message {message_count}: [Media/No text]")
        
        if message_count == 0:
            print("   ⚠️ No messages found (channel might be empty or access restricted)")
        else:
            print(f"\n✅ SUCCESS: Read {message_count} messages from channel!")
            
    except ChannelPrivateError:
        print("   ❌ CRITICAL: Cannot read messages - Channel is PRIVATE!")
        print("   This is why signals aren't being received!")
    except ChatAdminRequiredError:
        print("   ❌ CRITICAL: Admin permissions required to read messages!")
    except Exception as e:
        print(f"   ❌ Cannot read messages: {type(e).__name__}: {e}")
        message_count = 0
    
    # Test 4: Check if we're subscribed
    print("\n5️⃣ Checking subscription status...")
    try:
        dialogs = await client.get_dialogs()
        found = False
        for dialog in dialogs:
            if dialog.id == CHANNEL_ID:
                found = True
                print(f"✅ You ARE subscribed to this channel")
                print(f"   - Unread messages: {dialog.unread_count}")
                print(f"   - Last message date: {dialog.date}")
                break
        
        if not found:
            print("❌ You are NOT subscribed to this channel!")
            print("   This might be why messages aren't being received.")
    except Exception as e:
        print(f"⚠️ Could not check subscription: {type(e).__name__}: {e}")
    
    await client.disconnect()
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    if message_count > 0:
        print("✅ RESULT: Telethon session CAN read messages from channel")
        print("   The session has proper access.")
        print("   If signals aren't being received, the issue is elsewhere.")
    else:
        print("❌ RESULT: Telethon session CANNOT read messages!")
        print("   Possible causes:")
        print("   1. Channel admin changed read permissions")
        print("   2. You were removed and re-added (session needs refresh)")
        print("   3. Session expired or was revoked")
        print("\n🔧 SOLUTION: Recreate the Telethon session:")
        print("   python setup_telethon.py")
    
    print("=" * 60)

# Run the test
with client:
    client.loop.run_until_complete(test_channel_access())
