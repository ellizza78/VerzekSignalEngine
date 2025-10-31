# Phase 1 + 2: Health Monitoring System Deployment

## 📦 Files Ready on Replit

The following files have been created and are ready to download:

1. **telethon_forwarder.py** - Updated forwarder with heartbeat monitoring
2. **forwarder_watchdog.py** - Health monitor script
3. **telethon-forwarder.service** - Systemd service for forwarder
4. **forwarder-watchdog.service** - Systemd service for watchdog
5. **forwarder-watchdog.timer** - Timer to run watchdog every minute

---

## 🚀 Deployment Steps

### Step 1: Download Files from Replit

On your computer, download these 5 files from the Replit file explorer.

### Step 2: Upload to Vultr

Use SCP or SFTP to upload all files to `/var/www/VerzekAutoTrader/`:

**Example with SCP:**
```bash
scp telethon_forwarder.py root@80.240.29.142:/var/www/VerzekAutoTrader/
scp forwarder_watchdog.py root@80.240.29.142:/var/www/VerzekAutoTrader/
scp telethon-forwarder.service root@80.240.29.142:/var/www/VerzekAutoTrader/
scp forwarder-watchdog.service root@80.240.29.142:/var/www/VerzekAutoTrader/
scp forwarder-watchdog.timer root@80.240.29.142:/var/www/VerzekAutoTrader/
```

### Step 3: Deploy on Vultr (Via SSH)

**A. Stop Current Forwarder:**
```bash
pkill -f telethon_forwarder.py
```

**B. Make Watchdog Executable:**
```bash
cd /var/www/VerzekAutoTrader
chmod +x forwarder_watchdog.py
```

**C. Install Systemd Services:**
```bash
cp telethon-forwarder.service /etc/systemd/system/
cp forwarder-watchdog.service /etc/systemd/system/
cp forwarder-watchdog.timer /etc/systemd/system/
systemctl daemon-reload
```

**D. Start Forwarder Service:**
```bash
systemctl enable telethon-forwarder.service
systemctl start telethon-forwarder.service
```

**E. Check Forwarder Status:**
```bash
systemctl status telethon-forwarder.service
```

You should see "active (running)" in green.

**F. Enable Watchdog Timer:**
```bash
systemctl enable forwarder-watchdog.timer
systemctl start forwarder-watchdog.timer
```

**G. Verify Watchdog Timer:**
```bash
systemctl status forwarder-watchdog.timer
```

You should see "active (waiting)" in green.

**H. Wait for Heartbeat (35 seconds):**
```bash
sleep 35
cat /tmp/forwarder_heartbeat.json
```

You should see JSON with timestamp, status, PID.

---

## ✅ What You Get

### 1. Heartbeat Monitoring
- File: `/tmp/forwarder_heartbeat.json`
- Updates every 30 seconds
- Contains: timestamp, status, last_signal_time, PID

### 2. Auto-Restart Watchdog
- Checks heartbeat every minute
- If heartbeat is >90 seconds old → Auto-restart forwarder
- If forwarder crashes → Auto-restart

### 3. Telegram Alerts
- You receive notification when forwarder freezes
- You receive notification when forwarder restarts
- Sent to your admin Telegram account (ADMIN_CHAT_ID)

### 4. Professional Management
- Systemd keeps forwarder running 24/7
- Automatic restart on crash
- Survives server reboots

---

## 📊 Monitoring Commands

**Check Forwarder:**
```bash
systemctl status telethon-forwarder
```

**Check Watchdog:**
```bash
systemctl status forwarder-watchdog.timer
```

**View Forwarder Logs:**
```bash
journalctl -u telethon-forwarder -f
```

**View Watchdog Logs:**
```bash
journalctl -u forwarder-watchdog -f
```

**Check Heartbeat:**
```bash
cat /tmp/forwarder_heartbeat.json
```

---

## 🔧 Troubleshooting

**Forwarder Not Starting:**
```bash
journalctl -u telethon-forwarder --no-pager -n 50
```

**Watchdog Not Running:**
```bash
systemctl status forwarder-watchdog.timer
journalctl -u forwarder-watchdog --no-pager -n 20
```

**Manual Restart:**
```bash
systemctl restart telethon-forwarder
```

---

## 🎯 Next Steps

1. Download the 5 files from Replit
2. Upload to Vultr
3. Run the deployment commands above
4. Verify everything is working

Total deployment time: **10-15 minutes**

---

**Questions? Let me know and I'll help!** 🚀
