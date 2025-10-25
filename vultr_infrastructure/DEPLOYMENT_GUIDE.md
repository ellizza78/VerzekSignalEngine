# Vultr Infrastructure Deployment Guide
## Static IP Proxy for Binance API Whitelisting

This guide provides step-by-step instructions for deploying the Vultr-based static IP proxy infrastructure to fix Binance IP rejection issues.

---

## 🎯 Overview

### The Problem
Binance requires API keys to be restricted to whitelisted IP addresses. Replit uses dynamic IPs that can change on restart/redeploy, causing authentication failures.

### The Solution
Deploy a WireGuard VPN mesh on Vultr servers with:
- **Static egress IP** from Frankfurt hub (45.76.90.149)
- **HAProxy load balancing** across multiple nodes
- **HTTPS with Let's Encrypt** for secure communication
- **FastAPI proxy service** with HMAC authentication

---

## 📋 Prerequisites

### 1. Vultr Account & Servers

You need **3 Vultr Cloud Compute instances**:

| Server | Location | IP | VPN IP | Role |
|--------|----------|-----|--------|------|
| Hub | Frankfurt | 45.76.90.149 | 10.10.0.1 | Load balancer + SSL |
| Node1 | Any | TBD | 10.10.0.2 | Worker |
| Node2 | Any | TBD | 10.10.0.3 | Worker |

**Recommended specs:** 1 vCPU, 1GB RAM, Ubuntu 22.04 LTS

### 2. Domain Name

You need a domain pointing to your hub server:
- **Example:** `verzekhub.yourdomain.com` → `45.76.90.149`
- Create an **A record** in your DNS provider

### 3. SSH Access

Ensure you can SSH into all servers:
```bash
ssh root@45.76.90.149
ssh root@<NODE1_IP>
ssh root@<NODE2_IP>
```

---

## 🚀 Deployment Steps

### Step 1: Update Server Inventory

Edit `orchestrator.py` and update the server IPs:

```python
INV = {
    "hub": {
        "ip": "45.76.90.149",  # Your hub IP
        "vpn": "10.10.0.1",
        "user": "root",
        "location": "Frankfurt"
    },
    "node1": {
        "ip": "YOUR_NODE1_IP",  # Update this
        "vpn": "10.10.0.2",
        "user": "root",
        "location": "Node1"
    },
    "node2": {
        "ip": "YOUR_NODE2_IP",  # Update this
        "vpn": "10.10.0.3",
        "user": "root",
        "location": "Node2"
    }
}
```

### Step 2: Generate Proxy Secret Key

```bash
# Generate a secure random secret
openssl rand -hex 32

# Save this - you'll need it later
# Example: a1b2c3d4e5f6...
```

### Step 3: Deploy Infrastructure (Automated)

Run the orchestrator script from your local machine:

```bash
cd vultr_infrastructure
python3 orchestrator.py
```

This will automatically:
- ✅ Install dependencies on all nodes
- ✅ Configure WireGuard VPN mesh
- ✅ Deploy FastAPI services
- ✅ Setup HAProxy on hub
- ✅ Configure Nginx with SSL
- ✅ Setup firewall rules

**Note:** The script will prompt for your domain and email for SSL certificates.

### Step 4: Manual Deployment (Alternative)

If you prefer manual control, deploy on each server individually:

#### On All Nodes (Hub + Node1 + Node2):

```bash
# 1. Setup WireGuard
./scripts/setup_wireguard.sh hub 10.10.0.1  # Hub
./scripts/setup_wireguard.sh node1 10.10.0.2  # Node1
./scripts/setup_wireguard.sh node2 10.10.0.3  # Node2

# 2. Configure WireGuard peers
# Edit /etc/wireguard/wg0.conf and add peer sections
nano /etc/wireguard/wg0.conf

# 3. Start WireGuard
systemctl enable wg-quick@wg0
systemctl start wg-quick@wg0
wg show

# 4. Deploy FastAPI service
./scripts/deploy_fastapi.sh YOUR_PROXY_SECRET_KEY
```

#### On Hub Only:

```bash
# 5. Setup HAProxy
./scripts/setup_haproxy.sh 10.10.0.2 10.10.0.3 10.10.0.1

# 6. Setup Nginx + SSL
./scripts/setup_nginx_ssl.sh verzekhub.yourdomain.com support@vezekinnovative.com
```

---

## 🔧 Configuration

### WireGuard Peer Configuration

After running `setup_wireguard.sh`, add peers to `/etc/wireguard/wg0.conf`:

**On Hub (10.10.0.1):**
```ini
[Interface]
Address = 10.10.0.1/24
ListenPort = 51820
PrivateKey = <HUB_PRIVATE_KEY>

[Peer]
PublicKey = <NODE1_PUBLIC_KEY>
AllowedIPs = 10.10.0.2/32
Endpoint = <NODE1_EXTERNAL_IP>:51820
PersistentKeepalive = 25

[Peer]
PublicKey = <NODE2_PUBLIC_KEY>
AllowedIPs = 10.10.0.3/32
Endpoint = <NODE2_EXTERNAL_IP>:51820
PersistentKeepalive = 25
```

**On Node1 (10.10.0.2):**
```ini
[Interface]
Address = 10.10.0.2/24
ListenPort = 51820
PrivateKey = <NODE1_PRIVATE_KEY>

[Peer]
PublicKey = <HUB_PUBLIC_KEY>
AllowedIPs = 10.10.0.0/24
Endpoint = 45.76.90.149:51820
PersistentKeepalive = 25
```

Repeat similar configuration for Node2.

---

## ✅ Testing & Verification

### 1. Test WireGuard VPN

From hub, ping worker nodes:
```bash
ping 10.10.0.2  # Should work
ping 10.10.0.3  # Should work
```

### 2. Test FastAPI Service

On each node:
```bash
curl http://localhost:5000/health
# Expected: {"status":"ok","service":"VerzekProxyMesh"}
```

### 3. Test HAProxy

On hub:
```bash
curl http://127.0.0.1:5000/health
# Should route to one of the mesh nodes

# View HAProxy stats
curl http://127.0.0.1:8404/stats
```

### 4. Test Nginx + SSL

From your local machine:
```bash
curl https://verzekhub.yourdomain.com/health
# Expected: {"status":"ok",...}

curl https://verzekhub.yourdomain.com/ip
# Shows your IP information
```

### 5. Test Complete Proxy Flow

From Replit or local machine:
```bash
# Generate signature
BODY=""
SECRET="your_proxy_secret_key"
SIGNATURE=$(echo -n "$BODY" | openssl dgst -sha256 -hmac "$SECRET" | cut -d' ' -f2)

# Make request
curl -X GET "https://verzekhub.yourdomain.com/fapi/v1/time" \
  -H "X-Exchange-Host: fapi.binance.com" \
  -H "X-Proxy-Signature: $SIGNATURE"

# Should return Binance server time
```

---

## 🔐 Replit Configuration

Update your Replit Secrets:

```bash
PROXY_ENABLED=true
PROXY_URL=https://verzekhub.yourdomain.com
PROXY_SECRET_KEY=<your_generated_secret>
```

The existing `ProxyHelper` in `exchanges/proxy_helper.py` will automatically route all exchange API calls through your Vultr infrastructure.

---

## 🎯 Binance IP Whitelisting

### Step 1: Get Your Static IP

Your static egress IP is: **45.76.90.149** (Frankfurt hub)

### Step 2: Whitelist on Binance

1. Go to **Binance** → **API Management**
2. Edit your API key
3. Enable **"Restrict access to trusted IPs only"**
4. Add IP: `45.76.90.149`
5. Save changes

### Step 3: Test Trading

Try a simple balance request through your proxy:
```python
from exchanges.exchange_interface import ExchangeFactory

factory = ExchangeFactory()
client = factory.get_client("binance", api_key="YOUR_KEY", api_secret="YOUR_SECRET")
balance = client.get_balance()
print(balance)
```

Should work without IP rejection! ✅

---

## 🛡️ Security Checklist

- [x] HMAC signature verification on all requests
- [x] Whitelisted exchanges only (Binance, Bybit, Phemex, Kraken)
- [x] UFW firewall enabled on all nodes
- [x] HTTPS with Let's Encrypt SSL
- [x] Auto-renewal for SSL certificates
- [x] WireGuard encrypted VPN mesh
- [x] No public access to worker nodes
- [x] Proxy secret stored in environment variables

---

## 📊 Monitoring

### Service Status

Check all services on each node:
```bash
# WireGuard
wg show
systemctl status wg-quick@wg0

# FastAPI
systemctl status verzek-proxy
journalctl -u verzek-proxy -f

# HAProxy (hub only)
systemctl status haproxy
journalctl -u haproxy -f

# Nginx (hub only)
systemctl status nginx
tail -f /var/log/nginx/verzek-access.log
```

### HAProxy Stats Dashboard

Access HAProxy statistics:
```bash
# On hub
curl http://127.0.0.1:8404/stats
```

Or setup port forwarding to view in browser:
```bash
ssh -L 8404:127.0.0.1:8404 root@45.76.90.149
# Then visit: http://localhost:8404/stats
```

---

## 🔄 Maintenance

### Update FastAPI Service

```bash
# On each node
cd /opt/verzek-proxy
source venv/bin/activate
pip install --upgrade fastapi uvicorn httpx
systemctl restart verzek-proxy
```

### Renew SSL Certificate (Manual)

```bash
# On hub
certbot renew
systemctl reload nginx
```

### Restart All Services

```bash
# Full restart sequence
systemctl restart wg-quick@wg0
systemctl restart verzek-proxy
systemctl restart haproxy  # Hub only
systemctl restart nginx    # Hub only
```

---

## ❗ Troubleshooting

### Issue: Binance still rejects IP

**Solution:**
1. Verify proxy is working: `curl https://verzekhub.yourdomain.com/health`
2. Check Replit secrets: `PROXY_ENABLED=true`, `PROXY_URL` correct
3. Confirm IP whitelisted: 45.76.90.149
4. Test signature generation in `proxy_helper.py`

### Issue: WireGuard VPN not connecting

**Solution:**
```bash
# Check WireGuard status
wg show

# Check firewall
ufw status
ufw allow 51820/udp

# Restart WireGuard
systemctl restart wg-quick@wg0
```

### Issue: HAProxy shows backends down

**Solution:**
```bash
# Check FastAPI on each node
systemctl status verzek-proxy

# Test health endpoint
curl http://10.10.0.1:5000/health
curl http://10.10.0.2:5000/health
curl http://10.10.0.3:5000/health

# Check HAProxy config
haproxy -c -f /etc/haproxy/haproxy.cfg
```

### Issue: SSL certificate not renewing

**Solution:**
```bash
# Test renewal
certbot renew --dry-run

# Check cron job
crontab -l | grep certbot

# Force renewal
certbot renew --force-renewal
systemctl reload nginx
```

---

## 💰 Cost Estimate

### Vultr Pricing (as of 2025)

- **3 servers** @ $5/month each = **$15/month**
- **Domain name** = ~$12/year
- **Total**: ~$16.50/month

**Much cheaper than Binance IP whitelisting alternatives!**

---

## 📚 Additional Resources

- [WireGuard Documentation](https://www.wireguard.com/)
- [HAProxy Configuration](http://www.haproxy.org/#docs)
- [Let's Encrypt](https://letsencrypt.org/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vultr Cloud Compute](https://www.vultr.com/products/cloud-compute/)

---

## 🎉 Success!

Once deployed, your architecture will look like this:

```
Replit (VerzekAutoTrader)
    ↓ HTTPS + HMAC
Vultr Hub (45.76.90.149)
    ├─ Nginx (SSL Termination)
    ├─ HAProxy (Load Balancer)
    └─ WireGuard VPN Mesh
        ├─ Hub Node (FastAPI)
        ├─ Node1 (FastAPI)
        └─ Node2 (FastAPI)
            ↓ API Requests
Binance / Bybit / Phemex / Kraken
```

All exchange API calls now route through **45.76.90.149** - a static IP you control! 🚀

---

**Questions?** Contact support: support@vezekinnovative.com
