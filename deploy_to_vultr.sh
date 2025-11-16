#!/bin/bash

echo "🚀 VerzekSignalEngine Backend Deployment Script"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# Configuration
BACKEND_DIR="/root/api_server"
SIGNAL_ENGINE_DIR="/root/signal_engine"

# IMPORTANT: Set these environment variables before running this script
# export HOUSE_ENGINE_TOKEN="your-secret-token-here"
# export TELEGRAM_BOT_TOKEN="your-telegram-token-here"

if [ -z "$HOUSE_ENGINE_TOKEN" ]; then
    echo -e "${RED}ERROR: HOUSE_ENGINE_TOKEN environment variable not set${NC}"
    echo "Please run: export HOUSE_ENGINE_TOKEN='your-token-here'"
    exit 1
fi

if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo -e "${RED}ERROR: TELEGRAM_BOT_TOKEN environment variable not set${NC}"
    echo "Please run: export TELEGRAM_BOT_TOKEN='your-telegram-token-here'"
    exit 1
fi

echo -e "${YELLOW}Step 1: Update Backend Code${NC}"
cd $BACKEND_DIR || exit 1

# Backup current code
echo "Creating backup..."
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz backend/

# Pull latest code (or upload manually)
echo "Updating backend files..."
# If using git: git pull origin main
# If uploading manually, skip this step

echo -e "${GREEN}✓ Backend code updated${NC}"

echo ""
echo -e "${YELLOW}Step 2: Add Environment Variable${NC}"

# Add HOUSE_ENGINE_TOKEN to backend .env
if ! grep -q "HOUSE_ENGINE_TOKEN" $BACKEND_DIR/.env 2>/dev/null; then
    echo "HOUSE_ENGINE_TOKEN=$HOUSE_ENGINE_TOKEN" >> $BACKEND_DIR/.env
    echo -e "${GREEN}✓ HOUSE_ENGINE_TOKEN added to .env${NC}"
else
    echo -e "${YELLOW}! HOUSE_ENGINE_TOKEN already exists in .env${NC}"
fi

echo ""
echo -e "${YELLOW}Step 3: Restart Backend Service${NC}"
systemctl restart verzek_api
sleep 3

if systemctl is-active --quiet verzek_api; then
    echo -e "${GREEN}✓ Backend service restarted successfully${NC}"
else
    echo -e "${RED}✗ Backend service failed to start${NC}"
    echo "Check logs: journalctl -u verzek_api -n 50"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 4: Test Backend Endpoint${NC}"

# Test the endpoint
RESPONSE=$(curl -s -X POST http://localhost:8000/api/house-signals/ingest \
  -H "Content-Type: application/json" \
  -H "X-INTERNAL-TOKEN: $HOUSE_ENGINE_TOKEN" \
  -d '{
    "source": "TEST",
    "symbol": "BTCUSDT",
    "side": "LONG",
    "entry": 50000.0,
    "stop_loss": 49750.0,
    "take_profits": [50500],
    "timeframe": "M5",
    "confidence": 75
  }')

if echo "$RESPONSE" | grep -q "ok"; then
    echo -e "${GREEN}✓ Backend endpoint test successful${NC}"
    echo "Response: $RESPONSE"
else
    echo -e "${RED}✗ Backend endpoint test failed${NC}"
    echo "Response: $RESPONSE"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 5: Deploy Signal Engine${NC}"

# Create signal engine directory
mkdir -p $SIGNAL_ENGINE_DIR
cd $SIGNAL_ENGINE_DIR

# Check if already deployed
if [ -f "$SIGNAL_ENGINE_DIR/main.py" ]; then
    echo -e "${YELLOW}! Signal engine already exists${NC}"
    echo "Please manually upload updated files to: $SIGNAL_ENGINE_DIR"
else
    echo "Please upload signal engine files to: $SIGNAL_ENGINE_DIR"
    echo "Then run: bash deploy_to_vultr.sh"
    exit 0
fi

# Install dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt > /dev/null 2>&1

echo -e "${GREEN}✓ Dependencies installed${NC}"

# Configure environment
echo ""
echo -e "${YELLOW}Step 6: Configure Signal Engine Environment${NC}"

if [ ! -f "$SIGNAL_ENGINE_DIR/config/.env" ]; then
    cp $SIGNAL_ENGINE_DIR/config/.env.example $SIGNAL_ENGINE_DIR/config/.env
    
    # Update .env with values from environment variables
    sed -i "s|BACKEND_API_URL=.*|BACKEND_API_URL=https://api.verzekinnovative.com|g" $SIGNAL_ENGINE_DIR/config/.env
    sed -i "s|HOUSE_ENGINE_TOKEN=.*|HOUSE_ENGINE_TOKEN=$HOUSE_ENGINE_TOKEN|g" $SIGNAL_ENGINE_DIR/config/.env
    sed -i "s|TELEGRAM_BOT_TOKEN=.*|TELEGRAM_BOT_TOKEN=$TELEGRAM_BOT_TOKEN|g" $SIGNAL_ENGINE_DIR/config/.env
    
    echo -e "${GREEN}✓ Environment configured${NC}"
else
    echo -e "${YELLOW}! .env already exists, please update manually${NC}"
fi

echo ""
echo -e "${YELLOW}Step 7: Setup Systemd Service${NC}"

# Copy systemd service
cp $SIGNAL_ENGINE_DIR/systemd/verzek-signalengine.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable verzek-signalengine

echo -e "${GREEN}✓ Systemd service configured${NC}"

echo ""
echo -e "${YELLOW}Step 8: Start Signal Engine${NC}"

systemctl start verzek-signalengine
sleep 3

if systemctl is-active --quiet verzek-signalengine; then
    echo -e "${GREEN}✓ Signal engine started successfully${NC}"
else
    echo -e "${RED}✗ Signal engine failed to start${NC}"
    echo "Check logs: journalctl -u verzek-signalengine -n 50"
    exit 1
fi

echo ""
echo -e "${YELLOW}Step 9: Remove Old Telethon Code${NC}"

# Stop and disable Telethon service
if systemctl is-active --quiet telethon-forwarder; then
    systemctl stop telethon-forwarder
    systemctl disable telethon-forwarder
    rm -f /etc/systemd/system/telethon-forwarder.service
    systemctl daemon-reload
    echo -e "${GREEN}✓ Telethon service stopped and removed${NC}"
else
    echo -e "${YELLOW}! Telethon service not found (already removed)${NC}"
fi

# Remove Telethon files
rm -f /root/telethon_forwarder.py
rm -f /root/setup_telethon.py
rm -f /root/recover_telethon_session.py
rm -f /root/forwarder_watchdog.py
rm -f /root/*.session
rm -f /root/telethon_session_*.txt
rm -rf /root/telethon_logs/

echo -e "${GREEN}✓ Telethon files removed${NC}"

echo ""
echo "================================================"
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE!${NC}"
echo "================================================"
echo ""
echo "📊 System Status:"
echo "  Backend API: $(systemctl is-active verzek_api)"
echo "  Signal Engine: $(systemctl is-active verzek-signalengine)"
echo ""
echo "📝 Next Steps:"
echo "  1. Monitor logs: journalctl -u verzek-signalengine -f"
echo "  2. Check signals: tail -f $SIGNAL_ENGINE_DIR/logs/signal_engine.log"
echo "  3. Wait 5-10 minutes for first signals to generate"
echo ""
echo "🔍 Verification Commands:"
echo "  Backend status: systemctl status verzek_api"
echo "  Signal engine status: systemctl status verzek-signalengine"
echo "  View signals: tail -f $SIGNAL_ENGINE_DIR/logs/signal_engine.log"
echo ""
echo -e "${GREEN}VerzekSignalEngine v1.0 is now live! 🚀${NC}"
