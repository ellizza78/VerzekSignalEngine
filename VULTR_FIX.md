# 🔧 Vultr Backend Port Binding Fix

## Issue: Backend Not Responding on Port 8000

**Problem:** Services are running but the backend API isn't responding to HTTP requests.

**Root Cause:** Port mismatch between systemd service configuration and application binding.

---

## 🔍 Diagnostic Commands (Run on Vultr)

```bash
# 1. Check which ports Python processes are listening on
netstat -tlnp | grep python
# Expected: Should show python listening on 0.0.0.0:8050 (or 8000)

# 2. Check running processes
ps aux | grep -E "gunicorn|api_server"
# Expected: Should show gunicorn with --bind parameter

# 3. Check systemd service configuration
cat /etc/systemd/system/verzek-api.service
# Expected: Should show ExecStart with correct port

# 4. Check backend logs for startup errors
journalctl -u verzek-api.service -n 100 --no-pager | grep -E "bind|port|error|started"
# Look for: "Booting worker" or "Listening at" messages

# 5. Try both ports
curl http://localhost:8000/api/ping
curl http://localhost:8050/api/ping
# One should respond with {"status":"ok"}
```

---

## ✅ Fix #1: Correct systemd Service Configuration

**Check current config:**
```bash
cat /etc/systemd/system/verzek-api.service
```

**Should contain:**
```ini
[Unit]
Description=Verzek API Server
After=network.target postgresql.service

[Service]
Type=notify
User=root
WorkingDirectory=/root/VerzekBackend/backend
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="DATABASE_URL=postgresql://..."
ExecStart=/usr/local/bin/gunicorn --bind 0.0.0.0:8050 --workers 4 --timeout 120 --worker-class sync api_server:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Key Points:**
- ✅ `--bind 0.0.0.0:8050` (not 8000!)
- ✅ `WorkingDirectory=/root/VerzekBackend/backend` (correct path)
- ✅ `api_server:app` (entry point)

**If incorrect, fix it:**
```bash
sudo nano /etc/systemd/system/verzek-api.service
# Update the ExecStart line to use port 8050

sudo systemctl daemon-reload
sudo systemctl restart verzek-api.service
sudo systemctl status verzek-api.service
```

---

## ✅ Fix #2: Verify Environment Variables

```bash
# Check if DATABASE_URL is set
cat /root/VerzekBackend/backend/.env | grep DATABASE_URL

# If missing or incorrect:
sudo nano /root/VerzekBackend/backend/.env

# Add:
DATABASE_URL=postgresql://user:password@localhost:5432/verzek_db
PORT=8050
```

---

## ✅ Fix #3: Check Directory Structure

```bash
# Ensure backend is in correct location
ls -la /root/VerzekBackend/backend/
# Should show: api_server.py, requirements.txt, models.py, etc.

# If backend is in wrong location:
cd /root
mv backend VerzekBackend/ 2>/dev/null || echo "Already in correct location"

# Update systemd service path
sudo nano /etc/systemd/system/verzek-api.service
# Set: WorkingDirectory=/root/VerzekBackend/backend

sudo systemctl daemon-reload
sudo systemctl restart verzek-api.service
```

---

## ✅ Fix #4: Dependencies Check

```bash
cd /root/VerzekBackend/backend

# Reinstall dependencies (force upgrade)
pip3 install --upgrade -r requirements.txt

# Verify gunicorn is installed
which gunicorn
# Expected: /usr/local/bin/gunicorn

# If not found:
pip3 install gunicorn
```

---

## ✅ Fix #5: Firewall/Network Check

```bash
# Check if port 8050 is open
sudo ufw status | grep 8050

# If firewall is enabled and port not open:
sudo ufw allow 8050/tcp
sudo ufw reload

# Check if Nginx is proxying correctly (if using Nginx)
sudo nginx -t
sudo systemctl status nginx
```

---

## 🧪 Validation (After Fixes)

```bash
# 1. Wait for service to fully start
sleep 10

# 2. Check service status
sudo systemctl status verzek-api.service
# Should show: "active (running)"

# 3. Check logs for successful start
journalctl -u verzek-api.service -n 50 --no-pager | tail -20
# Look for: "Booting worker", "Listening at http://0.0.0.0:8050"

# 4. Test API locally
curl http://localhost:8050/api/ping
# Expected: {"status":"ok","service":"VerzekBackend","version":"2.1.1"}

# 5. Test from external IP (if domain configured)
curl https://api.verzekinnovative.com/api/ping
# Expected: Same response as above

# 6. Check new exchange balance endpoint
journalctl -u verzek-api.service -n 200 --no-pager | grep "exchange.*balance"
# Should show route registration or API calls
```

---

## 🆘 Emergency Restart (If All Else Fails)

```bash
# Stop all services
sudo systemctl stop verzek-api.service
sudo systemctl stop verzek-worker.service
sudo systemctl stop verzek-signalengine.service

# Check for zombie processes
ps aux | grep -E "gunicorn|api_server" | grep -v grep
# If any found, kill them:
killall gunicorn 2>/dev/null

# Restart services
sudo systemctl start verzek-api.service
sudo systemctl start verzek-worker.service
sudo systemctl start verzek-signalengine.service

# Check status
sudo systemctl status verzek-api.service
```

---

## 📊 Service Names Reference

Your Vultr server uses these service names:
- **Backend API:** `verzek-api.service` (NOT `backend-api.service`)
- **Signal Engine:** `verzek-signalengine.service`
- **Worker:** `verzek-worker.service`
- **Watchdog:** `verzek-watchdog.service`

Always use the `verzek-*` prefix when managing services.

---

## ✅ Success Criteria

After fixes, you should see:
1. ✅ `systemctl status verzek-api.service` shows "active (running)"
2. ✅ `curl http://localhost:8050/api/ping` returns valid JSON
3. ✅ `journalctl -u verzek-api.service -n 20` shows no errors
4. ✅ `netstat -tlnp | grep 8050` shows gunicorn listening

---

**Next:** After backend is fixed, test mobile app and build APK.
