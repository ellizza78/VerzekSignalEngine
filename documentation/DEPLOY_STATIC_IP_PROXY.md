# 🌐 STATIC IP PROXY - IMMEDIATE DEPLOYMENT GUIDE

## ⚡ **QUICK START** (Recommended: Cloudflare Workers)

**Deployment time:** ~5 minutes  
**Cost:** FREE (shared IP) or $200-500/month (dedicated IP)

---

## 📋 **OPTION 1: CLOUDFLARE WORKERS** (Fastest)

### **Step 1: Install Wrangler CLI**
```bash
npm install -g wrangler
```

### **Step 2: Login to Cloudflare**
```bash
wrangler login
```

### **Step 3: Deploy Worker**
```bash
cd cloudflare_proxy
wrangler deploy
```

**Expected output:**
```
✨ Successfully published your Worker
🌍 Your Worker is available at: https://verzek-proxy.YOUR_USERNAME.workers.dev
```

### **Step 4: Set Environment Variables**

**In Replit Secrets, add:**
```bash
PROXY_ENABLED=true
PROXY_URL=https://verzek-proxy.YOUR_USERNAME.workers.dev/proxy
PROXY_SECRET_KEY=YOUR_RANDOM_SECRET_KEY_HERE
```

**Generate secret key:**
```bash
openssl rand -hex 32
```

**In Cloudflare Dashboard:**
1. Go to Workers & Pages → Your Worker → Settings → Variables
2. Add environment variable:
   - Name: `PROXY_SECRET_KEY`
   - Value: (same as above)

### **Step 5: Test Proxy**
```bash
curl https://verzek-proxy.YOUR_USERNAME.workers.dev/health
```

**Expected:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-17T18:30:00.000Z",
  "service": "VerzekAutoTrader Exchange Proxy"
}
```

### **Step 6: Get Your Egress IP**
```bash
curl https://verzek-proxy.YOUR_USERNAME.workers.dev/ip
```

**Note:** Cloudflare Free tier uses shared IPs. For dedicated IP, contact Cloudflare Enterprise.

---

## 📋 **OPTION 2: VULTR VPN MESH** (Dedicated IP)

**Deployment time:** ~30 minutes  
**Cost:** ~$10-20/month (3 Vultr instances)  
**Static IP:** 80.240.29.142 (already available)

### **Prerequisites:**
- SSH access to Vultr server (80.240.29.142)
- Root access

### **Step 1: Prepare Deployment**
```bash
# On your local machine or Replit shell
cd vultr_infrastructure
```

### **Step 2: Update Server Inventory**

Edit `orchestrator.py` line 18-36 with your actual server IPs:
```python
INV = {
    "hub": {
        "ip": "80.240.29.142",  # Your main Vultr server
        "vpn": "10.10.0.1",
        "user": "root",
        "location": "Frankfurt"
    }
    # Add more nodes if you have them for load balancing
}
```

### **Step 3: Run Orchestrator**
```bash
python3 orchestrator.py
```

**This will:**
1. ✅ Install WireGuard, HAProxy, Nginx
2. ✅ Setup VPN mesh network
3. ✅ Configure load balancer
4. ✅ Deploy FastAPI proxy service
5. ✅ Setup SSL with Let's Encrypt
6. ✅ Configure systemd services

### **Step 4: Set Environment Variables**

**In Replit Secrets:**
```bash
PROXY_ENABLED=true
PROXY_URL=https://80.240.29.142:8443/proxy
PROXY_SECRET_KEY=YOUR_RANDOM_SECRET_KEY_HERE
```

### **Step 5: Whitelist IP on Exchanges**

**Binance:**
1. Login → API Management
2. Edit your API key → IP Access Restrictions
3. Add: `80.240.29.142`

**Bybit:**
1. Account & Security → API Management
2. Edit API key → IP Whitelist
3. Add: `80.240.29.142`

**Phemex:**
1. API Keys → Edit
2. IP Restrictions → Add: `80.240.29.142`

---

## 🔧 **MANUAL SETUP (If You Need Custom Configuration)**

### **Create FastAPI Proxy Service**

Save as `/opt/verzek_proxy/main.py` on your server:

```python
#!/usr/bin/env python3
"""
VerzekAutoTrader Static IP Proxy
Provides consistent egress IP for exchange API calls
"""

from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import Response
import httpx
import hmac
import hashlib
import os

app = FastAPI()

PROXY_SECRET = os.getenv("PROXY_SECRET_KEY", "")
ALLOWED_EXCHANGES = [
    "fapi.binance.com",
    "api.bybit.com",
    "api.phemex.com",
    "api.coinexx.com",
    "testnet.binancefuture.com",
    "api-testnet.bybit.com"
]

def verify_signature(body: bytes, signature: str) -> bool:
    """Verify HMAC SHA256 signature"""
    expected = hmac.new(
        PROXY_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    return signature == expected

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "VerzekAutoTrader Proxy",
        "version": "1.0.0"
    }

@app.api_route("/proxy", methods=["GET", "POST", "DELETE"])
async def proxy(
    request: Request,
    x_exchange_host: str = Header(...),
    x_proxy_signature: str = Header(...)
):
    # Verify signature
    body = await request.body()
    if not verify_signature(body, x_proxy_signature):
        raise HTTPException(401, "Invalid signature")
    
    # Validate exchange
    if x_exchange_host not in ALLOWED_EXCHANGES:
        raise HTTPException(403, f"Unauthorized exchange: {x_exchange_host}")
    
    # Get path and query params
    path = request.query_params.get("path", "/")
    query_params = dict(request.query_params)
    query_params.pop("path", None)
    
    # Build target URL
    query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
    url = f"https://{x_exchange_host}{path}"
    if query_string:
        url = f"{url}?{query_string}"
    
    # Forward request
    headers = dict(request.headers)
    headers.pop("x-proxy-signature", None)
    headers.pop("x-exchange-host", None)
    headers["host"] = x_exchange_host
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=body if request.method != "GET" else None
        )
    
    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8443)
```

### **Create Systemd Service**

Save as `/etc/systemd/system/verzek-proxy.service`:

```ini
[Unit]
Description=VerzekAutoTrader Static IP Proxy
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/verzek_proxy
Environment="PROXY_SECRET_KEY=YOUR_SECRET_HERE"
ExecStart=/usr/bin/python3 /opt/verzek_proxy/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
systemctl enable verzek-proxy
systemctl start verzek-proxy
systemctl status verzek-proxy
```

---

## ✅ **VERIFICATION AFTER DEPLOYMENT**

### **Test 1: Health Check**
```bash
# For Cloudflare
curl https://YOUR_WORKER_URL/health

# For Vultr
curl https://80.240.29.142:8443/health
```

**Expected:**
```json
{"status": "healthy", "service": "VerzekAutoTrader Proxy"}
```

### **Test 2: Test Exchange API Call**

**Test Binance through proxy:**
```bash
# Generate signature
BODY=""
SECRET="your_proxy_secret_key"
SIGNATURE=$(echo -n "$BODY" | openssl dgst -sha256 -hmac "$SECRET" | cut -d' ' -f2)

# Make request
curl -X GET "https://YOUR_PROXY_URL/proxy?path=/fapi/v1/ping" \
  -H "X-Exchange-Host: fapi.binance.com" \
  -H "X-Proxy-Signature: $SIGNATURE"
```

**Expected:**
```json
{}
```
(Empty response = success on Binance ping endpoint)

### **Test 3: Verify IP Routing**

**From your app, check if requests go through proxy:**
```python
# In Python
from exchanges.proxy_helper import get_proxy_helper

proxy = get_proxy_helper()
print(f"Proxy enabled: {proxy.proxy_enabled}")
print(f"Proxy URL: {proxy.proxy_url}")
```

---

## 🚨 **TROUBLESHOOTING**

### **Error: "Invalid signature"**
- ✅ Ensure PROXY_SECRET_KEY matches on both client and server
- ✅ Check signature generation (HMAC SHA256 of request body)

### **Error: "Unauthorized exchange host"**
- ✅ Add exchange domain to ALLOWED_EXCHANGES list
- ✅ Verify you're using exact domain (e.g., `fapi.binance.com`)

### **Error: Connection timeout**
- ✅ Check firewall allows traffic on port 8443
- ✅ Verify proxy service is running: `systemctl status verzek-proxy`
- ✅ Check proxy logs: `journalctl -u verzek-proxy -f`

### **Proxy not being used (direct connection)**
- ✅ Verify PROXY_ENABLED=true in environment
- ✅ Check PROXY_URL is set correctly
- ✅ Restart backend API: `systemctl restart verzek_api`

---

## 📊 **MONITORING**

### **Check Proxy Usage**
```bash
# Cloudflare Dashboard → Analytics
# Shows request count, errors, latency

# Vultr - Check logs
journalctl -u verzek-proxy -f
```

### **Performance Metrics**
```bash
# Test latency
time curl https://YOUR_PROXY_URL/health

# Compare direct vs proxy
time curl https://fapi.binance.com/fapi/v1/ping
time curl "https://YOUR_PROXY_URL/proxy?path=/fapi/v1/ping" -H "X-Exchange-Host: fapi.binance.com"
```

---

## 🎯 **RECOMMENDED SETUP FOR IMMEDIATE USE**

**For fastest deployment:**

1. ✅ **Use Cloudflare Workers** (5 minutes setup)
2. ✅ **Deploy with wrangler** (no server needed)
3. ✅ **Set environment variables** in Replit
4. ✅ **Test health endpoint**
5. ✅ **Users can start trading immediately**

**Upgrade to Vultr later if:**
- You need dedicated IP for exchange whitelisting
- Cloudflare shared IP gets rate-limited
- You want full control over infrastructure

---

## 📞 **NEXT STEPS**

1. **Choose deployment option** (Cloudflare recommended)
2. **Run deployment commands** (see above)
3. **Set environment variables** in Replit Secrets
4. **Restart backend API** to load new config
5. **Test with mobile app** - users' exchange calls now route through proxy
6. **Whitelist IP on exchanges** (if using Vultr dedicated IP)

---

**After deployment, ALL users' exchange API calls will automatically route through the static IP proxy!** 🚀

No code changes needed - ProxyHelper is already integrated in all exchange clients.
