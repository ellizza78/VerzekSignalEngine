# 🛠️ TROUBLESHOOTING GUIDE - VerzekAutoTrader

**Date:** October 28, 2025  
**Issues Addressed:**
1. Backend connection refused on port 5000
2. Broadcast bot not receiving signals for 3+ hours

---

## 🔍 ISSUE #1: Backend Connection Refused

### **Root Cause:**
The `api_server.py` file had **duplicate `if __name__ == "__main__":` blocks**, causing Flask to start incorrectly with debug mode enabled instead of binding properly to `0.0.0.0:5000`.

### **Symptoms:**
- `curl http://localhost:5000/ping` returns "Connection refused"
- `systemctl status verzekapi` shows "Active (running)" but port 5000 not listening
- Bridge returns HTTP 502/504 timeouts

### **Solution:**

#### **Option 1: Automated Fix (Recommended)**
```bash
# SSH into Vultr server
ssh root@80.240.29.142

# Run the fix script
bash /tmp/FIX_BACKEND.sh
```

#### **Option 2: Manual Fix**
```bash
# SSH into Vultr
ssh root@80.240.29.142

# Edit the file
nano /var/www/VerzekAutoTrader/api_server.py

# Go to the very end of the file
# Delete the duplicate startup code (last ~10 lines)
# Replace with:

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    log_event("API", f"Starting Flask API on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)

# Save and exit (Ctrl+X, Y, Enter)

# Restart service
sudo systemctl restart verzekapi

# Test
curl http://localhost:5000/ping
```

### **Verification:**
```bash
# All three should return JSON {"status": "running", ...}
curl http://localhost:5000/ping
curl http://80.240.29.142:5000/ping
curl https://verzek-auto-trader.replit.app/ping
```

---

## 🔍 ISSUE #2: Broadcast Bot Not Receiving Signals

### **Root Cause:**
The Telethon forwarder service (`verzekbot`) is either:
1. Not running on Vultr
2. Missing Telegram session file
3. Missing environment variables (TELEGRAM_API_ID, TELEGRAM_API_HASH)
4. Signal source channel inactive

### **Symptoms:**
- No signals forwarded for 3+ hours
- No new messages in VIP/TRIAL groups
- `broadcast_log.txt` not updating
- Mobile app shows no new signals

### **Diagnostic Steps:**

#### **Step 1: Check Service Status**
```bash
ssh root@80.240.29.142

# Check if verzekbot is running
systemctl status verzekbot

# If not running:
sudo systemctl start verzekbot
sudo systemctl enable verzekbot
```

#### **Step 2: Check Logs**
```bash
# View live logs
journalctl -u verzekbot -f

# Look for:
# ✅ Good: "[TELETHON] Connected successfully"
# ✅ Good: "🔔 Received message from chat 2249790469"
# ❌ Bad: "ERROR: Missing Telegram API credentials"
# ❌ Bad: "No telethon_session_prod.txt found"
```

#### **Step 3: Verify Session File**
```bash
# Check if session exists
ls -lh /var/www/VerzekAutoTrader/telethon_session_*.txt

# If missing, you need to create it:
cd /var/www/VerzekAutoTrader
source venv/bin/activate
python3 setup_telethon.py
```

#### **Step 4: Verify Environment Variables**
```bash
# Check .env file
cat /var/www/VerzekAutoTrader/.env | grep TELEGRAM

# Should have:
# TELEGRAM_API_ID=your_api_id
# TELEGRAM_API_HASH=your_api_hash

# If missing, add them:
echo "TELEGRAM_API_ID=your_api_id_here" >> /var/www/VerzekAutoTrader/.env
echo "TELEGRAM_API_HASH=your_api_hash_here" >> /var/www/VerzekAutoTrader/.env
```

#### **Step 5: Check Channel Activity**
```bash
# The monitored channel is: 2249790469 (Ai Golden Crypto 🔱VIP)
# Verify it's still active and posting signals

# Check forwarder configuration:
grep "2249790469" /var/www/VerzekAutoTrader/telethon_forwarder.py
```

### **Solution:**

#### **Quick Fix:**
```bash
# Restart verzekbot service
sudo systemctl restart verzekbot

# Watch logs for activity
journalctl -u verzekbot -f

# You should see:
# "[TELETHON] Loading PRODUCTION session"
# "[TELETHON] Connected successfully"
# "🔔 Received message from chat..."
```

#### **If Still No Signals:**

**Possibility 1: Channel is inactive**
- The signal source channel (2249790469) may not have posted any signals in 3+ hours
- This is normal for some trading channels - they only post when there's a setup
- Check the channel manually in Telegram to confirm

**Possibility 2: Session expired**
```bash
# Regenerate session
cd /var/www/VerzekAutoTrader
source venv/bin/activate
python3 setup_telethon.py

# Follow prompts to login again
# Restart service
sudo systemctl restart verzekbot
```

**Possibility 3: Telethon not installed**
```bash
cd /var/www/VerzekAutoTrader
source venv/bin/activate
pip install telethon
sudo systemctl restart verzekbot
```

---

## 🧪 DIAGNOSTIC TOOL

Run this comprehensive diagnostic on your Vultr server:

```bash
bash /tmp/DIAGNOSE_ISSUES.sh
```

This will check:
- ✅ All services status
- ✅ Port 5000 listening
- ✅ Firewall configuration
- ✅ Backend connectivity (local + external)
- ✅ Telethon session files
- ✅ Environment variables
- ✅ Recent logs from all services
- ✅ Replit bridge connection

---

## 📋 COMPLETE DIAGNOSTIC CHECKLIST

### **Backend (Port 5000):**
- [ ] `systemctl status verzekapi` → Active (running)
- [ ] `ss -tuln | grep 5000` → Shows "0.0.0.0:5000" listening
- [ ] `ufw status | grep 5000` → Port allowed
- [ ] `curl http://localhost:5000/ping` → Returns JSON
- [ ] `curl http://80.240.29.142:5000/ping` → Returns JSON (external)
- [ ] `curl https://verzek-auto-trader.replit.app/ping` → Returns JSON (bridge)

### **Telethon Forwarder:**
- [ ] `systemctl status verzekbot` → Active (running)
- [ ] Session file exists: `/var/www/VerzekAutoTrader/telethon_session_prod.txt`
- [ ] Environment variables set: `TELEGRAM_API_ID`, `TELEGRAM_API_HASH`
- [ ] `journalctl -u verzekbot -n 20` → Shows "[TELETHON] Connected successfully"
- [ ] Logs show "🔔 Received message" periodically
- [ ] Channel 2249790469 is active and posting

### **Watchdog:**
- [ ] `systemctl status verzekwatchdog` → Active (running)
- [ ] `/var/log/verzek_watchdog.log` exists and updating
- [ ] Test: Stop verzekbot → Auto-restarts in 2 mins + Telegram alert

---

## 🚀 QUICK RECOVERY COMMANDS

```bash
# Restart everything
sudo systemctl restart verzekapi verzekbot verzekwatchdog

# Check all services
bash /opt/verzek_status.sh

# View live API logs
journalctl -u verzekapi -f

# View live bot logs
journalctl -u verzekbot -f

# View watchdog events
tail -f /var/log/verzek_watchdog.log

# Test endpoints
curl http://localhost:5000/ping
curl https://verzek-auto-trader.replit.app/ping
```

---

## 📞 SUPPORT

If issues persist after trying all solutions:

1. **Collect diagnostic info:**
   ```bash
   bash /tmp/DIAGNOSE_ISSUES.sh > diagnostic_output.txt
   ```

2. **Check service logs:**
   ```bash
   journalctl -u verzekapi -n 100 > api_logs.txt
   journalctl -u verzekbot -n 100 > bot_logs.txt
   ```

3. **Verify file structure:**
   ```bash
   ls -lR /var/www/VerzekAutoTrader
   ```

---

## ✅ SUCCESS INDICATORS

**Backend is working when:**
- All 3 curl tests return JSON with `{"status": "running"}`
- Mobile app can login and fetch data
- No timeouts or connection errors

**Signal forwarding is working when:**
- `journalctl -u verzekbot -f` shows "🔔 Received message" when signals are posted
- VIP/TRIAL groups receive forwarded messages
- `broadcast_log.txt` updates with new signals
- Mobile app shows new signals appearing

---

**Updated:** October 28, 2025  
**Status:** Diagnostic tools created and tested  
**Next Steps:** Run `/tmp/FIX_BACKEND.sh` on Vultr to resolve backend issue
