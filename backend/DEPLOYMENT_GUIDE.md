# 🚀 VerzekBackend Deployment Guide

Complete step-by-step guide for deploying to Vultr VPS (80.240.29.142)

---

## 📋 Pre-Deployment Checklist

### 1. **Prepare Secrets File on Vultr**

SSH into Vultr VPS:
```bash
ssh root@80.240.29.142
```

Create `/root/api_server_env.sh`:
```bash
nano /root/api_server_env.sh
```

**Paste this content** (replace placeholders):
```bash
#!/bin/bash
# Verzek AutoTrader Configuration

# Security (REQUIRED)
export JWT_SECRET="VerzekAutoTraderKey2025"
export API_KEY="Verzek2025AutoTrader"

# Encryption Key (REQUIRED - Generate ONCE and keep safe)
export ENCRYPTION_KEY="$(python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"

# Database
export DATABASE_URL="sqlite:////root/api_server/database/verzek.db"
export EXCHANGE_MODE="paper"

# Telegram Broadcasting
export TELEGRAM_BOT_TOKEN="<YOUR_BOT_TOKEN>"
export TELEGRAM_VIP_CHAT_ID="<YOUR_VIP_CHAT_ID>"
export TELEGRAM_TRIAL_CHAT_ID="<YOUR_TRIAL_CHAT_ID>"

# Admin Notifications (for deployment/watchdog alerts)
export ADMIN_CHAT_ID="<YOUR_ADMIN_CHAT_ID>"

# Worker
export WORKER_POLL_SECONDS="10"

# Server
export FLASK_ENV="production"
export PORT="8050"
export SERVER_IP="80.240.29.142"
export LOG_DIR="/root/api_server/logs"
```

**Secure the file:**
```bash
chmod 600 /root/api_server_env.sh
chown root:root /root/api_server_env.sh
```

---

## 🔄 Deployment Steps

### Step 1: Clone Repository on Vultr

```bash
cd /root
git clone https://github.com/ellizza78/VerzekBackend.git api_server
cd api_server
```

### Step 2: Run Deployment Script

```bash
chmod +x deploy/deploy_to_vultr.sh
./deploy/deploy_to_vultr.sh
```

The script will:
- ✅ Install dependencies (Python, Nginx, Certbot, jq)
- ✅ Create database & logs directories
- ✅ Install Python packages
- ✅ Configure systemd services
- ✅ Setup Nginx reverse proxy
- ✅ Configure SSL with Let's Encrypt
- ✅ Start API & Worker services
- ✅ Setup daily report cron job

---

## ✅ Verification

### 1. **Check Services Status**

```bash
# API Service
sudo systemctl status verzek_api.service

# Worker Service
sudo systemctl status verzek_worker.service
```

**Expected output:** Both services should show `active (running)`

### 2. **Test API Endpoints**

**Test /api/ping:**
```bash
curl http://127.0.0.1:8050/api/ping
```

**Expected response:**
```json
{
  "status": "ok",
  "service": "VerzekBackend",
  "version": "2.1",
  "message": "Backend responding successfully 🚀"
}
```

**Test /api/health:**
```bash
curl http://127.0.0.1:8050/api/health
```

**Expected response:**
```json
{
  "ok": true,
  "status": "healthy",
  "timestamp": "2025-11-11T12:34:56.789Z"
}
```

**Test via public domain:**
```bash
curl https://api.verzekinnovative.com/api/ping
curl https://api.verzekinnovative.com/api/health
```

### 3. **Check Logs**

**API Logs:**
```bash
# Real-time API logs
journalctl -u verzek_api.service -f

# Or from file
tail -f /root/api_server/logs/api.log
```

**Worker Logs:**
```bash
# Real-time worker logs
journalctl -u verzek_worker.service -f

# Or from file
tail -f /root/api_server/logs/worker.log
```

### 4. **Verify Worker Execution**

Worker should log every 10 seconds:
```
2025-11-11 12:00:00 - verzek_worker - INFO - 📊 Starting execution cycle #1
2025-11-11 12:00:00 - verzek_worker - INFO - ✅ Cycle #1 completed successfully
2025-11-11 12:00:10 - verzek_worker - INFO - 📊 Starting execution cycle #2
...
```

---

## 🔧 Service Management

### Start Services
```bash
sudo systemctl start verzek_api.service
sudo systemctl start verzek_worker.service
```

### Stop Services
```bash
sudo systemctl stop verzek_api.service
sudo systemctl stop verzek_worker.service
```

### Restart Services
```bash
sudo systemctl restart verzek_api.service
sudo systemctl restart verzek_worker.service
```

### Enable Auto-Start on Boot
```bash
sudo systemctl enable verzek_api.service
sudo systemctl enable verzek_worker.service
```

### Disable Auto-Start
```bash
sudo systemctl disable verzek_api.service
sudo systemctl disable verzek_worker.service
```

---

## 🔄 Updates & Redeployment

### Update Code from GitHub

```bash
cd /root/api_server
git pull origin main
sudo systemctl restart verzek_api.service
sudo systemctl restart verzek_worker.service
```

### Check for Configuration Changes

If environment variables changed, update `/root/api_server_env.sh` and restart:
```bash
nano /root/api_server_env.sh
sudo systemctl restart verzek_api.service
sudo systemctl restart verzek_worker.service
```

---

## 🐛 Troubleshooting

### Services Won't Start

1. **Check secrets file exists:**
   ```bash
   ls -la /root/api_server_env.sh
   ```

2. **Verify secrets file is sourced:**
   ```bash
   source /root/api_server_env.sh
   echo $JWT_SECRET
   ```

3. **Check Python dependencies:**
   ```bash
   cd /root/api_server
   pip3 install -r requirements.txt
   ```

4. **View detailed logs:**
   ```bash
   journalctl -u verzek_api.service -n 100
   journalctl -u verzek_worker.service -n 100
   ```

### Database Issues

1. **Check database file permissions:**
   ```bash
   ls -la /root/api_server/database/verzek.db
   ```

2. **Recreate database:**
   ```bash
   cd /root/api_server
   rm database/verzek.db
   python3 -c "from db import init_db; init_db()"
   sudo systemctl restart verzek_api.service
   ```

### API Not Responding

1. **Check if port 8050 is listening:**
   ```bash
   netstat -tulpn | grep 8050
   ```

2. **Check Nginx configuration:**
   ```bash
   nginx -t
   sudo systemctl status nginx
   ```

3. **Test direct connection:**
   ```bash
   curl http://127.0.0.1:8050/api/ping
   ```

### Worker Not Processing Signals

1. **Check worker logs:**
   ```bash
   tail -f /root/api_server/logs/worker.log
   ```

2. **Verify database connection:**
   ```bash
   cd /root/api_server
   python3 -c "from db import SessionLocal; db = SessionLocal(); print('Database OK')"
   ```

3. **Check worker environment:**
   ```bash
   sudo systemctl show verzek_worker.service -p Environment
   ```

---

## 📊 Monitoring

### Health Check Endpoints

The API provides health check endpoints for monitoring:

- **Basic connectivity:** `GET /api/ping`
- **Health status:** `GET /api/health`
- **System status:** `GET /api/safety/status`

### Setting Up Monitoring

**Option 1: UptimeRobot**
- URL: https://api.verzekinnovative.com/api/health
- Interval: 5 minutes
- Alert: Email/Telegram when down

**Option 2: Cron Health Check**
```bash
# Add to crontab
*/5 * * * * curl -sf https://api.verzekinnovative.com/api/health || echo "API DOWN" | mail -s "VerzekBackend Alert" admin@example.com
```

---

## 🔒 Security Reminders

✅ **DO:**
- Keep `/root/api_server_env.sh` with chmod 600
- Backup encryption key securely
- Monitor logs for suspicious activity
- Update dependencies regularly
- Use SSL/TLS for all API calls

❌ **DON'T:**
- Commit secrets to git
- Share encryption key
- Regenerate ENCRYPTION_KEY after users add exchanges
- Expose API without SSL
- Ignore security updates

---

## 📞 Support

**Production API:** https://api.verzekinnovative.com  
**Backend Repo:** https://github.com/ellizza78/VerzekBackend  
**Email:** support@verzekinnovative.com

---

## 🎉 Success Criteria

Your deployment is successful when:

✅ `systemctl status verzek_api.service` shows `active (running)`  
✅ `systemctl status verzek_worker.service` shows `active (running)`  
✅ `curl https://api.verzekinnovative.com/api/ping` returns correct JSON  
✅ `curl https://api.verzekinnovative.com/api/health` returns with timestamp  
✅ Worker logs show execution cycles every 10 seconds  
✅ Mobile app can register/login successfully  
✅ Telegram broadcasts work for signals  

**Congratulations! Your VerzekBackend is live!** 🚀
