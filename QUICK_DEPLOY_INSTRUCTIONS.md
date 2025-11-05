# 🚀 QUICK DEPLOYMENT INSTRUCTIONS
## VerzekAutoTrader Production Backend

**Target Server:** Vultr VPS (80.240.29.142)  
**Domain:** api.verzekinnovative.com

---

## ⚡ FASTEST DEPLOYMENT (One Command)

### Step 1: Upload Files to Vultr

From your local machine (or Replit Shell):

```bash
# Upload entire api_server directory
scp -r api_server/ root@80.240.29.142:/root/

# Or if you're in Replit, download and upload manually
```

### Step 2: SSH to Vultr

```bash
ssh root@80.240.29.142
```

### Step 3: Run Deployment Script

```bash
cd /root/api_server
chmod +x PRODUCTION_DEPLOYMENT.sh
./PRODUCTION_DEPLOYMENT.sh
```

**That's it!** The script will:
- ✅ Backup existing files
- ✅ Install all dependencies (Python, Nginx, Certbot)
- ✅ Configure Nginx with SSL
- ✅ Set up systemd service
- ✅ Configure log rotation
- ✅ Add auto-restart monitoring
- ✅ Start the API server
- ✅ Validate deployment

---

## 🔑 BEFORE YOU START

### Required Files on Vultr:

1. **Environment Variables** (`/root/api_server_env.sh`):
   ```bash
   export ENCRYPTION_MASTER_KEY="M43XK9_F18dHGVNtq_Op6aUY4zXDnJUMNGaahMiTynM="
   export RESEND_API_KEY="re_xxxxxxxxxxxxx"
   export TELEGRAM_BOT_TOKEN="your_bot_token"
   export BROADCAST_BOT_TOKEN="your_broadcast_bot_token"
   export ADMIN_CHAT_ID="your_admin_chat_id"
   export API_BASE_URL="https://api.verzekinnovative.com"
   export DOMAIN="api.verzekinnovative.com"
   export APP_NAME="Verzek AutoTrader"
   export SUPPORT_EMAIL="support@verzekinnovative.com"
   export SUBSCRIPTION_SECRET_KEY="verz3k_prod_!@#_2025"
   ```

2. **Firebase Service Account** (`/root/firebase_key.json`) - OPTIONAL
   - Download from Firebase Console → Project Settings → Service Accounts
   - Generate New Private Key
   - Upload to `/root/firebase_key.json`
   - Set permissions: `chmod 600 /root/firebase_key.json`

---

## 📋 MANUAL DEPLOYMENT (Step-by-Step)

If you prefer manual control:

### 1. Backup Current Setup

```bash
cp /root/api_server.py /root/api_server_backup_$(date +%F).py
cp /etc/systemd/system/verzek-api.service /root/verzek-api.service.backup
```

### 2. Install Dependencies

```bash
apt update
apt install -y python3-pip nginx certbot python3-certbot-nginx logrotate
pip3 install -r /root/api_server/requirements.txt
```

### 3. Configure Nginx

```bash
cp /root/api_server/vultr_infrastructure/nginx_verzekinnovative.conf /etc/nginx/sites-available/verzekinnovative
ln -sf /etc/nginx/sites-available/verzekinnovative /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx
```

### 4. Get SSL Certificate

```bash
certbot --nginx -d api.verzekinnovative.com --non-interactive --agree-tos --email admin@verzekinnovative.com
```

### 5. Set Up Systemd Service

```bash
cp /root/api_server/vultr_infrastructure/verzek-api.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable verzek-api.service
systemctl start verzek-api.service
```

### 6. Configure Log Rotation

```bash
cp /root/api_server/vultr_infrastructure/logrotate_verzek /etc/logrotate.d/verzek
```

### 7. Add Auto-Restart Cron

```bash
crontab -e
# Add this line:
*/5 * * * * systemctl is-active --quiet verzek-api.service || systemctl restart verzek-api.service
```

---

## ✅ VALIDATE DEPLOYMENT

Run the validation script:

```bash
cd /root/api_server
chmod +x validate_deployment.sh
./validate_deployment.sh
```

Or test manually:

```bash
# Test health endpoint
curl https://api.verzekinnovative.com/api/health

# Check service status
systemctl status verzek-api.service

# Check logs
journalctl -u verzek-api.service -n 50
```

---

## 🔧 POST-DEPLOYMENT

### Useful Commands:

```bash
# View live logs
journalctl -u verzek-api.service -f

# Restart service
systemctl restart verzek-api.service

# Check service status
systemctl status verzek-api.service

# Test endpoint
curl https://api.verzekinnovative.com/api/health

# Check Nginx status
systemctl status nginx

# Reload Nginx
systemctl reload nginx
```

### Update Backend Code:

```bash
# Stop service
systemctl stop verzek-api.service

# Update files
cd /root/api_server
# Make your changes or upload new files

# Restart service
systemctl start verzek-api.service
```

---

## 📱 MOBILE APP CONNECTION

After deployment, update your mobile app to use the production API:

**File:** `mobile_app/VerzekApp/src/config/api.js`

```javascript
export const API_BASE_URL = 'https://api.verzekinnovative.com';
```

Then rebuild your APK:

```bash
cd mobile_app/VerzekApp
eas build --platform android --profile preview --non-interactive
```

---

## 🚨 TROUBLESHOOTING

### Service Won't Start

```bash
# Check logs
journalctl -u verzek-api.service -n 100

# Check if port 8000 is in use
netstat -tulpn | grep 8000

# Check Python errors
python3 /root/api_server/api_server.py
```

### SSL Certificate Issues

```bash
# Manually renew certificate
certbot renew

# Check certificate status
certbot certificates

# Test SSL
curl -v https://api.verzekinnovative.com/api/health
```

### Nginx Errors

```bash
# Test configuration
nginx -t

# Check error logs
tail -f /var/log/nginx/verzekinnovative_error.log

# Reload configuration
systemctl reload nginx
```

---

## 📊 MONITORING

### Check System Resources:

```bash
# CPU and Memory
htop

# Disk usage
df -h

# Service resource usage
systemctl status verzek-api.service
```

### Check Logs:

```bash
# API logs
tail -f /root/api_server/logs/api_server.log

# Nginx access logs
tail -f /var/log/nginx/verzekinnovative_access.log

# Nginx error logs
tail -f /var/log/nginx/verzekinnovative_error.log
```

---

## 🔐 SECURITY CHECKLIST

- [x] Environment file (`/root/api_server_env.sh`) has chmod 600
- [x] Firebase key (`/root/firebase_key.json`) has chmod 600
- [x] SSL certificate installed and auto-renews
- [x] Rate limiting enabled (120 requests/minute)
- [x] CORS configured for mobile app
- [x] Auto-restart monitoring active
- [x] Log rotation configured

---

## 🎯 EXPECTED RESULTS

After successful deployment:

1. **Health Check:** https://api.verzekinnovative.com/api/health returns `{"status":"ok"}`
2. **SSL:** Green lock icon in browser
3. **Service:** `systemctl status verzek-api.service` shows "active (running)"
4. **Nginx:** `systemctl status nginx` shows "active (running)"
5. **Logs:** No errors in `/root/api_server/logs/api_server.log`

---

**🎉 Your backend is production-ready!**

For questions: support@verzekinnovative.com
