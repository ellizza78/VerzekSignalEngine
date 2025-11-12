# VerzekAutoTrader - Complete Deployment Guide
**Date:** November 12, 2025  
**Version:** 2.1 - PostgreSQL + Email Verification  
**Backend:** 198 commits to push  
**Mobile:** 194 commits to push

---

## 🚀 AUTOMATED DEPLOYMENT - COPY & PASTE INTO TERMIUS

Open **Termius**, connect to `root@80.240.29.142`, then copy-paste this entire script:

```bash
#!/bin/bash
# VerzekAutoTrader Complete Deployment - Nov 12, 2025
set -e

echo "🚀 VerzekAutoTrader Deployment Starting..."
echo "=========================================="

# Stop services
echo "⏸️  Stopping services..."
systemctl stop verzek-api.service 2>/dev/null || true

# Backup
BACKUP_DIR="/root/VerzekBackend_backup_$(date +%s)"
if [ -d "/root/VerzekBackend" ]; then
    echo "💾 Backing up to $BACKUP_DIR"
    mv /root/VerzekBackend $BACKUP_DIR
fi

# Clone latest
echo "📥 Cloning from GitHub..."
cd /root
git clone https://github.com/ellizza78/VerzekBackend.git
cd /root/VerzekBackend/backend

# Install dependencies
echo "📦 Installing Python packages..."
pip3 install -r requirements.txt --upgrade --quiet

# Setup logs
mkdir -p /root/api_server/logs
chmod 755 /root/api_server/logs

# Fix environment file (remove "export" keywords)
echo "⚙️  Fixing environment file..."
if [ -f "/root/api_server_env.sh" ]; then
    sed -i 's/^export //g' /root/api_server_env.sh
    
    # Add missing keys
    grep -q "RESEND_API_KEY" /root/api_server_env.sh || echo "RESEND_API_KEY=re_ACMWmmPe_CHiR7EtPzMwP8Dc9FLy_Lmyu" >> /root/api_server_env.sh
    grep -q "EMAIL_FROM" /root/api_server_env.sh || echo "EMAIL_FROM=support@verzekinnovative.com" >> /root/api_server_env.sh
    
    echo "✅ Environment file updated"
fi

# Update systemd service
echo "🔧 Updating systemd service..."
cat > /etc/systemd/system/verzek-api.service << 'EOF'
[Unit]
Description=Verzek Auto Trader API Server
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=exec
User=root
WorkingDirectory=/root/VerzekBackend/backend
EnvironmentFile=/root/api_server_env.sh
ExecStart=/bin/bash -c 'source /root/api_server_env.sh && exec /usr/local/bin/gunicorn --bind 0.0.0.0:8050 --workers 4 --timeout 120 --access-logfile /root/api_server/logs/access.log --error-logfile /root/api_server/logs/error.log --log-level info api_server:app'
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload and start
echo "🔄 Reloading systemd..."
systemctl daemon-reload
systemctl enable verzek-api.service
systemctl start verzek-api.service

# Wait for startup
sleep 5

# Check status
if systemctl is-active --quiet verzek-api.service; then
    echo "✅ verzek-api.service is ACTIVE"
else
    echo "❌ Service failed! Showing logs:"
    journalctl -u verzek-api.service -n 30 --no-pager
    exit 1
fi

# Test endpoints
echo ""
echo "🏥 Testing API..."
sleep 2
curl -s https://api.verzekinnovative.com/api/ping
echo ""
curl -s https://api.verzekinnovative.com/api/health
echo ""

echo ""
echo "=============================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "=============================================="
echo ""
echo "📊 Summary:"
echo "  • Service: verzek-api.service running"
echo "  • Workers: 4 Gunicorn processes"
echo "  • Database: PostgreSQL 14"
echo "  • API: https://api.verzekinnovative.com"
echo "  • Logs: /root/api_server/logs/"
echo ""
echo "🧪 Test email verification from APK now!"
echo ""
echo "Rollback if needed:"
echo "  systemctl stop verzek-api.service"
echo "  rm -rf /root/VerzekBackend"
echo "  mv $BACKUP_DIR /root/VerzekBackend"
echo "  systemctl start verzek-api.service"
```

---

## ✅ POST-DEPLOYMENT TESTING

### Test 1: Service Status
```bash
systemctl status verzek-api.service
```

### Test 2: API Endpoints
```bash
curl https://api.verzekinnovative.com/api/ping
curl https://api.verzekinnovative.com/api/health
```

### Test 3: Email Verification (APK)
1. Open APK v1.3.1
2. Register with real email
3. Check inbox/spam for verification email
4. Click link and login

### Test 4: Watch Email Logs
```bash
journalctl -u verzek-api.service -f | grep -i "email\|verification\|resend"
```

---

## 📝 WHAT THIS DEPLOYMENT INCLUDES

✅ PostgreSQL 14 database  
✅ Email verification system (Resend API)  
✅ 4 Gunicorn workers for concurrency  
✅ Rate limiting (1 signal/symbol/minute)  
✅ Verification tokens (24-hour expiry)  
✅ 4-day trial auto-logout  
✅ Automated backups before deploy  
✅ Environment variable fixes for systemd  

---

## 🔄 ROLLBACK PROCEDURE

If something breaks:

```bash
# Find backup directory
ls -lh /root/ | grep VerzekBackend_backup

# Restore (replace XXXXXXXXXX with actual timestamp)
systemctl stop verzek-api.service
rm -rf /root/VerzekBackend
mv /root/VerzekBackend_backup_XXXXXXXXXX /root/VerzekBackend
systemctl start verzek-api.service
```

---

## 📊 VERIFICATION CHECKLIST

After deployment, confirm:

- [ ] Service running: `systemctl status verzek-api.service`
- [ ] API responds: `curl https://api.verzekinnovative.com/api/health`
- [ ] PostgreSQL running: `systemctl status postgresql`
- [ ] Logs clean: `journalctl -u verzek-api.service -n 50`
- [ ] Registration works from APK
- [ ] Verification email received
- [ ] Login successful after verification

---

**Deployment Date:** November 12, 2025  
**Version:** 2.1  
**Backend Commits:** 198 ahead of origin/main  
**Mobile Commits:** 194 ahead of origin/main  
**Status:** Ready to deploy
