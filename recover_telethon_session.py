"""
Telethon Session Recovery Script
----------------------------------
Use this when you get AuthKeyDuplicatedError.
This script will:
1. Delete corrupted session files
2. Guide you to revoke session from Telegram app
3. Create a fresh PRODUCTION session

Command: python recover_telethon_session.py
"""

import os
import sys
from telethon import TelegramClient
from telethon.sessions import StringSession

# Your Telegram API credentials (from environment variables)
api_id = int(os.getenv("TELEGRAM_API_ID", "26395582"))
api_hash = os.getenv("TELEGRAM_API_HASH", "a32cb77b68ad84fb0dd60531d83698dc")

print("🔧 Telethon Session Recovery")
print("=" * 60)
print("\n⚠️  This will:")
print("  1. Delete all corrupted session files")
print("  2. Create a fresh PRODUCTION session for deployment")
print("\n📱 BEFORE CONTINUING:")
print("  1. Open Telegram app on your phone")
print("  2. Go to Settings → Devices (or Privacy & Security → Devices)")
print("  3. Find and TERMINATE the session called 'telethon'")
print("  4. Wait 10 seconds")
print("\n" + "=" * 60)

# Ask user confirmation
response = input("\n✋ Have you terminated the session in Telegram? (yes/no): ").lower().strip()
if response != "yes":
    print("\n❌ Please terminate the session in Telegram first, then run this script again")
    sys.exit(0)

# Delete old corrupted sessions
print("\n🗑️  Deleting corrupted session files...")
session_files = [
    "telethon_session_string.txt",
    "telethon_session_prod.txt", 
    "telethon_session_dev.txt",
    "telethon.session"  # SQLite session if exists
]

for f in session_files:
    if os.path.exists(f):
        os.remove(f)
        print(f"   ✓ Deleted {f}")

print("\n🔐 Creating fresh PRODUCTION session...")
print("You'll receive a code on your Telegram app.\n")

# Create fresh client
client = TelegramClient(StringSession(), api_id, api_hash)

async def main():
    await client.start()
    
    # Save PRODUCTION session
    session_string = client.session.save()
    prod_session_file = "telethon_session_prod.txt"
    
    with open(prod_session_file, "w") as f:
        f.write(session_string)
    
    print("\n✅ Recovery successful!")
    print(f"✅ Fresh production session saved to {prod_session_file}")
    print("\n📦 DEPLOYMENT STEPS:")
    print("  1. Click 'Republish' in the Deployments panel")
    print("  2. Wait 1-2 minutes for deployment to complete")
    print("  3. Check deployment logs for: 'Starting Telethon Auto-Forwarder (PRODUCTION)'")
    print("\n⚠️  REMEMBER: Never run Telethon in development workspace")
    print("  (Development is automatically disabled to prevent conflicts)")
    
    await client.disconnect()

with client:
    client.loop.run_until_complete(main())
