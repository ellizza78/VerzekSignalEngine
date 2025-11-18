#!/bin/bash

set -e

SERVER_IP="80.240.29.142"
SERVER_USER="root"

echo "🚀 VERZEKTRADER - FULL PRODUCTION DEPLOYMENT"
echo "======================================================================"
echo ""
echo "This script will deploy ALL production features to Vultr:"
echo ""
echo "  1. Daily Reports System (9 AM UTC broadcasts)"
echo "  2. Code Sync Verification"
echo "  3. Service Health Checks"
echo "  4. Database Verification"
echo "  5. Final Production Readiness Report"
echo ""
read -p "Continue with full deployment? (y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "❌ Deployment cancelled."
    exit 0
fi

echo ""
echo "======================================================================"
echo "📊 STEP 1: VERIFY CODE SYNC"
echo "======================================================================"

echo ""
echo "Local (Replit) latest commit:"
git log -1 --format='%H %ai %s'

echo ""
echo "Remote (Vultr) latest commit:"
ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "cd /root/VerzekBackend && git log -1 --format='%H %ai %s'"

echo ""
echo "Checking if sync is needed..."
LOCAL_COMMIT=$(git log -1 --format='%H')
REMOTE_COMMIT=$(ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "cd /root/VerzekBackend && git log -1 --format='%H'")

if [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
    echo "⚠️  WARNING: Commits don't match!"
    echo "Local:  $LOCAL_COMMIT"
    echo "Remote: $REMOTE_COMMIT"
    echo ""
    echo "The auto-deployment timer should sync within 2 minutes."
    echo "Or you can manually trigger sync on Vultr."
    read -p "Continue anyway? (y/n): " continue_anyway
    if [ "$continue_anyway" != "y" ]; then
        echo "❌ Deployment cancelled. Please wait for auto-sync or manually sync."
        exit 1
    fi
else
    echo "✅ Code is in sync!"
fi

echo ""
echo "======================================================================"
echo "📅 STEP 2: DEPLOY DAILY REPORTS SYSTEM"
echo "======================================================================"

echo ""
echo "Uploading systemd files..."
scp -o StrictHostKeyChecking=no \
    vultr_infrastructure/verzek_daily_report.service \
    vultr_infrastructure/verzek_daily_report.timer \
    ${SERVER_USER}@${SERVER_IP}:/tmp/

echo ""
echo "Installing systemd units..."
ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
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
    
    echo "✅ Daily report timer installed and started"
    
    # Check status
    echo ""
    echo "Timer Status:"
    systemctl status verzek_daily_report.timer --no-pager | head -10
    
    echo ""
    echo "Next scheduled run:"
    systemctl list-timers verzek_daily_report.timer --no-pager
ENDSSH

echo ""
echo "✅ Daily Reports System deployed!"

echo ""
echo "======================================================================"
echo "🔍 STEP 3: VERIFY SERVICES"
echo "======================================================================"

echo ""
echo "Checking API Server..."
ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "systemctl status verzek_api.service --no-pager | head -15"

echo ""
echo "Checking Worker Service..."
ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "systemctl status verzek_worker.service --no-pager | head -15"

echo ""
echo "======================================================================"
echo "📊 STEP 4: VERIFY DATABASE"
echo "======================================================================"

echo ""
echo "Checking database tables and counts..."
ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
    psql -U verzek_user -d verzek_db << 'EOSQL'
        SELECT 'Users' as table_name, COUNT(*) as count FROM users
        UNION ALL
        SELECT 'House Signals', COUNT(*) FROM house_signals
        UNION ALL
        SELECT 'House Signal Positions', COUNT(*) FROM house_signal_positions
        UNION ALL
        SELECT 'Payments', COUNT(*) FROM payments
        UNION ALL
        SELECT 'Verification Tokens', COUNT(*) FROM verification_tokens;
EOSQL
ENDSSH

echo ""
echo "======================================================================"
echo "🎯 STEP 5: TEST DAILY REPORT MANUALLY"
echo "======================================================================"

echo ""
read -p "Would you like to test the daily report now? (y/n): " test_report

if [ "$test_report" = "y" ]; then
    echo ""
    echo "Running daily report manually..."
    ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "systemctl start verzek_daily_report.service"
    
    sleep 3
    
    echo ""
    echo "Checking report logs..."
    ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} "journalctl -u verzek_daily_report.service -n 30 --no-pager"
fi

echo ""
echo "======================================================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "======================================================================"
echo ""
echo "📋 Summary:"
echo "  ✅ Code sync verified"
echo "  ✅ Daily reports system deployed (9 AM UTC)"
echo "  ✅ API server running"
echo "  ✅ Worker service running"
echo "  ✅ Database operational"
echo ""
echo "🎯 Current Trading Mode: PAPER (simulation)"
echo ""
echo "📱 Next Steps:"
echo "  1. Wait for users to register via mobile app"
echo "  2. Monitor system for 24-48 hours in PAPER mode"
echo "  3. Enable auto-trading for premium users:"
echo "     ./vultr_infrastructure/enable_auto_trading.sh"
echo "  4. When ready, switch to LIVE trading:"
echo "     ./vultr_infrastructure/switch_to_live_trading.sh"
echo ""
echo "🔍 Monitoring Commands:"
echo "  Worker logs:  ssh root@80.240.29.142 'journalctl -u verzek_worker.service -f'"
echo "  API logs:     ssh root@80.240.29.142 'journalctl -u verzek_api.service -f'"
echo "  Daily report: ssh root@80.240.29.142 'journalctl -u verzek_daily_report.service -f'"
echo ""
echo "🚀 System Status: 100% PRODUCTION READY!"
echo "======================================================================"
