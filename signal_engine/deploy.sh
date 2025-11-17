#!/bin/bash
# VerzekSignalEngine Auto-Deployment Script
# This script deploys the signal engine to Vultr production server

set -e

echo "=========================================="
echo "VerzekSignalEngine Deployment v1.0"
echo "=========================================="

# Configuration
DEPLOY_DIR="/root/signal_engine"
SERVICE_NAME="verzek-signalengine"
BACKUP_DIR="/root/backups/signal_engine"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    log_error "Please run as root (use sudo)"
    exit 1
fi

# Create deployment directory
log_info "Creating deployment directory..."
mkdir -p $DEPLOY_DIR
mkdir -p $DEPLOY_DIR/logs
mkdir -p $BACKUP_DIR

# Backup existing installation if present
if [ -d "$DEPLOY_DIR/bots" ]; then
    log_warn "Backing up existing installation..."
    BACKUP_FILE="$BACKUP_DIR/signal_engine_$(date +%Y%m%d_%H%M%S).tar.gz"
    tar -czf $BACKUP_FILE -C $DEPLOY_DIR . 2>/dev/null || true
    log_info "Backup created: $BACKUP_FILE"
fi

# Copy signal engine files
log_info "Copying VerzekSignalEngine files..."
cp -r /root/workspace/signal_engine/* $DEPLOY_DIR/

# Install Python dependencies
log_info "Installing Python dependencies..."
cd $DEPLOY_DIR
pip3 install -r requirements.txt --quiet

# Create environment file if not exists
if [ ! -f "$DEPLOY_DIR/.env" ]; then
    log_info "Creating environment configuration..."
    cat > $DEPLOY_DIR/.env << EOF
# VerzekSignalEngine Environment Configuration
BACKEND_API_URL=https://api.verzekinnovative.com
HOUSE_ENGINE_TOKEN=${HOUSE_ENGINE_TOKEN}
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
TELEGRAM_VIP_CHAT_ID=${TELEGRAM_VIP_CHAT_ID}
TELEGRAM_TRIAL_CHAT_ID=${TELEGRAM_TRIAL_CHAT_ID}

# Bot Configuration
ENABLE_SCALPING_BOT=true
ENABLE_TREND_BOT=true
ENABLE_QFL_BOT=true
ENABLE_AI_BOT=true

# Trading Symbols (comma-separated)
TRADING_SYMBOLS=BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,XRPUSDT

# Logging
LOG_LEVEL=INFO
EOF
    log_info "Environment file created"
else
    log_info "Using existing environment file"
fi

# Install systemd service
log_info "Installing systemd service..."
cp $DEPLOY_DIR/systemd/verzek-signalengine.service /etc/systemd/system/
systemctl daemon-reload

# Enable service to start on boot
log_info "Enabling service..."
systemctl enable $SERVICE_NAME

# Restart service
log_info "Restarting VerzekSignalEngine service..."
systemctl restart $SERVICE_NAME

# Wait for service to start
sleep 3

# Check service status
if systemctl is-active --quiet $SERVICE_NAME; then
    log_info "✅ VerzekSignalEngine deployed successfully!"
    log_info "Service status:"
    systemctl status $SERVICE_NAME --no-pager -l
    
    echo ""
    log_info "📊 View logs:"
    echo "  sudo journalctl -u $SERVICE_NAME -f"
    echo "  tail -f $DEPLOY_DIR/logs/signal_engine.log"
    
    echo ""
    log_info "🔧 Manage service:"
    echo "  sudo systemctl stop $SERVICE_NAME"
    echo "  sudo systemctl start $SERVICE_NAME"
    echo "  sudo systemctl restart $SERVICE_NAME"
    
else
    log_error "❌ Service failed to start!"
    log_error "Check logs: sudo journalctl -u $SERVICE_NAME -n 50"
    exit 1
fi

echo ""
echo "=========================================="
echo "🚀 Deployment Complete!"
echo "=========================================="
