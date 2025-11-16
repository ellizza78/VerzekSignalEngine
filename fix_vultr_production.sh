#!/bin/bash
#
# VerzekAutoTrader Production Fix Script
# Consolidates backend, fixes services, deploys signal engine
#

set -e

echo "🔧 VerzekAutoTrader Production Deployment Fix"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

###############################
# STEP 1: Backend Consolidation
###############################
echo -e "${YELLOW}Step 1: Consolidating backend directory...${NC}"

# Create unified backend structure
mkdir -p /root/VerzekBackend/backend
mkdir -p /root/VerzekBackend/backend/logs

# If api_server exists, migrate its .env
if [ -d "/root/api_server" ]; then
    echo "Migrating .env from api_server..."
    if [ -f "/root/api_server/.env" ]; then
        cp /root/api_server/.env /root/VerzekBackend/backend/.env
        echo -e "${GREEN}✓ .env migrated${NC}"
    fi
    
    # Backup old directory
    mv /root/api_server /root/api_server.backup.$(date +%Y%m%d_%H%M%S) || true
    echo -e "${GREEN}✓ Old api_server backed up${NC}"
fi

cd /root/VerzekBackend/backend

echo -e "${GREEN}✓ Backend consolidated to /root/VerzekBackend/backend${NC}"
echo ""

###############################
# STEP 2: Update Systemd Services
###############################
echo -e "${YELLOW}Step 2: Updating systemd services...${NC}"

# Update API service
cat > /etc/systemd/system/verzek_api.service << 'EOF'
[Unit]
Description=Verzek AutoTrader API Server
After=network.target postgresql.service

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

# Update Worker service
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

# Update Signal Engine service
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

LimitNOFILE=65536
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓ Signal engine service updated${NC}"
echo ""

###############################
# STEP 3: Fix Signal Engine Imports
###############################
echo -e "${YELLOW}Step 3: Fixing signal engine imports...${NC}"

cd /root/signal_engine

# Create missing __init__.py files
touch __init__.py 2>/dev/null || true
touch bots/__init__.py 2>/dev/null || true
touch bots/scalper/__init__.py 2>/dev/null || true
touch bots/trend/__init__.py 2>/dev/null || true
touch bots/qfl/__init__.py 2>/dev/null || true
touch bots/ai_ml/__init__.py 2>/dev/null || true
touch services/__init__.py 2>/dev/null || true
touch common/__init__.py 2>/dev/null || true
touch data_feed/__init__.py 2>/dev/null || true
touch engine/__init__.py 2>/dev/null || true

# Create logs directory
mkdir -p logs

echo -e "${GREEN}✓ Signal engine package structure fixed${NC}"
echo ""

###############################
# STEP 4: Reload and Restart Services
###############################
echo -e "${YELLOW}Step 4: Reloading systemd and restarting services...${NC}"

systemctl daemon-reload

# Stop all services first
systemctl stop verzek_api || true
systemctl stop verzek_worker || true
systemctl stop verzek-signalengine || true

sleep 2

# Start services in order
echo "Starting API service..."
systemctl start verzek_api
sleep 3

echo "Starting worker service..."
systemctl start verzek_worker
sleep 3

echo "Starting signal engine..."
systemctl start verzek-signalengine
sleep 3

echo ""

###############################
# STEP 5: Verify Services
###############################
echo -e "${YELLOW}Step 5: Verifying services...${NC}"
echo ""

# Check API
if systemctl is-active --quiet verzek_api; then
    echo -e "${GREEN}✅ verzek_api: RUNNING${NC}"
else
    echo -e "${RED}❌ verzek_api: FAILED${NC}"
    journalctl -u verzek_api -n 20 --no-pager
fi

# Check Worker
if systemctl is-active --quiet verzek_worker; then
    echo -e "${GREEN}✅ verzek_worker: RUNNING${NC}"
else
    echo -e "${RED}❌ verzek_worker: FAILED${NC}"
    journalctl -u verzek_worker -n 20 --no-pager
fi

# Check Signal Engine
if systemctl is-active --quiet verzek-signalengine; then
    echo -e "${GREEN}✅ verzek-signalengine: RUNNING${NC}"
else
    echo -e "${RED}❌ verzek-signalengine: FAILED${NC}"
    journalctl -u verzek-signalengine -n 20 --no-pager
fi

echo ""
echo "=============================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=============================================="
echo ""
echo "📊 Service Status:"
echo "  API: $(systemctl is-active verzek_api)"
echo "  Worker: $(systemctl is-active verzek_worker)"
echo "  Signal Engine: $(systemctl is-active verzek-signalengine)"
echo ""
echo "📝 View Logs:"
echo "  API:           journalctl -u verzek_api -f"
echo "  Worker:        journalctl -u verzek_worker -f"
echo "  Signal Engine: journalctl -u verzek-signalengine -f"
echo ""
echo "🔍 Test Backend:"
echo "  curl http://localhost:8000/api/ping"
echo ""
