#!/bin/bash
#############################################################################
# VERZEK DYNAMIC CONFIG DEPLOYMENT SCRIPT
# 
# This script implements the complete remote config system on Vultr backend
# Run this on your Vultr server as: bash VULTR_DEPLOY_DYNAMIC_CONFIG.sh
#############################################################################

set -e  # Exit on error

echo "=================================================="
echo "   VERZEK DYNAMIC CONFIG DEPLOYMENT"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

cd /root

#############################################################################
# STEP 1: Create config schema and database table
#############################################################################
echo -e "${YELLOW}[1/6] Creating remote config database schema...${NC}"

python3 << 'EOF_SCHEMA'
import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('/root/database/verzek.db')
cursor = conn.cursor()

# Create remote config table
cursor.execute("""
CREATE TABLE IF NOT EXISTS remote_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    config_version TEXT NOT NULL UNIQUE,
    config_data TEXT NOT NULL,
    active INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
)
""")

# Create default config
default_config = {
    "version": "1.1.3",
    "configVersion": "1.0.0",
    "appVersionMin": "1.1.0",
    "bundleVersion": "1.1.3",
    "forceUpdate": False,
    "updateUrl": "https://verzek-auto-trader.replit.app/downloads/verzek-latest.apk",
    "playStoreUrl": "https://play.google.com/store/apps/details?id=com.verzek.autotrader",
    "featureFlags": {
        "autoTrade": True,
        "realtimeSignals": True,
        "emailVerification": False,
        "telegramIntegration": True,
        "multiExchange": True,
        "dcaEngine": True,
        "aiAssistant": False,
        "pushNotifications": False,
        "websocketPrices": False,
        "socialTrading": False,
        "advancedCharting": False
    },
    "serviceEndpoints": {
        "apiBaseUrl": "https://verzek-auto-trader.replit.app",
        "websocketUrl": "wss://verzek-auto-trader.replit.app/ws",
        "signalsUrl": "https://verzek-auto-trader.replit.app/api/signals",
        "pricesFeedUrl": "https://verzek-auto-trader.replit.app/api/prices/realtime"
    },
    "uiMessages": {
        "welcome": "Welcome to Verzek AutoTrader!",
        "maintenance": False,
        "maintenanceMessage": "",
        "banner": "",
        "announcement": ""
    },
    "tradingLimits": {
        "maxPositionsPerUser": 50,
        "minOrderSize": 10,
        "maxOrderSize": 10000,
        "maxLeverage": 20,
        "defaultLeverage": 5
    },
    "subscriptionPlans": {
        "FREE": {
            "maxPositions": 3,
            "maxExchanges": 1,
            "features": ["basicSignals", "manualTrade"]
        },
        "TRIAL": {
            "maxPositions": 10,
            "maxExchanges": 2,
            "features": ["basicSignals", "autoTrade", "dcaEngine"]
        },
        "VIP": {
            "maxPositions": 30,
            "maxExchanges": 3,
            "features": ["premiumSignals", "autoTrade", "dcaEngine", "telegramAlerts"]
        },
        "PREMIUM": {
            "maxPositions": 50,
            "maxExchanges": 5,
            "features": ["premiumSignals", "autoTrade", "dcaEngine", "telegramAlerts", "aiAssistant", "prioritySupport"]
        }
    },
    "experiments": {},
    "rollout": {
        "enabledForAll": True,
        "betaUsers": []
    }
}

# Check if default config exists
cursor.execute("SELECT id FROM remote_config WHERE config_version = ?", ("1.0.0",))
if not cursor.fetchone():
    cursor.execute("""
        INSERT INTO remote_config (config_version, config_data, active)
        VALUES (?, ?, 1)
    """, ("1.0.0", json.dumps(default_config)))
    print("✅ Created default config version 1.0.0")
else:
    print("✅ Default config already exists")

conn.commit()
conn.close()
print("✅ Remote config database schema created")
EOF_SCHEMA

#############################################################################
# STEP 2: Create remote config endpoint in Flask API
#############################################################################
echo -e "${YELLOW}[2/6] Adding remote config endpoint to API...${NC}"

# Backup original API file
cp api_server.py api_server.py.backup_$(date +%s)

# Add remote config endpoint
python3 << 'EOF_API'
import re

with open('api_server.py', 'r') as f:
    content = f.read()

# Check if endpoint already exists
if '/api/app-config' in content:
    print("✅ Remote config endpoint already exists")
else:
    # Find the position to insert (before if __name__ == '__main__')
    insertion_point = content.find("if __name__ == '__main__':")
    
    if insertion_point == -1:
        print("❌ Could not find insertion point")
        exit(1)
    
    # Create the new endpoint
    new_endpoint = '''
#############################################################################
# REMOTE CONFIG API - Dynamic App Configuration
#############################################################################

@app.route('/api/app-config', methods=['GET'])
def get_app_config():
    """
    Serve dynamic app configuration for mobile app
    This allows updating app behavior without rebuilding APK
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get active config
        cursor.execute("""
            SELECT config_data, config_version, updated_at
            FROM remote_config
            WHERE active = 1
            ORDER BY updated_at DESC
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            config_data = json.loads(result[0])
            
            # Add metadata
            config_data['_metadata'] = {
                'configVersion': result[1],
                'lastUpdated': result[2],
                'serverTime': datetime.now(timezone.utc).isoformat()
            }
            
            # Cache for 5 minutes
            response = jsonify(config_data)
            response.headers['Cache-Control'] = 'public, max-age=300'
            response.headers['ETag'] = result[1]
            return response, 200
        else:
            # Return minimal fallback config
            fallback = {
                "version": "1.1.3",
                "appVersionMin": "1.1.0",
                "forceUpdate": False,
                "featureFlags": {"autoTrade": True},
                "serviceEndpoints": {"apiBaseUrl": "https://verzek-auto-trader.replit.app"}
            }
            return jsonify(fallback), 200
            
    except Exception as e:
        logger.error(f"Error fetching remote config: {e}")
        return jsonify({"error": "Config unavailable"}), 500

@app.route('/api/admin/config', methods=['GET', 'POST'])
@require_auth
def manage_config():
    """
    Admin endpoint to view/update remote config
    Requires authentication
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if request.method == 'GET':
            # Get all configs
            cursor.execute("""
                SELECT id, config_version, config_data, active, created_at, updated_at
                FROM remote_config
                ORDER BY created_at DESC
            """)
            
            configs = []
            for row in cursor.fetchall():
                configs.append({
                    'id': row[0],
                    'version': row[1],
                    'data': json.loads(row[2]),
                    'active': bool(row[3]),
                    'created_at': row[4],
                    'updated_at': row[5]
                })
            
            conn.close()
            return jsonify({'configs': configs}), 200
            
        elif request.method == 'POST':
            data = request.get_json()
            new_version = data.get('config_version')
            config_data = data.get('config_data')
            set_active = data.get('set_active', True)
            
            if not new_version or not config_data:
                return jsonify({'error': 'Missing config_version or config_data'}), 400
            
            # Deactivate all configs if setting this as active
            if set_active:
                cursor.execute("UPDATE remote_config SET active = 0")
            
            # Insert new config
            cursor.execute("""
                INSERT INTO remote_config (config_version, config_data, active)
                VALUES (?, ?, ?)
            """, (new_version, json.dumps(config_data), 1 if set_active else 0))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Created new config version: {new_version}")
            return jsonify({'success': True, 'version': new_version}), 201
            
    except Exception as e:
        logger.error(f"Error managing config: {e}")
        return jsonify({'error': str(e)}), 500

'''
    
    # Insert the new endpoint
    new_content = content[:insertion_point] + new_endpoint + '\n' + content[insertion_point:]
    
    with open('api_server.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Added remote config endpoints to API")

EOF_API

#############################################################################
# STEP 3: Create admin CLI tool for config management
#############################################################################
echo -e "${YELLOW}[3/6] Creating admin config management tool...${NC}"

cat > /root/manage_config.py << 'EOF_MANAGE'
#!/usr/bin/env python3
"""
Verzek Remote Config Management Tool
Usage: python3 manage_config.py [action]
Actions: view, activate <version>, update <json_file>
"""

import sqlite3
import json
import sys
from datetime import datetime

DB_PATH = '/root/database/verzek.db'

def get_connection():
    return sqlite3.connect(DB_PATH)

def view_configs():
    """View all configs"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, config_version, active, created_at, updated_at
        FROM remote_config
        ORDER BY created_at DESC
    """)
    
    print("\n" + "="*80)
    print("REMOTE CONFIG VERSIONS")
    print("="*80)
    
    for row in cursor.fetchall():
        status = "✓ ACTIVE" if row[2] == 1 else "  "
        print(f"{status} v{row[1]} (ID: {row[0]}) - Created: {row[3]}, Updated: {row[4]}")
    
    print("="*80 + "\n")
    conn.close()

def view_active_config():
    """View active config details"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT config_data, config_version
        FROM remote_config
        WHERE active = 1
        ORDER BY updated_at DESC
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    if result:
        print(f"\n{'='*80}")
        print(f"ACTIVE CONFIG: v{result[1]}")
        print('='*80)
        print(json.dumps(json.loads(result[0]), indent=2))
        print('='*80 + "\n")
    else:
        print("❌ No active config found")
    
    conn.close()

def update_feature_flag(flag_name, enabled):
    """Toggle feature flag"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get active config
    cursor.execute("""
        SELECT id, config_data, config_version
        FROM remote_config
        WHERE active = 1
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    if not result:
        print("❌ No active config found")
        conn.close()
        return
    
    config_id, config_data_str, version = result
    config_data = json.loads(config_data_str)
    
    # Update feature flag
    if 'featureFlags' not in config_data:
        config_data['featureFlags'] = {}
    
    config_data['featureFlags'][flag_name] = enabled
    
    # Update in database
    cursor.execute("""
        UPDATE remote_config
        SET config_data = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (json.dumps(config_data), config_id))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Feature flag '{flag_name}' set to {enabled}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 manage_config.py [view|feature <name> <on|off>]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'view':
        view_configs()
        view_active_config()
    elif action == 'feature' and len(sys.argv) >= 4:
        flag_name = sys.argv[2]
        enabled = sys.argv[3].lower() in ['on', 'true', '1', 'yes']
        update_feature_flag(flag_name, enabled)
    else:
        print("Invalid action")
        sys.exit(1)
EOF_MANAGE

chmod +x /root/manage_config.py
echo "✅ Created config management tool at /root/manage_config.py"

#############################################################################
# STEP 4: Restart Flask API
#############################################################################
echo -e "${YELLOW}[4/6] Restarting Flask API...${NC}"

pkill -9 -f api_server.py || true
sleep 3
nohup python3 /root/api_server.py > /tmp/api_dynamic_config.log 2>&1 &
sleep 5

echo "✅ Flask API restarted"

#############################################################################
# STEP 5: Test remote config endpoint
#############################################################################
echo -e "${YELLOW}[5/6] Testing remote config endpoint...${NC}"

curl -s http://localhost:5000/api/app-config | python3 -m json.tool | head -30

#############################################################################
# STEP 6: Create update notification system (WebSocket)
#############################################################################
echo -e "${YELLOW}[6/6] Creating config update notification system...${NC}"

cat > /root/config_notifier.py << 'EOF_NOTIFIER'
#!/usr/bin/env python3
"""
Config Update Notifier
Monitors config changes and sends notifications
"""

import sqlite3
import time
import requests
from datetime import datetime

DB_PATH = '/root/database/verzek.db'
CHECK_INTERVAL = 60  # Check every 60 seconds

def get_active_config_version():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT config_version FROM remote_config WHERE active = 1 LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def notify_config_update(old_version, new_version):
    """Send notification about config update"""
    print(f"📢 Config updated: {old_version} → {new_version}")
    # In future: Send WebSocket notification to connected clients
    # In future: Send Telegram notification to admins

if __name__ == '__main__':
    print("🚀 Config Notifier started")
    last_version = get_active_config_version()
    
    while True:
        try:
            current_version = get_active_config_version()
            if current_version != last_version:
                notify_config_update(last_version, current_version)
                last_version = current_version
            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(CHECK_INTERVAL)
EOF_NOTIFIER

chmod +x /root/config_notifier.py
echo "✅ Created config notifier (run manually: python3 config_notifier.py)"

#############################################################################
# DEPLOYMENT COMPLETE
#############################################################################
echo ""
echo -e "${GREEN}=================================================="
echo "   ✅ DEPLOYMENT COMPLETE!"
echo "==================================================${NC}"
echo ""
echo "📋 What was deployed:"
echo "  ✓ Remote config database table"
echo "  ✓ /api/app-config endpoint (public)"
echo "  ✓ /api/admin/config endpoint (admin only)"
echo "  ✓ Config management CLI tool"
echo "  ✓ Config update notifier"
echo ""
echo "🔗 Test endpoint:"
echo "  curl http://localhost:5000/api/app-config"
echo ""
echo "🛠️  Manage config:"
echo "  python3 /root/manage_config.py view"
echo "  python3 /root/manage_config.py feature autoTrade on"
echo ""
echo "📱 Mobile app will fetch config from:"
echo "  https://verzek-auto-trader.replit.app/api/app-config"
echo ""
echo -e "${GREEN}All systems ready! 🚀${NC}"
