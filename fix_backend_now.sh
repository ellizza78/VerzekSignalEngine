#!/bin/bash
#
# Quick fix for backend API - Run this directly on Vultr server
#

echo "🔧 Quick Backend Fix"
echo "==================="
echo ""

cd /root/VerzekBackend/backend

# Step 1: Ensure utils directory structure
echo "1️⃣ Creating utils structure..."
mkdir -p utils
touch utils/__init__.py

# Step 2: Create notifications.py stub
echo "2️⃣ Creating notifications.py..."
cat > utils/notifications.py << 'EOF'
"""Notification utilities"""
import logging

logger = logging.getLogger(__name__)

def send_signal_notification(tokens, notification_data):
    """Send push notification (stub)"""
    logger.info(f"Would send notification to {len(tokens)} users: {notification_data}")
    return True

def get_subscription_user_tokens(db, subscription_types):
    """Get FCM tokens (stub)"""
    logger.info(f"Would get tokens for: {subscription_types}")
    return {}
EOF

echo "✅ Utils created"

# Step 3: Restart API
echo ""
echo "3️⃣ Restarting backend API..."
systemctl restart verzek_api
sleep 3

# Step 4: Check status
echo ""
echo "4️⃣ Checking status..."
API_STATUS=$(systemctl is-active verzek_api)
echo "API Status: $API_STATUS"

if [ "$API_STATUS" == "active" ]; then
    echo "✅ Backend API is RUNNING"
    
    # Test endpoint
    echo ""
    echo "5️⃣ Testing API endpoint..."
    curl -s http://localhost:8050/api/ping | python3 -m json.tool || echo "API not responding"
    
    echo ""
    echo "6️⃣ Testing house-signals endpoint..."
    curl -s http://localhost:8050/api/house-signals/ingest \
      -H "Content-Type: application/json" \
      -H "X-INTERNAL-TOKEN: test" \
      -X POST -d '{}' | head -5
    
else
    echo "❌ API FAILED - Checking logs..."
    tail -30 /root/VerzekBackend/backend/logs/api_error.log
fi

echo ""
echo "7️⃣ Signal Engine Status..."
systemctl status verzek-signalengine --no-pager -l | head -10

echo ""
echo "✅ Done!"
