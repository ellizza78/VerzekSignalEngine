#!/bin/bash
# Emergency fix for auto-deployment git pull issues
# Run this on Vultr server if auto-deployment is stuck

set -e

LOG_FILE="/var/log/verzek_auto_deploy.log"
WORKSPACE="/root/workspace"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a $LOG_FILE
}

log "=========================================="
log "Emergency Deployment Fix"
log "=========================================="

# Navigate to workspace
cd $WORKSPACE || {
    log "ERROR: Workspace not found at $WORKSPACE"
    exit 1
}

# Fix git repository
log "Resetting git repository..."
git reset --hard HEAD
git clean -fd
git fetch --all
git reset --hard origin/main

log "✅ Git repository fixed"

# Check if signal_engine exists
if [ -d "$WORKSPACE/signal_engine" ]; then
    log "VerzekSignalEngine code found, deploying..."
    
    cd $WORKSPACE/signal_engine
    if [ -f "deploy.sh" ]; then
        chmod +x deploy.sh
        ./deploy.sh
    else
        log "ERROR: deploy.sh not found!"
        exit 1
    fi
else
    log "ERROR: signal_engine directory not found!"
    exit 1
fi

log "=========================================="
log "Emergency fix completed"
log "=========================================="
