#!/bin/bash
# Quick Deploy Script - Email Verification Security Fix
# Run this on Vultr server: bash DEPLOY_TO_VULTR.sh

echo "🚀 Deploying Email Verification Security Fixes to Vultr..."
echo "=================================================="

cd /root/workspace/backend || exit 1

# Backup current files
cp utils/tokens.py utils/tokens.py.backup
cp utils/email.py utils/email.py.backup
cp auth_routes.py auth_routes.py.backup

echo "✅ Backed up existing files"

# Fix 1: Change token expiration from 24 hours to 15 minutes
sed -i 's/timedelta(hours=24)/timedelta(minutes=15)/g' utils/tokens.py
echo "✅ Fixed token expiration (15 minutes)"

# Fix 2: Update email template text
sed -i 's/This link expires in 24 hours/This link expires in 15 minutes/g' utils/email.py
echo "✅ Fixed email template text"

# Fix 3: Add GET endpoint support (requires manual edit - see below)
echo "⚠️  Manual step required for auth_routes.py GET endpoints"

# Restart API server
echo "🔄 Restarting API server..."
systemctl restart verzek_api

sleep 3

# Check status
if systemctl is-active --quiet verzek_api; then
    echo "✅ API server restarted successfully!"
    echo ""
    echo "📊 Server Status:"
    systemctl status verzek_api --no-pager | head -10
    echo ""
    echo "🎉 Deployment Complete!"
    echo "New users will receive emails with 15-minute expiration links"
else
    echo "❌ API server failed to start!"
    echo "Rolling back..."
    cp utils/tokens.py.backup utils/tokens.py
    cp utils/email.py.backup utils/email.py
    systemctl restart verzek_api
    exit 1
fi
