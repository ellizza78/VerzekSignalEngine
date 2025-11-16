#!/bin/bash
#
# VerzekAutoTrader - Automated Pull-Based Deployment
# Runs on Vultr server, checks for Git updates and auto-deploys
#

set -euo pipefail

# Configuration
REPO_DIR="/root/VerzekBackend"
BACKEND_DIR="/root/VerzekBackend/backend"
LOG_FILE="/var/log/verzek_auto_deploy.log"
BACKUP_DIR="/root/VerzekBackend/backups"
SERVICE_NAME="verzek_api"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Error handler
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

log "=== Starting auto-deploy check ==="

# Navigate to repo
cd "$REPO_DIR" || error_exit "Cannot access repo directory"

# Fetch latest from origin
log "Fetching latest changes from origin..."
git fetch origin main || error_exit "Git fetch failed"

# Check if there are new commits
LOCAL_HASH=$(git rev-parse HEAD)
REMOTE_HASH=$(git rev-parse origin/main)

if [ "$LOCAL_HASH" = "$REMOTE_HASH" ]; then
    log "No new changes detected. Exiting."
    exit 0
fi

log "New changes detected! Local: $LOCAL_HASH, Remote: $REMOTE_HASH"

# Create timestamped backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/backup_$TIMESTAMP"
mkdir -p "$BACKUP_PATH"

log "Creating backup at $BACKUP_PATH..."
cp "$BACKEND_DIR/models.py" "$BACKUP_PATH/models.py.bak" 2>/dev/null || log "models.py not found for backup"
cp "$BACKEND_DIR/house_signals_routes.py" "$BACKUP_PATH/house_signals_routes.py.bak" 2>/dev/null || log "house_signals_routes.py not found for backup"

# Pull latest changes
log "Pulling latest changes..."
git pull origin main || error_exit "Git pull failed"

# Clear Python cache
log "Clearing Python cache..."
find "$BACKEND_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$BACKEND_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true

# Verify critical files exist
if [ ! -f "$BACKEND_DIR/models.py" ]; then
    error_exit "models.py missing after pull - rolling back"
fi

if [ ! -f "$BACKEND_DIR/house_signals_routes.py" ]; then
    error_exit "house_signals_routes.py missing after pull - rolling back"
fi

# Stop service gracefully
log "Stopping $SERVICE_NAME..."
systemctl stop "$SERVICE_NAME" || log "Warning: Failed to stop service gracefully"

# Kill any remaining gunicorn processes
pkill -9 gunicorn 2>/dev/null || true
sleep 2

# Start service
log "Starting $SERVICE_NAME..."
systemctl start "$SERVICE_NAME" || error_exit "Failed to start service"

# Wait for service to be ready
sleep 5

# Health check
if systemctl is-active --quiet "$SERVICE_NAME"; then
    log "✅ SUCCESS: Deployment completed. Service is active."
    log "Deployed commit: $REMOTE_HASH"
    
    # Test the API endpoint
    if command -v curl &> /dev/null; then
        log "Testing API endpoint..."
        RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8050/api/health 2>/dev/null || echo "000")
        if [ "$RESPONSE" = "200" ] || [ "$RESPONSE" = "404" ]; then
            log "API is responding (HTTP $RESPONSE)"
        else
            log "Warning: API health check returned HTTP $RESPONSE"
        fi
    fi
else
    error_exit "Service failed to start after deployment"
fi

# Clean old backups (keep last 10)
log "Cleaning old backups..."
cd "$BACKUP_DIR"
ls -t | tail -n +11 | xargs rm -rf 2>/dev/null || true

log "=== Auto-deploy completed successfully ==="
exit 0
