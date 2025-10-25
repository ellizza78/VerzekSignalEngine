# Replit Configuration for Vultr Proxy
## Switch from Cloudflare Workers to Vultr Infrastructure

---

## 🔄 Migration Overview

Your existing `ProxyHelper` in `exchanges/proxy_helper.py` already supports the Vultr infrastructure! You just need to update your Replit Secrets to point to your Vultr hub instead of Cloudflare Workers.

**No code changes required!** ✅

---

## 📋 Required Replit Secrets

After deploying your Vultr infrastructure, update these secrets:

### Current (Cloudflare Workers)
```bash
PROXY_ENABLED=true
PROXY_URL=https://verzek-proxy.workers.dev
PROXY_SECRET_KEY=<cloudflare_secret>
```

### New (Vultr Infrastructure)
```bash
PROXY_ENABLED=true
PROXY_URL=https://verzekhub.yourdomain.com
PROXY_SECRET_KEY=<vultr_secret>
```

---

## 🔐 Setting Replit Secrets

### Option 1: Via Replit UI

1. Open your Replit project
2. Click **Tools** → **Secrets**
3. Update or add these secrets:

| Secret Key | Value | Example |
|------------|-------|---------|
| `PROXY_ENABLED` | `true` | `true` |
| `PROXY_URL` | Your Vultr hub URL | `https://verzekhub.yourdomain.com` |
| `PROXY_SECRET_KEY` | Your generated secret | `a1b2c3d4e5f6789...` |

### Option 2: Via `.env` (Development Only)

**⚠️ Never commit `.env` to Git!**

```bash
# .env (for local testing)
PROXY_ENABLED=true
PROXY_URL=https://verzekhub.yourdomain.com
PROXY_SECRET_KEY=a1b2c3d4e5f6789...
```

---

## ✅ Verification

### 1. Check Secrets Are Loaded

Add this to your code temporarily:

```python
import os

print("PROXY_ENABLED:", os.getenv("PROXY_ENABLED"))
print("PROXY_URL:", os.getenv("PROXY_URL"))
print("PROXY_SECRET:", "*" * 20 if os.getenv("PROXY_SECRET_KEY") else "NOT SET")
```

**Expected output:**
```
PROXY_ENABLED: true
PROXY_URL: https://verzekhub.yourdomain.com
PROXY_SECRET: ********************
```

### 2. Test Proxy Connection

```python
from exchanges.proxy_helper import get_proxy_helper

proxy = get_proxy_helper()

# Test health endpoint
response = proxy.request(
    method="GET",
    url="https://verzekhub.yourdomain.com/health",
    timeout=10
)

print(response.json())
# Expected: {"status": "ok", "service": "VerzekProxyMesh"}
```

### 3. Test Exchange API Call

```python
from exchanges.exchange_interface import ExchangeFactory

factory = ExchangeFactory()
client = factory.get_client(
    "binance",
    api_key="YOUR_API_KEY",
    api_secret="YOUR_API_SECRET"
)

# This should work without IP rejection now!
balance = client.get_balance()
print(balance)
```

---

## 🔄 How It Works

### Request Flow

```
Your Code (Replit)
    ↓
ProxyHelper (exchanges/proxy_helper.py)
    ├─ Checks PROXY_ENABLED
    ├─ Generates HMAC signature
    ├─ Adds X-Proxy-Signature header
    └─ Adds X-Exchange-Host header
    ↓ HTTPS Request
Vultr Hub (verzekhub.yourdomain.com)
    ├─ Nginx (SSL termination)
    ├─ HAProxy (load balancer)
    └─ FastAPI (verifies signature)
    ↓ Proxies to
Binance API
    └─ Sees request from 45.76.90.149 ✅
```

### Headers Added Automatically

The `ProxyHelper` automatically adds these headers:

```python
{
    "X-Exchange-Host": "fapi.binance.com",
    "X-Proxy-Signature": "a1b2c3d4...",  # HMAC-SHA256
    "Content-Type": "application/json",
    # ... plus your original headers (API keys, etc.)
}
```

---

## 🎯 Binance IP Whitelisting

### Step 1: Whitelist Static IP

1. Go to **Binance** → **API Management**
2. Edit your API key
3. Enable **"Restrict access to trusted IPs only"**
4. Add IP: **45.76.90.149** (your Vultr hub)
5. Save changes

### Step 2: Verify It Works

```python
# This should now work without "IP not whitelisted" errors
from exchanges.binance_client import BinanceClient

client = BinanceClient(
    api_key="YOUR_KEY",
    api_secret="YOUR_SECRET"
)

# Test with a simple API call
server_time = client.get_server_time()
print(f"Binance server time: {server_time}")

# If this works, your proxy is configured correctly! ✅
```

---

## 🛠️ Troubleshooting

### Issue: "PROXY_URL not set" Warning

**Solution:** Check Replit Secrets are configured correctly.

```bash
# In Replit Shell
echo $PROXY_URL
# Should output: https://verzekhub.yourdomain.com
```

### Issue: "Invalid signature" Error

**Problem:** Secret key mismatch between Replit and Vultr.

**Solution:**
1. Check `PROXY_SECRET_KEY` in Replit Secrets
2. Verify it matches the secret on Vultr nodes:
```bash
# On Vultr nodes
systemctl status verzek-proxy | grep PROXY_SECRET
```
3. Update if they don't match

### Issue: Binance Still Rejects IP

**Solution:**
1. Verify proxy is working:
```bash
curl https://verzekhub.yourdomain.com/health
```

2. Check IP is whitelisted:
   - Binance → API Management → Your Key
   - Should show: `45.76.90.149`

3. Test from Replit:
```python
import requests
response = requests.get("https://verzekhub.yourdomain.com/ip")
print(response.json())
# Your Vultr hub IP should be shown
```

### Issue: "Connection timeout" Errors

**Problem:** Firewall blocking traffic or service down.

**Solution:**
1. Check Vultr firewall allows HTTPS (port 443)
2. Verify services running:
```bash
ssh root@45.76.90.149
systemctl status nginx
systemctl status haproxy
systemctl status verzek-proxy
```

---

## 🔄 Fallback Behavior

The `ProxyHelper` has built-in fallback logic:

```python
try:
    # Try proxy
    response = requests.get(proxy_url, ...)
except RequestException:
    print("[PROXY ERROR] Falling back to direct connection")
    # Fallback to direct API call
    response = requests.get(exchange_url, ...)
```

This means:
- ✅ If proxy is down, trading still works (but may get IP rejection)
- ✅ Automatic recovery when proxy comes back online
- ✅ No manual intervention needed

---

## 📊 Monitoring

### Check Proxy Status from Replit

```python
from exchanges.proxy_helper import get_proxy_helper

proxy = get_proxy_helper()

# Health check
response = proxy.request("GET", "https://verzekhub.yourdomain.com/health")
print(response.json())

# Expected: {"status": "ok", "service": "VerzekProxyMesh"}
```

### Check Vultr Services

```bash
# SSH to hub
ssh root@45.76.90.149

# Check all services
systemctl status nginx
systemctl status haproxy
systemctl status verzek-proxy

# View proxy logs
journalctl -u verzek-proxy -f
```

---

## 💡 Pro Tips

### 1. Test Proxy Before Enabling

```python
# Test connection first
import requests

response = requests.get("https://verzekhub.yourdomain.com/health")
if response.status_code == 200:
    print("✅ Proxy is ready!")
    # Now enable in secrets
else:
    print("❌ Proxy not responding")
```

### 2. Gradual Migration

```python
# Start with proxy disabled
PROXY_ENABLED=false

# Test your Vultr setup
# Once confirmed working:
PROXY_ENABLED=true
```

### 3. Multiple Environments

```python
# Development
PROXY_ENABLED=false  # Direct connection for testing
PROXY_URL=

# Production
PROXY_ENABLED=true
PROXY_URL=https://verzekhub.yourdomain.com
```

---

## 📝 Configuration Checklist

Before enabling the proxy:

- [ ] Vultr infrastructure deployed and running
- [ ] Domain pointing to hub IP (45.76.90.149)
- [ ] SSL certificate installed (Let's Encrypt)
- [ ] All services running (Nginx, HAProxy, FastAPI)
- [ ] Proxy secret generated and saved
- [ ] Health endpoint responding: `https://verzekhub.yourdomain.com/health`
- [ ] Replit Secrets updated:
  - [ ] `PROXY_ENABLED=true`
  - [ ] `PROXY_URL=https://verzekhub.yourdomain.com`
  - [ ] `PROXY_SECRET_KEY=<your_secret>`
- [ ] Binance API key whitelisted to 45.76.90.149
- [ ] Test exchange API call successful

---

## 🎉 Success!

Once configured, all your exchange API calls will automatically route through your Vultr infrastructure:

```
✅ Static IP: 45.76.90.149
✅ No more IP rejection errors
✅ Reliable trading 24/7
✅ Automatic failover
```

---

**Support:** support@vezekinnovative.com  
**Docs:** See DEPLOYMENT_GUIDE.md for Vultr setup
