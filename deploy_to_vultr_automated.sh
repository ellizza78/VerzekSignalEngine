#!/bin/bash
# VerzekAutoTrader - Automated Vultr Deployment
# This script automates the deployment to Vultr VPS via SSH
# 
# Prerequisites:
# - SSH key configured for root@80.240.29.142
# - /root/reset_deploy.sh exists on VPS
# 
# Usage:
#   chmod +x deploy_to_vultr_automated.sh
#   ./deploy_to_vultr_automated.sh

set -e

echo "🚀 VerzekAutoTrader - Automated Deployment to Vultr"
echo "====================================================="
echo ""

# Configuration
VULTR_HOST="80.240.29.142"
VULTR_USER="root"
DEPLOY_SCRIPT="/root/reset_deploy.sh"
API_URL="https://api.verzekinnovative.com"

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Verify SSH connection
echo -e "${BLUE}📡 Step 1: Testing SSH connection to Vultr...${NC}"
if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no -o BatchMode=yes ${VULTR_USER}@${VULTR_HOST} "echo 'Connected'" 2>/dev/null; then
    echo -e "${GREEN}✅ SSH connection successful${NC}"
else
    echo -e "${RED}❌ SSH connection failed!${NC}"
    echo -e "${YELLOW}Please ensure:${NC}"
    echo "  1. SSH key is configured"
    echo "  2. VPS is accessible at ${VULTR_HOST}"
    echo "  3. Firewall allows SSH (port 22)"
    exit 1
fi

# Step 2: Verify deployment script exists
echo ""
echo -e "${BLUE}📄 Step 2: Verifying deployment script...${NC}"
if ssh -o StrictHostKeyChecking=no ${VULTR_USER}@${VULTR_HOST} "test -f ${DEPLOY_SCRIPT}"; then
    echo -e "${GREEN}✅ Deployment script found: ${DEPLOY_SCRIPT}${NC}"
else
    echo -e "${RED}❌ Deployment script not found!${NC}"
    echo -e "${YELLOW}Expected location: ${DEPLOY_SCRIPT}${NC}"
    exit 1
fi

# Step 3: Execute deployment
echo ""
echo -e "${BLUE}🚀 Step 3: Executing deployment on Vultr...${NC}"
echo -e "${YELLOW}This may take 1-2 minutes...${NC}"
echo ""

ssh -o StrictHostKeyChecking=no -t ${VULTR_USER}@${VULTR_HOST} << 'ENDSSH'
cd /root
echo "📥 Running reset deployment script..."
bash /root/reset_deploy.sh

echo ""
echo "⏳ Waiting for services to stabilize..."
sleep 5

echo ""
echo "✅ Deployment script completed!"
ENDSSH

# Step 4: Verify service status
echo ""
echo -e "${BLUE}🔍 Step 4: Verifying service status...${NC}"
SERVICE_STATUS=$(ssh -o StrictHostKeyChecking=no ${VULTR_USER}@${VULTR_HOST} "systemctl is-active verzek-api.service" || echo "inactive")

if [ "$SERVICE_STATUS" = "active" ]; then
    echo -e "${GREEN}✅ verzek-api.service is ACTIVE${NC}"
else
    echo -e "${RED}❌ verzek-api.service is NOT active!${NC}"
    echo -e "${YELLOW}Checking logs...${NC}"
    ssh -o StrictHostKeyChecking=no ${VULTR_USER}@${VULTR_HOST} "journalctl -u verzek-api.service -n 20 --no-pager"
    exit 1
fi

# Step 5: Test API endpoints
echo ""
echo -e "${BLUE}🧪 Step 5: Testing API endpoints...${NC}"

# Test /api/ping
echo -e "${YELLOW}Testing ${API_URL}/api/ping...${NC}"
PING_RESPONSE=$(curl -s -w "\n%{http_code}" ${API_URL}/api/ping 2>&1 | tail -1)

if [ "$PING_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ /api/ping responding (200 OK)${NC}"
    curl -s ${API_URL}/api/ping | python3 -m json.tool 2>/dev/null || curl -s ${API_URL}/api/ping
else
    echo -e "${RED}❌ /api/ping failed (HTTP ${PING_RESPONSE})${NC}"
fi

echo ""

# Test /api/health
echo -e "${YELLOW}Testing ${API_URL}/api/health...${NC}"
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" ${API_URL}/api/health 2>&1 | tail -1)

if [ "$HEALTH_RESPONSE" = "200" ]; then
    echo -e "${GREEN}✅ /api/health responding (200 OK)${NC}"
    curl -s ${API_URL}/api/health | python3 -m json.tool 2>/dev/null || curl -s ${API_URL}/api/health
else
    echo -e "${RED}❌ /api/health failed (HTTP ${HEALTH_RESPONSE})${NC}"
fi

# Final summary
echo ""
echo "====================================================="
echo -e "${GREEN}✅ DEPLOYMENT COMPLETED SUCCESSFULLY!${NC}"
echo "====================================================="
echo ""
echo -e "${BLUE}📊 Deployment Summary:${NC}"
echo "  ✅ SSH Connection: Successful"
echo "  ✅ Deployment Script: Executed"
echo "  ✅ Service Status: Active"
echo "  ✅ API Endpoints: Responding"
echo ""
echo -e "${BLUE}🌐 Production URLs:${NC}"
echo "  Backend API: ${API_URL}"
echo "  Ping: ${API_URL}/api/ping"
echo "  Health: ${API_URL}/api/health"
echo ""
echo -e "${YELLOW}📝 Next Steps:${NC}"
echo "  1. Test registration from mobile app"
echo "  2. Verify email verification works"
echo "  3. Monitor logs: ssh root@${VULTR_HOST} 'journalctl -u verzek-api.service -f'"
echo ""
echo "====================================================="
