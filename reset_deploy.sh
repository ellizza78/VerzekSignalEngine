#!/usr/bin/env bash
#
# Verzek AutoTrader - Quick Deployment Script
# Run on Vultr VPS: /root/reset_deploy.sh
#

set -e

echo "🚀 Verzek AutoTrader - Quick Deployment"
echo "========================================"

# Configuration
REPO_DIR="/root/VerzekBackend"
BACKEND_DIR="$REPO_DIR/backend"
ENV_FILE="$BACKEND_DIR/.env"
ENV_EXAMPLE="$BACKEND_DIR/.env.example"

# Step 1: Navigate to repository
cd "$REPO_DIR"
echo "📂 Working directory: $(pwd)"

# Step 2: Pull latest changes (safe, fast-forward only)
echo "📥 Pulling latest code from GitHub..."
git fetch origin
git merge --ff-only origin/main || {
    echo "❌ Cannot fast-forward merge. Manual intervention required."
    echo "Run: git status"
    exit 1
}
echo "✅ Code updated to latest version"

# Step 3: Install/Update Python dependencies
echo "🐍 Installing Python dependencies..."
cd "$BACKEND_DIR"
pip3 install --upgrade pip --quiet
pip3 install -r requirements.txt --quiet
echo "✅ Dependencies installed"

# Step 4: Create .env from .env.example if missing
if [ ! -f "$ENV_FILE" ]; then
    echo "⚙️  Creating .env from .env.example..."
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    echo "⚠️  WARNING: Please update $ENV_FILE with production values!"
else
    echo "✅ .env file exists"
fi

# Step 5: Create necessary directories
mkdir -p "$BACKEND_DIR/database"
mkdir -p /var/log
chmod 755 "$BACKEND_DIR/database"

# Step 6: Restart services
echo "♻️  Restarting services..."
systemctl daemon-reload
systemctl restart verzek-api.service
sleep 3

# Step 7: Check service status
echo "🔍 Checking service status..."
SERVICE_STATUS=$(systemctl is-active verzek-api.service || echo "inactive")

if [ "$SERVICE_STATUS" = "active" ]; then
    echo "✅ verzek-api.service is ACTIVE"
else
    echo "❌ Service is NOT active! Status: $SERVICE_STATUS"
    echo "📋 Last 20 log lines:"
    journalctl -u verzek-api.service -n 20 --no-pager
    exit 1
fi

# Step 8: Test API endpoint
echo "🧪 Testing API endpoint..."
sleep 2
RESPONSE=$(curl -s http://localhost:8050/api/ping || echo "FAILED")

if echo "$RESPONSE" | grep -q "ok"; then
    VERSION=$(echo "$RESPONSE" | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
    echo "✅ API responding - Version: $VERSION"
else
    echo "❌ API test failed!"
    echo "Response: $RESPONSE"
    exit 1
fi

# Step 9: Display deployment summary
echo ""
echo "✅ DEPLOYMENT SUCCESSFUL!"
echo "=========================="
echo "Service: verzek-api.service"
echo "Status: $SERVICE_STATUS"
echo "API: http://localhost:8050"
echo "Public: https://api.verzekinnovative.com"
echo "Time: $(date)"
echo ""
echo "🎉 Ready for production traffic!"
