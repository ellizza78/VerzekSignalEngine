#!/bin/bash

set -e

SERVER_IP="80.240.29.142"
SERVER_USER="root"

echo "📄 PAPER TRADING MODE SWITCH"
echo "============================"
echo ""
echo "This will switch back to PAPER TRADING (simulation mode)"
echo ""
read -p "Continue? (y/n): " confirmation

if [ "$confirmation" != "y" ]; then
    echo "❌ Cancelled."
    exit 1
fi

echo ""
echo "🔧 Switching to PAPER TRADING mode..."

ssh -i ~/.ssh/vultr_verzek ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
    # Backup current .env
    cp /root/VerzekBackend/.env /root/VerzekBackend/.env.backup.$(date +%Y%m%d_%H%M%S)
    
    # Update environment variables
    sed -i 's/LIVE_TRADING_ENABLED=true/LIVE_TRADING_ENABLED=false/' /root/VerzekBackend/.env
    sed -i 's/EXCHANGE_MODE=live/EXCHANGE_MODE=paper/' /root/VerzekBackend/.env
    sed -i 's/USE_TESTNET=false/USE_TESTNET=true/' /root/VerzekBackend/.env
    sed -i 's/EMERGENCY_STOP=true/EMERGENCY_STOP=false/' /root/VerzekBackend/.env
    
    # Restart worker service
    systemctl restart verzek_worker.service
    
    echo "✅ Environment variables updated"
    echo "✅ Worker service restarted"
    echo ""
    echo "Current configuration:"
    grep -E "LIVE_TRADING_ENABLED|EXCHANGE_MODE|USE_TESTNET|EMERGENCY_STOP" /root/VerzekBackend/.env
ENDSSH

echo ""
echo "📄 PAPER TRADING MODE IS NOW ACTIVE"
echo ""
echo "All trades will be simulated (no real money)"
