#!/bin/bash
# Verify if the Vultr server has been fixed already

echo "🔍 VerzekAutoTrader - Server Status Verification"
echo "================================================"
echo ""

API_URL="https://api.verzekinnovative.com"

echo "1️⃣ Testing API availability..."
if curl -s --connect-timeout 5 "$API_URL/api/ping" | grep -q '"status":"ok"'; then
    echo "✅ API is reachable"
else
    echo "❌ API not responding"
    exit 1
fi

echo ""
echo "2️⃣ Testing house-signals endpoint..."

# Get token from environment
if [ -z "$HOUSE_ENGINE_TOKEN" ]; then
    echo "❌ HOUSE_ENGINE_TOKEN not set in environment"
    exit 1
fi

RESPONSE=$(curl -s -X POST "$API_URL/api/house-signals/ingest" \
  -H "Content-Type: application/json" \
  -H "X-INTERNAL-TOKEN: $HOUSE_ENGINE_TOKEN" \
  -d '{
    "source": "TEST",
    "symbol": "BTCUSDT",
    "side": "LONG",
    "entry": 50000.0,
    "stop_loss": 49500.0,
    "take_profits": [50500.0],
    "timeframe": "M5",
    "confidence": 85
  }')

echo "Response: $RESPONSE"

if echo "$RESPONSE" | grep -q '"ok": *true'; then
    echo ""
    echo "✅ SUCCESS! House signals endpoint is working!"
    echo "✅ Metadata column bug has been fixed"
    echo "✅ Server is ready to receive signals"
    echo ""
    exit 0
else
    echo ""
    echo "❌ Endpoint not working yet"
    echo "ℹ️  The metadata column bug needs to be fixed on the server"
    echo ""
    echo "Run this command on your Vultr server:"
    echo "    bash /root/fix_metadata.sh"
    echo ""
    exit 1
fi
