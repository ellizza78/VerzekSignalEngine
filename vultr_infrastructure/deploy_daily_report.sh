#!/bin/bash

set -e

echo "📊 Deploying Daily Report System to Vultr Production..."

SERVER_IP="80.240.29.142"
SERVER_USER="root"

echo "📤 Uploading systemd files..."
scp -i ~/.ssh/vultr_verzek \
    vultr_infrastructure/verzek_daily_report.service \
    vultr_infrastructure/verzek_daily_report.timer \
    ${SERVER_USER}@${SERVER_IP}:/tmp/

echo "🔧 Installing systemd units..."
ssh -i ~/.ssh/vultr_verzek ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
    # Move service files
    mv /tmp/verzek_daily_report.service /etc/systemd/system/
    mv /tmp/verzek_daily_report.timer /etc/systemd/system/
    
    # Set permissions
    chmod 644 /etc/systemd/system/verzek_daily_report.service
    chmod 644 /etc/systemd/system/verzek_daily_report.timer
    
    # Reload systemd
    systemctl daemon-reload
    
    # Enable and start timer
    systemctl enable verzek_daily_report.timer
    systemctl start verzek_daily_report.timer
    
    # Check status
    echo "✅ Timer Status:"
    systemctl status verzek_daily_report.timer --no-pager
    
    echo ""
    echo "📅 Next scheduled run:"
    systemctl list-timers verzek_daily_report.timer --no-pager
ENDSSH

echo ""
echo "✅ Daily Report System Deployed Successfully!"
echo "📅 Reports will run daily at 9:00 AM UTC"
echo ""
echo "Manual Commands:"
echo "  Run now:        systemctl start verzek_daily_report.service"
echo "  Check status:   systemctl status verzek_daily_report.timer"
echo "  View next run:  systemctl list-timers verzek_daily_report.timer"
echo "  Check logs:     journalctl -u verzek_daily_report.service -f"
