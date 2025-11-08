#!/usr/bin/env bash
#
# Verzek AutoTrader Backend Deployment Script
# Run this on Vultr VPS (80.240.29.142)
#

set -e

echo "🚀 Verzek AutoTrader - Backend Deployment"
echo "========================================="

# Configuration
API_DIR="/root/api_server"
REPO_URL="https://github.com/ellizza78/VerzekBackend.git"

# Step 1: Update system
echo "📦 Step 1: Updating system packages..."
apt-get update -qq
apt-get install -y python3-pip python3-venv git nginx certbot python3-certbot-nginx jq

# Step 2: Clone or update repository
if [ -d "$API_DIR" ]; then
    echo "📥 Step 2: Updating existing repository..."
    cd $API_DIR
    git pull --rebase origin main
else
    echo "📥 Step 2: Cloning repository..."
    git clone $REPO_URL $API_DIR
    cd $API_DIR
fi

# Step 3: Install Python dependencies
echo "🐍 Step 3: Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Step 4: Create database directory
echo "💾 Step 4: Creating database directory..."
mkdir -p $API_DIR/database

# Step 5: Configure environment variables
echo "⚙️  Step 5: Configuring environment..."
if [ ! -f "/etc/environment.backup" ]; then
    cp /etc/environment /etc/environment.backup
fi

# Check if required secrets file exists
if [ ! -f "/root/api_server_env.sh" ]; then
    echo "❌ ERROR: /root/api_server_env.sh not found!"
    echo ""
    echo "Please create /root/api_server_env.sh with the following content:"
    echo ""
    cat << 'EXAMPLE_EOF'
#!/bin/bash
# Verzek AutoTrader Configuration
export JWT_SECRET="VerzekAutoTraderKey2025"
export API_KEY="Verzek2025AutoTrader"
export DATABASE_URL="sqlite:////root/api_server/database/verzek.db"
export EXCHANGE_MODE="paper"
export ENCRYPTION_KEY="<GENERATE_WITH: python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'>"
export TELEGRAM_BOT_TOKEN="<YOUR_BOT_TOKEN>"
export TELEGRAM_VIP_CHAT_ID="<YOUR_VIP_CHAT_ID>"
export TELEGRAM_TRIAL_CHAT_ID="<YOUR_TRIAL_CHAT_ID>"
export WORKER_POLL_SECONDS="10"
export FLASK_ENV="production"
export PORT="8050"
export SERVER_IP="80.240.29.142"
EXAMPLE_EOF
    echo ""
    echo "Then run: chmod 600 /root/api_server_env.sh"
    exit 1
fi

# Source environment file
source /root/api_server_env.sh

# Step 6: Install systemd services
echo "🔧 Step 6: Installing systemd services..."
cp $API_DIR/deploy/verzek_api.service /etc/systemd/system/
cp $API_DIR/deploy/verzek_worker.service /etc/systemd/system/

# Step 7: Reload systemd and enable services
echo "🔄 Step 7: Enabling services..."
systemctl daemon-reload
systemctl enable verzek_api.service
systemctl enable verzek_worker.service

# Step 8: Restart services
echo "♻️  Step 8: Restarting services..."
systemctl restart verzek_api.service
systemctl restart verzek_worker.service

# Step 9: Check status
echo "✅ Step 9: Checking service status..."
systemctl status verzek_api.service --no-pager || true
systemctl status verzek_worker.service --no-pager || true

# Step 10: Test API
echo "🧪 Step 10: Testing API..."
sleep 2
curl -s http://127.0.0.1:8050/api/health | jq . || echo "API test failed - check logs"

# Step 11: Configure Nginx (if not already configured)
echo "🌐 Step 11: Checking Nginx configuration..."
if [ ! -f "/etc/nginx/sites-available/verzek_api" ]; then
    cat > /etc/nginx/sites-available/verzek_api << 'NGINX_EOF'
server {
    listen 80;
    server_name api.verzekinnovative.com;

    location / {
        proxy_pass http://127.0.0.1:8050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX_EOF

    ln -sf /etc/nginx/sites-available/verzek_api /etc/nginx/sites-enabled/
    nginx -t && systemctl reload nginx
    
    echo "🔒 Setting up SSL certificate..."
    certbot --nginx -d api.verzekinnovative.com --non-interactive --agree-tos --email admin@verzekinnovative.com
fi

# Step 12: Setup daily report cron
echo "⏰ Step 12: Setting up daily report cron..."
CRON_LINE="0 23 * * * /usr/bin/python3 $API_DIR/reports/daily_report.py >> /var/log/verzek_daily.log 2>&1"
(crontab -l 2>/dev/null | grep -v "daily_report.py"; echo "$CRON_LINE") | crontab -

echo ""
echo "========================================="
echo "✅ Deployment completed successfully!"
echo ""
echo "📊 Service Status:"
echo "  API:    systemctl status verzek_api.service"
echo "  Worker: systemctl status verzek_worker.service"
echo ""
echo "📝 Logs:"
echo "  API:    journalctl -u verzek_api.service -f"
echo "  Worker: journalctl -u verzek_worker.service -f"
echo ""
echo "🌐 API Endpoint:"
echo "  https://api.verzekinnovative.com/api/health"
echo ""
echo "🎉 Backend is now live and auto-trading is operational!"
echo "========================================="
