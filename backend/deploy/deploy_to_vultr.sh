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

# Step 3: Create virtual environment and install dependencies
echo "🐍 Step 3: Setting up Python environment..."
cd $API_DIR/backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate

cd $API_DIR

# Step 4: Create database and logs directories
echo "💾 Step 4: Creating database and logs directories..."
mkdir -p $API_DIR/database
mkdir -p $API_DIR/logs
chmod 755 $API_DIR/logs

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
# Verzek AutoTrader Production Configuration
# ⚠️ SECURITY: Generate unique values for all secrets below!

# Security Keys (MUST BE UNIQUE - DO NOT USE THESE DEFAULTS IN PRODUCTION!)
export JWT_SECRET="<GENERATE_UNIQUE_SECRET_HERE>"  # Generate with: openssl rand -hex 32
export ENCRYPTION_KEY="<GENERATE_WITH: python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'>"

# Database
export DATABASE_URL="sqlite:////root/api_server/backend/database/verzek.db"

# Telegram Integration
export TELEGRAM_BOT_TOKEN="<YOUR_BOT_TOKEN>"
export BROADCAST_BOT_TOKEN="<YOUR_BROADCAST_BOT_TOKEN>"
export VIP_GROUP_ID="<YOUR_VIP_GROUP_ID>"
export TRIAL_GROUP_ID="<YOUR_TRIAL_GROUP_ID>"
export ADMIN_CHAT_ID="<YOUR_ADMIN_CHAT_ID>"

# Email (Resend API)
export EMAIL_FROM="support@verzekinnovative.com"
export RESEND_API_KEY="<YOUR_RESEND_API_KEY>"

# Trading Configuration
export EXCHANGE_MODE="paper"  # paper or live
export WORKER_POLL_SECONDS="10"

# Server Configuration
export FLASK_ENV="production"
export PORT="8050"
export SERVER_IP="80.240.29.142"
export LOG_DIR="/root/api_server/logs"
EXAMPLE_EOF
    echo ""
    echo "Then run: chmod 600 /root/api_server_env.sh"
    exit 1
fi

# Source environment file
source /root/api_server_env.sh

# Step 6: Install systemd services
echo "🔧 Step 6: Installing systemd services..."
cp $API_DIR/backend/deploy/verzek_api.service /etc/systemd/system/
cp $API_DIR/backend/deploy/verzek_worker.service /etc/systemd/system/

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

# Step 10: Test API endpoints
echo "🧪 Step 10: Testing API endpoints..."
sleep 3

# Test /api/ping
echo "   Testing /api/ping..."
PING_RESULT=$(curl -s http://127.0.0.1:8050/api/ping)
if echo "$PING_RESULT" | jq -e '.status == "ok"' > /dev/null 2>&1; then
    echo "   ✅ /api/ping - OK"
else
    echo "   ❌ /api/ping - FAILED"
    echo "   Response: $PING_RESULT"
fi

# Test /api/health
echo "   Testing /api/health..."
HEALTH_RESULT=$(curl -s http://127.0.0.1:8050/api/health)
if echo "$HEALTH_RESULT" | jq -e '.ok == true' > /dev/null 2>&1; then
    echo "   ✅ /api/health - OK"
    HEALTH_STATUS="healthy"
else
    echo "   ❌ /api/health - FAILED"
    echo "   Response: $HEALTH_RESULT"
    HEALTH_STATUS="unhealthy"
fi

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
CRON_LINE="0 23 * * * /bin/bash -c 'cd $API_DIR/backend && source venv/bin/activate && source /root/api_server_env.sh && python reports/daily_report.py' >> /var/log/verzek_daily.log 2>&1"
(crontab -l 2>/dev/null | grep -v "daily_report.py"; echo "$CRON_LINE") | crontab -
echo "✅ Daily report cron configured (runs at 11 PM daily)"

# Step 13: Setup watchdog monitoring
echo "🔍 Step 13: Setting up watchdog monitoring..."
if [ -f "$API_DIR/backend/scripts/watchdog.sh" ]; then
    # Make watchdog script executable
    chmod +x $API_DIR/backend/scripts/watchdog.sh
    
    # Create watchdog cron with full environment setup (venv + env vars)
    WATCHDOG_CRON="*/5 * * * * /bin/bash -c 'cd $API_DIR/backend && source venv/bin/activate && source /root/api_server_env.sh && scripts/watchdog.sh' >> $API_DIR/logs/watchdog.log 2>&1"
    (crontab -l 2>/dev/null | grep -v "watchdog.sh"; echo "$WATCHDOG_CRON") | crontab -
    echo "✅ Watchdog monitoring configured (runs every 5 minutes)"
else
    echo "⚠️  Watchdog script not found - skipping"
fi

# Step 14: Log deployment
echo "📝 Step 14: Logging deployment..."
DEPLOY_LOG="/root/api_server/logs/deployment_history.log"
mkdir -p $(dirname "$DEPLOY_LOG")
cat >> "$DEPLOY_LOG" << EOF
========================================
Deployment: $(date '+%Y-%m-%d %H:%M:%S %Z')
Version: 2.1
Health Status: $HEALTH_STATUS
Services: verzek_api.service, verzek_worker.service
Deployed by: $(whoami)
========================================

EOF

# Step 15: Send Telegram success notification (if configured)
if [ "$HEALTH_STATUS" = "healthy" ] && [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$ADMIN_CHAT_ID" ]; then
    echo "📱 Step 15: Sending success notification..."
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d "chat_id=${ADMIN_CHAT_ID}" \
        -d "text=✅ <b>VerzekBackend Deployment Successful</b>%0A%0AVersion: 2.1%0ATime: $(date '+%Y-%m-%d %H:%M:%S')%0AStatus: ${HEALTH_STATUS}%0A%0AAll systems operational!" \
        -d "parse_mode=HTML" > /dev/null 2>&1
else
    echo "📱 Step 15: Skipping Telegram notification (not configured or unhealthy)"
fi

echo ""
echo "========================================="
echo "✅ Deployment completed successfully!"
echo ""
echo "📍 API URL: https://api.verzekinnovative.com"
echo "🏥 Health Check: curl https://api.verzekinnovative.com/api/health"
echo "📊 Status: $HEALTH_STATUS"
echo ""
echo "🔧 Service Commands:"
echo "  sudo systemctl status verzek_api.service"
echo "  sudo systemctl status verzek_worker.service"
echo "  sudo journalctl -u verzek_api.service -f"
echo "  sudo journalctl -u verzek_worker.service -f"
echo ""
echo "📁 Logs:"
echo "  /root/api_server/logs/api.log"
echo "  /root/api_server/logs/worker.log"
echo "  /root/api_server/logs/watchdog.log"
echo "  /root/api_server/logs/deployment_history.log"
echo ""
echo "🔍 Watchdog: Health checks every 5 minutes"
echo "🎉 Backend is now live and auto-trading is operational!"
echo "========================================="
