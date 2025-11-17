#!/bin/bash
# FINAL DEPLOYMENT SCRIPT - Copy these 2 files to Vultr and restart
# Run on Vultr: ssh root@80.240.29.142 'bash -s' < VULTR_DEPLOY_NOW.sh

echo "🚀 Deploying Email Verification Fix to Vultr Production"
echo "========================================================"

# Step 1: Navigate to production directory
cd /root/api_server || {
    echo "❌ ERROR: /root/api_server not found!"
    echo "Trying /root/workspace/backend..."
    cd /root/workspace/backend || exit 1
}

echo "✅ Working in: $(pwd)"

# Step 2: Backup existing files
echo "📦 Creating backups..."
cp utils/tokens.py utils/tokens.py.backup_$(date +%Y%m%d_%H%M%S)
cp utils/email.py utils/email.py.backup_$(date +%Y%m%d_%H%M%S)

# Step 3: Show current wrong content
echo ""
echo "❌ BEFORE (current WRONG content):"
echo "Token expiration:"
grep "timedelta(hours=" utils/tokens.py 2>/dev/null || echo "Not found"
echo ""
echo "Email text:"
grep "expires in" utils/email.py 2>/dev/null || echo "Not found"
echo ""
echo "Email URL:"
grep "verification_url.*=" utils/email.py 2>/dev/null || echo "Not found"
echo ""

# Step 4: Deploy fixed files
# You need to copy tokens.py and email.py from VULTR_FIX_FILES folder
# to /root/api_server/utils/ on the server

echo "⚠️  MANUAL STEP REQUIRED:"
echo "Copy these files to /root/api_server/utils/:"
echo "  - VULTR_FIX_FILES/tokens.py → /root/api_server/utils/tokens.py"
echo "  - VULTR_FIX_FILES/email.py → /root/api_server/utils/email.py"
echo ""
read -p "Press ENTER after copying files..."

# Step 5: Verify changes
echo ""
echo "✅ AFTER (verifying fixes):"
echo "Token expiration (should show 'minutes=15'):"
grep "timedelta(minutes=" utils/tokens.py | head -2
echo ""
echo "Email text (should show '15 minutes'):"
grep "expires in.*15 minutes" utils/email.py | head -2
echo ""
echo "Email URL (should show 'https://api.verzekinnovative.com'):"
grep "api.verzekinnovative.com" utils/email.py | head -2
echo ""

# Step 6: Clear Python cache
echo "🗑️  Clearing Python bytecode cache..."
find /root/api_server -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find /root/api_server -name "*.pyc" -delete 2>/dev/null || true

# Step 7: Restart with full reload
echo "🔄 Restarting verzek_api service..."
systemctl stop verzek_api
sleep 2
systemctl start verzek_api
sleep 5

# Step 8: Check status
if systemctl is-active --quiet verzek_api; then
    echo ""
    echo "✅✅✅ SUCCESS! Service is running ✅✅✅"
    echo ""
    systemctl status verzek_api --no-pager -l | head -15
    echo ""
    echo "🎉 DEPLOYMENT COMPLETE!"
    echo ""
    echo "Test with new registration - email should now show:"
    echo "  ✅ Expires in 15 minutes"
    echo "  ✅ URL: https://api.verzekinnovative.com/api/auth/verify-email?..."
else
    echo ""
    echo "❌❌❌ FAILED - Service not running ❌❌❌"
    echo ""
    journalctl -u verzek_api -n 30 --no-pager
    exit 1
fi
