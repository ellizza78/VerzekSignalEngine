#!/bin/bash
# VerzekSignalEngine Health Check Script
# Monitors signal engine status and alerts if down

SERVICE_NAME="verzek-signalengine"
LOG_FILE="/root/signal_engine/logs/signal_engine.log"
ALERT_THRESHOLD=300  # 5 minutes

# Check if service is running
if ! systemctl is-active --quiet $SERVICE_NAME; then
    echo "❌ Service is not running!"
    
    # Send alert
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$ADMIN_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -d chat_id="${ADMIN_CHAT_ID}" \
            -d text="🚨 VerzekSignalEngine is DOWN! Attempting auto-restart..." \
            -d parse_mode="HTML" > /dev/null 2>&1
    fi
    
    # Attempt restart
    systemctl restart $SERVICE_NAME
    sleep 5
    
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo "✅ Service restarted successfully"
        if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$ADMIN_CHAT_ID" ]; then
            curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
                -d chat_id="${ADMIN_CHAT_ID}" \
                -d text="✅ VerzekSignalEngine auto-restart successful" \
                -d parse_mode="HTML" > /dev/null 2>&1
        fi
    else
        echo "❌ Auto-restart failed!"
        if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$ADMIN_CHAT_ID" ]; then
            curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
                -d chat_id="${ADMIN_CHAT_ID}" \
                -d text="🚨 VerzekSignalEngine auto-restart FAILED! Manual intervention required." \
                -d parse_mode="HTML" > /dev/null 2>&1
        fi
    fi
    exit 1
fi

# Check if signals are being generated (recent log activity)
if [ -f "$LOG_FILE" ]; then
    LAST_SIGNAL=$(stat -c %Y "$LOG_FILE")
    CURRENT_TIME=$(date +%s)
    TIME_DIFF=$((CURRENT_TIME - LAST_SIGNAL))
    
    if [ $TIME_DIFF -gt $ALERT_THRESHOLD ]; then
        echo "⚠️ No recent signal activity detected (${TIME_DIFF}s ago)"
        if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$ADMIN_CHAT_ID" ]; then
            curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
                -d chat_id="${ADMIN_CHAT_ID}" \
                -d text="⚠️ VerzekSignalEngine: No signals generated in the last $((TIME_DIFF/60)) minutes" \
                -d parse_mode="HTML" > /dev/null 2>&1
        fi
    else
        echo "✅ Service healthy - Last signal: $((TIME_DIFF))s ago"
    fi
fi

# Check memory usage
MEM_USAGE=$(ps aux | grep python.*main.py | grep -v grep | awk '{print $4}')
if [ -n "$MEM_USAGE" ]; then
    echo "📊 Memory usage: ${MEM_USAGE}%"
fi

exit 0
