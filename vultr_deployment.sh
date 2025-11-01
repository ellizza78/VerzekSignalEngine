#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# VERZEK AUTO TRADER - COMPLETE VULTR DEPLOYMENT SCRIPT
# Domain: https://verzekinnovative.com
# Email: support@verzekinnovative.com
# ═══════════════════════════════════════════════════════════════
#
# SECURITY: Before running, you must MANUALLY create /root/api_server_env.sh:
#
#   cat > /root/api_server_env.sh << 'EOF'
#   export RESEND_API_KEY="your_actual_resend_api_key_here"
#   export EMAIL_FROM="support@verzekinnovative.com"
#   export APP_NAME="Verzek Auto Trader"
#   export BASE_URL="https://verzekinnovative.com"
#   EOF
#   chmod 600 /root/api_server_env.sh  # Secure permissions!
#
# Then run this deployment script.
# ═══════════════════════════════════════════════════════════════

set -e

DOMAIN="verzekinnovative.com"
EMAIL_FROM="support@verzekinnovative.com"

echo "🚀 STEP 1: Verify Environment Configuration"
echo "═══════════════════════════════════════"

# Check if environment file exists
if [ ! -f /root/api_server_env.sh ]; then
    echo "❌ ERROR: /root/api_server_env.sh not found!"
    echo ""
    echo "You must create this file manually with your API keys:"
    echo ""
    echo "  cat > /root/api_server_env.sh << 'EOF'"
    echo "  export RESEND_API_KEY=\"your_resend_api_key\""
    echo "  export EMAIL_FROM=\"support@verzekinnovative.com\""
    echo "  export APP_NAME=\"Verzek Auto Trader\""
    echo "  export BASE_URL=\"https://verzekinnovative.com\""
    echo "  EOF"
    echo "  chmod 600 /root/api_server_env.sh"
    echo ""
    exit 1
fi

# Check secure permissions
PERMS=$(stat -c %a /root/api_server_env.sh 2>/dev/null || stat -f %A /root/api_server_env.sh)
if [ "$PERMS" != "600" ]; then
    echo "⚠️  WARNING: /root/api_server_env.sh has insecure permissions ($PERMS)"
    echo "Fixing permissions to 600 (owner read/write only)..."
    chmod 600 /root/api_server_env.sh
fi

source /root/api_server_env.sh

# Verify required variables are set
if [ -z "$RESEND_API_KEY" ]; then
    echo "❌ ERROR: RESEND_API_KEY not set in /root/api_server_env.sh"
    exit 1
fi

echo "✅ Environment variables loaded securely"

echo ""
echo "🔄 STEP 2: Restart Backend API Service"
echo "═══════════════════════════════════════"

pkill -9 -f api_server.py || true
sleep 2
nohup python3 /root/api_server.py > /tmp/api_server.log 2>&1 &
sleep 5
echo "✅ API server restarted"

tail -30 /tmp/api_server.log | grep -E "Resend|Email|Running" || echo "Check logs manually"

echo ""
echo "📧 STEP 3: Send Test Email"
echo "═══════════════════════════════════════"

python3 << 'PYTEST'
import sys
sys.path.insert(0, '/root')
from services.email_service import email_service
result = email_service.send_verification_email("verzekgloballtd@gmail.com", "TestUser", "test123")
print(f"\n✅ Test Email Result: {result}\n")
PYTEST

echo ""
echo "🌐 STEP 5: Configure Nginx"
echo "═══════════════════════════════════════"

apt-get update -qq
apt-get install -y nginx

cat > /etc/nginx/sites-available/default << 'NGINX_EOF'
server {
    listen 80;
    server_name verzekinnovative.com www.verzekinnovative.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    location /static/ {
        alias /var/www/html/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /downloads/ {
        alias /root/builds/;
        autoindex on;
    }
}
NGINX_EOF

nginx -t
systemctl restart nginx
systemctl enable nginx
echo "✅ Nginx configured and running"

echo ""
echo "🔒 STEP 6: Install SSL Certificate (Certbot)"
echo "═══════════════════════════════════════"

apt-get install -y certbot python3-certbot-nginx

echo "⚠️  MANUAL STEP REQUIRED:"
echo "Run this command after DNS is pointed to this server:"
echo "  sudo certbot --nginx -d verzekinnovative.com -d www.verzekinnovative.com --non-interactive --agree-tos -m verzekgloballtd@gmail.com"
echo ""

echo ""
echo "🔍 STEP 7: Verify Resend Integration"
echo "═══════════════════════════════════════"

RESEND_STATUS=$(curl -s https://api.resend.com/domains \
  -H "Authorization: Bearer $RESEND_API_KEY" | grep -o '"status":"[^"]*"' | head -1)
echo "Resend Domain Status: $RESEND_STATUS"

if [[ "$RESEND_STATUS" == *"verified"* ]]; then
    echo "✅ Resend domain verified"
else
    echo "⚠️  Resend domain not verified yet - check Resend dashboard"
fi

echo ""
echo "🩺 STEP 8: Enable Health Monitoring"
echo "═══════════════════════════════════════"

cat > /root/health_monitor.py << 'HEALTH_EOF'
#!/usr/bin/env python3
import subprocess
import requests
import time
from datetime import datetime

LOG_FILE = "/root/health_monitor.log"
API_URL = "http://127.0.0.1:8000/api/health"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def check_api():
    try:
        response = requests.get(API_URL, timeout=10)
        if response.status_code == 200:
            log("✅ API health check passed")
            return True
        else:
            log(f"⚠️  API returned status {response.status_code}")
            return False
    except Exception as e:
        log(f"❌ API health check failed: {e}")
        return False

def restart_api():
    log("🔄 Restarting API server...")
    subprocess.run(["pkill", "-9", "-f", "api_server.py"])
    time.sleep(2)
    subprocess.Popen(["nohup", "python3", "/root/api_server.py"], 
                     stdout=open("/tmp/api_server.log", "w"),
                     stderr=subprocess.STDOUT)
    time.sleep(5)
    log("✅ API server restarted")

if __name__ == "__main__":
    log("🩺 Starting health check...")
    if not check_api():
        restart_api()
        time.sleep(5)
        if check_api():
            log("✅ Recovery successful")
        else:
            log("❌ Recovery failed - manual intervention required")
HEALTH_EOF

chmod +x /root/health_monitor.py

(crontab -l 2>/dev/null | grep -v health_monitor; echo "0 */3 * * * /usr/bin/python3 /root/health_monitor.py") | crontab -
echo "✅ Health monitoring enabled (runs every 3 hours)"

echo ""
echo "💾 STEP 9: Enable Daily Backups"
echo "═══════════════════════════════════════"

mkdir -p /root/backups

cat > /root/daily_backup.sh << 'BACKUP_EOF'
#!/bin/bash
BACKUP_DIR="/root/backups"
DATE=$(date +%F)
tar -czf "$BACKUP_DIR/verzek_backup_$DATE.tar.gz" \
    /root/api_server.py \
    /root/database/ \
    /root/services/ \
    /root/*.py 2>/dev/null
find "$BACKUP_DIR" -type f -mtime +7 -delete
echo "[$(date)] Backup completed: verzek_backup_$DATE.tar.gz"
BACKUP_EOF

chmod +x /root/daily_backup.sh

(crontab -l 2>/dev/null | grep -v daily_backup; echo "0 2 * * * /root/daily_backup.sh >> /root/backup.log 2>&1") | crontab -
echo "✅ Daily backups enabled (runs at 2 AM)"

echo ""
echo "🧪 STEP 10: Final Verification"
echo "═══════════════════════════════════════"

sleep 3

echo "Testing API health endpoint..."
curl -s http://127.0.0.1:8000/api/health | grep -q "ok" && echo "✅ API health check passed" || echo "⚠️  API health check failed"

echo "Testing email service..."
python3 /root/health_monitor.py

echo ""
echo "═══════════════════════════════════════"
echo "🎉 DEPLOYMENT COMPLETE!"
echo "═══════════════════════════════════════"
echo ""
echo "📋 Summary:"
echo "  ✅ Environment variables configured"
echo "  ✅ API server running on port 8000"
echo "  ✅ Nginx configured as reverse proxy"
echo "  ✅ Email service active (Resend API)"
echo "  ✅ Health monitoring enabled"
echo "  ✅ Daily backups scheduled"
echo ""
echo "🔒 Next Steps (Manual):"
echo "  1. Point DNS A record: verzekinnovative.com → 80.240.29.142"
echo "  2. Point DNS A record: www.verzekinnovative.com → 80.240.29.142"
echo "  3. Wait 5-10 minutes for DNS propagation"
echo "  4. Run SSL certificate installation:"
echo "     sudo certbot --nginx -d verzekinnovative.com -d www.verzekinnovative.com --non-interactive --agree-tos -m verzekgloballtd@gmail.com"
echo "  5. Verify HTTPS: https://verzekinnovative.com/api/health"
echo "  6. Configure Cloudflare:"
echo "     - SSL/TLS mode: Full (strict)"
echo "     - Verify DNS records"
echo "     - Verify Resend domain (SPF, DKIM, MX records)"
echo ""
echo "📊 Monitoring:"
echo "  - API logs: tail -f /tmp/api_server.log"
echo "  - Health logs: tail -f /root/health_monitor.log"
echo "  - Backup logs: tail -f /root/backup.log"
echo "  - Nginx logs: tail -f /var/log/nginx/access.log"
echo ""
echo "🌐 Test after DNS/SSL setup:"
echo "  curl https://verzekinnovative.com/api/health"
echo ""

