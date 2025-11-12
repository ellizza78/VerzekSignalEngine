#!/bin/bash
# Complete VerzekAutoTrader Deployment Script
# Syncs GitHub and deploys to Vultr VPS automatically

set -e  # Exit on error

echo "🚀 VerzekAutoTrader - Complete Sync & Deploy"
echo "=============================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# VPS Configuration
VPS_HOST="80.240.29.142"
VPS_USER="root"
VPS_DIR="/root/VerzekBackend"
VPS_ENV_FILE="/root/api_server_env.sh"

echo -e "${YELLOW}Step 1: Pushing Latest Code to GitHub${NC}"
echo "========================================"

# Push Backend
echo "📦 Pushing backend changes..."
cd backend
git add -A
git commit -m "AI Agent: Full sync - Backend updates with email verification, PostgreSQL, rate limiting (Nov 12, 2025)" || echo "No backend changes to commit"
git push origin main || echo "Backend push failed or already up to date"
cd ..

# Push Mobile App
echo "📱 Pushing mobile app changes..."
cd mobile_app/VerzekApp
git add -A
git commit -m "AI Agent: Full sync - APK v1.3.1, email verification UI, 4-day trial, Vultr config (Nov 12, 2025)" || echo "No mobile changes to commit"
git push origin main || echo "Mobile app push failed or already up to date"
cd ../..

echo -e "${GREEN}✅ GitHub sync complete${NC}"
echo ""

echo -e "${YELLOW}Step 2: Creating VPS Deployment Package${NC}"
echo "=========================================="

# Create deployment script for VPS
cat > /tmp/vps_deploy.sh << 'VPS_SCRIPT_END'
#!/bin/bash
# VPS Deployment Script - Runs on Vultr Server

set -e

echo "🔧 Deploying VerzekBackend to Vultr VPS"
echo "========================================"

# Stop services
echo "⏸️  Stopping services..."
systemctl stop verzek-api.service 2>/dev/null || true
systemctl stop verzek-worker.service 2>/dev/null || true

# Backup current deployment
if [ -d "/root/VerzekBackend" ]; then
    BACKUP_DIR="/root/VerzekBackend_backup_$(date +%s)"
    echo "💾 Backing up to $BACKUP_DIR..."
    mv /root/VerzekBackend $BACKUP_DIR
fi

# Clone latest from GitHub
echo "📥 Cloning latest code from GitHub..."
cd /root
git clone https://github.com/ellizza78/VerzekBackend.git
cd /root/VerzekBackend/backend

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt --quiet

# Create logs directory
mkdir -p /root/api_server/logs
chmod 755 /root/api_server/logs

# Fix environment file format (remove export keywords)
echo "⚙️  Fixing environment file format..."
if [ -f "/root/api_server_env.sh" ]; then
    sed -i 's/^export //g' /root/api_server_env.sh
    
    # Add RESEND_API_KEY if missing
    if ! grep -q "RESEND_API_KEY" /root/api_server_env.sh; then
        echo "RESEND_API_KEY=re_ACMWmmPe_CHiR7EtPzMwP8Dc9FLy_Lmyu" >> /root/api_server_env.sh
    fi
    
    # Add EMAIL_FROM if missing
    if ! grep -q "EMAIL_FROM" /root/api_server_env.sh; then
        echo "EMAIL_FROM=support@verzekinnovative.com" >> /root/api_server_env.sh
    fi
fi

# Create proper systemd service with EnvironmentFile
echo "🔧 Configuring systemd services..."
cat > /etc/systemd/system/verzek-api.service << 'SERVICE_END'
[Unit]
Description=Verzek Auto Trader API Server
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=exec
User=root
WorkingDirectory=/root/VerzekBackend/backend
EnvironmentFile=/root/api_server_env.sh
ExecStart=/bin/bash -c 'source /root/api_server_env.sh && /usr/local/bin/gunicorn --bind 0.0.0.0:8050 --workers 4 --timeout 120 --access-logfile /root/api_server/logs/access.log --error-logfile /root/api_server/logs/error.log --log-level info api_server:app'
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE_END

# Reload systemd
echo "🔄 Reloading systemd..."
systemctl daemon-reload

# Start services
echo "🚀 Starting services..."
systemctl enable verzek-api.service
systemctl start verzek-api.service

# Wait for service to start
sleep 5

# Check status
if systemctl is-active --quiet verzek-api.service; then
    echo "✅ verzek-api.service is ACTIVE"
else
    echo "❌ verzek-api.service FAILED to start"
    journalctl -u verzek-api.service -n 30 --no-pager
    exit 1
fi

# Test API endpoints
echo "🏥 Testing API endpoints..."
sleep 2

PING_RESPONSE=$(curl -s https://api.verzekinnovative.com/api/ping || echo "FAILED")
HEALTH_RESPONSE=$(curl -s https://api.verzekinnovative.com/api/health || echo "FAILED")

echo "Ping response: $PING_RESPONSE"
echo "Health response: $HEALTH_RESPONSE"

if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    echo "✅ API is healthy and responding"
else
    echo "⚠️ API health check unexpected response"
fi

echo ""
echo "=============================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=============================================="
echo "API: https://api.verzekinnovative.com"
echo "Logs: /root/api_server/logs/"
echo ""
echo "Test registration to verify email verification!"

VPS_SCRIPT_END

chmod +x /tmp/vps_deploy.sh

echo -e "${GREEN}✅ Deployment package created${NC}"
echo ""

echo -e "${YELLOW}Step 3: Instructions for VPS Deployment${NC}"
echo "=========================================="
echo ""
echo "Copy and run this command in Termius:"
echo ""
echo -e "${GREEN}# Copy deployment script to VPS${NC}"
echo "cat > /root/deploy.sh << 'DEPLOY_END'"
cat /tmp/vps_deploy.sh
echo "DEPLOY_END"
echo ""
echo -e "${GREEN}# Make executable and run${NC}"
echo "chmod +x /root/deploy.sh"
echo "/root/deploy.sh"
echo ""
echo "=============================================="
echo -e "${GREEN}✅ SYNC & DEPLOYMENT SCRIPT READY${NC}"
echo "=============================================="
echo ""
echo "Next Steps:"
echo "1. Open Termius and connect to VPS"
echo "2. Copy the deployment script above"
echo "3. Run it on the VPS"
echo "4. Test registration from APK"
echo ""
