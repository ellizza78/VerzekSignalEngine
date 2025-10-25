"""
Environment-Specific Telethon Setup Script
-------------------------------------------
Creates PRODUCTION session for deployment (prevents dual-IP conflicts).
Run this in Replit workspace, then session will be deployed to production.

Command: python setup_telethon.py
"""

import os
import sys
from telethon import TelegramClient
from telethon.sessions import StringSession

# Your Telegram API credentials (REQUIRED from environment variables)
api_id = os.getenv("TELEGRAM_API_ID")
api_hash = os.getenv("TELEGRAM_API_HASH")

if not api_id or not api_hash:
    print("\n❌ ERROR: Missing Telegram API credentials!")
    print("Please set the following environment variables in Replit Secrets:")
    print("  - TELEGRAM_API_ID")
    print("  - TELEGRAM_API_HASH")
    print("\nGet your credentials from: https://my.telegram.org/apps")
    sys.exit(1)

api_id = int(api_id)

print("🔐 Telethon Production Session Setup")
print("=" * 50)
print("\n⚠️  IMPORTANT: This creates a PRODUCTION session for deployment")
print("This session will ONLY work in production (not in development workspace)")
print("\nYou'll receive a code on your Telegram app.\n")

# Ask user confirmation
response = input("Continue? (yes/no): ").lower().strip()
if response != "yes":
    print("❌ Setup cancelled")
    sys.exit(0)

# Create client
client = TelegramClient(StringSession(), api_id, api_hash)

async def main():
    await client.start()
    
    # Save PRODUCTION session
    session_string = client.session.save()
    prod_session_file = "telethon_session_prod.txt"
    
    with open(prod_session_file, "w") as f:
        f.write(session_string)
    
    print("\n✅ Authentication successful!")
    print(f"✅ Production session saved to {prod_session_file}")
    print("\n📦 NEXT STEPS:")
    print("  1. This file will be included in your next deployment")
    print("  2. Click 'Republish' in the Deployments panel")
    print("  3. Production will automatically use this session")
    print("\n⚠️  CRITICAL: Do NOT run Telethon in development workspace")
    print("  (It will conflict with production and break the session)")
    
    await client.disconnect()

with client:
    client.loop.run_until_complete(main())
