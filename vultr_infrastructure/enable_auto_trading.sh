#!/bin/bash

set -e

SERVER_IP="80.240.29.142"
SERVER_USER="root"

echo "🤖 Auto-Trading Configuration Tool"
echo "===================================="
echo ""
echo "This script helps enable/disable auto-trading for premium users"
echo ""

# Get user choice
echo "Select action:"
echo "1) Enable auto-trading for specific user (by email)"
echo "2) Enable auto-trading for all PREMIUM users"
echo "3) Disable auto-trading for specific user (by email)"
echo "4) List all users with auto-trading enabled"
echo "5) Check auto-trading status for user (by email)"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        read -p "Enter user email: " user_email
        echo "🔧 Enabling auto-trading for $user_email..."
        ssh -i ~/.ssh/vultr_verzek ${SERVER_USER}@${SERVER_IP} << ENDSSH
            cd /root/VerzekBackend
            source venv/bin/activate 2>/dev/null || true
            python3 << 'ENDPYTHON'
import sys
sys.path.insert(0, '/root/VerzekBackend')
from backend.models import User
from backend.database import SessionLocal

db = SessionLocal()
user = db.query(User).filter(User.email == "$user_email").first()
if user:
    if user.subscription_tier in ['VIP', 'PREMIUM']:
        user.auto_trade_enabled = True
        db.commit()
        print(f"✅ Auto-trading ENABLED for {user.email} (Tier: {user.subscription_tier})")
    else:
        print(f"❌ ERROR: User {user.email} must have VIP or PREMIUM subscription")
        print(f"   Current tier: {user.subscription_tier}")
else:
    print(f"❌ ERROR: User $user_email not found")
db.close()
ENDPYTHON
ENDSSH
        ;;
    
    2)
        echo "🔧 Enabling auto-trading for ALL PREMIUM users..."
        ssh -i ~/.ssh/vultr_verzek ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
            cd /root/VerzekBackend
            source venv/bin/activate 2>/dev/null || true
            python3 << 'ENDPYTHON'
import sys
sys.path.insert(0, '/root/VerzekBackend')
from backend.models import User
from backend.database import SessionLocal

db = SessionLocal()
premium_users = db.query(User).filter(User.subscription_tier == 'PREMIUM').all()
count = 0
for user in premium_users:
    user.auto_trade_enabled = True
    count += 1
db.commit()
print(f"✅ Auto-trading ENABLED for {count} PREMIUM users")
db.close()
ENDPYTHON
ENDSSH
        ;;
    
    3)
        read -p "Enter user email: " user_email
        echo "🔧 Disabling auto-trading for $user_email..."
        ssh -i ~/.ssh/vultr_verzek ${SERVER_USER}@${SERVER_IP} << ENDSSH
            cd /root/VerzekBackend
            source venv/bin/activate 2>/dev/null || true
            python3 << 'ENDPYTHON'
import sys
sys.path.insert(0, '/root/VerzekBackend')
from backend.models import User
from backend.database import SessionLocal

db = SessionLocal()
user = db.query(User).filter(User.email == "$user_email").first()
if user:
    user.auto_trade_enabled = False
    db.commit()
    print(f"✅ Auto-trading DISABLED for {user.email}")
else:
    print(f"❌ ERROR: User $user_email not found")
db.close()
ENDPYTHON
ENDSSH
        ;;
    
    4)
        echo "📊 Listing all users with auto-trading enabled..."
        ssh -i ~/.ssh/vultr_verzek ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
            cd /root/VerzekBackend
            source venv/bin/activate 2>/dev/null || true
            python3 << 'ENDPYTHON'
import sys
sys.path.insert(0, '/root/VerzekBackend')
from backend.models import User
from backend.database import SessionLocal

db = SessionLocal()
users = db.query(User).filter(User.auto_trade_enabled == True).all()
if users:
    print(f"\n{'ID':<5} {'Email':<30} {'Tier':<10} {'Capital':<10}")
    print("-" * 60)
    for user in users:
        print(f"{user.id:<5} {user.email:<30} {user.subscription_tier:<10} ${user.capital_usdt:<10.2f}")
    print(f"\nTotal: {len(users)} users")
else:
    print("❌ No users have auto-trading enabled")
db.close()
ENDPYTHON
ENDSSH
        ;;
    
    5)
        read -p "Enter user email: " user_email
        echo "📊 Checking auto-trading status for $user_email..."
        ssh -i ~/.ssh/vultr_verzek ${SERVER_USER}@${SERVER_IP} << ENDSSH
            cd /root/VerzekBackend
            source venv/bin/activate 2>/dev/null || true
            python3 << 'ENDPYTHON'
import sys
sys.path.insert(0, '/root/VerzekBackend')
from backend.models import User, ExchangeAccount
from backend.database import SessionLocal

db = SessionLocal()
user = db.query(User).filter(User.email == "$user_email").first()
if user:
    print(f"\n📊 User: {user.email}")
    print(f"├─ Subscription: {user.subscription_tier}")
    print(f"├─ Email Verified: {user.is_verified}")
    print(f"├─ Auto-trading: {'✅ ENABLED' if user.auto_trade_enabled else '❌ DISABLED'}")
    print(f"├─ Capital: \${user.capital_usdt:.2f}")
    print(f"├─ Max Concurrent: {user.max_concurrent_trades}")
    
    exchanges = db.query(ExchangeAccount).filter(ExchangeAccount.user_id == user.id).all()
    print(f"└─ Exchange Accounts: {len(exchanges)}")
    for ex in exchanges:
        print(f"   └─ {ex.exchange}")
    
    if not user.is_verified:
        print("\n⚠️  WARNING: Email not verified")
    if user.subscription_tier not in ['VIP', 'PREMIUM']:
        print(f"\n⚠️  WARNING: Requires VIP/PREMIUM (current: {user.subscription_tier})")
    if len(exchanges) == 0:
        print("\n⚠️  WARNING: No exchange accounts connected")
else:
    print(f"❌ ERROR: User $user_email not found")
db.close()
ENDPYTHON
ENDSSH
        ;;
    
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Done!"
