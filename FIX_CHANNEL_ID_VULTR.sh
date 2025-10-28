#!/bin/bash
# FIX_CHANNEL_ID_VULTR.sh - Update channel ID on Vultr server
# This fixes the signal monitoring issue by correcting the channel ID

echo "🔧 Fixing Channel ID on Vultr Server"
echo "====================================="
echo ""

cd /var/www/VerzekAutoTrader

echo "1️⃣ Backing up current telethon_forwarder.py..."
cp telethon_forwarder.py telethon_forwarder.py.backup.$(date +%Y%m%d_%H%M%S)

echo "2️⃣ Updating MONITORED_CHANNELS from 2249790469 to -1002249790469..."
sed -i 's/MONITORED_CHANNELS = \[/MONITORED_CHANNELS = [/' telethon_forwarder.py
sed -i 's/    2249790469,/    -1002249790469,/' telethon_forwarder.py

echo "3️⃣ Verifying the change..."
if grep -q "\-1002249790469" telethon_forwarder.py; then
    echo "✅ Channel ID updated successfully!"
    grep -A 2 "MONITORED_CHANNELS" telethon_forwarder.py | head -4
else
    echo "❌ Failed to update channel ID"
    exit 1
fi

echo ""
echo "4️⃣ Restarting verzekbot service..."
sudo systemctl restart verzekbot

echo ""
echo "5️⃣ Waiting 3 seconds for service to start..."
sleep 3

echo ""
echo "6️⃣ Checking verzekbot status..."
sudo systemctl status verzekbot --no-pager | head -15

echo ""
echo "7️⃣ Checking logs for channel monitoring..."
echo "Last 20 lines of verzekbot logs:"
journalctl -u verzekbot -n 20 --no-pager

echo ""
echo "✅ FIX COMPLETE!"
echo ""
echo "📋 Summary:"
echo "  - Old Channel ID: 2249790469 (WRONG - missing -100 prefix)"
echo "  - New Channel ID: -1002249790469 (CORRECT)"
echo "  - Service restarted: verzekbot"
echo ""
echo "🎯 Next signal from 'Ai Golden Crypto (🔱VIP)' will be detected and forwarded!"
echo ""
echo "To monitor signals in real-time, run:"
echo "  journalctl -u verzekbot -f"
