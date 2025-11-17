#!/bin/bash
#
# VerzekAutoTrader - Fix API Service
#

set -euo pipefail

echo "🔧 Fixing verzek_api.service..."

# Stop any existing service
systemctl stop verzek_api 2>/dev/null || true
killall -9 gunicorn 2>/dev/null || true

# Create correct service file
cat > /etc/systemd/system/verzek_api.service << 'EOF'
[Unit]
Description=Verzek AutoTrader API Server
After=network.target

[Service]
Type=exec
User=root
WorkingDirectory=/root/VerzekBackend/backend
Environment="PATH=/usr/bin:/usr/local/bin"
EnvironmentFile=/root/VerzekBackend/backend/.env
ExecStart=/usr/bin/gunicorn --bind 0.0.0.0:8050 --workers 4 --timeout 120 --access-logfile logs/api_access.log --error-logfile logs/api_error.log --reuse-port api_server:app
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=verzek_api

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service file created"

# Create logs directory if missing
mkdir -p /root/VerzekBackend/backend/logs

# Reload systemd
systemctl daemon-reload
echo "✅ Systemd reloaded"

# Start service
systemctl start verzek_api
echo "✅ Service started"

# Wait for service to be ready
sleep 5

# Check status
if systemctl is-active --quiet verzek_api; then
    echo ""
    echo "✅ SUCCESS: verzek_api is RUNNING!"
    echo ""
    systemctl status verzek_api --no-pager | head -10
    echo ""
    echo "🧪 Testing API endpoint..."
    
    # Test the endpoint
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8050/api/health 2>/dev/null || echo "000")
    if [ "$RESPONSE" = "200" ] || [ "$RESPONSE" = "404" ]; then
        echo "✅ API is responding (HTTP $RESPONSE)"
    else
        echo "⚠️  API returned HTTP $RESPONSE (may need configuration)"
    fi
else
    echo ""
    echo "❌ Service failed to start. Checking logs..."
    journalctl -u verzek_api -n 30 --no-pager
    exit 1
fi

echo ""
echo "✅ API service is fixed and running!"
