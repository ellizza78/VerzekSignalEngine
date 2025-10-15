"""
One-time Telethon Setup Script
-------------------------------
Run this script ONCE in the Replit Shell to authenticate your Telegram account.
After this, the auto-forwarder will work automatically 24/7.

Command: python setup_telethon.py
"""

import os
from telethon import TelegramClient
from telethon.sessions import StringSession

# Your Telegram API credentials
api_id = 26395582
api_hash = "a32cb77b68ad84fb0dd60531d83698dc"

session_file = "telethon_session_string.txt"

print("🔐 Telethon First-Time Setup")
print("=" * 50)
print("\nThis will authenticate your Telegram account.")
print("You'll receive a code on your Telegram app.\n")

# Create client
client = TelegramClient(StringSession(), api_id, api_hash)

async def main():
    await client.start()
    
    # Save session string
    session_string = client.session.save()
    with open(session_file, "w") as f:
        f.write(session_string)
    
    print("\n✅ Authentication successful!")
    print(f"✅ Session saved to {session_file}")
    print("\nYou can now run the auto-forwarder:")
    print("  python telethon_forwarder.py")
    print("\nOr restart the VerzekAutoTrader workflow - it will work automatically!")
    
    await client.disconnect()

with client:
    client.loop.run_until_complete(main())
