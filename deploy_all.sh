#!/bin/bash
set -e

echo "🚀 VerzekAutoTrader - Continuous Deployment"
echo "==========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

SERVER="root@80.240.29.142"

echo -e "${BLUE}📡 Syncing to Vultr Production Server...${NC}"

# Create directories on server
ssh $SERVER "mkdir -p /root/VerzekBackend/backend"
ssh $SERVER "mkdir -p /root/signal_engine"

# Upload backend files
echo -e "${GREEN}📤 Uploading backend...${NC}"
scp -r backend/* $SERVER:/root/VerzekBackend/backend/

# Upload worker
echo -e "${GREEN}📤 Uploading worker...${NC}"
scp worker.py $SERVER:/root/VerzekBackend/backend/

# Upload signal engine
echo -e "${GREEN}📤 Uploading signal engine...${NC}"
scp -r signal_engine/* $SERVER:/root/signal_engine/

# Clear Python cache and restart services
echo -e "${GREEN}🔄 Restarting services...${NC}"
ssh $SERVER << 'REMOTE'
cd /root/VerzekBackend/backend
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

systemctl restart verzek_api
systemctl restart verzek_worker
systemctl restart verzek-signalengine || true

sleep 3

echo ""
echo "✅ Services restarted:"
systemctl status verzek_api --no-pager | grep "Active:"
systemctl status verzek_worker --no-pager | grep "Active:"
systemctl status verzek-signalengine --no-pager | grep "Active:" || echo "Signal engine not yet enabled"
REMOTE

# Health check
echo ""
echo -e "${GREEN}🏥 Health check...${NC}"
ssh $SERVER "curl -s http://localhost:8050/api/ping | python3 -m json.tool || echo '❌ API not responding'"

echo ""
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo ""
