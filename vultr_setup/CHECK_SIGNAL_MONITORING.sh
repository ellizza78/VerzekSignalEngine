#!/bin/bash
# Signal Monitoring Diagnostic - VerzekAutoTrader
# Run this on Vultr to diagnose why signals aren't being forwarded

echo "════════════════════════════════════════════════════════════"
echo "  SIGNAL MONITORING DIAGNOSTIC"
echo "════════════════════════════════════════════════════════════"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "🔍 STEP 1: Check if verzekbot service is running"
echo "────────────────────────────────────────────────────────────"

if systemctl is-active --quiet verzekbot; then
    echo -e "${GREEN}✓ verzekbot is RUNNING${NC}"
else
    echo -e "${RED}✗ verzekbot is NOT RUNNING${NC}"
    echo ""
    echo "This is the problem! Starting verzekbot now..."
    sudo systemctl start verzekbot
    sudo systemctl enable verzekbot
    sleep 2
    if systemctl is-active --quiet verzekbot; then
        echo -e "${GREEN}✓ verzekbot started successfully${NC}"
    else
        echo -e "${RED}✗ Failed to start verzekbot${NC}"
        echo "Check logs: journalctl -u verzekbot -n 50"
        exit 1
    fi
fi

echo ""
echo "🔍 STEP 2: Check Telethon session file"
echo "────────────────────────────────────────────────────────────"

if [ -f "/var/www/VerzekAutoTrader/telethon_session_prod.txt" ]; then
    echo -e "${GREEN}✓ Production session exists${NC}"
elif [ -f "/var/www/VerzekAutoTrader/telethon_session_dev.txt" ]; then
    echo -e "${YELLOW}⚠ Only dev session found (may not work in production)${NC}"
else
    echo -e "${RED}✗ NO SESSION FILE FOUND${NC}"
    echo ""
    echo "You need to create a session:"
    echo "  cd /var/www/VerzekAutoTrader"
    echo "  source venv/bin/activate"
    echo "  python3 setup_telethon.py"
    exit 1
fi

echo ""
echo "🔍 STEP 3: Check environment variables"
echo "────────────────────────────────────────────────────────────"

cd /var/www/VerzekAutoTrader 2>/dev/null
if grep -q "TELEGRAM_API_ID" .env 2>/dev/null && grep -q "TELEGRAM_API_HASH" .env 2>/dev/null; then
    echo -e "${GREEN}✓ TELEGRAM_API_ID and TELEGRAM_API_HASH configured${NC}"
else
    echo -e "${RED}✗ Missing Telegram credentials in .env${NC}"
    echo "Add these to /var/www/VerzekAutoTrader/.env:"
    echo "  TELEGRAM_API_ID=your_api_id"
    echo "  TELEGRAM_API_HASH=your_api_hash"
    exit 1
fi

echo ""
echo "🔍 STEP 4: Check monitored channel configuration"
echo "────────────────────────────────────────────────────────────"

if grep -q "2249790469" /var/www/VerzekAutoTrader/telethon_forwarder.py 2>/dev/null; then
    echo -e "${GREEN}✓ Monitoring channel 2249790469 (Ai Golden Crypto VIP)${NC}"
else
    echo -e "${RED}✗ Channel 2249790469 not configured${NC}"
fi

echo ""
echo "🔍 STEP 5: Check recent logs for signal activity"
echo "────────────────────────────────────────────────────────────"

echo "Last 20 log lines from verzekbot:"
journalctl -u verzekbot -n 20 --no-pager

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  LIVE MONITORING TEST"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Now watching for incoming messages in REAL-TIME..."
echo "When a signal is posted to channel 2249790469, you should see:"
echo "  - '🔔 Received message from chat 2249790469'"
echo "  - Either '[SIGNAL] Forwarding signal' or '⏭️ Skipped non-signal'"
echo ""
echo "Press Ctrl+C to stop monitoring"
echo ""
echo "────────────────────────────────────────────────────────────"

journalctl -u verzekbot -f
