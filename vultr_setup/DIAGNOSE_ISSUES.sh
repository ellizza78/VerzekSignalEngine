#!/bin/bash
# Diagnostic Script for VerzekAutoTrader Issues
# Run this on Vultr server to diagnose backend and signal issues

echo "════════════════════════════════════════════════════════════"
echo "  VERZEK AUTO TRADER - DIAGNOSTIC TOOL"
echo "════════════════════════════════════════════════════════════"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 ISSUE #1: Backend Connection (Port 5000)"
echo "────────────────────────────────────────────────────────────"

echo -n "1. Checking if Flask API service is running... "
if systemctl is-active --quiet verzekapi; then
    echo -e "${GREEN}✓ RUNNING${NC}"
else
    echo -e "${RED}✗ NOT RUNNING${NC}"
    echo "   Fix: sudo systemctl start verzekapi"
fi

echo -n "2. Checking if port 5000 is listening... "
if ss -tuln | grep -q ":5000 "; then
    echo -e "${GREEN}✓ LISTENING${NC}"
    ss -tuln | grep ":5000 "
else
    echo -e "${RED}✗ NOT LISTENING${NC}"
    echo "   This means Flask is not binding to 0.0.0.0:5000"
    echo "   Check logs: journalctl -u verzekapi -n 50"
fi

echo -n "3. Checking firewall for port 5000... "
if ufw status | grep -q "5000.*ALLOW"; then
    echo -e "${GREEN}✓ ALLOWED${NC}"
elif ! command -v ufw &> /dev/null; then
    echo -e "${YELLOW}⚠ UFW not installed${NC}"
else
    echo -e "${RED}✗ BLOCKED${NC}"
    echo "   Fix: sudo ufw allow 5000/tcp && sudo ufw reload"
fi

echo -n "4. Testing local backend connection... "
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/ping 2>&1)
if [ "$response" = "200" ]; then
    echo -e "${GREEN}✓ RESPONDS (HTTP $response)${NC}"
    curl -s http://localhost:5000/ping | python3 -m json.tool 2>/dev/null || echo "   JSON parse error"
elif [ "$response" = "000" ]; then
    echo -e "${RED}✗ CONNECTION REFUSED${NC}"
    echo "   Flask is not running or not binding to 0.0.0.0:5000"
else
    echo -e "${YELLOW}⚠ HTTP $response${NC}"
fi

echo -n "5. Testing external backend connection... "
external_response=$(curl -s -o /dev/null -w "%{http_code}" http://80.240.29.142:5000/ping 2>&1)
if [ "$external_response" = "200" ]; then
    echo -e "${GREEN}✓ RESPONDS (HTTP $external_response)${NC}"
else
    echo -e "${RED}✗ FAILED (HTTP $external_response)${NC}"
fi

echo ""
echo "📊 API Service Logs (last 20 lines):"
echo "────────────────────────────────────────────────────────────"
journalctl -u verzekapi -n 20 --no-pager
echo ""

echo "🔍 ISSUE #2: Broadcast Bot Not Receiving Signals"
echo "────────────────────────────────────────────────────────────"

echo -n "1. Checking if Telethon bot service is running... "
if systemctl is-active --quiet verzekbot; then
    echo -e "${GREEN}✓ RUNNING${NC}"
else
    echo -e "${RED}✗ NOT RUNNING${NC}"
    echo "   Fix: sudo systemctl start verzekbot"
fi

echo -n "2. Checking Telethon session file... "
if [ -f "/var/www/VerzekAutoTrader/telethon_session_prod.txt" ]; then
    echo -e "${GREEN}✓ EXISTS${NC}"
    echo "   Location: /var/www/VerzekAutoTrader/telethon_session_prod.txt"
elif [ -f "/var/www/VerzekAutoTrader/telethon_session_dev.txt" ]; then
    echo -e "${YELLOW}⚠ DEV SESSION ONLY${NC}"
    echo "   You're using dev session, production may not work"
else
    echo -e "${RED}✗ MISSING${NC}"
    echo "   You need to run: python3 setup_telethon.py"
fi

echo -n "3. Checking environment variables... "
missing_vars=""
cd /var/www/VerzekAutoTrader 2>/dev/null
if ! grep -q "TELEGRAM_API_ID" .env 2>/dev/null; then
    missing_vars="$missing_vars TELEGRAM_API_ID"
fi
if ! grep -q "TELEGRAM_API_HASH" .env 2>/dev/null; then
    missing_vars="$missing_vars TELEGRAM_API_HASH"
fi

if [ -z "$missing_vars" ]; then
    echo -e "${GREEN}✓ CONFIGURED${NC}"
else
    echo -e "${RED}✗ MISSING:$missing_vars${NC}"
    echo "   Add them to /var/www/VerzekAutoTrader/.env"
fi

echo -n "4. Checking monitored channel configuration... "
if grep -q "2249790469" /var/www/VerzekAutoTrader/telethon_forwarder.py 2>/dev/null; then
    echo -e "${GREEN}✓ CONFIGURED (Channel: 2249790469)${NC}"
else
    echo -e "${RED}✗ NOT FOUND${NC}"
fi

echo ""
echo "📊 Telethon Bot Logs (last 20 lines):"
echo "────────────────────────────────────────────────────────────"
journalctl -u verzekbot -n 20 --no-pager
echo ""

echo "🔍 ISSUE #3: Replit Bridge Connection"
echo "────────────────────────────────────────────────────────────"

echo -n "Testing Replit bridge... "
bridge_response=$(curl -s -o /dev/null -w "%{http_code}" https://verzek-auto-trader.replit.app/ping 2>&1)
if [ "$bridge_response" = "200" ]; then
    echo -e "${GREEN}✓ RESPONDS (HTTP $bridge_response)${NC}"
    curl -s https://verzek-auto-trader.replit.app/ping | python3 -m json.tool 2>/dev/null
elif [ "$bridge_response" = "502" ] || [ "$bridge_response" = "504" ]; then
    echo -e "${YELLOW}⚠ BACKEND UNREACHABLE (HTTP $bridge_response)${NC}"
    echo "   The bridge is working but cannot reach this Vultr server"
else
    echo -e "${RED}✗ FAILED (HTTP $bridge_response)${NC}"
fi

echo ""
echo "🔍 WATCHDOG STATUS"
echo "────────────────────────────────────────────────────────────"

echo -n "Watchdog service status... "
if systemctl is-active --quiet verzekwatchdog; then
    echo -e "${GREEN}✓ RUNNING${NC}"
else
    echo -e "${RED}✗ NOT RUNNING${NC}"
    echo "   Fix: sudo systemctl start verzekwatchdog"
fi

echo ""
if [ -f "/var/log/verzek_watchdog.log" ]; then
    echo "📊 Watchdog Log (last 10 lines):"
    tail -10 /var/log/verzek_watchdog.log
else
    echo -e "${YELLOW}⚠ No watchdog log found${NC}"
fi

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  DIAGNOSTIC COMPLETE"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "📋 QUICK FIXES:"
echo "────────────────────────────────────────────────────────────"
echo "• Restart all services:"
echo "  sudo systemctl restart verzekapi verzekbot verzekwatchdog"
echo ""
echo "• View live logs:"
echo "  journalctl -u verzekapi -f"
echo "  journalctl -u verzekbot -f"
echo ""
echo "• Open firewall:"
echo "  sudo ufw allow 5000/tcp && sudo ufw reload"
echo ""
echo "• Check system status:"
echo "  bash /opt/verzek_status.sh"
echo ""
