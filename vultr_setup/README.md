# 🚀 Vultr Server Deployment Package

This directory contains everything you need to deploy VerzekAutoTrader on your Vultr server.

---

## 📦 What's Included

| File | Purpose |
|------|---------|
| `QUICK_DEPLOY.sh` | **One-command deployment** - Runs all 5 phases automatically |
| `VULTR_SETUP_INSTRUCTIONS.md` | **Complete manual setup guide** - Step-by-step for each phase |
| `verzekapi.service` | Systemd service for Flask API server |
| `verzekbot.service` | Systemd service for Telegram forwarder |
| `verzekwatchdog.service` | Systemd service for auto-recovery watchdog |
| `verzek_watchdog.sh` | Watchdog script with Telegram alerts |
| `verzek_status.sh` | System status monitoring script |

---

## ⚡ Quick Deployment (Recommended)

The fastest way to deploy everything:

### **Step 1: Upload files to Vultr**

```bash
# From your local machine, upload the deployment package
scp -r vultr_setup/* root@80.240.29.142:/tmp/

# SSH into Vultr
ssh root@80.240.29.142
```

### **Step 2: Run quick deploy**

```bash
cd /tmp
bash QUICK_DEPLOY.sh
```

This will automatically:
- ✅ Install all systemd services
- ✅ Configure firewall (port 5000)
- ✅ Install watchdog with Telegram alerts
- ✅ Install status monitoring
- ✅ Start all services
- ✅ Show system status

**Done!** Your entire system will be running in under 60 seconds.

---

## 📋 Manual Deployment

If you prefer step-by-step manual control, follow the complete guide:

```bash
cd /tmp
cat VULTR_SETUP_INSTRUCTIONS.md
```

Then execute each phase manually.

---

## 🧪 Testing After Deployment

Run these commands to verify everything works:

```bash
# 1. Check all services
bash /opt/verzek_status.sh

# 2. Test backend locally
curl http://localhost:5000/ping

# 3. Test backend externally
curl http://80.240.29.142:5000/ping

# 4. Test Replit bridge
curl https://verzek-auto-trader.replit.app/ping

# 5. View logs
journalctl -u verzekapi -f
journalctl -u verzekbot -f
journalctl -u verzekwatchdog -f
```

---

## ✅ Success Checklist

After deployment, verify:

- [ ] `systemctl status verzekapi` shows **active (running)**
- [ ] `systemctl status verzekbot` shows **active (running)**
- [ ] `systemctl status verzekwatchdog` shows **active (running)**
- [ ] `curl http://localhost:5000/ping` returns valid JSON
- [ ] `curl http://80.240.29.142:5000/ping` returns valid JSON
- [ ] `curl https://verzek-auto-trader.replit.app/ping` returns valid JSON
- [ ] Port 5000 is open: `ufw status | grep 5000`
- [ ] Watchdog is monitoring: `tail /var/log/verzek_watchdog.log`

---

## 🔧 Troubleshooting

### Service won't start

```bash
# Check detailed logs
journalctl -u verzekapi -n 50
journalctl -u verzekbot -n 50

# Verify Python environment
/var/www/VerzekAutoTrader/venv/bin/python3 --version
```

### Port 5000 not listening

```bash
# Check if service is running
systemctl status verzekapi

# Check port binding
ss -tuln | grep 5000

# Verify firewall
sudo ufw allow 5000/tcp
sudo ufw reload
```

### Watchdog not working

```bash
# Check watchdog service
systemctl status verzekwatchdog

# View watchdog logs
tail -f /var/log/verzek_watchdog.log

# Test manually
sudo systemctl stop verzekbot
# Wait 2 minutes
sudo systemctl status verzekbot  # Should be auto-restarted
```

### Bridge timeout

```bash
# From Vultr server, test external access
curl http://80.240.29.142:5000/ping

# If this fails, firewall issue:
sudo ufw allow 5000/tcp
sudo ufw reload

# If succeeds but bridge times out, check backend binding:
ss -tuln | grep 5000
# Should show 0.0.0.0:5000, not 127.0.0.1:5000
```

---

## 🛠️ Useful Commands

```bash
# Restart all services
sudo systemctl restart verzekapi verzekbot verzekwatchdog

# View system status
bash /opt/verzek_status.sh

# Follow all logs in real-time
journalctl -u verzekapi -u verzekbot -u verzekwatchdog -f

# Check watchdog activity
tail -f /var/log/verzek_watchdog.log

# Test watchdog auto-restart
sudo systemctl stop verzekbot
sleep 130
sudo systemctl status verzekbot  # Should be running again
```

---

## 📱 Mobile App Configuration

After successful deployment, your mobile app should use:

```javascript
const API_BASE_URL = "https://verzek-auto-trader.replit.app";
```

The Replit bridge will automatically forward all requests to your Vultr backend.

---

## 🔔 Telegram Alerts

The watchdog sends alerts to:
- **Admin Chat ID:** 572038606
- **Bot Token:** @verzekpayflowbot (8351047055)

When a service crashes and auto-restarts, you'll receive:
> ⚠️ Watchdog Alert: Service verzekapi was restarted on [hostname] at 2025-10-28 14:30:00

---

## 📊 Monitoring

The system includes automatic monitoring:

- **Watchdog:** Checks services every 2 minutes
- **Auto-restart:** Failed services restart automatically
- **Telegram alerts:** Instant notifications on service failures
- **Status script:** Run `bash /opt/verzek_status.sh` anytime

---

**Created:** October 28, 2025  
**Deployment Time:** ~60 seconds with QUICK_DEPLOY.sh  
**Status:** Ready for production deployment
