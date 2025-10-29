#!/bin/bash
# CHECK_7AM_SIGNAL.sh - Check if 7:00am signal was received and processed

echo "🔍 Checking signal flow at 7:00am..."
echo "=================================================="
echo ""

echo "1️⃣ TELETHON LOGS (verzekbot) - Did Telethon receive the signal?"
echo "Looking for messages around 07:00..."
journalctl -u verzekbot --since "today 06:55" --until "today 07:10" --no-pager | grep -E "Received message|Signal|07:0"
echo ""

echo "2️⃣ FLASK API LOGS (verzekapi) - Did Flask receive the signal from Telethon?"
echo "Looking for /api/broadcast/signal calls..."
journalctl -u verzekapi --since "today 06:55" --until "today 07:10" --no-pager | grep -E "broadcast|signal|Signal"
echo ""

echo "3️⃣ CHECKING IF SERVICES ARE RUNNING"
sudo systemctl is-active verzekbot
sudo systemctl is-active verzekapi
echo ""

echo "4️⃣ RECENT VERZEKBOT LOGS (last 50 lines)"
journalctl -u verzekbot -n 50 --no-pager
echo ""

echo "5️⃣ RECENT VERZEKAPI LOGS (last 50 lines)"
journalctl -u verzekapi -n 50 --no-pager
