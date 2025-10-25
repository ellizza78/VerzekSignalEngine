# Vultr Proxy - Quick Start Guide
## Fix Binance IP Rejection in 5 Steps

---

## 🚀 Quick Setup (5 Minutes)

### Prerequisites
- 3 Vultr servers (1 vCPU, 1GB RAM, Ubuntu 22.04)
- Domain name pointing to hub server
- SSH access to all servers

---

## Step 1: Update Server IPs

Edit `vultr_infrastructure/orchestrator.py`:

```python
INV = {
    "hub": {"ip": "45.76.90.149", "vpn": "10.10.0.1"},  # Your hub IP
    "node1": {"ip": "YOUR_NODE1_IP", "vpn": "10.10.0.2"},  # Update
    "node2": {"ip": "YOUR_NODE2_IP", "vpn": "10.10.0.3"}   # Update
}
```

## Step 2: Generate Secret Key

```bash
openssl rand -hex 32
# Save this key - example: a1b2c3d4e5f6...
```

## Step 3: Deploy Infrastructure

### Option A: Automated (Recommended)

```bash
cd vultr_infrastructure

# Update domain in script first
nano orchestrator.py  # Change domain to yours

# Run deployment
python3 orchestrator.py
```

### Option B: Manual

```bash
# On each server
ssh root@SERVER_IP

# 1. Setup WireGuard
./scripts/setup_wireguard.sh hub 10.10.0.1
systemctl start wg-quick@wg0

# 2. Deploy FastAPI
./scripts/deploy_fastapi.sh YOUR_SECRET_KEY

# On hub only:
./scripts/setup_haproxy.sh
./scripts/setup_nginx_ssl.sh yourdomain.com your@email.com
```

## Step 4: Configure Replit

Add to **Replit Secrets**:

```bash
PROXY_ENABLED=true
PROXY_URL=https://verzekhub.yourdomain.com
PROXY_SECRET_KEY=a1b2c3d4e5f6...  # Your generated secret
```

## Step 5: Whitelist IP on Binance

1. Go to Binance → API Management
2. Edit API Key → "Restrict access to trusted IPs only"
3. Add IP: **45.76.90.149**
4. Save

---

## ✅ Test It Works

```bash
# From Replit or local machine
curl https://verzekhub.yourdomain.com/health

# Should return:
{"status":"ok","service":"VerzekProxyMesh"}
```

---

## 🎯 That's It!

All Binance API calls now route through your static IP (45.76.90.149).

**No more IP rejection errors!** ✅

---

## 📊 Monitoring

```bash
# Check services
systemctl status verzek-proxy
systemctl status haproxy
systemctl status nginx

# View logs
journalctl -u verzek-proxy -f
```

---

## ❗ Troubleshooting

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Check FastAPI: `systemctl restart verzek-proxy` |
| SSL certificate error | Run: `certbot renew` |
| Binance still rejects | Verify IP 45.76.90.149 whitelisted |
| VPN not working | Restart: `systemctl restart wg-quick@wg0` |

---

## 💰 Cost

**$15/month** for 3 Vultr servers + ~$12/year domain = **~$16.50/month**

---

## 📚 Need More Details?

See full deployment guide: `DEPLOYMENT_GUIDE.md`

---

**Support:** support@vezekinnovative.com
