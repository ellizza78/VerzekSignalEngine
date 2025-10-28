#!/usr/bin/env python3
"""
TEST_BROADCAST_BOT.py - Test if broadcast bot can send messages
---------------------------------------------------------------
Verifies bot token, permissions, and group membership
"""

import os
from telegram import Bot
from telegram.error import TelegramError

# Load environment
from dotenv import load_dotenv
load_dotenv()

BROADCAST_BOT_TOKEN = os.getenv("BROADCAST_BOT_TOKEN")
VIP_GROUP_ID = -1002721581400
TRIAL_GROUP_ID = -1002726167386

print("=" * 60)
print("🤖 BROADCAST BOT DIAGNOSTIC TEST")
print("=" * 60)
print()

# 1. Check if token exists
if not BROADCAST_BOT_TOKEN:
    print("❌ BROADCAST_BOT_TOKEN not found in environment!")
    print("   Add it to .env file")
    exit(1)

print(f"✅ Bot token found: {BROADCAST_BOT_TOKEN[:10]}...{BROADCAST_BOT_TOKEN[-5:]}")
print()

# 2. Initialize bot
try:
    bot = Bot(token=BROADCAST_BOT_TOKEN)
    print("✅ Bot initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize bot: {e}")
    exit(1)

# 3. Get bot info
try:
    me = bot.get_me()
    print(f"✅ Bot username: @{me.username}")
    print(f"   Bot name: {me.first_name}")
    print(f"   Bot ID: {me.id}")
except Exception as e:
    print(f"❌ Failed to get bot info: {e}")
    print("   This usually means the token is invalid!")
    exit(1)

print()

# 4. Test VIP group access
print(f"📤 Testing VIP group ({VIP_GROUP_ID})...")
try:
    # Try to get chat info
    chat = bot.get_chat(chat_id=VIP_GROUP_ID)
    print(f"✅ Can access VIP group: {chat.title}")
    
    # Check if bot is admin
    admins = bot.get_chat_administrators(chat_id=VIP_GROUP_ID)
    bot_is_admin = any(admin.user.id == me.id for admin in admins)
    
    if bot_is_admin:
        print(f"✅ Bot is an admin in VIP group")
    else:
        print(f"⚠️  Bot is NOT an admin (may not be able to post)")
    
    # Try to send test message
    try:
        msg = bot.send_message(
            chat_id=VIP_GROUP_ID,
            text="🔧 **DIAGNOSTIC TEST**\n\nThis is an automated test from VerzekBroadcastBot.\nIf you see this, the bot can send messages to this group!"
        )
        print(f"✅ Successfully sent test message to VIP group! (msg_id: {msg.message_id})")
    except Exception as e:
        print(f"❌ Cannot send to VIP group: {e}")

except Exception as e:
    print(f"❌ Cannot access VIP group: {e}")
    print("   Possible reasons:")
    print("   - Bot is not a member of the group")
    print("   - Bot was removed or banned")
    print("   - Group ID is incorrect")

print()

# 5. Test TRIAL group access
print(f"📤 Testing TRIAL group ({TRIAL_GROUP_ID})...")
try:
    # Try to get chat info
    chat = bot.get_chat(chat_id=TRIAL_GROUP_ID)
    print(f"✅ Can access TRIAL group: {chat.title}")
    
    # Check if bot is admin
    admins = bot.get_chat_administrators(chat_id=TRIAL_GROUP_ID)
    bot_is_admin = any(admin.user.id == me.id for admin in admins)
    
    if bot_is_admin:
        print(f"✅ Bot is an admin in TRIAL group")
    else:
        print(f"⚠️  Bot is NOT an admin (may not be able to post)")
    
    # Try to send test message
    try:
        msg = bot.send_message(
            chat_id=TRIAL_GROUP_ID,
            text="🔧 **DIAGNOSTIC TEST**\n\nThis is an automated test from VerzekBroadcastBot.\nIf you see this, the bot can send messages to this group!"
        )
        print(f"✅ Successfully sent test message to TRIAL group! (msg_id: {msg.message_id})")
    except Exception as e:
        print(f"❌ Cannot send to TRIAL group: {e}")

except Exception as e:
    print(f"❌ Cannot access TRIAL group: {e}")
    print("   Possible reasons:")
    print("   - Bot is not a member of the group")
    print("   - Bot was removed or banned")
    print("   - Group ID is incorrect")

print()
print("=" * 60)
print("✅ DIAGNOSTIC COMPLETE")
print("=" * 60)
print()
print("📋 NEXT STEPS:")
print("   1. If bot is not in groups, add it: @{username} (paste link in group)")
print("   2. If bot cannot send, make it an admin with 'Post Messages' permission")
print("   3. If token is wrong, update BROADCAST_BOT_TOKEN in .env file")
