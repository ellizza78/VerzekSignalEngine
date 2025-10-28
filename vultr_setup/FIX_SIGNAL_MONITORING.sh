#!/bin/bash
# Quick Fix for Signal Monitoring - VerzekAutoTrader
# This script will get your signal monitoring working

echo "════════════════════════════════════════════════════════════"
echo "  FIXING SIGNAL MONITORING"
echo "════════════════════════════════════════════════════════════"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Step 1: Restart verzekbot service
echo "🔄 Step 1: Restarting verzekbot service..."
sudo systemctl restart verzekbot
sudo systemctl enable verzekbot
sleep 3

# Step 2: Check if it's running
echo -n "Checking verzekbot status... "
if systemctl is-active --quiet verzekbot; then
    echo -e "${GREEN}✓ RUNNING${NC}"
else
    echo -e "${RED}✗ FAILED TO START${NC}"
    echo ""
    echo "Checking error logs:"
    journalctl -u verzekbot -n 30 --no-pager
    echo ""
    echo "Common issues:"
    echo "1. Missing session file - Run: python3 setup_telethon.py"
    echo "2. Missing credentials - Check .env file"
    echo "3. Python dependencies - Run: pip install telethon"
    exit 1
fi

# Step 3: Check logs for connection
echo ""
echo "📊 Recent logs (checking for 'Connected successfully'):"
echo "────────────────────────────────────────────────────────────"
journalctl -u verzekbot -n 20 --no-pager | grep -E "TELETHON|Connected|ERROR|session"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  ✅ VERZEKBOT RESTARTED"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "What to expect now:"
echo ""
echo "1. When a signal is posted to channel 2249790469, you will see:"
echo "   - '🔔 Received message from chat 2249790469: ...'"
echo "   - '[SIGNAL] Forwarding signal to broadcast bot'"
echo "   - '✅ Signal forwarded successfully'"
echo ""
echo "2. If you see '⏭️ Skipped non-signal message', the filter is"
echo "   working but the message didn't contain signal keywords."
echo ""
echo "3. Monitor live activity with:"
echo "   journalctl -u verzekbot -f"
echo ""
echo "🧪 Testing connection to broadcast API..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5000/ping 2>&1)
if [ "$response" = "200" ]; then
    echo -e "${GREEN}✓ Broadcast API is reachable${NC}"
else
    echo -e "${YELLOW}⚠ Broadcast API not reachable (HTTP $response)${NC}"
    echo "Signals will be detected but may fail to forward"
    echo "Fix backend first: bash /tmp/FIX_BACKEND.sh"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Wait for a signal to be posted to channel 2249790469"
echo "2. Watch logs: journalctl -u verzekbot -f"
echo "3. You should see it detect and forward the signal"
echo ""
echo "If still no signals appear, run:"
echo "  bash /tmp/CHECK_SIGNAL_MONITORING.sh"
echo ""
