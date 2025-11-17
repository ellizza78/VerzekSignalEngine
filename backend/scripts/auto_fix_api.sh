#!/bin/bash
#
# VerzekAutoTrader - Automatic API Diagnostic and Fix
# Diagnoses issues and applies fixes automatically
#

set -euo pipefail

echo "🔍 VerzekAutoTrader API Auto-Fix Starting..."
echo ""

cd /root/VerzekBackend/backend

# Check logs for specific errors
echo "📊 Analyzing error logs..."
LOGS=$(journalctl -u verzek_api -n 100 --no-pager 2>/dev/null || echo "")

# Check for common issues
if echo "$LOGS" | grep -q "ModuleNotFoundError"; then
    echo "⚠️  Missing Python modules detected"
    MODULE=$(echo "$LOGS" | grep "ModuleNotFoundError" | tail -1 | sed -n "s/.*No module named '\(.*\)'.*/\1/p")
    echo "Installing missing module: $MODULE"
    python3 -m pip install "$MODULE" -q
fi

if echo "$LOGS" | grep -q "ImportError"; then
    echo "⚠️  Import errors detected - reinstalling all dependencies"
    python3 -m pip install -r requirements.txt -q 2>/dev/null || echo "No requirements.txt, installing manually"
fi

if echo "$LOGS" | grep -q "could not connect to server"; then
    echo "⚠️  Database connection issue - checking PostgreSQL"
    if ! systemctl is-active --quiet postgresql; then
        echo "Starting PostgreSQL..."
        systemctl start postgresql
        sleep 3
    fi
fi

# Install critical dependencies
echo "📦 Ensuring all dependencies are installed..."
python3 -m pip install -q flask flask-cors flask-jwt-extended sqlalchemy psycopg2-binary gunicorn requests schedule python-telegram-bot cryptography pyjwt bcrypt openai python-dotenv

# Check if api_server.py can be imported
echo "🧪 Testing api_server.py import..."
if ! python3 -c "import api_server" 2>/dev/null; then
    echo "❌ api_server.py has import errors. Checking details..."
    python3 -c "import api_server" 2>&1 | tail -20
    echo ""
    echo "Attempting to fix common issues..."
    
    # Install any missing packages mentioned in error
    python3 -c "import api_server" 2>&1 | grep "No module named" | sed -n "s/.*No module named '\(.*\)'.*/\1/p" | while read module; do
        echo "Installing $module..."
        python3 -m pip install "$module" -q || true
    done
fi

# Restart API service
echo ""
echo "🔄 Restarting API service..."
systemctl stop verzek_api 2>/dev/null || true
killall -9 gunicorn 2>/dev/null || true
sleep 2
systemctl start verzek_api
sleep 5

# Check if it's running
if systemctl is-active --quiet verzek_api; then
    echo "✅ API service is running"
    
    # Test if port is actually listening
    if netstat -tlnp 2>/dev/null | grep -q ":8050"; then
        echo "✅ API is listening on port 8050"
        
        # Test the endpoint
        echo ""
        echo "🧪 Testing metadata endpoint..."
        RESPONSE=$(curl -s -X POST http://localhost:8050/api/house-signals/ingest \
          -H "Content-Type: application/json" \
          -H "X-INTERNAL-TOKEN: EXEE_TueWz6vSSUlWus3jStZKFM8JCP1mPuUjQ6SX5o" \
          -d '{"source":"TEST","symbol":"BTCUSDT","side":"LONG","entry":50000,"stop_loss":49500,"take_profits":[50500],"timeframe":"M5","confidence":85,"metadata":{"test":true}}' 2>/dev/null || echo "ERROR")
        
        if echo "$RESPONSE" | grep -q '"ok"'; then
            echo "✅ SUCCESS! API is working correctly!"
            echo "$RESPONSE" | python3 -m json.tool
        else
            echo "⚠️  API responded but with unexpected output:"
            echo "$RESPONSE"
        fi
    else
        echo "⚠️  Service running but not listening on port 8050"
        echo "Checking logs for startup errors..."
        journalctl -u verzek_api -n 30 --no-pager
    fi
else
    echo "❌ API service failed to start"
    echo ""
    echo "Last 50 log lines:"
    journalctl -u verzek_api -n 50 --no-pager
fi

echo ""
echo "=== Auto-fix complete ==="
