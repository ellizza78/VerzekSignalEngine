#!/bin/bash
################################################################################
# Verzek Backend Deployment Script
# Syncs latest backend code from Replit to Vultr production server
################################################################################

echo "🚀 Deploying Verzek Backend to Vultr..."
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
   echo "❌ Please run as root"
   exit 1
fi

cd /var/www/VerzekAutoTrader || { echo "❌ Project directory not found"; exit 1; }

echo "📋 Step 1: Backing up current version..."
timestamp=$(date +%Y%m%d_%H%M%S)
mkdir -p backups
tar -czf backups/backup_$timestamp.tar.gz api_server.py modules/ *.py 2>/dev/null
echo "  ✅ Backup created: backups/backup_$timestamp.tar.gz"

echo ""
echo "📋 Step 2: Stopping services..."
systemctl stop telethon-forwarder verzekapi verzekbot 2>/dev/null
pkill -f api_server.py 2>/dev/null
pkill -f telethon_forwarder.py 2>/dev/null
sleep 2
echo "  ✅ Services stopped"

echo ""
echo "📋 Step 3: Updating backend code..."
echo "  Note: telethon_forwarder.py v2.2 already deployed (heartbeat monitoring)"
echo "  Skipping forwarder update to preserve health monitoring system"

echo ""
echo "📋 Step 4: Creating requirements.txt for dependencies..."
cat > requirements_prod.txt << 'REQS_EOF'
flask==3.0.0
flask-cors==4.0.0
gunicorn==21.2.0
gevent==23.9.1
requests==2.31.0
telethon==1.32.1
python-telegram-bot==20.7
pyjwt==2.8.0
bcrypt==4.1.1
cryptography==41.0.7
schedule==1.2.0
pyotp==2.9.0
qrcode==7.4.2
pillow==10.1.0
python-dotenv==1.0.0
REQS_EOF

echo "  ✅ Requirements file created"

echo ""
echo "📋 Step 5: Installing/updating Python dependencies..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements_prod.txt
deactivate
echo "  ✅ Dependencies installed"

echo ""
echo "📋 Step 6: Restarting services..."
systemctl daemon-reload
systemctl restart telethon-forwarder
sleep 3
echo "  ✅ Telegram forwarder restarted"

# Start API server with gunicorn (production WSGI server)
echo "  Starting API server with Gunicorn..."
cd /var/www/VerzekAutoTrader
source venv/bin/activate
nohup gunicorn -w 4 -b 0.0.0.0:5000 --worker-class gevent api_server:app > api_server.log 2>&1 &
deactivate
sleep 3
echo "  ✅ API server started"

echo ""
echo "📋 Step 7: Verifying services..."

# Check if telethon forwarder is running
if systemctl is-active --quiet telethon-forwarder; then
    echo "  ✅ Telethon Forwarder: RUNNING"
else
    echo "  ⚠️  Telethon Forwarder: NOT RUNNING"
fi

# Check if API server is listening on port 5000
if ss -tuln | grep -q ":5000"; then
    echo "  ✅ API Server (Port 5000): LISTENING"
else
    echo "  ⚠️  API Server (Port 5000): NOT LISTENING"
fi

# Check heartbeat
if [ -f /tmp/forwarder_heartbeat.json ]; then
    echo "  ✅ Heartbeat monitoring: ACTIVE"
    echo "     $(cat /tmp/forwarder_heartbeat.json)"
else
    echo "  ⚠️  Heartbeat monitoring: NO FILE YET (wait 30 seconds)"
fi

echo ""
echo "✅ =========================================="
echo "✅ BACKEND DEPLOYMENT COMPLETE!"
echo "✅ =========================================="
echo ""
echo "📊 Quick Status Check:"
echo "  - Forwarder: systemctl status telethon-forwarder"
echo "  - Watchdog: systemctl status forwarder-watchdog.timer"
echo "  - API Server: curl http://localhost:5000/ping"
echo "  - Heartbeat: cat /tmp/forwarder_heartbeat.json"
echo "  - Logs: tail -f api_server.log"
echo ""
echo "🔔 Telegram forwarder has health monitoring active!"
echo "🔔 Watchdog will auto-restart if forwarder freezes!"
echo ""
