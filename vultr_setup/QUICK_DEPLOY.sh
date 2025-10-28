#!/bin/bash
# ==========================================================
# Verzek Auto Trader - Quick Deploy Script for Vultr
# ==========================================================
# Run this script on your Vultr server to deploy everything
# Usage: bash QUICK_DEPLOY.sh
# ==========================================================

set -e

echo "================================================"
echo "🚀 VERZEK AUTO TRADER - QUICK DEPLOYMENT"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

PROJECT_DIR="/var/www/VerzekAutoTrader"

echo -e "${YELLOW}📁 Checking project directory...${NC}"
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ Error: $PROJECT_DIR not found${NC}"
    echo "Please ensure VerzekAutoTrader is cloned to /var/www/"
    exit 1
fi

cd "$PROJECT_DIR"
echo -e "${GREEN}✅ Project directory found${NC}"
echo ""

# Phase 1: Install systemd services
echo -e "${YELLOW}📋 PHASE 1: Installing systemd services...${NC}"

echo "Installing verzekapi.service..."
cat > /etc/systemd/system/verzekapi.service << 'EOF'
[Unit]
Description=Verzek Auto Trader API Server
After=network.target

[Service]
Type=simple
ExecStart=/var/www/VerzekAutoTrader/venv/bin/python3 /var/www/VerzekAutoTrader/api_server.py
WorkingDirectory=/var/www/VerzekAutoTrader
User=root
Environment=PYTHONUNBUFFERED=1
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "Installing verzekbot.service..."
cat > /etc/systemd/system/verzekbot.service << 'EOF'
[Unit]
Description=Verzek Telegram Signal Forwarder
After=network.target

[Service]
Type=simple
ExecStart=/var/www/VerzekAutoTrader/venv/bin/python3 /var/www/VerzekAutoTrader/telethon_forwarder.py
WorkingDirectory=/var/www/VerzekAutoTrader
User=root
Environment=PYTHONUNBUFFERED=1
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ Services installed${NC}"
echo ""

# Phase 2: Configure firewall
echo -e "${YELLOW}🔥 PHASE 2: Configuring firewall...${NC}"
ufw allow 5000/tcp
ufw reload
echo -e "${GREEN}✅ Port 5000 opened${NC}"
echo ""

# Phase 3: Install watchdog
echo -e "${YELLOW}🐕 PHASE 3: Installing watchdog...${NC}"

cat > /opt/verzek_watchdog.sh << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/verzek_watchdog.log"
ADMIN_CHAT_ID="572038606"
TELEGRAM_BOT_TOKEN="8351047055:AAEqBFx5g0NJpEvUOCP_DCPD0VsGpEAjvRE"

send_telegram_alert() {
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d chat_id="$ADMIN_CHAT_ID" \
        -d text="⚠️ Watchdog Alert: Service $1 was restarted on $(hostname) at $(date '+%Y-%m-%d %H:%M:%S')" > /dev/null
}

while true; do
    for svc in verzekbot verzekapi; do
        if ! systemctl is-active --quiet "$svc"; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') ⚠️ Service $svc is down. Restarting..." >> "$LOG_FILE"
            systemctl restart "$svc"
            send_telegram_alert "$svc"
            echo "$(date '+%Y-%m-%d %H:%M:%S') ✅ Service $svc restarted" >> "$LOG_FILE"
        fi
    done
    sleep 120
done
EOF

chmod +x /opt/verzek_watchdog.sh

cat > /etc/systemd/system/verzekwatchdog.service << 'EOF'
[Unit]
Description=Verzek Auto Trader Watchdog
After=network.target

[Service]
Type=simple
ExecStart=/opt/verzek_watchdog.sh
Restart=always
RestartSec=10
User=root

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✅ Watchdog installed${NC}"
echo ""

# Phase 4: Install status monitoring
echo -e "${YELLOW}📊 PHASE 4: Installing status monitor...${NC}"

cat > /opt/verzek_status.sh << 'EOF'
#!/bin/bash
echo "🚀 VERZEK AUTO TRADER - SYSTEM STATUS"
echo "========================================"
for svc in verzekbot verzekapi verzekwatchdog; do
    if systemctl is-active --quiet "$svc"; then
        echo "✅ $svc: RUNNING"
    else
        echo "❌ $svc: STOPPED"
    fi
done
echo ""
ss -tuln | grep ":5000" && echo "✅ Port 5000: LISTENING" || echo "❌ Port 5000: NOT LISTENING"
EOF

chmod +x /opt/verzek_status.sh
echo -e "${GREEN}✅ Status monitor installed${NC}"
echo ""

# Phase 5: Start all services
echo -e "${YELLOW}🎯 PHASE 5: Starting all services...${NC}"

systemctl daemon-reload
systemctl enable verzekapi verzekbot verzekwatchdog
systemctl restart verzekapi verzekbot verzekwatchdog

sleep 3

echo ""
echo "================================================"
echo -e "${GREEN}✅ DEPLOYMENT COMPLETE!${NC}"
echo "================================================"
echo ""

# Show status
bash /opt/verzek_status.sh

echo ""
echo "📝 Next steps:"
echo "  1. Test backend: curl http://localhost:5000/ping"
echo "  2. Test bridge: curl https://verzek-auto-trader.replit.app/ping"
echo "  3. Check logs: journalctl -u verzekapi -f"
echo "  4. Monitor status: bash /opt/verzek_status.sh"
echo ""
echo "🎉 Your Verzek Auto Trader is now running!"
