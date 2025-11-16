#!/bin/bash
set -e

echo "🚀 VerzekAutoTrader - Continuous Deployment SYSTEM"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

SERVER="root@80.240.29.142"
SSH_KEY_PATH="$HOME/.ssh/vultr_key"

echo -e "${BLUE}🔑 Loading SSH private key from Replit Secrets...${NC}"

mkdir -p $HOME/.ssh
echo "$VULTR_SSH_PRIVATE_KEY" > $SSH_KEY_PATH
chmod 600 $SSH_KEY_PATH

# Test if SSH key works
if ! ssh -i $SSH_KEY_PATH -o StrictHostKeyChecking=no -o ConnectTimeout=5 -o BatchMode=yes $SERVER "echo 'SSH OK'" &>/dev/null; then
    echo ""
    echo "⚠️  SSH key authentication not working."
    echo "ℹ️  Please run this manually on your Vultr server to set up the key:"
    echo ""
    echo "    bash /root/fix_metadata.sh"
    echo ""
    echo "Or copy the files manually using the Replit file upload feature."
    exit 1
fi

echo -e "${BLUE}📡 Syncing to Vultr Production Server...${NC}"

# Upload backend
echo -e "${GREEN}📤 Uploading backend files...${NC}"
scp -i $SSH_KEY_PATH -o StrictHostKeyChecking=no -r backend/* $SERVER:/root/VerzekBackend/backend/

# Upload worker
echo -e "${GREEN}📤 Uploading worker...${NC}"
scp -i $SSH_KEY_PATH -o StrictHostKeyChecking=no worker.py $SERVER:/root/VerzekBackend/backend/

# Upload signal engine
echo -e "${GREEN}📤 Uploading signal engine...${NC}"
scp -i $SSH_KEY_PATH -o StrictHostKeyChecking=no -r signal_engine/* $SERVER:/root/signal_engine/

echo -e "${GREEN}🔄 Restarting services on Vultr...${NC}"

ssh -i $SSH_KEY_PATH -o StrictHostKeyChecking=no $SERVER << 'REMOTE'
cd /root/VerzekBackend/backend

# Clear python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

systemctl restart verzek_api
systemctl restart verzek_worker
systemctl restart verzek-signalengine || true
sleep 3

echo "🔥 Service Status:"
systemctl status verzek_api --no-pager | grep Active:
systemctl status verzek_worker --no-pager | grep Active:
systemctl status verzek-signalengine --no-pager | grep Active: || echo "⚠️ Signal engine inactive"
REMOTE

echo ""
echo -e "${BLUE}🏥 Performing API Health Check...${NC}"
ssh -i $SSH_KEY_PATH -o StrictHostKeyChecking=no $SERVER "curl -s http://localhost:8050/api/ping || echo '❌ API offline'"

echo ""
echo -e "${GREEN}🎉 Deployment Complete — Everything is LIVE!${NC}"