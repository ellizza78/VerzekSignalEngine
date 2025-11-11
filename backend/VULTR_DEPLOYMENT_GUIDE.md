# Vultr VPS Deployment Guide - VerzekAutoTrader v2.1

## 🚀 Quick Deploy (One Command)

```bash
curl -sL https://raw.githubusercontent.com/ellizza78/VerzekBackend/main/backend/deploy/deploy_to_vultr.sh | bash
```

**Note**: You must still create `/root/api_server_env.sh` with your secrets before running this!

---

## 📋 Prerequisites

- **VPS**: Vultr Server (80.240.29.142)
- **OS**: Ubuntu 20.04/22.04 LTS
- **Access**: Root SSH access
- **Domain**: verzekinnovative.com (DNS pointing to VPS IP)
- **Ports**: 80, 443, 8050 open

---

## 🔧 Manual Deployment Steps

### **Step 1: Connect to VPS**

```bash
ssh root@80.240.29.142
```

### **Step 2: Install Dependencies**

```bash
# Update system
apt update && apt upgrade -y

# Install Python 3.11 and essential tools
apt install -y python3.11 python3.11-venv python3-pip nginx git supervisor cron

# Install PostgreSQL (optional, recommended for production)
apt install -y postgresql postgresql-contrib
```

### **Step 3: Clone Repository**

```bash
cd /root
git clone https://github.com/ellizza78/VerzekBackend.git api_server
cd api_server
```

### **Step 4: Configure Environment Variables**

Create `/root/api_server_env.sh`:

```bash
cat > /root/api_server_env.sh << 'EOF'
#!/bin/bash
# VerzekAutoTrader Production Environment Variables
# ⚠️ SECURITY: Generate UNIQUE values for all secrets - DO NOT use these defaults!

# Security Keys (MUST BE UNIQUE PER INSTALLATION)
export JWT_SECRET="$(openssl rand -hex 32)"  # Generate unique: openssl rand -hex 32
export ENCRYPTION_KEY="$(python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"

# Database
export DATABASE_URL="sqlite:////root/api_server/backend/database/verzek.db"
# For PostgreSQL (recommended for production):
# export DATABASE_URL="postgresql://verzek_user:YOUR_PASSWORD@localhost/verzek_db"

# Telegram Integration
export TELEGRAM_BOT_TOKEN="YOUR_TELEGRAM_BOT_TOKEN"
export BROADCAST_BOT_TOKEN="YOUR_BROADCAST_BOT_TOKEN"
export VIP_GROUP_ID="YOUR_VIP_GROUP_ID"
export TRIAL_GROUP_ID="YOUR_TRIAL_GROUP_ID"
export ADMIN_CHAT_ID="YOUR_ADMIN_CHAT_ID"

# Email (Resend API)
export EMAIL_FROM="support@verzekinnovative.com"
export RESEND_API_KEY="YOUR_RESEND_API_KEY"

# Trading Configuration
export EXCHANGE_MODE="paper"  # paper or live
export WORKER_POLL_SECONDS="10"

# Server Configuration
export FLASK_ENV="production"
export PORT="8050"
export SERVER_IP="80.240.29.142"
export LOG_DIR="/root/api_server/logs"
EOF

# Secure the file
chmod 600 /root/api_server_env.sh
```

**🔒 CRITICAL SECURITY REQUIREMENTS**:
1. **JWT_SECRET**: Generate unique with `openssl rand -hex 32` - NEVER use defaults!
2. **ENCRYPTION_KEY**: Generate with Python command above - required for API key encryption
3. **All Telegram tokens**: Get from @BotFather on Telegram
4. **RESEND_API_KEY**: Get from resend.com dashboard
5. **Replace ALL `YOUR_*` placeholders** with actual values

### **Step 5: Install Python Dependencies**

```bash
cd /root/api_server/backend
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt  # requirements.txt is in backend/ directory
```

### **Step 6: Initialize Database**

```bash
source /root/api_server_env.sh
source venv/bin/activate
cd /root/api_server/backend

# Create database directory
mkdir -p database

# Initialize database schema
python -c "from db import init_db; init_db()"
```

### **Step 7: Configure Systemd Services**

**API Server Service** (`/etc/systemd/system/verzek_api.service`):

```ini
[Unit]
Description=Verzek AutoTrader API Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/api_server/backend
EnvironmentFile=/root/api_server_env.sh
ExecStart=/root/api_server/backend/venv/bin/gunicorn --bind 0.0.0.0:8050 --workers 4 --timeout 120 --reuse-port api_server:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Worker Service** (`/etc/systemd/system/verzek_worker.service`):

```ini
[Unit]
Description=Verzek AutoTrader Worker
After=network.target verzek_api.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/api_server/backend
EnvironmentFile=/root/api_server_env.sh
ExecStart=/root/api_server/backend/venv/bin/python worker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### **Step 8: Configure Nginx Reverse Proxy**

Create `/etc/nginx/sites-available/verzek-api`:

```nginx
server {
    listen 80;
    server_name api.verzekinnovative.com verzekinnovative.com;

    location / {
        proxy_pass http://127.0.0.1:8050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_connect_timeout 120s;
    }
}
```

Enable site:

```bash
ln -s /etc/nginx/sites-available/verzek-api /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx
```

### **Step 9: Install SSL Certificate (Optional but Recommended)**

```bash
apt install -y certbot python3-certbot-nginx
certbot --nginx -d api.verzekinnovative.com -d verzekinnovative.com
```

### **Step 10: Setup Watchdog Monitoring**

Add to crontab (`crontab -e`):

```bash
*/5 * * * * /bin/bash /root/api_server/backend/scripts/watchdog.sh >> /root/api_server/logs/watchdog.log 2>&1
```

### **Step 11: Start All Services**

```bash
# Enable services to start on boot
systemctl enable verzek_api verzek_worker

# Start services
systemctl start verzek_api verzek_worker

# Check status
systemctl status verzek_api verzek_worker
```

---

## ✅ Verification Tests

### **Test API Endpoints**

```bash
# Test ping
curl -s http://localhost:8050/api/ping

# Expected output:
# {"service":"VerzekAutoTrader API","version":"2.1","status":"operational","timestamp":"..."}

# Test health
curl -s http://localhost:8050/api/health

# Expected output:
# {"ok":true,"timestamp":"2025-11-11T10:00:00Z"}

# Test from external
curl -s https://api.verzekinnovative.com/api/ping
```

### **Check Logs**

```bash
# API logs
journalctl -u verzek_api -f

# Worker logs
journalctl -u verzek_worker -f

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## 🔄 Deployment Updates

To deploy code updates:

```bash
cd /root/api_server
git pull origin main
systemctl restart verzek_api verzek_worker
```

---

## 📊 Monitoring

- **Health Check**: GET `/api/health` (every 5 minutes via watchdog)
- **Service Status**: `systemctl status verzek_api verzek_worker`
- **Logs**: `journalctl -u verzek_api -f`
- **Watchdog Log**: `/root/api_server/logs/watchdog.log`

---

## 🆘 Troubleshooting

### Service Won't Start

```bash
# Check environment variables
source /root/api_server_env.sh
env | grep -E "TELEGRAM|ENCRYPTION|JWT"

# Check Python dependencies
source /root/api_server/backend/venv/bin/activate
pip list

# Check database
ls -la /root/api_server/backend/database/
```

### Database Errors

```bash
# Reinitialize database
cd /root/api_server/backend
source venv/bin/activate
source /root/api_server_env.sh
python -c "from db import init_db; init_db()"
```

### Port Already in Use

```bash
# Find process using port 8050
lsof -i :8050
# Kill if needed
kill -9 <PID>
```

---

## 🔒 Security Checklist

- ✅ Environment file is chmod 600
- ✅ SSL certificate installed
- ✅ Firewall configured (ufw)
- ✅ Database credentials rotated
- ✅ Telegram bot tokens secured
- ✅ Regular backups enabled

---

## 📦 Post-Deployment Configuration

### Configure App Config

```bash
cd /root/api_server/backend
source venv/bin/activate
source /root/api_server_env.sh

python << EOF
from db import SessionLocal
from models import AppConfig

db = SessionLocal()
config = AppConfig(
    min_app_version='1.0.0',
    force_update_required=False,
    maintenance_mode=False,
    feature_flags={
        'paper_trading': True,
        'live_trading': False,
        'ai_assistant': True,
        'telegram_signals': True
    }
)
db.add(config)
db.commit()
print("✅ App config created!")
db.close()
EOF
```

---

## 🎯 Production Ready Checklist

- [ ] All environment variables configured
- [ ] Database initialized
- [ ] Services running and enabled
- [ ] Nginx reverse proxy configured
- [ ] SSL certificate installed
- [ ] Watchdog monitoring active
- [ ] Logs rotating properly
- [ ] Backup strategy in place
- [ ] Mobile app connected and tested

**Your VerzekAutoTrader backend is now live at https://api.verzekinnovative.com! 🚀**
