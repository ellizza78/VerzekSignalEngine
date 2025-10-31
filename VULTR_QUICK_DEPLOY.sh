#!/bin/bash
set -e
cd /root

echo "🚀 Verzek Dynamic Config - Quick Deploy"

python3 << 'PYEOF'
import sqlite3
import json

# 1. Create database table
conn = sqlite3.connect('/root/database/verzek.db')
cursor = conn.cursor()
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

# 2. Insert default config
config = {
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
    }
}

cursor.execute("SELECT id FROM remote_config WHERE config_version = ?", ("1.0.0",))
if not cursor.fetchone():
    cursor.execute("INSERT INTO remote_config (config_version, config_data, active) VALUES (?, ?, 1)", ("1.0.0", json.dumps(config)))
    print("✅ Created config v1.0.0")
else:
    print("✅ Config already exists")

conn.commit()
conn.close()
PYEOF

# 3. Create standalone config API file
cat > /root/config_api.py << 'APIEOF'
from flask import Flask, jsonify
import sqlite3
import json
from datetime import datetime, timezone

app = Flask(__name__)

def get_db():
    return sqlite3.connect('/root/database/verzek.db')

@app.route('/api/app-config', methods=['GET'])
def get_config():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT config_data, config_version, updated_at FROM remote_config WHERE active = 1 LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        
        if result:
            config = json.loads(result[0])
            config['_metadata'] = {
                'configVersion': result[1],
                'lastUpdated': result[2],
                'serverTime': datetime.now(timezone.utc).isoformat()
            }
            response = jsonify(config)
            response.headers['Cache-Control'] = 'public, max-age=300'
            return response, 200
        return jsonify({"error": "No config"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
APIEOF

# 4. Create CLI tool
cat > /root/manage_config.py << 'CLIEOF'
#!/usr/bin/env python3
import sqlite3, json, sys

DB = '/root/database/verzek.db'

def view():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT config_data, config_version FROM remote_config WHERE active = 1 LIMIT 1")
    result = cursor.fetchone()
    if result:
        print(f"\n{'='*80}\nACTIVE CONFIG: v{result[1]}\n{'='*80}")
        print(json.dumps(json.loads(result[0]), indent=2))
    conn.close()

def feature(name, enabled):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, config_data FROM remote_config WHERE active = 1 LIMIT 1")
    result = cursor.fetchone()
    if result:
        config = json.loads(result[1])
        config['featureFlags'][name] = enabled
        cursor.execute("UPDATE remote_config SET config_data = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (json.dumps(config), result[0]))
        conn.commit()
        print(f"✅ {name} = {enabled}")
    conn.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 manage_config.py [view|feature <name> <on|off>]")
    elif sys.argv[1] == 'view':
        view()
    elif sys.argv[1] == 'feature' and len(sys.argv) >= 4:
        feature(sys.argv[2], sys.argv[3].lower() in ['on', 'true', '1', 'yes'])
CLIEOF

chmod +x /root/manage_config.py

# 5. Start config API service
pkill -9 -f config_api.py 2>/dev/null || true
sleep 2
nohup python3 /root/config_api.py > /tmp/config_api.log 2>&1 &
sleep 3

echo ""
echo "✅ DEPLOYED!"
echo ""
echo "🔗 Config endpoint: http://localhost:5001/api/app-config"
echo "🛠️  Manage: python3 /root/manage_config.py view"
echo ""
curl -s http://localhost:5001/api/app-config | python3 -m json.tool | head -20
