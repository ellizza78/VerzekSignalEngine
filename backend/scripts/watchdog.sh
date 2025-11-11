#!/usr/bin/env bash
#
# Watchdog script for Verzek AutoTrader API
# Monitors /api/health endpoint and auto-restarts on failure
#

set -e

# Configuration
HEALTH_URL="${1:-https://api.verzekinnovative.com/api/health}"
LOG_FILE="/root/api_server/logs/watchdog.log"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN}"
ADMIN_CHAT_ID="${ADMIN_CHAT_ID}"
SERVICE_NAME="verzek_api.service"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Send Telegram alert
send_alert() {
    local message="$1"
    
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$ADMIN_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -d "chat_id=${ADMIN_CHAT_ID}" \
            -d "text=${message}" \
            -d "parse_mode=HTML" > /dev/null 2>&1
    fi
}

# Check health endpoint
check_health() {
    local response
    local http_code
    
    response=$(curl -s -w "\n%{http_code}" --max-time 10 "$HEALTH_URL" 2>&1)
    http_code=$(echo "$response" | tail -n1)
    
    if [ "$http_code" = "200" ]; then
        # Check if JSON contains "ok":true
        if echo "$response" | grep -q '"ok":true'; then
            return 0
        else
            log "❌ Health check failed: Invalid response format"
            return 1
        fi
    else
        log "❌ Health check failed: HTTP $http_code"
        return 1
    fi
}

# Main watchdog logic
main() {
    log "🔍 Watchdog started - Monitoring $HEALTH_URL"
    
    if check_health; then
        log "✅ Health check passed"
        exit 0
    else
        log "⚠️  Health check failed - Attempting to restart $SERVICE_NAME"
        
        # Restart the service
        if systemctl restart "$SERVICE_NAME"; then
            log "♻️  Service restarted successfully"
            
            # Wait 10 seconds and check again
            sleep 10
            
            if check_health; then
                log "✅ Service recovered after restart"
                send_alert "⚠️ <b>VerzekBackend Alert</b>%0A%0AService was down but automatically recovered.%0A%0AStatus: ✅ Online"
                exit 0
            else
                log "❌ Service still unhealthy after restart"
                send_alert "🚨 <b>VerzekBackend CRITICAL</b>%0A%0AService failed to recover after restart!%0A%0AStatus: ❌ Down%0A%0AAction Required: Manual intervention needed"
                exit 1
            fi
        else
            log "❌ Failed to restart service"
            send_alert "🚨 <b>VerzekBackend CRITICAL</b>%0A%0AFailed to restart service!%0A%0AStatus: ❌ Down%0A%0AAction Required: SSH into server immediately"
            exit 1
        fi
    fi
}

# Run main function
main
