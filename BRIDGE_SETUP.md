# Replit Bridge Setup - COMPLETE ✅

## Overview
Your Replit project (`https://verzek-auto-trader.replit.app`) now acts as an HTTPS bridge that forwards all requests to your Vultr backend server.

---

## ✅ What's Configured

### **1. Bridge API (bridge.py)**
- **Status:** Running on port 5000
- **Public URL:** https://verzek-auto-trader.replit.app
- **Backend Target:** http://80.240.29.142:5000 (Your Vultr server)

### **2. Forwarded Endpoints**

| Replit Endpoint | Forwards To | Purpose |
|----------------|-------------|---------|
| `/` | Vultr `/` | Bridge status check |
| `/ping` | Vultr `/ping` | Health check |
| `/status` | Vultr `/status` | System status |
| `/signals` | Vultr `/logs` | Trading signals/logs |
| `/api/*` | Vultr `/api/*` | All API endpoints (supports GET, POST, PUT, DELETE, PATCH) |
| `/health` | Local | Replit health check |

### **3. Features**

✅ **Full HTTP Method Support**: GET, POST, PUT, DELETE, PATCH  
✅ **Header Forwarding**: Preserves all request headers (except host)  
✅ **Timeout Protection**: 10-second timeout for API calls, 6 seconds for others  
✅ **Error Handling**: Returns proper error codes (502 for backend errors, 504 for timeouts)  
✅ **Logging**: All requests logged with timestamps  
✅ **HTTPS**: Replit provides automatic HTTPS for your bridge  

---

## 📱 Testing Your Bridge

### **Test Bridge Status:**
```bash
curl https://verzek-auto-trader.replit.app/
```

**Expected Response:**
```json
{
  "bridge": "VerzekAutoTrader",
  "status": "running",
  "backend": "http://80.240.29.142:5000",
  "message": "HTTPS bridge active - forwarding to Vultr backend"
}
```

### **Test Ping (Vultr Health):**
```bash
curl https://verzek-auto-trader.replit.app/ping
```

### **Test Status (Vultr System):**
```bash
curl https://verzek-auto-trader.replit.app/status
```

### **Test API Forwarding:**
```bash
# Example: User login
curl -X POST https://verzek-auto-trader.replit.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'
```

---

## 🔧 Mobile App Configuration

Your mobile app should now point to:
```javascript
const API_BASE_URL = "https://verzek-auto-trader.replit.app";
```

**No code changes needed!** The bridge automatically forwards all requests to your Vultr backend.

---

## ⚙️ Vultr Backend Requirements

Make sure your Vultr server is:

1. **Running 24/7:**
   ```bash
   sudo systemctl status verzekbot
   ```

2. **Listening on Port 5000:**
   ```bash
   ss -tlnp | grep 5000
   ```

3. **Accepting External Connections:**
   ```bash
   # Check if binding to 0.0.0.0 (not just 127.0.0.1)
   netstat -an | grep 5000
   ```

4. **Firewall Allows Port 5000:**
   ```bash
   sudo ufw status
   # Should show: 5000/tcp ALLOW Anywhere
   ```

---

## 🔄 Workflow Configuration

The bridge runs as a Replit workflow:

- **Workflow Name:** VerzekBridge
- **Command:** `python bridge.py`
- **Port:** 5000 (mapped to external port 80)
- **Output:** Webview (accessible via browser)

---

## 📊 Monitoring

### **Check Bridge Logs:**
Use Replit's built-in logs viewer or:
```bash
# View live logs
tail -f /tmp/logs/VerzekBridge_*.log
```

### **Common Log Messages:**
- `🌉 VerzekBridge starting...` - Bridge initialized
- `Forwarding /api/... to Vultr` - Request being proxied
- `Backend timeout` - Vultr server didn't respond in time
- `error: str(e)` - Connection error to Vultr

---

## ⚠️ Important Notes

### **1. Expo Dev Server Still Running**
The mobile app development server (Expo) is still active on port 8080. This is separate from the bridge and doesn't interfere.

### **2. Signal Broadcasting Disabled**
The bridge **only** forwards requests. The following services are now **disabled**:
- ❌ Telethon signal monitoring
- ❌ Broadcast bot
- ❌ Auto-trading engine

If you need signal broadcasting, you should run those services on your Vultr server instead.

### **3. Deployment Configuration**
The current `.replit` deployment config uses Gunicorn for `api_server.py`. To deploy the bridge in production, update `.replit`:

```toml
[deployment]
deploymentTarget = "vm"
run = ["python", "bridge.py"]
build = ["pip", "install", "-r", "requirements.txt"]
```

---

## 🚀 Next Steps

1. **Verify Vultr Backend:**
   ```bash
   curl http://80.240.29.142:5000/ping
   ```
   If this fails, check:
   - Is the server running? (`systemctl status verzekbot`)
   - Is the firewall open? (`sudo ufw allow 5000/tcp`)
   - Is it binding to 0.0.0.0? (check Flask/Gunicorn config)

2. **Test from Mobile App:**
   - Open your React Native app
   - Try login/registration
   - Check if signals appear
   - Verify all API calls work

3. **Monitor Performance:**
   - Watch bridge logs for errors
   - Check Vultr server resources (CPU, RAM, network)
   - Ensure response times are acceptable

---

## 🔧 Troubleshooting

### **"Backend timeout" errors:**
- Vultr server is slow or overloaded
- Network connectivity issues
- Increase timeout in `bridge.py` (current: 10s for API, 6s for others)

### **"502 Bad Gateway" errors:**
- Vultr server is down
- Port 5000 is not accessible
- Firewall blocking connections

### **"404 Not Found" errors:**
- Endpoint doesn't exist on Vultr backend
- Check Vultr API routes match bridge routes

### **Replit Bridge Not Starting:**
- Port 5000 conflict (check workflows)
- Missing dependencies (`pip install flask requests`)
- Syntax errors in `bridge.py`

---

## 📚 Related Files

- `bridge.py` - Main bridge application
- `.replit` - Workflow configuration
- `TELEGRAM_BOTS_REFERENCE.md` - Bot configuration reference
- `TELEGRAM_BOTS_IDS.md` - Bot IDs and admin configuration

---

**Last Updated:** October 28, 2025  
**Bridge Version:** 1.0  
**Status:** ✅ Active and Running
