#!/bin/bash
# FastAPI Mesh Service Deployment Script
# Deploy the proxy service on Vultr nodes

set -e

echo "=========================================="
echo "Verzek - FastAPI Mesh Service Deployment"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo "Please run as root (sudo)"
   exit 1
fi

# Variables
PROXY_SECRET="${1:-}"
if [ -z "$PROXY_SECRET" ]; then
    echo "ERROR: PROXY_SECRET_KEY is required"
    echo "Usage: ./deploy_fastapi.sh YOUR_SECRET_KEY"
    exit 1
fi

echo "Installing Python dependencies..."
apt update -y
apt install -y python3 python3-pip python3-venv

# Create application directory
echo "Creating application directory..."
mkdir -p /opt/verzek-proxy
cd /opt/verzek-proxy

# Create virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing FastAPI and dependencies..."
pip install --upgrade pip
pip install fastapi uvicorn httpx python-multipart

# Copy mesh_proxy.py (assumes it's in the same directory)
if [ -f "../mesh_proxy.py" ]; then
    cp ../mesh_proxy.py /opt/verzek-proxy/
else
    echo "ERROR: mesh_proxy.py not found"
    echo "Please copy mesh_proxy.py to this directory first"
    exit 1
fi

# Create systemd service
echo "Creating systemd service..."
cat > /etc/systemd/system/verzek-proxy.service <<EOF
[Unit]
Description=Verzek Proxy Mesh - FastAPI Service
After=network.target wg-quick@wg0.service
Wants=wg-quick@wg0.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/verzek-proxy
Environment="PROXY_SECRET_KEY=$PROXY_SECRET"
ExecStart=/opt/verzek-proxy/venv/bin/uvicorn mesh_proxy:app --host 0.0.0.0 --port 5000 --workers 2
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security settings
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
echo "Reloading systemd..."
systemctl daemon-reload

# Enable and start service
echo "Enabling and starting Verzek Proxy service..."
systemctl enable verzek-proxy
systemctl restart verzek-proxy

# Wait for service to start
sleep 3

# Check status
echo ""
echo "Checking service status..."
systemctl status verzek-proxy --no-pager || true

echo ""
echo "=========================================="
echo "FastAPI Mesh Service deployed!"
echo "=========================================="
echo "Service: verzek-proxy"
echo "Port: 5000"
echo "Workers: 2"
echo ""
echo "Commands:"
echo "  Status: systemctl status verzek-proxy"
echo "  Logs: journalctl -u verzek-proxy -f"
echo "  Restart: systemctl restart verzek-proxy"
echo "  Stop: systemctl stop verzek-proxy"
echo ""
echo "Test endpoint:"
echo "  curl http://localhost:5000/health"
echo "=========================================="
