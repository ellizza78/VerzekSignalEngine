#!/bin/bash
# VerzekAutoTrader Production Verification Script
# Run this on Vultr server to verify entire system

set -e

echo "=========================================="
echo "VERZEK AUTOTRADER - PRODUCTION VERIFICATION"
echo "=========================================="
echo "Server: $(hostname)"
echo "IP: $(curl -s ifconfig.me)"
echo "Date: $(date)"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PASS=0
FAIL=0

check_pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((PASS++))
}

check_fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((FAIL++))
}

check_warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
}

echo "=========================================="
echo "1. BACKEND API SERVICE"
echo "=========================================="

# Check verzek_api service
if systemctl is-active --quiet verzek_api; then
    check_pass "Backend API service is running"
    
    # Check process details
    GUNICORN_WORKERS=$(ps aux | grep "gunicorn.*api_server:app" | grep -v grep | wc -l)
    if [ "$GUNICORN_WORKERS" -gt 0 ]; then
        check_pass "Gunicorn running with $GUNICORN_WORKERS workers"
    else
        check_fail "Gunicorn not running (found Flask dev server)"
    fi
else
    check_fail "Backend API service is NOT running"
    echo "   To start: sudo systemctl start verzek_api"
fi

# Check API endpoint
if curl -s --max-time 5 http://localhost:8050/api/health | grep -q "healthy"; then
    check_pass "Backend API responding on port 8050"
else
    check_fail "Backend API not responding on port 8050"
fi

# Check external access
if curl -s --max-time 5 https://api.verzekinnovative.com/api/health | grep -q "healthy"; then
    check_pass "Backend API accessible via HTTPS"
else
    check_fail "Backend API NOT accessible via HTTPS"
fi

echo ""
echo "=========================================="
echo "2. VERZEKSIGNALENGINE SERVICE"
echo "=========================================="

# Check VerzekSignalEngine service
if systemctl is-active --quiet verzek-signalengine; then
    check_pass "VerzekSignalEngine service is running"
    
    # Check how long it's been running
    UPTIME=$(systemctl show verzek-signalengine --property=ActiveEnterTimestamp --value)
    echo "   Started: $UPTIME"
    
    # Check process
    if ps aux | grep -q "python3 -m signal_engine.main"; then
        check_pass "SignalEngine process found"
    else
        check_warn "SignalEngine service active but process not found"
    fi
else
    check_fail "VerzekSignalEngine service is NOT running"
    echo "   To start: sudo systemctl start verzek-signalengine"
    echo "   To enable: sudo systemctl enable verzek-signalengine"
fi

# Check signal engine logs
if [ -f "/root/signal_engine/logs/signalengine.log" ]; then
    LOG_SIZE=$(du -h /root/signal_engine/logs/signalengine.log | cut -f1)
    check_pass "SignalEngine log file exists (${LOG_SIZE})"
    
    # Check for recent activity
    RECENT_LOGS=$(tail -5 /root/signal_engine/logs/signalengine.log 2>/dev/null | wc -l)
    if [ "$RECENT_LOGS" -gt 0 ]; then
        echo "   Recent log entries found:"
        tail -3 /root/signal_engine/logs/signalengine.log | sed 's/^/   /'
    fi
else
    check_warn "SignalEngine log file not found"
fi

echo ""
echo "=========================================="
echo "3. DATABASE"
echo "=========================================="

# Load secrets
if [ -f "/root/.verzek_secrets" ]; then
    source /root/.verzek_secrets
    check_pass "Secrets file loaded"
else
    check_fail "Secrets file not found at /root/.verzek_secrets"
fi

# Check PostgreSQL
if systemctl is-active --quiet postgresql; then
    check_pass "PostgreSQL service is running"
else
    check_fail "PostgreSQL service is NOT running"
fi

# Check database connection
if [ -n "$DATABASE_URL" ]; then
    # Extract database name from URL
    DB_NAME=$(echo $DATABASE_URL | sed 's/.*\/\([^?]*\).*/\1/')
    
    # Try to count house signals
    SIGNAL_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM house_signals;" 2>/dev/null | tr -d ' ')
    if [ -n "$SIGNAL_COUNT" ]; then
        check_pass "Database connected - $SIGNAL_COUNT house signals found"
        
        if [ "$SIGNAL_COUNT" -eq 0 ]; then
            check_warn "No signals in database - VerzekSignalEngine may not be generating signals yet"
        fi
    else
        check_fail "Could not query database"
    fi
fi

echo ""
echo "=========================================="
echo "4. TELEGRAM INTEGRATION"
echo "=========================================="

# Check Telegram bot token
if [ -n "$BROADCAST_BOT_TOKEN" ]; then
    check_pass "Telegram bot token configured"
    
    # Test bot API
    BOT_RESPONSE=$(curl -s "https://api.telegram.org/bot${BROADCAST_BOT_TOKEN}/getMe")
    if echo "$BOT_RESPONSE" | grep -q '"ok":true'; then
        BOT_USERNAME=$(echo "$BOT_RESPONSE" | grep -o '"username":"[^"]*"' | cut -d'"' -f4)
        check_pass "Telegram bot API working (@${BOT_USERNAME})"
    else
        check_fail "Telegram bot token invalid or API not accessible"
    fi
else
    check_fail "BROADCAST_BOT_TOKEN not set"
fi

# Check chat IDs
if [ -n "$TELEGRAM_VIP_CHAT_ID" ]; then
    check_pass "VIP chat ID configured ($TELEGRAM_VIP_CHAT_ID)"
else
    check_fail "TELEGRAM_VIP_CHAT_ID not set"
fi

if [ -n "$TELEGRAM_TRIAL_CHAT_ID" ]; then
    check_pass "TRIAL chat ID configured ($TELEGRAM_TRIAL_CHAT_ID)"
else
    check_fail "TELEGRAM_TRIAL_CHAT_ID not set"
fi

echo ""
echo "=========================================="
echo "5. ENVIRONMENT CONFIGURATION"
echo "=========================================="

# Check mode
MODE="${MODE:-paper}"
if [ "$MODE" = "paper" ]; then
    check_pass "Trading mode: PAPER (safe for testing)"
elif [ "$MODE" = "live" ]; then
    check_warn "Trading mode: LIVE (real money trading enabled)"
else
    check_warn "Trading mode: $MODE (unknown)"
fi

# Check critical secrets
[ -n "$HOUSE_ENGINE_TOKEN" ] && check_pass "HOUSE_ENGINE_TOKEN set" || check_fail "HOUSE_ENGINE_TOKEN not set"
[ -n "$DATABASE_URL" ] && check_pass "DATABASE_URL set" || check_fail "DATABASE_URL not set"
[ -n "$ENCRYPTION_MASTER_KEY" ] && check_pass "ENCRYPTION_MASTER_KEY set" || check_fail "ENCRYPTION_MASTER_KEY not set"

echo ""
echo "=========================================="
echo "6. SIGNAL GENERATION TEST"
echo "=========================================="

# Send a test signal to verify the pipeline
echo "Sending test signal to backend..."

TEST_SIGNAL='{
  "source": "VERIFICATION_TEST",
  "symbol": "BTCUSDT",
  "side": "LONG",
  "entry": 43500.00,
  "stop_loss": 43000.00,
  "take_profits": [43800, 44000, 44500],
  "timeframe": "M5",
  "confidence": 99,
  "metadata": {"test": true, "verification": "automated"}
}'

TEST_RESPONSE=$(curl -s -X POST http://localhost:8050/api/house-signals/ingest \
  -H "Content-Type: application/json" \
  -H "X-INTERNAL-TOKEN: $HOUSE_ENGINE_TOKEN" \
  -d "$TEST_SIGNAL")

if echo "$TEST_RESPONSE" | grep -q '"ok":true'; then
    SIGNAL_ID=$(echo "$TEST_RESPONSE" | grep -o '"signal_id":[0-9]*' | cut -d':' -f2)
    check_pass "Test signal ingested successfully (ID: $SIGNAL_ID)"
    
    # Verify it was stored
    sleep 1
    VERIFY_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM house_signals WHERE id=$SIGNAL_ID;" 2>/dev/null | tr -d ' ')
    if [ "$VERIFY_COUNT" = "1" ]; then
        check_pass "Test signal verified in database"
    else
        check_fail "Test signal not found in database"
    fi
else
    check_fail "Test signal ingestion failed"
    echo "$TEST_RESPONSE" | jq . 2>/dev/null || echo "$TEST_RESPONSE"
fi

echo ""
echo "=========================================="
echo "7. AUTO-DEPLOYMENT"
echo "=========================================="

# Check auto-deployment timer
if systemctl is-active --quiet verzek-deploy.timer; then
    check_pass "Auto-deployment timer is active"
    
    # Check last deployment
    LAST_DEPLOY=$(systemctl list-timers verzek-deploy.timer --no-pager | grep verzek-deploy.timer | awk '{print $4, $5, $6}')
    echo "   Next deployment: $LAST_DEPLOY"
else
    check_warn "Auto-deployment timer not active"
fi

echo ""
echo "=========================================="
echo "SUMMARY"
echo "=========================================="
echo -e "${GREEN}Passed: $PASS${NC}"
echo -e "${RED}Failed: $FAIL${NC}"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ ALL SYSTEMS OPERATIONAL${NC}"
    echo "Your VerzekAutoTrader production system is ready!"
    exit 0
else
    echo -e "${YELLOW}⚠️  ISSUES DETECTED${NC}"
    echo "Please review the failed checks above."
    exit 1
fi
