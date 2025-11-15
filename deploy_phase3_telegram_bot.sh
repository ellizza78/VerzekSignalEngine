#!/bin/bash
###############################################################################
# Phase 3 Telegram Bot Deployment Script
# VerzekAutoTrader - Signal Bot Setup
# Run this on Vultr VPS (80.240.29.142)
###############################################################################

echo "======================================================================"
echo "🤖 VerzekAutoTrader - Phase 3 Telegram Bot Deployment"
echo "======================================================================"
echo ""

# Configuration
BOT_TOKEN="7516420499:AAHkf1VIt-uYZQ33eJLQRcF6Vnw-IJ8OLWE"
ADMIN_CHAT_ID="572038606"
ENV_FILE="/root/api_server_env.sh"
SERVICE_FILE="/root/VerzekBackend/backend/systemd/verzek-signal-bot.service"

# Step 1: Install Pyrogram
echo "📦 Step 1/5: Installing Pyrogram..."
pip3 install pyrogram --quiet
if [ $? -eq 0 ]; then
    echo "   ✅ Pyrogram installed successfully"
else
    echo "   ❌ Pyrogram installation failed"
    exit 1
fi
echo ""

# Step 2: Backup environment file
echo "💾 Step 2/5: Backing up environment file..."
if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "${ENV_FILE}.backup_$(date +%Y%m%d_%H%M%S)"
    echo "   ✅ Backup created: ${ENV_FILE}.backup_$(date +%Y%m%d_%H%M%S)"
else
    echo "   ⚠️  Environment file not found, will be created"
fi
echo ""

# Step 3: Add Telegram configuration to environment
echo "🔧 Step 3/5: Adding Telegram bot configuration..."

# Check if bot token already exists
if grep -q "TELEGRAM_BOT_TOKEN" "$ENV_FILE" 2>/dev/null; then
    echo "   ⚠️  TELEGRAM_BOT_TOKEN already exists, updating..."
    sed -i "s|^TELEGRAM_BOT_TOKEN=.*|TELEGRAM_BOT_TOKEN=$BOT_TOKEN|" "$ENV_FILE"
else
    echo "" >> "$ENV_FILE"
    echo "# Telegram Bot Configuration (Phase 3)" >> "$ENV_FILE"
    echo "TELEGRAM_BOT_TOKEN=$BOT_TOKEN" >> "$ENV_FILE"
fi

# Check if admin chat ID already exists
if grep -q "ADMIN_CHAT_ID" "$ENV_FILE" 2>/dev/null; then
    echo "   ⚠️  ADMIN_CHAT_ID already exists, updating..."
    sed -i "s|^ADMIN_CHAT_ID=.*|ADMIN_CHAT_ID=$ADMIN_CHAT_ID|" "$ENV_FILE"
else
    echo "ADMIN_CHAT_ID=$ADMIN_CHAT_ID" >> "$ENV_FILE"
fi

echo "   ✅ Telegram configuration added to $ENV_FILE"
echo ""

# Step 4: Deploy systemd service
echo "🚀 Step 4/5: Deploying signal bot systemd service..."
if [ -f "$SERVICE_FILE" ]; then
    cp "$SERVICE_FILE" /etc/systemd/system/
    systemctl daemon-reload
    echo "   ✅ Service file deployed"
else
    echo "   ❌ Service file not found: $SERVICE_FILE"
    echo "   Please ensure VerzekBackend repo is pulled to /root/VerzekBackend"
    exit 1
fi
echo ""

# Step 5: Start and enable service
echo "▶️  Step 5/5: Starting signal bot service..."
systemctl enable verzek-signal-bot.service
systemctl restart verzek-signal-bot.service
sleep 2

# Check service status
if systemctl is-active --quiet verzek-signal-bot.service; then
    echo "   ✅ Signal bot service started successfully"
else
    echo "   ❌ Service failed to start, checking logs..."
    journalctl -u verzek-signal-bot.service -n 20 --no-pager
    exit 1
fi
echo ""

echo "======================================================================"
echo "✅ Phase 3 Deployment Complete!"
echo "======================================================================"
echo ""
echo "📊 Service Status:"
systemctl status verzek-signal-bot.service --no-pager | head -10
echo ""
echo "======================================================================"
echo "🧪 Testing Instructions:"
echo "======================================================================"
echo "1. Open Telegram on your phone"
echo "2. Search for your bot (the username you created with @BotFather)"
echo "3. Send: /start"
echo "4. Send test signal: BUY BTCUSDT @ 50000"
echo ""
echo "Expected response:"
echo "  ✅ Signal Parsed:"
echo "  • Symbol: BTCUSDT"
echo "  • Type: BUY"
echo "  • Entry: 50000.0"
echo ""
echo "======================================================================"
echo "📋 Useful Commands:"
echo "======================================================================"
echo "View logs:        journalctl -u verzek-signal-bot.service -f"
echo "Check status:     systemctl status verzek-signal-bot.service"
echo "Restart bot:      systemctl restart verzek-signal-bot.service"
echo "Stop bot:         systemctl stop verzek-signal-bot.service"
echo ""
echo "======================================================================"
echo "⚠️  SAFETY REMINDER:"
echo "======================================================================"
echo "• Bot is in DRY-RUN mode (Phase 2)"
echo "• NO REAL TRADING enabled"
echo "• NO BROADCASTING to groups yet"
echo "• All exchanges return MOCK responses"
echo ""
echo "Before enabling live trading, review:"
echo "  /root/VerzekBackend/LIVE_TRADING_PRECHECK_REPORT.md"
echo ""
echo "======================================================================"
echo "🎉 Deployment complete! Test your bot now on Telegram!"
echo "======================================================================"
