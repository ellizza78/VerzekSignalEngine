#!/usr/bin/env python3
"""
Convert legacy session string to production session file
This bypasses the need for re-authentication if the old session is still valid
"""
import os
import sys

def convert_legacy_to_production():
    """Convert backup session to production format"""
    
    backup_file = "telethon_session_string.txt.backup"
    prod_file = "telethon_session_prod.txt"
    
    if not os.path.exists(backup_file):
        print("❌ No backup session found")
        return False
    
    print("📋 Reading legacy session backup...")
    with open(backup_file, 'r') as f:
        session_string = f.read().strip()
    
    if not session_string or len(session_string) < 100:
        print("❌ Backup session appears invalid or corrupted")
        return False
    
    print(f"✅ Legacy session found ({len(session_string)} chars)")
    print("\n⚠️  WARNING: This session was used on dual IPs and may already be revoked by Telegram")
    print("⚠️  If conversion succeeds but deployment fails, you MUST wait 24h for flood limit reset\n")
    
    confirm = input("Convert legacy session to production? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ Conversion cancelled")
        return False
    
    # Write to production session file
    print(f"💾 Writing to: {prod_file}")
    with open(prod_file, 'w') as f:
        f.write(session_string)
    
    print(f"✅ Production session created: {prod_file}")
    print("\n📌 NEXT STEPS:")
    print("1. Click 'Deployments' → 'Republish'")
    print("2. Check deployment logs for Telethon errors")
    print("3. If you see AuthKeyDuplicatedError, the session is revoked - wait 24h")
    print("4. If successful, signals will start flowing! 🎉")
    
    return True

if __name__ == "__main__":
    success = convert_legacy_to_production()
    sys.exit(0 if success else 1)
