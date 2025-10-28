#!/bin/bash
LOG_FILE="/var/log/verzek_watchdog.log"
ADMIN_CHAT_ID="572038606"
TELEGRAM_BOT_TOKEN="8351047055:AAEqBFx5g0NJpEvUOCP_DCPD0VsGpEAjvRE"
EMAIL="support@vezekinnovative.com"

send_telegram_alert() {
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d chat_id="$ADMIN_CHAT_ID" \
        -d text="⚠️ Watchdog Alert: Service $1 was restarted on $(hostname) at $(date '+%Y-%m-%d %H:%M:%S')" > /dev/null
}

send_email_alert() {
    echo "Verzek Watchdog restarted $1 on $(date)" | mail -s "⚠️ Verzek Watchdog Alert" "$EMAIL" 2>/dev/null || true
}

while true; do
    for svc in verzekbot verzekapi; do
        if ! systemctl is-active --quiet "$svc"; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') ⚠️ Service $svc is down. Restarting..." >> "$LOG_FILE"
            systemctl restart "$svc"
            send_telegram_alert "$svc"
            send_email_alert "$svc"
            echo "$(date '+%Y-%m-%d %H:%M:%S') ✅ Service $svc restarted" >> "$LOG_FILE"
        fi
    done
    sleep 120
done
