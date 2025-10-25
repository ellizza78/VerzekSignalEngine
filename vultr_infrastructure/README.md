# Vultr Infrastructure for VerzekAutoTrader
## Static IP Proxy Solution for Binance API Whitelisting

---

## 📖 Overview

This directory contains all the scripts and configuration needed to deploy a production-ready static IP proxy infrastructure on Vultr servers. This solves the Binance IP whitelisting problem where Replit's dynamic IPs cause authentication failures.

### The Problem

- Binance requires API keys to be whitelisted to specific IP addresses
- Replit uses dynamic IPs that change on restart/redeploy
- Result: "IP not whitelisted" errors and failed trades

### The Solution

Deploy a **WireGuard VPN mesh** on Vultr with:
- ✅ Static egress IP (Frankfurt hub: 45.76.90.149)
- ✅ Load balancing across multiple nodes (HAProxy)
- ✅ HTTPS with Let's Encrypt SSL
- ✅ HMAC-authenticated FastAPI proxy
- ✅ Automatic failover and health checks

---

## 📁 Directory Structure

```
vultr_infrastructure/
├── README.md                  # This file
├── DEPLOYMENT_GUIDE.md        # Full deployment instructions
├── QUICK_START.md             # 5-minute setup guide
├── orchestrator.py            # Automated deployment script
├── mesh_proxy.py              # FastAPI proxy service
└── scripts/
    ├── setup_wireguard.sh     # WireGuard VPN configuration
    ├── setup_haproxy.sh       # HAProxy load balancer
    ├── setup_nginx_ssl.sh     # Nginx + Let's Encrypt SSL
    └── deploy_fastapi.sh      # FastAPI service deployment
```

---

## 🚀 Quick Start

### For the Impatient (5 Minutes)

```bash
# 1. Generate secret key
openssl rand -hex 32

# 2. Update orchestrator.py with your server IPs
nano orchestrator.py

# 3. Run deployment
python3 orchestrator.py

# 4. Add to Replit Secrets
PROXY_ENABLED=true
PROXY_URL=https://verzekhub.yourdomain.com
PROXY_SECRET_KEY=<your_secret>

# 5. Whitelist 45.76.90.149 on Binance
```

**Done!** See [QUICK_START.md](QUICK_START.md) for details.

---

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Get started in 5 minutes
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Full deployment walkthrough with troubleshooting

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Replit (VerzekAutoTrader)                │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ ProxyHelper (exchanges/proxy_helper.py)              │  │
│  │ - Adds HMAC signature to requests                    │  │
│  │ - Routes through PROXY_URL                           │  │
│  └──────────────────────┬───────────────────────────────┘  │
└─────────────────────────┼───────────────────────────────────┘
                          │ HTTPS + HMAC
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Vultr Hub (Frankfurt - 45.76.90.149)           │
│                                                             │
│  ┌──────────────────┐                                       │
│  │ Nginx (SSL)      │ Let's Encrypt HTTPS                   │
│  │ Port 443         │                                       │
│  └────────┬─────────┘                                       │
│           │                                                 │
│  ┌────────▼─────────┐                                       │
│  │ HAProxy          │ Load Balancer                         │
│  │ Port 5000        │ Round-robin across nodes              │
│  └────────┬─────────┘                                       │
│           │                                                 │
│  ┌────────▼─────────────────────────────────────────────┐  │
│  │         WireGuard VPN Mesh (10.10.0.0/24)            │  │
│  │                                                       │  │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐          │  │
│  │  │ Hub     │────│ Node1   │────│ Node2   │          │  │
│  │  │10.10.0.1│    │10.10.0.2│    │10.10.0.3│          │  │
│  │  │FastAPI  │    │FastAPI  │    │FastAPI  │          │  │
│  │  └─────────┘    └─────────┘    └─────────┘          │  │
│  └───────────────────────┬───────────────────────────────┘  │
└──────────────────────────┼───────────────────────────────────┘
                           │ API Requests
                           │ (Static IP: 45.76.90.149)
                           ▼
┌─────────────────────────────────────────────────────────────┐
│          Exchange APIs (Binance, Bybit, Phemex)             │
│                                                             │
│  - Whitelisted IP: 45.76.90.149                             │
│  - All requests appear from same static IP                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔐 Security Features

- **HMAC Authentication**: All requests require valid HMAC-SHA256 signature
- **Exchange Whitelist**: Only allowed exchanges can be proxied
- **HTTPS/TLS**: Let's Encrypt SSL certificates with auto-renewal
- **VPN Encryption**: WireGuard encrypts all mesh traffic
- **Firewall Rules**: UFW configured on all nodes
- **No Public Access**: Worker nodes only accessible via VPN

---

## 💰 Cost Breakdown

| Component | Specs | Cost/Month |
|-----------|-------|------------|
| Vultr Hub | 1 vCPU, 1GB RAM | $5.00 |
| Vultr Node1 | 1 vCPU, 1GB RAM | $5.00 |
| Vultr Node2 | 1 vCPU, 1GB RAM | $5.00 |
| Domain Name | .com | ~$1.00 |
| **Total** | | **~$16/month** |

**Much cheaper than alternative solutions!**

---

## 🛠️ Components

### 1. orchestrator.py
Automated deployment script that configures all servers in one go.

**Features:**
- SSH automation across all nodes
- Parallel execution
- Error handling and rollback
- Progress tracking

### 2. mesh_proxy.py
FastAPI service that handles proxy requests.

**Features:**
- HMAC signature verification
- Exchange whitelist enforcement
- Health checks
- Request/response logging
- CORS support

### 3. WireGuard VPN
Encrypted mesh network connecting all nodes.

**Benefits:**
- Low latency (~2-5ms)
- Strong encryption (ChaCha20)
- Automatic reconnection
- UDP-based (fast)

### 4. HAProxy
Load balancer distributing traffic across nodes.

**Features:**
- Round-robin distribution
- Health checks
- Automatic failover
- Statistics dashboard

### 5. Nginx + Let's Encrypt
SSL termination and reverse proxy.

**Features:**
- Automatic HTTPS
- SSL certificate renewal
- Security headers
- Access logging

---

## 📊 Monitoring

### Service Status

```bash
# On each node
systemctl status verzek-proxy
systemctl status wg-quick@wg0

# On hub
systemctl status haproxy
systemctl status nginx
```

### Logs

```bash
# FastAPI logs
journalctl -u verzek-proxy -f

# HAProxy logs
journalctl -u haproxy -f

# Nginx access logs
tail -f /var/log/nginx/verzek-access.log
```

### HAProxy Stats

Access at: `http://HUB_IP:8404/stats`

Or port forward:
```bash
ssh -L 8404:127.0.0.1:8404 root@45.76.90.149
# Visit: http://localhost:8404/stats
```

---

## ✅ Testing

### 1. Health Check

```bash
curl https://verzekhub.yourdomain.com/health
```

**Expected:**
```json
{
  "status": "ok",
  "service": "VerzekProxyMesh",
  "timestamp": "2025-10-25T00:00:00"
}
```

### 2. IP Check

```bash
curl https://verzekhub.yourdomain.com/ip
```

**Expected:**
```json
{
  "client_ip": "YOUR_IP",
  "service": "VerzekProxyMesh"
}
```

### 3. Exchange Proxy

```bash
# Generate signature
BODY=""
SECRET="your_secret_key"
SIG=$(echo -n "$BODY" | openssl dgst -sha256 -hmac "$SECRET" | cut -d' ' -f2)

# Test Binance
curl "https://verzekhub.yourdomain.com/fapi/v1/time" \
  -H "X-Exchange-Host: fapi.binance.com" \
  -H "X-Proxy-Signature: $SIG"
```

---

## ❗ Troubleshooting

### Binance Still Rejects IP

1. Verify proxy working: `curl https://verzekhub.yourdomain.com/health`
2. Check Replit secrets are set correctly
3. Confirm IP whitelisted: 45.76.90.149
4. Test signature generation

### 502 Bad Gateway

```bash
# Check FastAPI on all nodes
systemctl status verzek-proxy
journalctl -u verzek-proxy -f

# Restart if needed
systemctl restart verzek-proxy
```

### VPN Connection Issues

```bash
# Check WireGuard
wg show

# Check firewall
ufw status
ufw allow 51820/udp

# Restart
systemctl restart wg-quick@wg0
```

### SSL Certificate Issues

```bash
# Test renewal
certbot renew --dry-run

# Force renewal
certbot renew --force-renewal
systemctl reload nginx
```

---

## 🔄 Maintenance

### Update FastAPI

```bash
cd /opt/verzek-proxy
source venv/bin/activate
pip install --upgrade fastapi uvicorn httpx
systemctl restart verzek-proxy
```

### Rotate Proxy Secret

```bash
# 1. Generate new secret
openssl rand -hex 32

# 2. Update on all nodes
nano /etc/systemd/system/verzek-proxy.service
# Change PROXY_SECRET_KEY
systemctl daemon-reload
systemctl restart verzek-proxy

# 3. Update Replit Secrets
PROXY_SECRET_KEY=<new_secret>
```

### Add More Nodes

```bash
# Deploy new node
./scripts/setup_wireguard.sh node3 10.10.0.4
./scripts/deploy_fastapi.sh YOUR_SECRET

# Update HAProxy on hub
nano /etc/haproxy/haproxy.cfg
# Add: server node3 10.10.0.4:5000 check
systemctl reload haproxy
```

---

## 🤝 Support

- **Email:** support@vezekinnovative.com
- **Telegram:** @VerzekSupportBot
- **Documentation:** See DEPLOYMENT_GUIDE.md

---

## 📝 License

Proprietary - VerzekAutoTrader Infrastructure

---

**Built with ❤️ for reliable crypto trading**
