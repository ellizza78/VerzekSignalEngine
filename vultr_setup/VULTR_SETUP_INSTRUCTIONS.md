# 🚀 Vultr Server Setup Instructions

**Complete setup guide for Phases 1-5**

---

## ⚠️ PREREQUISITES

SSH into your Vultr server:
```bash
ssh root@80.240.29.142
```

Navigate to your project directory:
```bash
cd /var/www/VerzekAutoTrader
```

---

## 📋 PHASE 1: Fix Flask API Binding

### **Step 1: Verify api_server.py binding**

Check if `api_server.py` ends with correct binding:
```bash
tail -5 /var/www/VerzekAutoTrader/api_server.py
```

Should show:
```python
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
```

If not, fix it:
```bash
# Backup first
cp api_server.py api_server.py.backup

# Add correct binding (if missing)
cat >> api_server.py << 'EOF'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
EOF
```

### **Step 2: Install systemd service**

Copy the service file to systemd:
```bash
# Download the service file from Replit or create it manually
cat > /etc/systemd/system/verzekapi.service << 'EOF'
[Unit]
Description=Verzek Auto Trader API Server
After=network.target

[Service]
Type=simple
ExecStart=/var/www/VerzekAutoTrader/venv/bin/python3 /var/www/VerzekAutoTrader/api_server.py
WorkingDirectory=/var/www/VerzekAutoTrader
User=root
Environment=PYTHONUNBUFFERED=1
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
```

### **Step 3: Reload and start service**

```bash
sudo systemctl daemon-reload
sudo systemctl restart verzekapi
sudo systemctl enable verzekapi
sudo systemctl status verzekapi
```

Expected output: `Active: active (running)`

### **Step 4: Open firewall**

```bash
sudo ufw allow 5000/tcp
sudo ufw reload
sudo ufw status
```

Verify port is listening:
```bash
ss -tuln | grep 5000
```

Should show: `LISTEN 0.0.0.0:5000`

### **Step 5: Test endpoint**

```bash
curl http://localhost:5000/ping
```

Expected response:
```json
{
  "status": "running",
  "message": "✅ Verzek Auto Trader API is alive"
}
```

---

## 📋 PHASE 2: Verify Full Connectivity

### **Step 1: Test backend directly**

From Vultr server:
```bash
curl http://localhost:5000/ping
curl http://80.240.29.142:5000/ping
```

Both should return the same JSON response.

### **Step 2: Test from external source**

From your local machine (NOT Vultr):
```bash
curl http://80.240.29.142:5000/ping
```

If this fails, check firewall:
```bash
sudo ufw status | grep 5000
```

### **Step 3: Test Replit bridge**

From anywhere:
```bash
curl https://verzek-auto-trader.replit.app/ping
```

Should return the same response as backend.

### **Step 4: Auto-recovery test**

If responses don't match or timeout:
```bash
sudo systemctl restart verzekapi
sudo systemctl restart verzekbot
sleep 10
curl http://localhost:5000/ping
curl https://verzek-auto-trader.replit.app/ping
```

### **Step 5: Verify matching responses**

Both endpoints should return:
```json
{
  "status": "running",
  "message": "✅ Backend alive and connected to Replit Bridge"
}
```

---

## 📋 PHASE 3: Validate Signal Flow

### **Step 1: Install verzekbot service**

```bash
cat > /etc/systemd/system/verzekbot.service << 'EOF'
[Unit]
Description=Verzek Telegram Signal Forwarder
After=network.target

[Service]
Type=simple
ExecStart=/var/www/VerzekAutoTrader/venv/bin/python3 /var/www/VerzekAutoTrader/telethon_forwarder.py
WorkingDirectory=/var/www/VerzekAutoTrader
User=root
Environment=PYTHONUNBUFFERED=1
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl restart verzekbot
sudo systemctl enable verzekbot
sudo systemctl status verzekbot
```

### **Step 2: Monitor Telethon forwarder**

```bash
journalctl -u verzekbot -f
```

Look for:
- `[FORWARDER] Signal detected`
- `[BROADCAST] ✅ Sent message`

### **Step 3: Trigger test signal**

Send a test message to your monitored Telegram channel:
```
#Signal #BTC/USDT
Long 🚀 Lev x20
Entry: 62000
Targets: 62500, 63000, 63500
Stop Loss: 61500
```

### **Step 4: Verify backend logs**

```bash
tail -f /var/www/VerzekAutoTrader/logs/*.log
# or
journalctl -u verzekapi -f
```

Look for:
- `[TRADE] Simulated trade triggered`
- `[API] Signal processed`

### **Step 5: Test API endpoint**

```bash
curl https://verzek-auto-trader.replit.app/api/status
curl https://verzek-auto-trader.replit.app/signals
```

Should show recent signal data.

---

## 📋 PHASE 4: Automatic Recovery & Monitoring

### **Step 1: Create watchdog script**

```bash
cat > /opt/verzek_watchdog.sh << 'EOF'
#!/bin/bash
LOG_FILE="/var/log/verzek_watchdog.log"
ADMIN_CHAT_ID="572038606"
TELEGRAM_BOT_TOKEN="8351047055:AAEqBFx5g0NJpEvUOCP_DCPD0VsGpEAjvRE"
EMAIL="support@vezekinnovative.com"

send_telegram_alert() {
    curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
        -d chat_id="$ADMIN_CHAT_ID" \
        -d text="⚠️ Watchdog Alert: Service $1 was restarted on $(hostname) at $(date '+%Y-%m-%d %H:%M:%S')" > /dev/null
}

send_email_alert() {
    echo "Verzek Watchdog restarted $1 on $(date)" | mail -s "⚠️ Verzek Watchdog Alert" "$EMAIL" 2>/dev/null || true
}

while true; do
    for svc in verzekbot verzekapi; do
        if ! systemctl is-active --quiet "$svc"; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') ⚠️ Service $svc is down. Restarting..." >> "$LOG_FILE"
            systemctl restart "$svc"
            send_telegram_alert "$svc"
            send_email_alert "$svc"
            echo "$(date '+%Y-%m-%d %H:%M:%S') ✅ Service $svc restarted" >> "$LOG_FILE"
        fi
    done
    sleep 120
done
EOF
```

### **Step 2: Make it executable**

```bash
sudo chmod +x /opt/verzek_watchdog.sh
```

### **Step 3: Create watchdog service**

```bash
cat > /etc/systemd/system/verzekwatchdog.service << 'EOF'
[Unit]
Description=Verzek Auto Trader Watchdog
After=network.target

[Service]
Type=simple
ExecStart=/opt/verzek_watchdog.sh
Restart=always
RestartSec=10
User=root

[Install]
WantedBy=multi-user.target
EOF
```

### **Step 4: Enable and start watchdog**

```bash
sudo systemctl daemon-reload
sudo systemctl enable verzekwatchdog
sudo systemctl start verzekwatchdog
sudo systemctl status verzekwatchdog
```

Expected output: `Active: active (running)`

### **Step 5: Create status monitoring script**

```bash
cat > /opt/verzek_status.sh << 'EOF'
#!/bin/bash

echo "================================================"
echo "🚀 VERZEK AUTO TRADER - SYSTEM STATUS"
echo "================================================"
echo ""

echo "📊 SERVICE STATUS:"
echo "----------------------------------------"
for svc in verzekbot verzekapi verzekwatchdog; do
    if systemctl is-active --quiet "$svc"; then
        echo "✅ $svc: RUNNING"
    else
        echo "❌ $svc: STOPPED"
    fi
done

echo ""
echo "🌐 NETWORK STATUS:"
echo "----------------------------------------"
if ss -tuln | grep -q ":5000"; then
    echo "✅ Port 5000: LISTENING"
else
    echo "❌ Port 5000: NOT LISTENING"
fi

echo ""
echo "🔗 BACKEND CONNECTIVITY:"
echo "----------------------------------------"
response=$(curl -s -w "\n%{http_code}" http://localhost:5000/ping 2>/dev/null)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "200" ]; then
    echo "✅ Backend API: RESPONDING"
    echo "   Response: $body"
else
    echo "❌ Backend API: NOT RESPONDING (HTTP $http_code)"
fi

echo ""
echo "🌉 REPLIT BRIDGE STATUS:"
echo "----------------------------------------"
bridge_response=$(curl -s -w "\n%{http_code}" -m 5 https://verzek-auto-trader.replit.app/ping 2>/dev/null)
bridge_code=$(echo "$bridge_response" | tail -n1)
bridge_body=$(echo "$bridge_response" | head -n-1)

if [ "$bridge_code" = "200" ]; then
    echo "✅ Replit Bridge: CONNECTED"
    echo "   Response time: $(curl -s -w "%{time_total}s" -o /dev/null https://verzek-auto-trader.replit.app/ping 2>/dev/null)"
else
    echo "⚠️ Replit Bridge: TIMEOUT OR ERROR (HTTP $bridge_code)"
fi

echo ""
echo "📝 RECENT WATCHDOG LOGS:"
echo "----------------------------------------"
if [ -f /var/log/verzek_watchdog.log ]; then
    tail -n 5 /var/log/verzek_watchdog.log
else
    echo "No watchdog logs found"
fi

echo ""
echo "================================================"
EOF

chmod +x /opt/verzek_status.sh
```

### **Step 6: Test watchdog**

Stop a service manually:
```bash
sudo systemctl stop verzekbot
```

Wait 2-3 minutes and check:
```bash
sudo systemctl status verzekbot
tail /var/log/verzek_watchdog.log
```

You should see:
- Service automatically restarted
- Log entry showing restart
- Telegram message sent to admin

---

## 📋 PHASE 5: Enhanced Alerting

Already included in Phase 4 watchdog script!

The watchdog now:
- ✅ Monitors verzekbot and verzekapi every 2 minutes
- ✅ Auto-restarts failed services
- ✅ Sends Telegram alerts to admin (572038606)
- ✅ Sends email alerts (if mail is configured)
- ✅ Logs all events to /var/log/verzek_watchdog.log

---

## 🚀 VERIFICATION COMMANDS

Run these to verify everything is working:

```bash
# Check all services
bash /opt/verzek_status.sh

# Test backend
curl http://localhost:5000/ping

# Test external access
curl http://80.240.29.142:5000/ping

# Test bridge
curl https://verzek-auto-trader.replit.app/ping

# Check logs
tail -50 /var/log/verzek_watchdog.log
journalctl -u verzekapi -n 50
journalctl -u verzekbot -n 50
journalctl -u verzekwatchdog -n 50
```

---

## ✅ SUCCESS CHECKLIST

- [ ] verzekapi service is running
- [ ] verzekbot service is running
- [ ] verzekwatchdog service is running
- [ ] Port 5000 is open in firewall
- [ ] Backend responds to curl http://localhost:5000/ping
- [ ] Backend accessible externally at http://80.240.29.142:5000/ping
- [ ] Replit bridge forwards to backend successfully
- [ ] Watchdog auto-restarts failed services
- [ ] Telegram alerts working
- [ ] Status script shows all green ✅

---

**Created:** October 28, 2025  
**Status:** Ready for deployment on Vultr server
