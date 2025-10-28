#!/bin/bash

echo "================================================"
echo "🚀 VERZEK AUTO TRADER - SYSTEM STATUS"
echo "================================================"
echo ""

echo "📊 SERVICE STATUS:"
echo "----------------------------------------"
for svc in verzekbot verzekapi verzekwatchdog; do
    if systemctl is-active --quiet "$svc"; then
        echo "✅ $svc: RUNNING"
    else
        echo "❌ $svc: STOPPED"
    fi
done

echo ""
echo "🌐 NETWORK STATUS:"
echo "----------------------------------------"
if ss -tuln | grep -q ":5000"; then
    echo "✅ Port 5000: LISTENING"
else
    echo "❌ Port 5000: NOT LISTENING"
fi

echo ""
echo "🔗 BACKEND CONNECTIVITY:"
echo "----------------------------------------"
response=$(curl -s -w "\n%{http_code}" http://localhost:5000/ping 2>/dev/null)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo "✅ Backend API: RESPONDING"
    echo "   Response: $body"
else
    echo "❌ Backend API: NOT RESPONDING (HTTP $http_code)"
fi

echo ""
echo "🌉 REPLIT BRIDGE STATUS:"
echo "----------------------------------------"
bridge_response=$(curl -s -w "\n%{http_code}" -m 5 https://verzek-auto-trader.replit.app/ping 2>/dev/null)
bridge_code=$(echo "$bridge_response" | tail -n1)
bridge_body=$(echo "$bridge_response" | head -n-1)

if [ "$bridge_code" = "200" ]; then
    echo "✅ Replit Bridge: CONNECTED"
    echo "   Response time: $(curl -s -w "%{time_total}s" -o /dev/null https://verzek-auto-trader.replit.app/ping 2>/dev/null)"
else
    echo "⚠️ Replit Bridge: TIMEOUT OR ERROR (HTTP $bridge_code)"
fi

echo ""
echo "📝 RECENT WATCHDOG LOGS:"
echo "----------------------------------------"
if [ -f /var/log/verzek_watchdog.log ]; then
    tail -n 5 /var/log/verzek_watchdog.log
else
    echo "No watchdog logs found"
fi

echo ""
echo "================================================"
