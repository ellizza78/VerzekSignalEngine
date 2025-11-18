#!/bin/bash

set -e

SERVER_IP="80.240.29.142"
SERVER_USER="root"

echo "🗑️  CLEAR REGISTRATION DATA FROM VULTR PRODUCTION"
echo "======================================================================"
echo ""
echo "⚠️  WARNING: This will DELETE ALL user registration data!"
echo ""
echo "This includes:"
echo "  - All user accounts"
echo "  - Email verification tokens"
echo "  - Password reset tokens"
echo "  - User settings"
echo "  - Exchange account connections"
echo "  - User positions"
echo "  - Device tokens"
echo "  - Payment records"
echo ""
echo "⚠️  House signals and positions will be PRESERVED"
echo ""
read -p "Are you sure you want to clear ALL registration data? Type 'CLEAR ALL DATA' to confirm: " confirmation

if [ "$confirmation" != "CLEAR ALL DATA" ]; then
    echo "❌ Cancelled. No data was deleted."
    exit 1
fi

echo ""
echo "🗑️  Clearing registration data from Vultr database..."

ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_IP} << 'ENDSSH'
    psql -U verzek_user -d verzek_db << 'EOSQL'
        -- Count current records
        SELECT 'Current counts:' as info;
        SELECT 'Users' as table_name, COUNT(*) as count FROM users
        UNION ALL
        SELECT 'Verification Tokens', COUNT(*) FROM verification_tokens
        UNION ALL
        SELECT 'User Settings', COUNT(*) FROM user_settings
        UNION ALL
        SELECT 'Exchange Accounts', COUNT(*) FROM exchange_accounts
        UNION ALL
        SELECT 'Positions', COUNT(*) FROM positions
        UNION ALL
        SELECT 'Position Targets', COUNT(*) FROM position_targets
        UNION ALL
        SELECT 'Device Tokens', COUNT(*) FROM device_tokens
        UNION ALL
        SELECT 'Payments', COUNT(*) FROM payments
        UNION ALL
        SELECT 'Trade Logs', COUNT(*) FROM trade_logs;
        
        -- Delete all user-related data (CASCADE will handle related tables)
        DELETE FROM users;
        DELETE FROM verification_tokens;
        DELETE FROM payments;
        DELETE FROM trade_logs;
        
        -- Reset sequences to start fresh
        ALTER SEQUENCE users_id_seq RESTART WITH 1;
        ALTER SEQUENCE payments_id_seq RESTART WITH 1;
        ALTER SEQUENCE verification_tokens_id_seq RESTART WITH 1;
        ALTER SEQUENCE positions_id_seq RESTART WITH 1;
        
        SELECT '✅ All registration data cleared!' as result;
        
        -- Verify deletion
        SELECT 'Final counts:' as info;
        SELECT 'Users' as table_name, COUNT(*) as count FROM users
        UNION ALL
        SELECT 'Verification Tokens', COUNT(*) FROM verification_tokens
        UNION ALL
        SELECT 'User Settings', COUNT(*) FROM user_settings
        UNION ALL
        SELECT 'Exchange Accounts', COUNT(*) FROM exchange_accounts
        UNION ALL
        SELECT 'Positions', COUNT(*) FROM positions
        UNION ALL
        SELECT 'Device Tokens', COUNT(*) FROM device_tokens
        UNION ALL
        SELECT 'Payments', COUNT(*) FROM payments
        UNION ALL
        SELECT 'Trade Logs', COUNT(*) FROM trade_logs;
        
        -- House signals are preserved
        SELECT 'House Signals (preserved)' as table_name, COUNT(*) as count FROM house_signals
        UNION ALL
        SELECT 'House Signal Positions (preserved)', COUNT(*) FROM house_signal_positions;
EOSQL
ENDSSH

echo ""
echo "✅ Registration data cleared successfully from Vultr!"
echo ""
echo "📊 Summary:"
echo "  ✅ All user accounts deleted"
echo "  ✅ All verification tokens deleted"
echo "  ✅ All user settings deleted"
echo "  ✅ All exchange accounts deleted"
echo "  ✅ All positions deleted"
echo "  ✅ All payments deleted"
echo "  ✅ All trade logs deleted"
echo "  ✅ Sequences reset to start from ID 1"
echo ""
echo "✅ House signals and positions preserved (not deleted)"
echo ""
echo "🎯 Ready for fresh registrations!"
