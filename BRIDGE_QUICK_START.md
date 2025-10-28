# 🌉 Replit Bridge - Quick Start Guide

## ✅ Setup Complete!

Your Replit project is now a **secure HTTPS bridge** between your mobile app and Vultr backend.

---

## 📊 Current Status

| Component | Status | Details |
|-----------|--------|---------|
| **Replit Bridge** | ✅ Running | Port 5000, HTTPS enabled |
| **Vultr Backend** | ⚠️ Check Required | http://80.240.29.142:5000 |
| **Public URL** | ✅ Active | https://verzek-auto-trader.replit.app |
| **Expo Dev Server** | ✅ Running | Port 8080 (mobile app dev) |

---

## 🔗 Your Bridge Endpoints

### **Test Bridge (Local):**
```bash
curl http://localhost:5000/
```

### **Test Bridge (Public):**
```bash
curl https://verzek-auto-trader.replit.app/
```

### **Expected Response:**
```json
{
  "backend": "http://80.240.29.142:5000",
  "bridge": "VerzekAutoTrader",
  "message": "HTTPS bridge active - forwarding to Vultr backend",
  "status": "running"
}
```

---

## ⚠️ Next Steps - CRITICAL

### **1. Start Your Vultr Backend**

SSH into your Vultr server and ensure the backend is running:

```bash
# Check if verzekbot service is running
sudo systemctl status verzekbot

# If not running, start it
sudo systemctl start verzekbot

# Enable auto-start on boot
sudo systemctl enable verzekbot
```

### **2. Verify Vultr is Accessible**

From your local machine or Replit:

```bash
# Test direct connection to Vultr
curl http://80.240.29.142:5000/ping

# If this fails, check:
# - Is the server running?
# - Is port 5000 open in firewall?
# - Is Flask/Gunicorn binding to 0.0.0.0 (not 127.0.0.1)?
```

### **3. Open Vultr Firewall**

If the curl command above fails:

```bash
# On Vultr server, run:
sudo ufw allow 5000/tcp
sudo ufw reload
sudo ufw status
```

### **4. Update Mobile App**

In your React Native app config, ensure:

```javascript
// API configuration
const API_BASE_URL = "https://verzek-auto-trader.replit.app";

// All API calls should use this base URL
export default {
  apiUrl: API_BASE_URL,
};
```

---

##  Forwarded Endpoints

| Mobile App Calls | Replit Bridge | Vultr Backend |
|------------------|---------------|---------------|
| `GET /ping` | → | `GET /ping` |
| `GET /status` | → | `GET /status` |
| `GET /signals` | → | `GET /logs` |
| `POST /api/auth/login` | → | `POST /api/auth/login` |
| `GET /api/user/profile` | → | `GET /api/user/profile` |
| **Any /api/* endpoint** | → | **Same endpoint** |

---

## 🔧 Troubleshooting

### **"Backend timeout" Error**

**Symptom:** `{"error": "Backend timeout"}`

**Causes:**
1. Vultr server is not running
2. Vultr firewall blocking port 5000
3. Network issues

**Solutions:**
```bash
# On Vultr server:
sudo systemctl restart verzekbot
sudo ufw allow 5000/tcp
ss -tlnp | grep 5000  # Verify port is listening
```

### **"502 Bad Gateway" Error**

**Symptom:** `{"error": "Connection refused"}`

**Causes:**
1. Vultr backend is down
2. Wrong IP address or port

**Solutions:**
- Verify Vultr IP: `80.240.29.142`
- Check if backend is running on port 5000
- Ping the server: `ping 80.240.29.142`

---

## 📱 Mobile App Testing

Once Vultr backend is running:

1. **Test Login:**
   ```bash
   curl -X POST https://verzek-auto-trader.replit.app/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "test123"}'
   ```

2. **Test in React Native App:**
   - Open the app
   - Try login/registration
   - Check if signals load
   - Verify dashboard data

---

## 📊 Monitoring

### **View Bridge Logs:**
```bash
# In Replit shell:
tail -f /tmp/logs/VerzekBridge_*.log
```

### **What to Look For:**
- ✅ `Forwarding /api/... to Vultr` - Request proxied successfully
- ✅ `200 -` HTTP status - Successful response
- ❌ `Backend timeout` - Vultr not responding
- ❌ `Connection refused` - Vultr not accessible

---

## ⚙️ Vultr Backend Checklist

Before the bridge works fully, ensure:

- [ ] Vultr server is powered on
- [ ] `verzekbot` service is running (`systemctl status verzekbot`)
- [ ] Port 5000 is open in firewall (`ufw status`)
- [ ] Flask/Gunicorn binding to `0.0.0.0:5000` (not `127.0.0.1`)
- [ ] All environment variables set (Telegram tokens, DB credentials, etc.)
- [ ] Database is accessible and migrations run

---

## 🚀 Quick Verification Commands

Run these to confirm everything is working:

```bash
# 1. Test Bridge Status (should succeed)
curl https://verzek-auto-trader.replit.app/

# 2. Test Vultr Direct (should succeed when backend is running)
curl http://80.240.29.142:5000/ping

# 3. Test Bridge → Vultr (should succeed when backend is running)
curl https://verzek-auto-trader.replit.app/ping

# 4. Test API Forwarding (replace with real credentials)
curl -X POST https://verzek-auto-trader.replit.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@test.com", "password": "test"}'
```

If all 4 commands return valid responses, your bridge is **fully operational**! 🎉

---

## 📚 Complete Documentation

- **BRIDGE_SETUP.md** - Full setup and configuration guide
- **TELEGRAM_BOTS_IDS.md** - Bot IDs and admin configuration
- **replit.md** - Project architecture and recent changes

---

**Created:** October 28, 2025  
**Status:** ✅ Bridge Running, ⏳ Awaiting Vultr Backend
