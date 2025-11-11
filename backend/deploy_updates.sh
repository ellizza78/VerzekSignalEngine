#!/bin/bash

# Deploy VerzekAutoTrader Backend Updates to VPS
# This script updates the backend code and recreates the database schema

echo "🚀 VerzekAutoTrader Backend Deployment"
echo "======================================"

VPS_IP="80.240.29.142"
VPS_PATH="/root/VerzekBackend/backend"

echo "📦 Step 1: Copy updated files to VPS..."
scp backend/models.py root@${VPS_IP}:${VPS_PATH}/
scp backend/auth_routes.py root@${VPS_IP}:${VPS_PATH}/blueprints/
scp backend/utils/email.py root@${VPS_IP}:${VPS_PATH}/utils/
scp backend/utils/tokens.py root@${VPS_IP}:${VPS_PATH}/utils/

echo "📧 Step 2: Install resend package..."
ssh root@${VPS_IP} "cd ${VPS_PATH} && pip install resend"

echo "🗄️  Step 3: Recreate database schema..."
ssh root@${VPS_IP} "cd ${VPS_PATH} && python3 << 'PYEOF'
from db import engine, Base
from models import User, UserSettings, ExchangeAccount, Signal, Position, Payment, SafetyState, RemoteConfig

# Drop all tables
Base.metadata.drop_all(bind=engine)
print('✅ Old tables dropped')

# Create all tables with new schema
Base.metadata.create_all(bind=engine)
print('✅ New tables created with referral_code support')
PYEOF"

echo "🔄 Step 4: Restart API service..."
ssh root@${VPS_IP} "systemctl restart verzek-api"

echo "✅ Deployment complete!"
echo ""
echo "Test endpoints:"
echo "curl https://api.verzekinnovative.com/api/health"
echo "curl -X POST https://api.verzekinnovative.com/api/auth/register -H 'Content-Type: application/json' -d '{\"email\":\"test@example.com\",\"password\":\"Test123\"}'"

