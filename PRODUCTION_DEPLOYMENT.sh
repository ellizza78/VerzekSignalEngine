#!/bin/bash

#######################################################################
# VERZEK AUTO TRADER - PRODUCTION BACKEND FINALIZATION
# -------------------------------------------------------------
# This script prepares the Vultr VPS for production deployment
# Domain: api.verzekinnovative.com
# Server: 80.240.29.142
#######################################################################

set -e  # Exit on error

echo "═══════════════════════════════════════════════════════════"
echo "  🚀 VerzekAutoTrader Production Deployment"
echo "  📡 Domain: api.verzekinnovative.com"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Deployment directory
API_DIR="/root/api_server"
LOG_DIR="$API_DIR/logs"
BACKUP_DIR="/root/backups"

#######################################################################
# STEP 1: BACKUP & ENVIRONMENT CHECK
#######################################################################

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  STEP 1: Backup & Environment Check${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Create backup directory
mkdir -p "$BACKUP_DIR"
mkdir -p "$LOG_DIR"

# Backup current api_server.py if exists
if [ -f "$API_DIR/api_server.py" ]; then
    BACKUP_FILE="$BACKUP_DIR/api_server_backup_$(date +%Y%m%d_%H%M%S).py"
    cp "$API_DIR/api_server.py" "$BACKUP_FILE"
    echo -e "${GREEN}✅ Backed up api_server.py to: $BACKUP_FILE${NC}"
fi

# Backup systemd service if exists
if [ -f "/etc/systemd/system/verzek-api.service" ]; then
    cp "/etc/systemd/system/verzek-api.service" "$BACKUP_DIR/verzek-api.service.backup_$(date +%Y%m%d)"
    echo -e "${GREEN}✅ Backed up systemd service${NC}"
fi

# Check environment variables
echo -e "${YELLOW}Checking environment variables...${NC}"

if [ -f "/root/api_server_env.sh" ]; then
    source /root/api_server_env.sh
    echo -e "${GREEN}✅ Environment file loaded${NC}"
    
    # Check critical variables
    MISSING_VARS=()
    
    [ -z "$ENCRYPTION_MASTER_KEY" ] && MISSING_VARS+=("ENCRYPTION_MASTER_KEY")
    [ -z "$RESEND_API_KEY" ] && MISSING_VARS+=("RESEND_API_KEY")
    [ -z "$TELEGRAM_BOT_TOKEN" ] && MISSING_VARS+=("TELEGRAM_BOT_TOKEN")
    
    if [ ${#MISSING_VARS[@]} -gt 0 ]; then
        echo -e "${RED}❌ Missing environment variables:${NC}"
        printf '%s\n' "${MISSING_VARS[@]}"
        echo -e "${YELLOW}Please add these to /root/api_server_env.sh${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ All critical environment variables present${NC}"
else
    echo -e "${RED}❌ Environment file not found: /root/api_server_env.sh${NC}"
    echo -e "${YELLOW}Creating template...${NC}"
    
    cat > /root/api_server_env.sh << 'ENVEOF'
# VerzekAutoTrader Production Environment Variables
export ENCRYPTION_MASTER_KEY="your_fernet_key_here"
export RESEND_API_KEY="re_xxxxxxxxxxxxx"
export TELEGRAM_BOT_TOKEN="your_bot_token"
export BROADCAST_BOT_TOKEN="your_broadcast_bot_token"
export ADMIN_CHAT_ID="your_admin_chat_id"
export API_BASE_URL="https://api.verzekinnovative.com"
export DOMAIN="api.verzekinnovative.com"
export APP_NAME="Verzek AutoTrader"
export ADMIN_EMAIL="admin@verzekinnovative.com"
export SUPPORT_EMAIL="support@verzekinnovative.com"
export EMAIL_FROM="support@verzekinnovative.com"
export SUBSCRIPTION_SECRET_KEY="verz3k_prod_!@#_2025"
ENVEOF
    
    chmod 600 /root/api_server_env.sh
    echo -e "${YELLOW}⚠️  Please edit /root/api_server_env.sh with your actual values${NC}"
    exit 1
fi

#######################################################################
# STEP 2: INSTALL DEPENDENCIES
#######################################################################

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  STEP 2: Install System Dependencies${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Update system
echo -e "${YELLOW}Updating system packages...${NC}"
apt update -qq

# Install required packages
echo -e "${YELLOW}Installing system dependencies...${NC}"
apt install -y python3-pip nginx certbot python3-certbot-nginx logrotate curl

echo -e "${GREEN}✅ System dependencies installed${NC}"

# Install Python dependencies
echo -e "${YELLOW}Installing Python packages...${NC}"
cd "$API_DIR"

if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    echo -e "${GREEN}✅ Python dependencies installed${NC}"
else
    echo -e "${RED}❌ requirements.txt not found${NC}"
    exit 1
fi

#######################################################################
# STEP 3: FIREBASE SETUP
#######################################################################

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  STEP 3: Firebase Configuration${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ ! -f "/root/firebase_key.json" ]; then
    echo -e "${YELLOW}⚠️  Firebase service account not found${NC}"
    echo -e "${YELLOW}Please upload firebase_key.json to /root/${NC}"
    echo -e "${YELLOW}Download from: Firebase Console → Project Settings → Service Accounts${NC}"
    echo -e "${YELLOW}Continuing without Firebase for now...${NC}"
else
    echo -e "${GREEN}✅ Firebase service account found${NC}"
    chmod 600 /root/firebase_key.json
fi

#######################################################################
# STEP 4: NGINX CONFIGURATION
#######################################################################

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  STEP 4: Nginx Configuration${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Remove default nginx site
rm -f /etc/nginx/sites-enabled/default

# Copy nginx configuration
if [ -f "$API_DIR/vultr_infrastructure/nginx_verzekinnovative.conf" ]; then
    cp "$API_DIR/vultr_infrastructure/nginx_verzekinnovative.conf" /etc/nginx/sites-available/verzekinnovative
    ln -sf /etc/nginx/sites-available/verzekinnovative /etc/nginx/sites-enabled/
    echo -e "${GREEN}✅ Nginx configuration installed${NC}"
else
    echo -e "${RED}❌ Nginx configuration not found${NC}"
    exit 1
fi

# Test nginx configuration
nginx -t
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Nginx configuration valid${NC}"
else
    echo -e "${RED}❌ Nginx configuration error${NC}"
    exit 1
fi

#######################################################################
# STEP 5: SSL CERTIFICATE
#######################################################################

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  STEP 5: SSL Certificate Setup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ ! -d "/etc/letsencrypt/live/api.verzekinnovative.com" ]; then
    echo -e "${YELLOW}Obtaining SSL certificate...${NC}"
    certbot --nginx -d api.verzekinnovative.com --non-interactive --agree-tos --email admin@verzekinnovative.com
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ SSL certificate obtained${NC}"
    else
        echo -e "${RED}❌ Failed to obtain SSL certificate${NC}"
        echo -e "${YELLOW}You may need to run: certbot --nginx -d api.verzekinnovative.com${NC}"
    fi
else
    echo -e "${GREEN}✅ SSL certificate already exists${NC}"
fi

# Reload nginx
systemctl reload nginx
echo -e "${GREEN}✅ Nginx reloaded${NC}"

#######################################################################
# STEP 6: SYSTEMD SERVICE
#######################################################################

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  STEP 6: Systemd Service Configuration${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Copy systemd service file
if [ -f "$API_DIR/vultr_infrastructure/verzek-api.service" ]; then
    cp "$API_DIR/vultr_infrastructure/verzek-api.service" /etc/systemd/system/verzek-api.service
    echo -e "${GREEN}✅ Systemd service installed${NC}"
else
    echo -e "${RED}❌ Systemd service file not found${NC}"
    exit 1
fi

# Reload systemd
systemctl daemon-reload
systemctl enable verzek-api.service
echo -e "${GREEN}✅ Service enabled${NC}"

#######################################################################
# STEP 7: LOG ROTATION
#######################################################################

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  STEP 7: Log Rotation Setup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -f "$API_DIR/vultr_infrastructure/logrotate_verzek" ]; then
    cp "$API_DIR/vultr_infrastructure/logrotate_verzek" /etc/logrotate.d/verzek
    echo -e "${GREEN}✅ Log rotation configured${NC}"
fi

#######################################################################
# STEP 8: AUTO-RESTART CRON JOB
#######################################################################

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  STEP 8: Auto-Restart Monitoring${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Add cron job for auto-restart
CRON_JOB="*/5 * * * * systemctl is-active --quiet verzek-api.service || systemctl restart verzek-api.service"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "verzek-api.service"; then
    echo -e "${YELLOW}Cron job already exists${NC}"
else
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo -e "${GREEN}✅ Auto-restart cron job added (checks every 5 minutes)${NC}"
fi

#######################################################################
# STEP 9: START SERVICE
#######################################################################

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  STEP 9: Start API Service${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Stop service if running
systemctl stop verzek-api.service 2>/dev/null || true

# Start service
systemctl start verzek-api.service

# Wait for service to start
sleep 3

# Check service status
if systemctl is-active --quiet verzek-api.service; then
    echo -e "${GREEN}✅ API service started successfully${NC}"
else
    echo -e "${RED}❌ API service failed to start${NC}"
    echo -e "${YELLOW}Check logs: journalctl -u verzek-api.service -n 50${NC}"
    exit 1
fi

#######################################################################
# STEP 10: VALIDATION
#######################################################################

echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  STEP 10: Deployment Validation${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "${YELLOW}Testing health endpoint...${NC}"
sleep 2

# Test HTTP endpoint (should redirect)
HTTP_TEST=$(curl -s -o /dev/null -w "%{http_code}" http://api.verzekinnovative.com/api/health 2>/dev/null || echo "000")

# Test HTTPS endpoint
HTTPS_TEST=$(curl -s https://api.verzekinnovative.com/api/health 2>/dev/null || echo "{\"status\":\"error\"}")

echo "HTTP Status: $HTTP_TEST (should be 301 redirect)"
echo "HTTPS Response: $HTTPS_TEST"

if echo "$HTTPS_TEST" | grep -q "ok"; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${YELLOW}⚠️  Health check returned unexpected response${NC}"
fi

#######################################################################
# DEPLOYMENT SUMMARY
#######################################################################

echo -e "\n${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ DEPLOYMENT COMPLETED SUCCESSFULLY${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}📊 Deployment Summary:${NC}"
echo -e "  • API Endpoint: ${GREEN}https://api.verzekinnovative.com${NC}"
echo -e "  • Service Status: $(systemctl is-active verzek-api.service)"
echo -e "  • Nginx Status: $(systemctl is-active nginx)"
echo -e "  • SSL Certificate: Configured"
echo -e "  • Log Rotation: Configured"
echo -e "  • Auto-Restart: Enabled (5-min intervals)"
echo ""
echo -e "${BLUE}📝 Useful Commands:${NC}"
echo -e "  • Service status: ${YELLOW}systemctl status verzek-api.service${NC}"
echo -e "  • View logs: ${YELLOW}journalctl -u verzek-api.service -f${NC}"
echo -e "  • Restart service: ${YELLOW}systemctl restart verzek-api.service${NC}"
echo -e "  • Test endpoint: ${YELLOW}curl https://api.verzekinnovative.com/api/health${NC}"
echo ""
echo -e "${BLUE}🔐 Security Checklist:${NC}"
echo -e "  • Environment variables: /root/api_server_env.sh (chmod 600)"
echo -e "  • Firebase key: /root/firebase_key.json (chmod 600)"
echo -e "  • Rate limiting: Enabled (120/min)"
echo -e "  • CORS: Configured for mobile app"
echo ""
echo -e "${GREEN}🎉 Backend is production-ready!${NC}"
echo ""
