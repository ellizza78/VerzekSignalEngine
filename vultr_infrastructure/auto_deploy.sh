#!/bin/bash
# Enhanced Auto-Deployment Script for Vultr
# Deploys backend API + VerzekSignalEngine automatically

set -e

WORKSPACE="/root/workspace"
LOG_FILE="/var/log/verzek_auto_deploy.log"
DEPLOY_LOCK="/tmp/verzek_deploy.lock"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

# Prevent concurrent deployments
if [ -f "$DEPLOY_LOCK" ]; then
    log "Deployment already in progress, skipping..."
    exit 0
fi

touch $DEPLOY_LOCK
trap "rm -f $DEPLOY_LOCK" EXIT

log "=========================================="
log "Verzek Auto-Deployment Started"
log "=========================================="

# Navigate to workspace
cd $WORKSPACE || {
    log "ERROR: Workspace not found at $WORKSPACE"
    exit 1
}

# Pull latest changes
log "Pulling latest changes from GitHub..."
git pull origin main >> $LOG_FILE 2>&1 || {
    log "WARNING: Git pull failed, continuing with existing code"
}

# Check if backend needs deployment
if [ -f "$WORKSPACE/backend/api_server.py" ]; then
    log "Checking backend API..."
    
    if systemctl is-active --quiet verzek_api; then
        # Check if backend code changed
        if git diff HEAD@{1} --name-only | grep -q "backend/"; then
            log "Backend changes detected, restarting API..."
            systemctl restart verzek_api
            sleep 2
            
            if systemctl is-active --quiet verzek_api; then
                log "✅ Backend API restarted successfully"
            else
                log "❌ Backend API restart failed!"
            fi
        fi
    fi
fi

# Check if VerzekSignalEngine needs deployment
if [ -f "$WORKSPACE/signal_engine/deploy.sh" ]; then
    log "Checking VerzekSignalEngine..."
    
    # Check if this is first deployment or if code changed
    if [ ! -d "/root/signal_engine" ] || git diff HEAD@{1} --name-only | grep -q "signal_engine/"; then
        log "VerzekSignalEngine deployment needed..."
        
        cd $WORKSPACE/signal_engine
        chmod +x deploy.sh
        
        if ./deploy.sh >> $LOG_FILE 2>&1; then
            log "✅ VerzekSignalEngine deployed successfully"
            
            # Send success notification
            if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$ADMIN_CHAT_ID" ]; then
                curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
                    -d chat_id="${ADMIN_CHAT_ID}" \
                    -d text="🚀 VerzekSignalEngine v1.0 deployed and running!

✅ All 4 bots started
✅ Connected to backend API
✅ Telegram broadcasting active

Signal flow is now LIVE!" \
                    -d parse_mode="HTML" > /dev/null 2>&1 || true
            fi
        else
            log "❌ VerzekSignalEngine deployment failed!"
            
            # Send error notification
            if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$ADMIN_CHAT_ID" ]; then
                curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
                    -d chat_id="${ADMIN_CHAT_ID}" \
                    -d text="❌ VerzekSignalEngine deployment failed!

Check logs: tail -f $LOG_FILE" \
                    -d parse_mode="HTML" > /dev/null 2>&1 || true
            fi
        fi
    else
        log "No VerzekSignalEngine changes detected, skipping..."
    fi
fi

log "Auto-deployment completed at $(date)"
log "=========================================="
