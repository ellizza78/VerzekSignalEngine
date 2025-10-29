#!/bin/bash
# CHECK_BROADCAST_FLOW.sh - Debug why signals aren't reaching VIP/TRIAL groups

echo "🔍 BROADCAST FLOW DIAGNOSTIC"
echo "=================================================="
echo ""

echo "1️⃣ Check if BROADCAST_BOT_TOKEN exists in .env"
grep BROADCAST_BOT_TOKEN /var/www/VerzekAutoTrader/.env
echo ""

echo "2️⃣ Check verzekapi logs for broadcast attempts (last 100 lines)"
journalctl -u verzekapi -n 100 --no-pager | grep -E "broadcast|signal|VIP|TRIAL|Message sent"
echo ""

echo "3️⃣ Check for any errors in verzekapi"
journalctl -u verzekapi -n 100 --no-pager | grep -E "Error|error|Failed|failed|Exception"
echo ""

echo "4️⃣ Check if verzekapi is loading environment variables"
sudo systemctl show verzekapi | grep Environment
echo ""

echo "5️⃣ Test if Flask can import broadcast handler"
cd /var/www/VerzekAutoTrader
source venv/bin/activate
python3 -c "import broadcast_bot_webhook_handler; print('✅ Broadcast handler imports OK')" 2>&1
echo ""

echo "6️⃣ Check recent signal receives in verzekapi"
journalctl -u verzekapi --since "today 06:00" --no-pager | grep -E "Received signal|broadcast/signal"
