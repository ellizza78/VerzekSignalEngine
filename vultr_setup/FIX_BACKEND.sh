#!/bin/bash
# Quick Fix Script for Backend Connection Issue
# This updates api_server.py to fix the duplicate startup code bug

echo "════════════════════════════════════════════════════════════"
echo "  FIXING BACKEND CONNECTION ISSUE"
echo "════════════════════════════════════════════════════════════"
echo ""

API_FILE="/var/www/VerzekAutoTrader/api_server.py"

if [ ! -f "$API_FILE" ]; then
    echo "❌ ERROR: $API_FILE not found!"
    echo "Make sure VerzekAutoTrader is installed in /var/www/"
    exit 1
fi

echo "📝 Backing up current api_server.py..."
cp "$API_FILE" "${API_FILE}.backup_$(date +%Y%m%d_%H%M%S)"
echo "✅ Backup created"

echo ""
echo "🔧 Fixing duplicate startup code..."

# Remove the last 10 lines (which contain the duplicate startup code)
head -n -10 "$API_FILE" > "${API_FILE}.tmp"

# Add the corrected startup code
cat >> "${API_FILE}.tmp" << 'PYTHON_CODE'


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    log_event("API", f"Starting Flask API on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)
PYTHON_CODE

# Replace the original file
mv "${API_FILE}.tmp" "$API_FILE"

echo "✅ Fixed duplicate startup code in api_server.py"
echo ""

echo "🔄 Restarting verzekapi service..."
sudo systemctl restart verzekapi
sleep 2

echo ""
echo "🧪 Testing backend connection..."
sleep 3

# Test local connection
echo -n "Testing http://localhost:5000/ping... "
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/ping 2>&1)

if [ "$response" = "200" ]; then
    echo "✅ SUCCESS (HTTP $response)"
    echo ""
    echo "Response:"
    curl -s http://localhost:5000/ping | python3 -m json.tool
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "  🎉 BACKEND CONNECTION FIXED!"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "Next steps:"
    echo "1. Test external: curl http://80.240.29.142:5000/ping"
    echo "2. Test bridge: curl https://verzek-auto-trader.replit.app/ping"
    echo ""
else
    echo "❌ FAILED (HTTP $response)"
    echo ""
    echo "Checking service status..."
    sudo systemctl status verzekapi --no-pager -l
    echo ""
    echo "Check logs with: journalctl -u verzekapi -n 50"
fi
