#!/usr/bin/env bash
#
# Setup Watchdog Cron Job
# Runs health check every 5 minutes and auto-restarts on failure
#

set -e

CRON_FILE="/etc/cron.d/verzek_watchdog"
SCRIPT_PATH="/root/api_server/scripts/watchdog.sh"

echo "🔧 Setting up Watchdog cron job..."

# Create cron file
cat > "$CRON_FILE" << 'EOF'
# Verzek AutoTrader Watchdog
# Runs every 5 minutes to check API health
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

*/5 * * * * root bash /root/api_server/scripts/watchdog.sh >> /root/api_server/logs/watchdog.log 2>&1
EOF

# Set permissions
chmod 644 "$CRON_FILE"

# Reload cron
systemctl restart cron

echo "✅ Watchdog cron job installed successfully"
echo "📋 Health checks will run every 5 minutes"
echo "📁 Logs: /root/api_server/logs/watchdog.log"
