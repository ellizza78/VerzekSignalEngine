#!/bin/bash
# AUTOMATED VULTR VERIFICATION & FIX
# This runs automatically once SSH is configured

VULTR_IP="80.240.29.142"
VULTR_USER="root"

echo "=========================================="
echo "AUTOMATED VULTR VERIFICATION & FIX"
echo "=========================================="

# 1. Check VerzekSignalEngine status
echo "1️⃣ Checking VerzekSignalEngine service..."
ssh $VULTR_USER@$VULTR_IP << 'ENDSSH'
if systemctl is-active --quiet verzek-signalengine; then
    echo "✅ VerzekSignalEngine is RUNNING"
    systemctl status verzek-signalengine --no-pager | head -10
else
    echo "❌ VerzekSignalEngine is NOT running - Starting now..."
    sudo systemctl start verzek-signalengine
    sudo systemctl enable verzek-signalengine
    sleep 3
    if systemctl is-active --quiet verzek-signalengine; then
        echo "✅ VerzekSignalEngine STARTED successfully"
    else
        echo "❌ FAILED to start VerzekSignalEngine"
        journalctl -u verzek-signalengine -n 20 --no-pager
    fi
fi
ENDSSH

# 2. Check Backend API (Gunicorn workers)
echo ""
echo "2️⃣ Checking Backend API service..."
ssh $VULTR_USER@$VULTR_IP << 'ENDSSH'
if systemctl is-active --quiet verzek_api; then
    echo "✅ Backend API is RUNNING"
    WORKER_COUNT=$(ps aux | grep "gunicorn.*api_server:app" | grep -v grep | wc -l)
    echo "   Workers: $WORKER_COUNT (should be 4)"
    
    if [ "$WORKER_COUNT" -lt 4 ]; then
        echo "⚠️  Restarting backend to ensure 4 workers..."
        sudo systemctl restart verzek_api
        sleep 2
    fi
else
    echo "❌ Backend API is NOT running - Starting now..."
    sudo systemctl start verzek_api
    sudo systemctl enable verzek_api
fi
ENDSSH

# 3. Check Database signals
echo ""
echo "3️⃣ Checking database for signals..."
ssh $VULTR_USER@$VULTR_IP << 'ENDSSH'
source /root/.verzek_secrets
SIGNAL_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM house_signals;" 2>/dev/null | tr -d ' ')
echo "📊 Total signals in database: $SIGNAL_COUNT"

if [ "$SIGNAL_COUNT" -gt 0 ]; then
    echo ""
    echo "Recent signals:"
    psql "$DATABASE_URL" -c "SELECT id, source, symbol, side, confidence, created_at FROM house_signals ORDER BY created_at DESC LIMIT 5;"
fi
ENDSSH

# 4. Monitor SignalEngine logs (30 seconds)
echo ""
echo "4️⃣ Monitoring VerzekSignalEngine for 30 seconds..."
ssh $VULTR_USER@$VULTR_IP "timeout 30 tail -f /root/signal_engine/logs/signalengine.log 2>/dev/null || echo 'No logs yet'" &
TAIL_PID=$!

sleep 30
kill $TAIL_PID 2>/dev/null

# 5. Final status check
echo ""
echo "=========================================="
echo "5️⃣ FINAL STATUS"
echo "=========================================="
ssh $VULTR_USER@$VULTR_IP << 'ENDSSH'
echo "Backend API:         $(systemctl is-active verzek_api)"
echo "VerzekSignalEngine:  $(systemctl is-active verzek-signalengine)"
echo "PostgreSQL:          $(systemctl is-active postgresql)"
echo "Auto-Deploy Timer:   $(systemctl is-active verzek-deploy.timer)"
echo ""
source /root/.verzek_secrets
SIGNAL_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM house_signals;" 2>/dev/null | tr -d ' ')
echo "📊 Total Signals: $SIGNAL_COUNT"
echo "🔧 Trading Mode: ${MODE:-paper}"
ENDSSH

echo ""
echo "=========================================="
echo "✅ AUTOMATED CHECK COMPLETE"
echo "=========================================="
