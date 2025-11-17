#!/bin/bash
# Automated VerzekSignalEngine Deployment to Vultr
# Runs via auto-deployment systemd timer

set -e

WORKSPACE="/root/workspace"
SIGNAL_ENGINE_DIR="/root/signal_engine"
LOG_FILE="/var/log/verzek_signal_deploy.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

log "========================================"
log "VerzekSignalEngine Auto-Deployment"
log "========================================"

# Check if workspace exists (auto-pulled from GitHub)
if [ ! -d "$WORKSPACE/signal_engine" ]; then
    log "ERROR: signal_engine directory not found in workspace"
    exit 1
fi

# Run deployment script
log "Running deployment script..."
cd $WORKSPACE/signal_engine
chmod +x deploy.sh

# Execute deployment
if ./deploy.sh >> $LOG_FILE 2>&1; then
    log "✅ VerzekSignalEngine deployed successfully"
    
    # Send Telegram notification
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$ADMIN_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -d chat_id="${ADMIN_CHAT_ID}" \
            -d text="🚀 VerzekSignalEngine v1.0 deployed successfully!" \
            -d parse_mode="HTML" > /dev/null 2>&1 || true
    fi
else
    log "❌ Deployment failed!"
    
    # Send error notification
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$ADMIN_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -d chat_id="${ADMIN_CHAT_ID}" \
            -d text="❌ VerzekSignalEngine deployment failed! Check logs: tail -f $LOG_FILE" \
            -d parse_mode="HTML" > /dev/null 2>&1 || true
    fi
    
    exit 1
fi

log "Deployment complete at $(date)"
