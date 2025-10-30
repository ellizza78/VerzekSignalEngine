#!/bin/bash
# Deploy Complete Referral System to Vultr
# Run this script from your local machine or any server that can SSH to Vultr

VULTR_IP="80.240.29.142"
VULTR_USER="root"
VULTR_PATH="/var/www/VerzekAutoTrader"

echo "🚀 Deploying Referral System to Vultr..."

# Connect to Vultr and fix the API server
ssh ${VULTR_USER}@${VULTR_IP} << 'ENDSSH'

cd /var/www/VerzekAutoTrader

echo "📝 Backing up current api_server.py..."
cp api_server.py api_server.py.backup.$(date +%Y%m%d_%H%M%S)

echo "🔍 Checking for referral_handler import..."
if grep -q "from referral_handler import\|import referral_handler" api_server.py; then
    echo "❌ Found outdated referral_handler import - removing it..."
    sed -i '/from referral_handler import/d' api_server.py
    sed -i '/import referral_handler/d' api_server.py
    echo "✅ Removed referral_handler import"
else
    echo "✅ No referral_handler import found - already clean"
fi

echo "🔍 Checking if referral endpoints exist..."
if grep -q "@app.route(\"/api/referral/code\"" api_server.py; then
    echo "✅ Referral endpoints already exist in api_server.py"
else
    echo "❌ Referral endpoints missing - need to update api_server.py from Replit"
    exit 1
fi

echo "🔄 Restarting API server..."
sudo systemctl restart verzekapi.service

echo "⏳ Waiting for service to start..."
sleep 3

echo "✅ Checking service status..."
sudo systemctl status verzekapi.service --no-pager

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "📋 Test the referral system:"
echo "  curl http://localhost:5000/api/referral/code -H 'Authorization: Bearer YOUR_TOKEN'"
echo ""

ENDSSH

echo "✅ Done! Check the output above for any errors."
