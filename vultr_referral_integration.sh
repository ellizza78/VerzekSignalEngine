#!/bin/bash
# Script to integrate referral system into Vultr backend
# Run this on Vultr VPS: ssh root@80.240.29.142

cd /var/www/VerzekAutoTrader

echo "=== INTEGRATING REFERRAL SYSTEM ===" 

# Create referral handler function
cat > referral_handler.py << 'REFEOF'
import os
import requests
from datetime import datetime

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')

def send_telegram_notification(message):
    """Send notification to Telegram support"""
    if not TELEGRAM_BOT_TOKEN or not ADMIN_CHAT_ID:
        print("⚠️ Telegram credentials not configured")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": ADMIN_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram notification error: {e}")
        return False

def process_referral(referrer_user, new_user, referral_bonus=10.0):
    """
    Process a referral when a new user registers with a referral code
    
    Args:
        referrer_user: The user who referred (User object)
        new_user: The newly registered user (User object)
        referral_bonus: Bonus amount in USD (default $10)
    
    Returns:
        dict with success status and message
    """
    try:
        # Update referrer's earnings
        if not hasattr(referrer_user, 'referral_earnings'):
            referrer_user.referral_earnings = 0.0
        
        referrer_user.referral_earnings += referral_bonus
        
        # Send Telegram notification to support
        message = f"""
🎁 <b>NEW REFERRAL!</b>

<b>Referrer:</b>
• Name: {referrer_user.username or referrer_user.email}
• User ID: {referrer_user.user_id}
• Email: {referrer_user.email}
• Total Referrals Earnings: ${referrer_user.referral_earnings:.2f}

<b>New User (Referred):</b>
• Name: {new_user.username or new_user.full_name or new_user.email}
• User ID: {new_user.user_id}
• Email: {new_user.email}

<b>Bonus:</b> ${referral_bonus:.2f}

<i>Process this referral bonus payment via your preferred method.</i>
        """.strip()
        
        notification_sent = send_telegram_notification(message)
        
        print(f"✅ Referral processed: {new_user.email} referred by {referrer_user.email}")
        print(f"📧 Telegram notification: {'Sent' if notification_sent else 'Failed'}")
        
        return {
            "success": True,
            "referrer_id": referrer_user.user_id,
            "bonus_amount": referral_bonus,
            "notification_sent": notification_sent
        }
        
    except Exception as e:
        print(f"❌ Error processing referral: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def validate_referral_code(referral_code, user_manager):
    """
    Validate that a referral code exists and return the referrer user
    
    Args:
        referral_code: The referral code to validate
        user_manager: UserManager instance
    
    Returns:
        User object if valid, None otherwise
    """
    if not referral_code or not referral_code.strip():
        return None
    
    referral_code = referral_code.strip().upper()
    
    # Find user with this referral code
    all_users = user_manager.get_all_users()
    for user in all_users:
        if hasattr(user, 'referral_code') and user.referral_code == referral_code:
            return user
    
    return None
REFEOF

echo "✅ referral_handler.py created"

# Create backup of api_server.py
cp api_server.py api_server.py.referral_backup
echo "✅ Backup created: api_server.py.referral_backup"

# Add import at the top of api_server.py (after other imports)
python3 << 'PYEOF'
import re

with open('api_server.py', 'r') as f:
    content = f.read()

# Check if already imported
if 'from referral_handler import' in content:
    print("✅ Referral handler already imported")
else:
    # Find imports section and add our import
    import_pattern = r'(from modules\.user_manager import.*?\n)'
    import_addition = r'\1from referral_handler import validate_referral_code, process_referral\n'
    content = re.sub(import_pattern, import_addition, content, count=1)
    
    with open('api_server.py', 'w') as f:
        f.write(content)
    
    print("✅ Import added to api_server.py")
PYEOF

echo ""
echo "=== NEXT STEPS ==="
echo "1. Manually update the /api/auth/register endpoint in api_server.py"
echo "2. Add this code after user creation (around line 340):"
echo ""
cat << 'CODEEOF'

    # Process referral code if provided
    referral_code = data.get('referral_code')
    if referral_code:
        referrer = validate_referral_code(referral_code, user_manager)
        if referrer:
            user.referred_by = referrer.user_id
            process_referral(referrer, user, referral_bonus=10.0)
            user_manager._save_user_to_db(user)
            user_manager._save_user_to_db(referrer)
            print(f"✅ Referral linked: {user.email} referred by {referrer.email}")
        else:
            print(f"⚠️ Invalid referral code: {referral_code}")
    
CODEEOF

echo ""
echo "3. Restart API server:"
echo "   pkill -f api_server.py"
echo "   cd /var/www/VerzekAutoTrader"
echo "   nohup python3 api_server.py > logs/api.log 2>&1 &"
echo ""
echo "✅ Referral system files created!"
