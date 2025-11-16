#!/bin/bash
###############################################################################
# VERZEK PRODUCTION FIX - PASTE THIS ENTIRE SCRIPT INTO VULTR SSH
# This script consolidates backend, fixes all services, and deploys signal engine
###############################################################################

set -e

echo "🔧 VerzekAutoTrader Production Deployment Fix"
echo "=============================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

###############################
# STEP 1: Backend Consolidation
###############################
echo -e "${YELLOW}Step 1: Consolidating backend directory...${NC}"

mkdir -p /root/VerzekBackend/backend/logs
mkdir -p /root/signal_engine/logs

# Migrate .env if api_server exists
if [ -d "/root/api_server" ]; then
    if [ -f "/root/api_server/.env" ]; then
        cp /root/api_server/.env /root/VerzekBackend/backend/.env
        echo -e "${GREEN}✓ .env migrated from api_server${NC}"
    fi
    mv /root/api_server /root/api_server.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
fi

cd /root/VerzekBackend/backend
echo -e "${GREEN}✓ Backend consolidated${NC}"

###############################
# STEP 2: Update API Service
###############################
echo -e "${YELLOW}Step 2: Updating verzek_api service...${NC}"

cat > /etc/systemd/system/verzek_api.service << 'EOF'
[Unit]
Description=Verzek AutoTrader API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/VerzekBackend/backend
EnvironmentFile=/root/VerzekBackend/backend/.env
ExecStart=/usr/local/bin/gunicorn -c gunicorn.conf.py api_server:app
Restart=always
RestartSec=10
StandardOutput=append:/root/VerzekBackend/backend/logs/api_server.log
StandardError=append:/root/VerzekBackend/backend/logs/api_server_error.log

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ API service updated${NC}"

###############################
# STEP 3: Update Worker Service
###############################
echo -e "${YELLOW}Step 3: Updating verzek_worker service...${NC}"

cat > /etc/systemd/system/verzek_worker.service << 'EOF'
[Unit]
Description=Verzek AutoTrader Worker
After=network.target verzek_api.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/VerzekBackend/backend
EnvironmentFile=/root/VerzekBackend/backend/.env
ExecStart=/usr/bin/python3 worker.py
Restart=always
RestartSec=10
StandardOutput=append:/root/VerzekBackend/backend/logs/worker.log
StandardError=append:/root/VerzekBackend/backend/logs/worker_error.log

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ Worker service updated${NC}"

###############################
# STEP 4: Fix Signal Engine
###############################
echo -e "${YELLOW}Step 4: Fixing signal engine...${NC}"

cd /root/signal_engine

# Create __init__.py files
touch __init__.py
touch bots/__init__.py
touch bots/scalper/__init__.py 2>/dev/null || true
touch bots/trend/__init__.py 2>/dev/null || true
touch bots/qfl/__init__.py 2>/dev/null || true
touch bots/ai_ml/__init__.py 2>/dev/null || true
touch services/__init__.py
touch common/__init__.py 2>/dev/null || true
touch data_feed/__init__.py 2>/dev/null || true
touch engine/__init__.py 2>/dev/null || true

# Update service
cat > /etc/systemd/system/verzek-signalengine.service << 'EOF'
[Unit]
Description=VerzekSignalEngine - Multi-Bot Trading Signal System
After=network.target verzek_api.service
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

LimitNOFILE=65536
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ Signal engine fixed${NC}"

###############################
# STEP 5: Reload & Restart
###############################
echo -e "${YELLOW}Step 5: Restarting services...${NC}"

systemctl daemon-reload

# Stop all
systemctl stop verzek_api verzek_worker verzek-signalengine 2>/dev/null || true
sleep 2

# Start in order
systemctl start verzek_api
sleep 3

systemctl start verzek_worker  
sleep 3

systemctl start verzek-signalengine
sleep 3

###############################
# STEP 6: Verify
###############################
echo -e "${YELLOW}Step 6: Verifying...${NC}"
echo ""

if systemctl is-active --quiet verzek_api; then
    echo -e "${GREEN}✅ API: RUNNING${NC}"
else
    echo -e "${RED}❌ API: FAILED${NC}"
    journalctl -u verzek_api -n 15 --no-pager
fi

if systemctl is-active --quiet verzek_worker; then
    echo -e "${GREEN}✅ Worker: RUNNING${NC}"
else
    echo -e "${RED}❌ Worker: FAILED${NC}"
    journalctl -u verzek_worker -n 15 --no-pager
fi

if systemctl is-active --quiet verzek-signalengine; then
    echo -e "${GREEN}✅ Signal Engine: RUNNING${NC}"
else
    echo -e "${RED}❌ Signal Engine: FAILED${NC}"
    journalctl -u verzek-signalengine -n 15 --no-pager
fi

echo ""
echo "=============================================="
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE${NC}"
echo "=============================================="
echo ""
echo "📊 Quick Status:"
echo "  systemctl status verzek_api verzek_worker verzek-signalengine"
echo ""
echo "📝 View Logs:"
echo "  journalctl -u verzek_api -f"
echo "  journalctl -u verzek_worker -f"
echo "  journalctl -u verzek-signalengine -f"
echo ""
echo "🧪 Test API:"
echo "  curl http://localhost:8000/api/ping"
echo ""
