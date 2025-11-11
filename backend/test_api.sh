#!/bin/bash
#
# Test script for VerzekBackend API endpoints
# Tests /api/ping and /api/health endpoints
#

set -e

API_URL="${1:-http://127.0.0.1:8050}"

echo "🧪 Testing VerzekBackend API Endpoints"
echo "======================================="
echo "API URL: $API_URL"
echo ""

# Test /api/ping
echo "📡 Testing /api/ping..."
PING_RESPONSE=$(curl -s "$API_URL/api/ping")
echo "Response: $PING_RESPONSE"

# Parse JSON and check fields
PING_STATUS=$(echo $PING_RESPONSE | grep -o '"status":"ok"' || true)
PING_SERVICE=$(echo $PING_RESPONSE | grep -o '"service":"VerzekBackend"' || true)
PING_VERSION=$(echo $PING_RESPONSE | grep -o '"version":"2.1"' || true)

if [ -n "$PING_STATUS" ] && [ -n "$PING_SERVICE" ] && [ -n "$PING_VERSION" ]; then
    echo "✅ /api/ping - PASSED"
else
    echo "❌ /api/ping - FAILED"
    echo "   Expected: {\"status\":\"ok\",\"service\":\"VerzekBackend\",\"version\":\"2.1\",...}"
    exit 1
fi

echo ""

# Test /api/health
echo "🏥 Testing /api/health..."
HEALTH_RESPONSE=$(curl -s "$API_URL/api/health")
echo "Response: $HEALTH_RESPONSE"

# Parse JSON and check fields
HEALTH_OK=$(echo $HEALTH_RESPONSE | grep -o '"ok":true' || true)
HEALTH_STATUS=$(echo $HEALTH_RESPONSE | grep -o '"status":"healthy"' || true)
HEALTH_TIMESTAMP=$(echo $HEALTH_RESPONSE | grep -o '"timestamp":"[^"]*"' || true)

if [ -n "$HEALTH_OK" ] && [ -n "$HEALTH_STATUS" ] && [ -n "$HEALTH_TIMESTAMP" ]; then
    echo "✅ /api/health - PASSED"
else
    echo "❌ /api/health - FAILED"
    echo "   Expected: {\"ok\":true,\"status\":\"healthy\",\"timestamp\":\"...\"}"
    exit 1
fi

echo ""
echo "======================================="
echo "✅ All tests passed!"
echo "🚀 Backend is responding correctly"
echo "======================================="
