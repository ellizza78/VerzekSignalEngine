#!/bin/bash
# CORRECT Deployment Script for Vultr Production Server
# Production path: /root/api_server (NOT /root/workspace/backend)

echo "🚀 Deploying Email Verification Security Fixes to Vultr Production..."
echo "======================================================================="

# Navigate to CORRECT production directory
cd /root/api_server || {
    echo "❌ ERROR: /root/api_server not found!"
    exit 1
}

echo "📁 Working directory: $(pwd)"

# Backup current files
echo "📦 Creating backups..."
cp utils/tokens.py utils/tokens.py.backup
cp utils/email.py utils/email.py.backup
cp auth_routes.py auth_routes.py.backup

# Fix 1: Token expiration (24 hours → 15 minutes)
echo "⚙️  Fix 1: Changing token expiration to 15 minutes..."
sed -i 's/timedelta(hours=24)/timedelta(minutes=15)/g' utils/tokens.py

# Fix 2: Email template text
echo "⚙️  Fix 2: Updating email template text..."
sed -i 's/This link expires in 24 hours/This link expires in 15 minutes/g' utils/email.py

# Verify changes
echo ""
echo "✅ Verifying changes..."
echo "Token expiration (should show 'minutes=15'):"
grep "timedelta(minutes=" utils/tokens.py | head -2
echo ""
echo "Email text (should show '15 minutes'):"
grep "expires in" utils/email.py | head -2
echo ""

# Delete .pyc cache files to force reload
echo "🗑️  Clearing Python cache..."
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Restart API with Gunicorn workers reload
echo "🔄 Restarting verzek_api service..."
systemctl restart verzek_api

# Wait for service to start
sleep 5

# Check status
echo ""
echo "📊 Checking service status..."
if systemctl is-active --quiet verzek_api; then
    echo "✅ verzek_api is RUNNING"
    echo ""
    echo "Service details:"
    systemctl status verzek_api --no-pager -l | head -15
    echo ""
    echo "🎉 DEPLOYMENT SUCCESSFUL!"
    echo ""
    echo "Next steps:"
    echo "1. Test with new registration - email should say '15 minutes'"
    echo "2. Mobile app will show '15 minutes' after OTA update loads"
else
    echo "❌ verzek_api FAILED TO START!"
    echo ""
    echo "Rolling back changes..."
    cp utils/tokens.py.backup utils/tokens.py
    cp utils/email.py.backup utils/email.py
    cp auth_routes.py.backup auth_routes.py
    systemctl restart verzek_api
    echo "⚠️  Rollback complete. Please check logs: journalctl -u verzek_api -n 50"
    exit 1
fi
