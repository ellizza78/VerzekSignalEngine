#!/bin/bash
################################################################################
# VerzekAutoTrader - Forwarder Health Monitoring Deployment Script
# Phase 1 + 2: Heartbeat Monitoring + Auto-Restart + Telegram Alerts
################################################################################

echo "🚀 Deploying Forwarder Health Monitoring System..."
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo "❌ Please run as root (you're currently logged in as root, so just run: bash DEPLOY_PHASE1_AND_2.sh)"
   exit 1
fi

# Set working directory
cd /var/www/VerzekAutoTrader || exit 1

echo "📋 Step 1: Backing up old forwarder..."
if [ -f telethon_forwarder.py ]; then
    cp telethon_forwarder.py telethon_forwarder.py.backup.$(date +%Y%m%d_%H%M%S)
    echo "  ✅ Backup created"
fi

echo ""
echo "📋 Step 2: Stopping current forwarder..."
pkill -f telethon_forwarder.py
sleep 2
echo "  ✅ Old forwarder stopped"

echo ""
echo "📋 Step 3: Installing new files..."
echo "  ⏳ Please upload the following files to /var/www/VerzekAutoTrader/:"
echo "     - telethon_forwarder.py (v2.2 with heartbeat)"
echo "     - forwarder_watchdog.py"
echo ""
echo "  Press ENTER when files are uploaded..."
read

echo ""
echo "📋 Step 4: Making watchdog executable..."
chmod +x forwarder_watchdog.py
echo "  ✅ Permissions set"

echo ""
echo "📋 Step 5: Installing systemd services..."
cp telethon-forwarder.service /etc/systemd/system/
cp forwarder-watchdog.service /etc/systemd/system/
cp forwarder-watchdog.timer /etc/systemd/system/
systemctl daemon-reload
echo "  ✅ Services installed"

echo ""
echo "📋 Step 6: Enabling and starting forwarder service..."
systemctl enable telethon-forwarder.service
systemctl start telethon-forwarder.service
sleep 3
echo "  ✅ Forwarder service started"

echo ""
echo "📋 Step 7: Checking forwarder status..."
systemctl status telethon-forwarder.service --no-pager -l
echo ""

echo "📋 Step 8: Enabling watchdog timer..."
systemctl enable forwarder-watchdog.timer
systemctl start forwarder-watchdog.timer
echo "  ✅ Watchdog timer started"

echo ""
echo "📋 Step 9: Verifying heartbeat..."
sleep 35  # Wait for first heartbeat
if [ -f /tmp/forwarder_heartbeat.json ]; then
    echo "  ✅ Heartbeat file detected:"
    cat /tmp/forwarder_heartbeat.json
    echo ""
else
    echo "  ⚠️  Warning: No heartbeat file yet (may take up to 60 seconds)"
fi

echo ""
echo "✅ =========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "✅ =========================================="
echo ""
echo "📊 System Status:"
echo "  - Forwarder: systemctl status telethon-forwarder"
echo "  - Watchdog: systemctl status forwarder-watchdog.timer"
echo "  - Logs: tail -f telethon_forwarder.log"
echo "  - Heartbeat: cat /tmp/forwarder_heartbeat.json"
echo ""
echo "🔔 You will receive Telegram alerts if the forwarder freezes!"
echo ""
