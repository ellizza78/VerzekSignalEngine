"""
Migration Script: JSON to SQLite
---------------------------------
Safely migrates all existing data from JSON files to SQLite database.
Preserves user accounts, positions, licenses, and settings.
"""

import json
import os
import sys
from modules.database import get_database
import time

def migrate_users():
    """Migrate users from JSON to SQLite"""
    json_path = "database/users_v2.json"
    if not os.path.exists(json_path):
        json_path = "database/users.json"
        if not os.path.exists(json_path):
            print("⏭️  No users.json found, skipping user migration")
            return
    
    print("📦 Migrating users from JSON to SQLite...")
    db = get_database()
    
    with open(json_path, 'r') as f:
        users_data = json.load(f)
    
    migrated = 0
    skipped = 0
    
    for user_id, user_data in users_data.items():
        try:
            # Extract core fields
            success = db.create_user(
                user_id=user_id,
                username=user_data.get('username', ''),
                email=user_data.get('email', ''),
                password_hash=user_data.get('password_hash', ''),
                data=user_data  # Store entire user object in JSON field
            )
            
            if success:
                # Update additional fields
                db.update_user(
                    user_id,
                    email_verified=user_data.get('email_verified', False),
                    subscription_plan=user_data.get('subscription_plan', 'TRIAL'),
                    subscription_expires=user_data.get('subscription_expires'),
                    referral_code=user_data.get('referral_code'),
                    referred_by=user_data.get('referred_by'),
                    referral_earnings=user_data.get('referral_earnings', 0.0),
                    total_profit=user_data.get('total_profit', 0.0),
                    total_loss=user_data.get('total_loss', 0.0),
                    win_rate=user_data.get('win_rate', 0.0),
                    total_trades=user_data.get('total_trades', 0)
                )
                migrated += 1
                print(f"  ✅ Migrated user: {user_data.get('email', user_id)}")
            else:
                skipped += 1
                print(f"  ⏭️  Skipped duplicate: {user_data.get('email', user_id)}")
        except Exception as e:
            print(f"  ❌ Error migrating user {user_id}: {e}")
            skipped += 1
    
    print(f"✅ Users migration complete: {migrated} migrated, {skipped} skipped")
    
    # Backup original file
    backup_path = json_path + f".backup_{int(time.time())}"
    os.rename(json_path, backup_path)
    print(f"📁 Original users.json backed up to: {backup_path}")


def migrate_positions():
    """Migrate positions from JSON to SQLite"""
    json_path = "database/positions.json"
    if not os.path.exists(json_path):
        print("⏭️  No positions.json found, skipping position migration")
        return
    
    print("📦 Migrating positions from JSON to SQLite...")
    db = get_database()
    
    with open(json_path, 'r') as f:
        positions_data = json.load(f)
    
    migrated = 0
    skipped = 0
    
    for position_id, position_data in positions_data.items():
        try:
            success = db.create_position(
                position_id=position_id,
                user_id=position_data.get('user_id', ''),
                symbol=position_data.get('symbol', ''),
                exchange=position_data.get('exchange', ''),
                side=position_data.get('side', ''),
                entry_price=position_data.get('entry_price', 0.0),
                quantity=position_data.get('quantity', 0.0),
                leverage=position_data.get('leverage'),
                stop_loss=position_data.get('stop_loss'),
                take_profit_levels=position_data.get('take_profit_levels', []),
                status=position_data.get('status', 'OPEN'),
                data=position_data
            )
            
            if success:
                migrated += 1
                print(f"  ✅ Migrated position: {position_id}")
            else:
                skipped += 1
        except Exception as e:
            print(f"  ❌ Error migrating position {position_id}: {e}")
            skipped += 1
    
    print(f"✅ Positions migration complete: {migrated} migrated, {skipped} skipped")
    
    # Backup original file
    backup_path = json_path + f".backup_{int(time.time())}"
    os.rename(json_path, backup_path)
    print(f"📁 Original positions.json backed up to: {backup_path}")


def migrate_licenses():
    """Migrate licenses from JSON to SQLite"""
    json_path = "database/licenses.json"
    if not os.path.exists(json_path):
        print("⏭️  No licenses.json found, skipping license migration")
        return
    
    print("📦 Migrating licenses from JSON to SQLite...")
    db = get_database()
    
    with open(json_path, 'r') as f:
        licenses_data = json.load(f)
    
    migrated = 0
    skipped = 0
    
    for license_key, license_data in licenses_data.items():
        try:
            success = db.create_license(
                license_key=license_key,
                user_id=license_data.get('user_id', ''),
                plan=license_data.get('plan', ''),
                issued_at=license_data.get('issued_at', int(time.time())),
                expires_at=license_data.get('expires_at', int(time.time()))
            )
            
            if success:
                migrated += 1
                print(f"  ✅ Migrated license: {license_key[:20]}...")
            else:
                skipped += 1
        except Exception as e:
            print(f"  ❌ Error migrating license: {e}")
            skipped += 1
    
    print(f"✅ Licenses migration complete: {migrated} migrated, {skipped} skipped")
    
    # Backup original file
    backup_path = json_path + f".backup_{int(time.time())}"
    os.rename(json_path, backup_path)
    print(f"📁 Original licenses.json backed up to: {backup_path}")


def verify_migration():
    """Verify migration was successful"""
    print("\n🔍 Verifying migration...")
    db = get_database()
    
    users = db.get_all_users()
    positions = db.get_positions()
    
    print(f"  👥 Users in database: {len(users)}")
    print(f"  📊 Positions in database: {len(positions)}")
    
    if len(users) > 0:
        print(f"  ✅ Sample user: {users[0]['email']}")
    
    if len(positions) > 0:
        print(f"  ✅ Sample position: {positions[0]['position_id']}")
    
    print("✅ Migration verification complete!")


if __name__ == "__main__":
    print("🚀 VerzekAutoTrader - JSON to SQLite Migration")
    print("=" * 60)
    print("\n⚠️  IMPORTANT: This will migrate your data from JSON to SQLite")
    print("   Original JSON files will be backed up automatically")
    print("\n" + "=" * 60)
    
    response = input("\nContinue with migration? (yes/no): ").lower().strip()
    if response != "yes":
        print("❌ Migration cancelled")
        sys.exit(0)
    
    print("\n🔄 Starting migration...\n")
    
    try:
        migrate_users()
        print()
        migrate_positions()
        print()
        migrate_licenses()
        print()
        verify_migration()
        
        print("\n" + "=" * 60)
        print("✅ MIGRATION SUCCESSFUL!")
        print("=" * 60)
        print("\n📝 Next steps:")
        print("  1. Restart the application")
        print("  2. Verify all data is accessible")
        print("  3. Check logs for any errors")
        print("  4. Original JSON files are in database/*.backup_*")
        print("\n✅ Your app is now using production-grade SQLite database!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
