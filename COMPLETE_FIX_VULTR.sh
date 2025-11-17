#!/bin/bash
# Complete VerzekAutoTrader Deployment Fix
# Run this on Vultr server: bash COMPLETE_FIX_VULTR.sh

echo "🔧 VerzekAutoTrader Complete Deployment Fix"
echo ""

cd /root/VerzekBackend/backend

echo "🛑 Step 1: Stop all services..."
systemctl stop verzek_api
pkill -9 -f gunicorn 2>/dev/null || true
pkill -9 -f api_server.py 2>/dev/null || true
sleep 2

echo ""
echo "🔍 Step 2: Check port 8050..."
PORT_CHECK=$(lsof -i :8050 2>/dev/null)
if [ -n "$PORT_CHECK" ]; then
    echo "⚠️  Port 8050 is in use:"
    echo "$PORT_CHECK"
    echo "Killing process..."
    fuser -k 8050/tcp 2>/dev/null || true
    sleep 2
else
    echo "✅ Port 8050 is free"
fi

echo ""
echo "🧹 Step 3: Clear Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo ""
echo "🧪 Step 4: Test Flask app import..."
python3 -c "from api_server import app; print('✅ Flask app imports successfully')" 2>&1

echo ""
echo "🧪 Step 5: Test Gunicorn with verbose logging..."
timeout 8 gunicorn --bind 0.0.0.0:8050 \
  --workers 1 \
  --timeout 120 \
  --log-level debug \
  --error-logfile - \
  --access-logfile - \
  api_server:app 2>&1 | head -100 &

GUNICORN_PID=$!
sleep 5

echo ""
echo "🧪 Step 6: Test endpoint while Gunicorn is running..."
curl -s -X POST http://localhost:8050/api/house-signals/ingest \
  -H "Content-Type: application/json" \
  -H "X-INTERNAL-TOKEN: EXEE_TueWz6vSSUlWus3jStZKFM8JCP1mPuUjQ6SX5o" \
  -d '{"source":"TEST","symbol":"BTCUSDT","side":"LONG","entry":50000,"stop_loss":49500,"take_profits":[50500],"timeframe":"M5","confidence":85,"metadata":{"test":true}}' \
  | python3 -m json.tool

kill $GUNICORN_PID 2>/dev/null || true
sleep 2

echo ""
echo "🔄 Step 7: Start systemd service..."
systemctl start verzek_api
sleep 8

echo ""
echo "🧪 Step 8: Final endpoint test..."
curl -s -X POST http://localhost:8050/api/house-signals/ingest \
  -H "Content-Type: application/json" \
  -H "X-INTERNAL-TOKEN: EXEE_TueWz6vSSUlWus3jStZKFM8JCP1mPuUjQ6SX5o" \
  -d '{"source":"FINAL","symbol":"ETHUSDT","side":"LONG","entry":3000,"stop_loss":2950,"take_profits":[3050,3100],"timeframe":"M5","confidence":92,"metadata":{"final_test":true}}' \
  | python3 -m json.tool

echo ""
echo "📊 Step 9: Check service status..."
systemctl status verzek_api --no-pager -l | head -30

echo ""
echo "🎉 Fix script completed!"
