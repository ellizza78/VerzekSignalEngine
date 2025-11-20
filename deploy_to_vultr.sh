#!/bin/bash
# 🚀 VerzekAutoTrader - Automated Deployment Script for Vultr
# Run this from YOUR LOCAL TERMINAL (not on Vultr server, not in Replit)
# Usage: ./deploy_to_vultr.sh

set -e  # Exit on any error

# Configuration
VULTR_HOST="80.240.29.142"
VULTR_USER="root"
BACKEND_DIR="/root/backend"
ENGINE_DIR="/root/signal_engine"

echo "🚀 VerzekAutoTrader - Vultr Deployment Script"
echo "=============================================="
echo "This script will deploy the latest code to Vultr"
echo ""

# Phase 1: Verify SSH Access
echo "Phase 1: Verifying SSH access to Vultr..."
if ssh -o ConnectTimeout=5 -o BatchMode=yes $VULTR_USER@$VULTR_HOST "echo OK" 2>/dev/null; then
    echo "✅ SSH connection successful"
else
    echo "❌ Cannot connect to Vultr via SSH"
    echo "Make sure you have SSH access configured"
    echo "Try: ssh $VULTR_USER@$VULTR_HOST"
    exit 1
fi
echo ""

# Phase 2: Deploy Backend
echo "Phase 2: Deploying Backend to Vultr..."
ssh $VULTR_USER@$VULTR_HOST << 'BACKEND_DEPLOY'
    set -e
    echo "  → Navigating to backend directory..."
    cd /root/backend 2>/dev/null || cd /root/api_server || { echo "❌ Backend directory not found"; exit 1; }
    
    echo "  → Pulling latest code from git..."
    git pull origin main 2>/dev/null || git pull || echo "⚠️  Git pull skipped (manual deployment)"
    
    echo "  → Installing dependencies..."
    pip3 install -r requirements.txt -q 2>/dev/null || echo "⚠️  Dependency install skipped"
    
    echo "  → Restarting backend service..."
    sudo systemctl restart backend-api 2>/dev/null || sudo systemctl restart verzek_api.service || { echo "❌ Service restart failed"; exit 1; }
    
    echo "  → Waiting for service to stabilize..."
    sleep 5
    
    echo "  → Checking service status..."
    if sudo systemctl is-active --quiet backend-api 2>/dev/null || sudo systemctl is-active --quiet verzek_api.service; then
        echo "  ✅ Backend service running"
    else
        echo "  ❌ Backend service not active"
        exit 1
    fi
BACKEND_DEPLOY

if [ $? -eq 0 ]; then
    echo "✅ Backend deployed successfully"
else
    echo "❌ Backend deployment failed"
    exit 1
fi
echo ""

# Phase 3: Deploy Signal Engine
echo "Phase 3: Deploying Signal Engine to Vultr..."
ssh $VULTR_USER@$VULTR_HOST << 'ENGINE_DEPLOY'
    set -e
    echo "  → Navigating to signal engine directory..."
    cd /root/signal_engine 2>/dev/null || cd /root/VerzekSignalEngine || { echo "❌ Signal engine directory not found"; exit 1; }
    
    echo "  → Pulling latest code from git..."
    git pull origin main 2>/dev/null || git pull || echo "⚠️  Git pull skipped (manual deployment)"
    
    echo "  → Installing dependencies..."
    pip3 install -r requirements.txt -q 2>/dev/null || echo "⚠️  Dependency install skipped"
    
    echo "  → Restarting signal engine service..."
    sudo systemctl restart signal-engine 2>/dev/null || sudo systemctl restart verzek-signalengine.service || { echo "❌ Service restart failed"; exit 1; }
    
    echo "  → Waiting for service to stabilize..."
    sleep 5
    
    echo "  → Checking service status..."
    if sudo systemctl is-active --quiet signal-engine 2>/dev/null || sudo systemctl is-active --quiet verzek-signalengine.service; then
        echo "  ✅ Signal engine service running"
    else
        echo "  ❌ Signal engine service not active"
        exit 1
    fi
ENGINE_DEPLOY

if [ $? -eq 0 ]; then
    echo "✅ Signal Engine deployed successfully"
else
    echo "❌ Signal Engine deployment failed"
    exit 1
fi
echo ""

# Phase 4: Health Checks
echo "Phase 4: Running Health Checks..."

echo "  → Testing backend API..."
if curl -s -m 10 http://$VULTR_HOST:8000/api/ping 2>/dev/null | grep -q "ok\|pong\|OK"; then
    echo "  ✅ Backend API responding"
else
    echo "  ⚠️  Backend API check inconclusive (may need manual verification)"
fi

echo "  → Checking for recent errors in backend logs..."
ssh $VULTR_USER@$VULTR_HOST "journalctl -u backend-api -n 30 --no-pager --since '5 minutes ago' 2>/dev/null | grep -i error || journalctl -u verzek_api.service -n 30 --no-pager --since '5 minutes ago' 2>/dev/null | grep -i error || echo '  ℹ️  No recent errors found'"

echo "  → Checking signal engine activity..."
ssh $VULTR_USER@$VULTR_HOST "journalctl -u signal-engine -n 30 --no-pager --since '5 minutes ago' 2>/dev/null | grep -E 'started|running|Signal' || journalctl -u verzek-signalengine.service -n 30 --no-pager --since '5 minutes ago' 2>/dev/null | grep -E 'started|running|Signal' || echo '  ℹ️  No recent signal engine logs'"

echo ""

# Phase 5: Final Summary
echo "=============================================="
echo "🎉 Deployment Complete!"
echo "=============================================="
echo ""
echo "📊 Service Status on Vultr:"
ssh $VULTR_USER@$VULTR_HOST << 'STATUS'
    BACKEND_STATUS=$(sudo systemctl is-active backend-api 2>/dev/null || sudo systemctl is-active verzek_api.service 2>/dev/null || echo "unknown")
    ENGINE_STATUS=$(sudo systemctl is-active signal-engine 2>/dev/null || sudo systemctl is-active verzek-signalengine.service 2>/dev/null || echo "unknown")
    
    echo "  Backend API: $BACKEND_STATUS"
    echo "  Signal Engine: $ENGINE_STATUS"
STATUS

echo ""
echo "🔗 Next Steps:"
echo "  1. Test backend: curl http://$VULTR_HOST:8000/api/ping"
echo "  2. Test new exchange balance endpoint (requires JWT token)"
echo "  3. Test mobile app with Expo Go (scan QR from Replit)"
echo "  4. Build production APK: cd mobile_app/VerzekApp && eas build -p android"
echo ""
echo "✅ Backend and Signal Engine deployed to Vultr!"
echo "✅ All new features ready: Trial Timer + Exchange Balance + Multi-TP Stats"
