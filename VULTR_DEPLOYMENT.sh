#!/bin/bash
# VerzekAutoTrader Backend Deployment Script
# Run this on your Vultr VPS (80.240.29.142)

echo "═══════════════════════════════════════════════════════════════"
echo "🚀 VerzekAutoTrader Backend Deployment"
echo "═══════════════════════════════════════════════════════════════"

# Step 1: Install flask-cors
echo ""
echo "📦 Step 1: Installing flask-cors..."
pip3 install flask-cors

# Step 2: Stop existing backend
echo ""
echo "🛑 Step 2: Stopping existing backend..."
pkill -9 -f api_server.py || true
sleep 3

# Step 3: Backup current api_server.py
echo ""
echo "💾 Step 3: Backing up current api_server.py..."
cp /root/api_server.py /root/api_server.py.backup.$(date +%s)

# Step 4: Add CORS import (if not already present)
echo ""
echo "🔧 Step 4: Checking CORS configuration..."
if ! grep -q "from flask_cors import CORS" /root/api_server.py; then
    echo "Adding CORS import..."
    sed -i '11 a from flask_cors import CORS' /root/api_server.py
fi

# Step 5: Add CORS configuration after app initialization
echo ""
echo "🔧 Step 5: Adding CORS configuration..."
# Check if CORS is already configured
if ! grep -q "CORS(app" /root/api_server.py; then
    # Find line with "app = Flask(__name__)" and add CORS config after it
    sed -i '/^app = Flask(__name__)$/a \\\n# Enable CORS for mobile app\nCORS(app, resources={\n    r"/api/*": {\n        "origins": "*",\n        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],\n        "allow_headers": ["Content-Type", "Authorization"],\n        "expose_headers": ["Content-Type", "Authorization"],\n        "supports_credentials": True\n    }\n})' /root/api_server.py
    echo "✅ CORS configuration added"
else
    echo "✅ CORS already configured"
fi

# Step 6: Verify environment variables
echo ""
echo "🔍 Step 6: Verifying environment variables..."
source /root/api_server_env.sh
echo "  ✅ RESEND_API_KEY: ${RESEND_API_KEY:0:10}..."
echo "  ✅ EMAIL_FROM: $EMAIL_FROM"
echo "  ✅ BASE_URL: $BASE_URL"
echo "  ✅ PORT: ${PORT:-8000}"

# Step 7: Start backend
echo ""
echo "🚀 Step 7: Starting backend..."
cd /root
nohup python3 /root/api_server.py > /tmp/api_server.log 2>&1 &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait for startup
echo ""
echo "⏳ Waiting 15 seconds for initialization..."
sleep 15

# Step 8: Test health endpoint
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🧪 Step 8: Testing Endpoints"
echo "═══════════════════════════════════════════════════════════════"

echo ""
echo "Testing local health endpoint..."
curl -s http://127.0.0.1:8000/api/health | python3 -m json.tool

echo ""
echo "Testing HTTPS health endpoint..."
curl -s https://verzekinnovative.com/api/health | python3 -m json.tool

echo ""
echo "Testing registration endpoint (OPTIONS - CORS preflight)..."
curl -X OPTIONS https://verzekinnovative.com/api/auth/register -H "Origin: http://localhost" -v 2>&1 | grep -E "(Access-Control|HTTP/)"

# Step 9: Check logs
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "📋 Step 9: Checking Backend Logs"
echo "═══════════════════════════════════════════════════════════════"
tail -30 /tmp/api_server.log | grep -E "(Resend|Email|CORS|error|Error|Exception)"

# Step 10: Final status
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "✅ FINAL STATUS"
echo "═══════════════════════════════════════════════════════════════"

# Check if backend is running
if ps aux | grep -v grep | grep -q "api_server.py"; then
    echo "✅ Backend process running (PID: $(pgrep -f api_server.py))"
else
    echo "❌ Backend process NOT running"
fi

# Check port
if netstat -tulnp 2>/dev/null | grep -q ":8000.*python" || ss -tulnp 2>/dev/null | grep -q ":8000.*python"; then
    echo "✅ Backend listening on port 8000"
else
    echo "❌ Backend NOT listening on port 8000"
fi

# Check health endpoint
if curl -s http://127.0.0.1:8000/api/health | grep -q '"status":"ok"'; then
    echo "✅ Health endpoint working"
else
    echo "❌ Health endpoint failed"
fi

# Check HTTPS
if curl -s https://verzekinnovative.com/api/health | grep -q '"status":"ok"'; then
    echo "✅ HTTPS endpoint working"
else
    echo "❌ HTTPS endpoint failed"
fi

# Check Resend
if grep -q "Resend API initialized" /tmp/api_server.log; then
    echo "✅ Resend API initialized"
else
    echo "⚠️  Resend API status unknown"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🎉 Deployment Complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Test registration from your mobile app"
echo "2. Check email delivery for verification"
echo "3. Test login flow"
echo ""
echo "If registration fails, check:"
echo "  tail -f /tmp/api_server.log"
echo ""
