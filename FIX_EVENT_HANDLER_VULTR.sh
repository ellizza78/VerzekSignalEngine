#!/bin/bash
# FIX_EVENT_HANDLER_VULTR.sh - Fix Telethon event handler to listen explicitly to monitored channels
# This solves the issue where channel messages aren't being received after service restart

echo "🔧 Fixing Telethon Event Handler on Vultr Server"
echo "================================================="
echo ""

cd /var/www/VerzekAutoTrader

echo "1️⃣ Backing up current telethon_forwarder.py..."
cp telethon_forwarder.py telethon_forwarder.py.backup.eventhandler.$(date +%Y%m%d_%H%M%S)

echo "2️⃣ Updating event handler to listen explicitly to monitored channels..."
sed -i 's/@client.on(events.NewMessage(incoming=True))/@client.on(events.NewMessage(chats=MONITORED_CHANNELS, incoming=True))/' telethon_forwarder.py

echo "3️⃣ Verifying the change..."
if grep -q "chats=MONITORED_CHANNELS" telethon_forwarder.py; then
    echo "✅ Event handler updated successfully!"
    grep "chats=MONITORED_CHANNELS" telethon_forwarder.py
else
    echo "❌ Failed to update event handler"
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
echo "7️⃣ Watching for channel messages..."
echo "Last 30 lines of verzekbot logs:"
journalctl -u verzekbot -n 30 --no-pager

echo ""
echo "✅ FIX COMPLETE!"
echo ""
echo "📋 What was fixed:"
echo "  - OLD: @client.on(events.NewMessage(incoming=True))"
echo "  - NEW: @client.on(events.NewMessage(chats=MONITORED_CHANNELS, incoming=True))"
echo ""
echo "🎯 Now Telethon will ONLY listen to channel -1002249790469"
echo "   This ensures channel messages are properly received and forwarded!"
echo ""
echo "To monitor signals in real-time, run:"
echo "  journalctl -u verzekbot -f"
