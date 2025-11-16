#!/bin/bash
# Run this script ON VULTR SERVER to fix signal engine imports

set -e

echo "🔧 Fixing VerzekSignalEngine Python imports..."

cd /root/signal_engine

# Create all missing __init__.py files
echo "Creating __init__.py files..."
touch bots/scalper/__init__.py
touch bots/trend/__init__.py
touch bots/qfl/__init__.py
touch bots/ai_ml/__init__.py

echo "✓ Package structure fixed"

# Update systemd service file
echo "Updating systemd service..."
cat > /etc/systemd/system/verzek-signalengine.service << 'EOF'
[Unit]
Description=VerzekSignalEngine - Multi-Bot Trading Signal System
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/signal_engine
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=/root/signal_engine"
ExecStart=/usr/bin/python3 -m main
Restart=always
RestartSec=10
StandardOutput=append:/root/signal_engine/logs/systemd.log
StandardError=append:/root/signal_engine/logs/systemd_error.log

# Resource limits
LimitNOFILE=65536

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Systemd service updated"

# Reload and restart
echo "Reloading systemd..."
systemctl daemon-reload

echo "Starting signal engine..."
systemctl restart verzek-signalengine
sleep 3

# Check status
if systemctl is-active --quiet verzek-signalengine; then
    echo "✅ Signal engine started successfully!"
    echo ""
    echo "📊 Status:"
    systemctl status verzek-signalengine --no-pager -l
    echo ""
    echo "📝 View logs:"
    echo "  journalctl -u verzek-signalengine -f"
else
    echo "❌ Signal engine failed to start"
    echo "Showing last 30 lines of logs:"
    journalctl -u verzek-signalengine -n 30 --no-pager
    exit 1
fi
