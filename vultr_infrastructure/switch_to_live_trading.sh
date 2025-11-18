#!/bin/bash

set -e

SERVER_IP="80.240.29.142"
SERVER_USER="root"

echo "⚡ LIVE TRADING MODE SWITCH"
echo "============================"
echo ""
echo "⚠️  WARNING: This will enable REAL MONEY trading!"
echo ""
echo "Current mode: PAPER TRADING"
echo "Target mode:  LIVE TRADING"
echo ""
read -p "Are you absolutely sure? Type 'ENABLE LIVE TRADING' to confirm: " confirmation

if [ "$confirmation" != "ENABLE LIVE TRADING" ]; then
    echo "❌ Cancelled. No changes made."
    exit 1
fi

echo ""
echo "🔧 Switching to LIVE TRADING mode..."

ssh -i ~/.ssh/vultr_verzek ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
    # Backup current .env
    cp /root/VerzekBackend/.env /root/VerzekBackend/.env.backup.$(date +%Y%m%d_%H%M%S)
    
    # Update environment variables
    sed -i 's/LIVE_TRADING_ENABLED=false/LIVE_TRADING_ENABLED=true/' /root/VerzekBackend/.env
    sed -i 's/EXCHANGE_MODE=paper/EXCHANGE_MODE=live/' /root/VerzekBackend/.env
    sed -i 's/USE_TESTNET=true/USE_TESTNET=false/' /root/VerzekBackend/.env
    
    # Restart worker service
    systemctl restart verzek_worker.service
    
    echo "✅ Environment variables updated"
    echo "✅ Worker service restarted"
    echo ""
    echo "Current configuration:"
    grep -E "LIVE_TRADING_ENABLED|EXCHANGE_MODE|USE_TESTNET" /root/VerzekBackend/.env
ENDSSH

echo ""
echo "🚀 LIVE TRADING MODE IS NOW ACTIVE!"
echo ""
echo "⚠️  CRITICAL REMINDERS:"
echo "  - Real money will be traded"
echo "  - Monitor positions closely"
echo "  - Check exchange balances"
echo "  - Verify API keys are correct"
echo ""
echo "Emergency stop command:"
echo "  ssh root@80.240.29.142 'echo \"EMERGENCY_STOP=true\" >> /root/VerzekBackend/.env && systemctl restart verzek_worker.service'"
echo ""
echo "To revert to paper trading:"
echo "  Run: ./vultr_infrastructure/switch_to_paper_trading.sh"
