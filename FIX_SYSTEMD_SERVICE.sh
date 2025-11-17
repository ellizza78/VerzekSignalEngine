#!/bin/bash
# Fix verzek_api.service to use Gunicorn properly
# Run on Vultr: bash FIX_SYSTEMD_SERVICE.sh

echo "🔧 Fixing verzek_api systemd service configuration"
echo ""

# Create the correct systemd service file
cat > /etc/systemd/system/verzek_api.service << 'SERVICEEOF'
[Unit]
Description=Verzek AutoTrader API Server
After=network.target postgresql.service

[Service]
Type=notify
User=root
WorkingDirectory=/root/VerzekBackend/backend
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONUNBUFFERED=1"

# Gunicorn with 4 workers for production scale
ExecStart=/usr/local/bin/gunicorn \
    --bind 0.0.0.0:8050 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    api_server:app

# Auto-restart on failure
Restart=always
RestartSec=5

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
SERVICEEOF

echo "✅ Service file updated"
echo ""

echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload

echo ""
echo "🛑 Stopping old service..."
systemctl stop verzek_api

echo ""
echo "🧹 Killing any stray processes..."
pkill -9 -f gunicorn 2>/dev/null || true
sleep 2

echo ""
echo "🚀 Starting service with new configuration..."
systemctl start verzek_api

echo ""
echo "⏳ Waiting for service to start..."
sleep 8

echo ""
echo "📊 Service status:"
systemctl status verzek_api --no-pager -l | head -25

echo ""
echo "🧪 Testing endpoint..."
curl -s -X POST http://localhost:8050/api/house-signals/ingest \
  -H "Content-Type: application/json" \
  -H "X-INTERNAL-TOKEN: EXEE_TueWz6vSSUlWus3jStZKFM8JCP1mPuUjQ6SX5o" \
  -d '{
    "source": "SYSTEMD_TEST",
    "symbol": "BTCUSDT",
    "side": "LONG",
    "entry": 50000,
    "stop_loss": 49500,
    "take_profits": [50500, 51000],
    "timeframe": "M5",
    "confidence": 95,
    "metadata": {
      "systemd_fixed": true,
      "gunicorn_workers": 4
    }
  }' | python3 -m json.tool

echo ""
echo "🎉 Fix completed! Service should now be running with Gunicorn + 4 workers"
echo ""
echo "To check logs: journalctl -u verzek_api -f"
