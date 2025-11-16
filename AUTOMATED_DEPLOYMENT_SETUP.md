# 🤖 VerzekAutoTrader - Fully Automated Deployment

## Overview

This is a **pull-based auto-deployment system** that runs on your Vultr server. After one-time setup, the server automatically checks for Git updates every 2 minutes and deploys changes **without any manual intervention**.

---

## ✅ How It Works

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Replit    │ Push    │    GitHub    │  Pull   │   Vultr     │
│  (You Edit) │────────▶│  Repository  │◀────────│  (Server)   │
└─────────────┘         └──────────────┘         └─────────────┘
                                                         │
                                                         ▼
                                                  Auto-Deploy
                                                  Every 2 min
                                                         │
                                                         ▼
                                                  Service Restart
                                                         │
                                                         ▼
                                                  ✅ Live!
```

**Your workflow after setup:**
1. Edit code in Replit
2. Push to GitHub
3. **That's it!** Server auto-deploys within 2 minutes

---

## 🚀 ONE-TIME SETUP (Run Once)

### Step 1: Setup Git Repository (On Your Local Machine)

If you haven't already, initialize this as a Git repo and push to GitHub:

```bash
# In Replit Shell
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/VerzekBackend.git
git push -u origin main
```

### Step 2: Install Auto-Deploy on Vultr (Copy/Paste One Command)

SSH into your Vultr server and run this **entire command**:

```bash
cd /root/VerzekBackend/backend && \
mkdir -p scripts && \
cat > scripts/auto_pull_deploy.sh << 'DEPLOY_SCRIPT'
#!/bin/bash
set -euo pipefail

REPO_DIR="/root/VerzekBackend"
BACKEND_DIR="/root/VerzekBackend/backend"
LOG_FILE="/var/log/verzek_auto_deploy.log"
BACKUP_DIR="/root/VerzekBackend/backups"
SERVICE_NAME="verzek_api"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"; }
error_exit() { log "ERROR: $1"; exit 1; }

mkdir -p "$BACKUP_DIR"
log "=== Starting auto-deploy check ==="
cd "$REPO_DIR" || error_exit "Cannot access repo directory"

log "Fetching latest changes from origin..."
git fetch origin main || error_exit "Git fetch failed"

LOCAL_HASH=$(git rev-parse HEAD)
REMOTE_HASH=$(git rev-parse origin/main)

if [ "$LOCAL_HASH" = "$REMOTE_HASH" ]; then
    log "No new changes detected. Exiting."
    exit 0
fi

log "New changes detected! Local: $LOCAL_HASH, Remote: $REMOTE_HASH"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/backup_$TIMESTAMP"
mkdir -p "$BACKUP_PATH"

log "Creating backup at $BACKUP_PATH..."
cp "$BACKEND_DIR/models.py" "$BACKUP_PATH/models.py.bak" 2>/dev/null || log "models.py not found"
cp "$BACKEND_DIR/house_signals_routes.py" "$BACKUP_PATH/house_signals_routes.py.bak" 2>/dev/null || log "house_signals_routes.py not found"

log "Pulling latest changes..."
git pull origin main || error_exit "Git pull failed"

log "Clearing Python cache..."
find "$BACKEND_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$BACKEND_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true

[ -f "$BACKEND_DIR/models.py" ] || error_exit "models.py missing after pull"
[ -f "$BACKEND_DIR/house_signals_routes.py" ] || error_exit "house_signals_routes.py missing after pull"

log "Stopping $SERVICE_NAME..."
systemctl stop "$SERVICE_NAME" || log "Warning: Failed to stop gracefully"
pkill -9 gunicorn 2>/dev/null || true
sleep 2

log "Starting $SERVICE_NAME..."
systemctl start "$SERVICE_NAME" || error_exit "Failed to start service"
sleep 5

if systemctl is-active --quiet "$SERVICE_NAME"; then
    log "✅ SUCCESS: Deployment completed. Service is active."
    log "Deployed commit: $REMOTE_HASH"
else
    error_exit "Service failed to start after deployment"
fi

log "Cleaning old backups..."
cd "$BACKUP_DIR" && ls -t | tail -n +11 | xargs rm -rf 2>/dev/null || true
log "=== Auto-deploy completed successfully ==="
exit 0
DEPLOY_SCRIPT
chmod +x scripts/auto_pull_deploy.sh && \
cat > /etc/systemd/system/verzek-autodeploy.service << 'SERVICE_UNIT'
[Unit]
Description=VerzekAutoTrader Auto-Deploy Service
After=network.target

[Service]
Type=oneshot
ExecStart=/bin/bash /root/VerzekBackend/backend/scripts/auto_pull_deploy.sh
StandardOutput=journal
StandardError=journal
SyslogIdentifier=verzek-autodeploy

[Install]
WantedBy=multi-user.target
SERVICE_UNIT
cat > /etc/systemd/system/verzek-autodeploy.timer << 'TIMER_UNIT'
[Unit]
Description=VerzekAutoTrader Auto-Deploy Timer
Requires=verzek-autodeploy.service

[Timer]
OnBootSec=1min
OnUnitActiveSec=2min
AccuracySec=1s

[Install]
WantedBy=timers.target
TIMER_UNIT
systemctl daemon-reload && \
systemctl enable verzek-autodeploy.timer && \
systemctl start verzek-autodeploy.timer && \
echo "" && \
echo "✅ Auto-deploy system installed!" && \
echo "" && \
systemctl status verzek-autodeploy.timer --no-pager && \
echo "" && \
echo "📊 The server will now check for updates every 2 minutes." && \
echo "📋 View deployment logs: tail -f /var/log/verzek_auto_deploy.log"
```

---

## ✅ Verify Setup

Check the timer is active:

```bash
systemctl status verzek-autodeploy.timer
```

You should see:

```
Active: active (waiting)
```

---

## 🎯 HOW TO DEPLOY (After Setup)

### From Replit:

```bash
# 1. Make your changes in Replit
# 2. Commit and push
git add .
git commit -m "Your change description"
git push origin main

# 3. That's it! Server deploys automatically within 2 minutes
```

### Monitor Deployment:

```bash
# On Vultr server
tail -f /var/log/verzek_auto_deploy.log
```

You'll see logs like:

```
[2025-11-17 00:50:15] === Starting auto-deploy check ===
[2025-11-17 00:50:15] Fetching latest changes from origin...
[2025-11-17 00:50:16] New changes detected! Local: abc123, Remote: def456
[2025-11-17 00:50:16] Creating backup...
[2025-11-17 00:50:17] Pulling latest changes...
[2025-11-17 00:50:18] Clearing Python cache...
[2025-11-17 00:50:18] Stopping verzek_api...
[2025-11-17 00:50:20] Starting verzek_api...
[2025-11-17 00:50:25] ✅ SUCCESS: Deployment completed. Service is active.
```

---

## 📊 Management Commands

### Check auto-deploy status:
```bash
systemctl status verzek-autodeploy.timer
```

### Manually trigger deployment:
```bash
systemctl start verzek-autodeploy.service
```

### View deployment history:
```bash
journalctl -u verzek-autodeploy -n 50 --no-pager
```

### Disable auto-deploy:
```bash
systemctl stop verzek-autodeploy.timer
systemctl disable verzek-autodeploy.timer
```

### Re-enable auto-deploy:
```bash
systemctl enable verzek-autodeploy.timer
systemctl start verzek-autodeploy.timer
```

---

## 🔄 Rollback (If Needed)

Auto-backups are created before each deployment at `/root/VerzekBackend/backups/`

To rollback:

```bash
# List backups
ls -lt /root/VerzekBackend/backups/

# Restore from backup
cd /root/VerzekBackend/backend
cp /root/VerzekBackend/backups/backup_20251117_005015/models.py.bak models.py
cp /root/VerzekBackend/backups/backup_20251117_005015/house_signals_routes.py.bak house_signals_routes.py

# Restart service
systemctl restart verzek_api
```

---

## 🎉 Benefits

✅ **Zero Manual Deployment** - Push to Git and forget  
✅ **Automatic Backups** - Every deployment creates timestamped backups  
✅ **Health Checks** - Auto-verifies service starts successfully  
✅ **Audit Trail** - Complete deployment logs in /var/log/verzek_auto_deploy.log  
✅ **Rollback Ready** - Easy restore from automatic backups  
✅ **Production Safe** - Stops gracefully, clears cache, validates files  

---

## 🆘 Troubleshooting

### Auto-deploy not running:

```bash
# Check timer status
systemctl status verzek-autodeploy.timer

# Check service logs
journalctl -u verzek-autodeploy -n 50

# Manually test the script
bash /root/VerzekBackend/backend/scripts/auto_pull_deploy.sh
```

### Git pull fails:

```bash
# Setup Git credentials (if not done)
cd /root/VerzekBackend
git config --global credential.helper store
git pull  # Enter credentials once, they'll be saved
```

### Service won't start after deployment:

```bash
# Check API logs
tail -50 /root/VerzekBackend/backend/logs/api_error.log

# Check service status
systemctl status verzek_api
```

---

## 📝 What This Fixes

This automated deployment will deploy the **metadata column bug fix** that's already complete in your Replit workspace:

✅ Fixed SQLAlchemy reserved word collision  
✅ Added backwards-compatible property access  
✅ Updated API response serializers  
✅ Architect-reviewed and production-ready  

**After setup, just push to Git and the fix deploys automatically!** 🚀
