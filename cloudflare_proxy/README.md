# Cloudflare Workers Proxy for Static IP

This proxy provides a **static egress IP address** for VerzekAutoTrader to meet Binance/Bybit/Phemex IP whitelisting requirements.

## Why This Is Needed

Replit Reserved VM deployments use **dynamic IP addresses** that can change on restart/redeploy. Binance Futures requires API keys to be restricted to trusted IPs only.

**Solution:** Route all exchange API calls through Cloudflare Workers, which provides consistent egress IPs.

---

## Architecture

```
VerzekAutoTrader (Replit)
    ↓ HTTPS + HMAC Signature
Cloudflare Workers Proxy (Static IP)
    ↓ Forwarded Request
Exchange APIs (Binance, Bybit, Phemex, Coinexx)
    ↓ Response
Cloudflare Workers Proxy
    ↓ Response
VerzekAutoTrader (Replit)
```

---

## Setup Instructions

### Step 1: Install Wrangler CLI

```bash
npm install -g wrangler
```

### Step 2: Login to Cloudflare

```bash
wrangler login
```

### Step 3: Generate Proxy Secret Key

```bash
# Generate a random 32-character secret key
openssl rand -hex 32
# Example output: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0
```

**Save this key!** You'll need it for both Cloudflare and Replit.

### Step 4: Set Secret in Cloudflare Workers

```bash
cd cloudflare_proxy
wrangler secret put PROXY_SECRET_KEY
# Paste the secret key you generated above
```

### Step 5: Deploy to Cloudflare Workers

```bash
wrangler deploy
```

Output:
```
✨ Built successfully
✨ Uploaded verzek-exchange-proxy
✨ Published verzek-exchange-proxy
   https://verzek-exchange-proxy.your-subdomain.workers.dev
```

**Copy the URL** - this is your proxy endpoint!

### Step 6: Get Cloudflare Egress IP

**Free Tier (Shared IP):**
Cloudflare Workers Free tier uses **shared egress IPs** that can change. This is NOT suitable for production IP whitelisting.

**Paid Tier Options:**

1. **Cloudflare Workers Unbound ($5/month):**
   - Still uses shared egress IPs
   - Not suitable for strict IP whitelisting

2. **Cloudflare Enterprise Plan:**
   - Provides **dedicated egress IP**
   - Contact Cloudflare Sales: https://www.cloudflare.com/enterprise/
   - Pricing: ~$200-500/month (custom pricing)

3. **Alternative: Cloudflare Spectrum (Recommended):**
   - Provides static IPs for proxying
   - Pricing: $0.10/GB transferred
   - Contact support to enable

**Recommended for Production:**
Contact Cloudflare Support to request **dedicated egress IP** for your Workers account.

### Step 7: Configure VerzekAutoTrader (Replit)

Add these secrets to your Replit project:

```bash
PROXY_ENABLED=true
PROXY_URL=https://verzek-exchange-proxy.your-subdomain.workers.dev/proxy
PROXY_SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0
```

### Step 8: Whitelist Cloudflare IP on Exchanges

Once you have the **dedicated egress IP** from Cloudflare:

**Binance:**
1. Go to API Management
2. Create API Key → "Restrict access to trusted IPs only"
3. Add Cloudflare egress IP
4. Enable: ✅ Futures, ✅ Reading, ❌ No withdrawals

**Bybit:**
1. Go to API Management
2. Create API Key → "Restrict to IP addresses"
3. Add Cloudflare egress IP
4. Enable: ✅ Derivatives Trading, ✅ Read-only

**Phemex:**
1. Go to API Management
2. Create API Key → "IP Restrictions" ON
3. Add Cloudflare egress IP
4. Enable: ✅ Contracts, ✅ Reading

**Coinexx:**
1. Go to API Settings
2. Enable IP filtering
3. Add Cloudflare egress IP
4. Enable: ✅ Trading, ✅ Read-only

---

## Testing

### Test Health Endpoint

```bash
curl https://verzek-exchange-proxy.your-subdomain.workers.dev/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-18T12:00:00.000Z",
  "service": "VerzekAutoTrader Exchange Proxy"
}
```

### Test Proxy Endpoint (from Replit)

The Replit backend will automatically use the proxy when `PROXY_ENABLED=true`.

---

## Security

### HMAC Signature Authentication

Every request to the proxy must include:
- **X-Proxy-Signature**: HMAC-SHA256(PROXY_SECRET_KEY, request_body)
- **X-Exchange-Host**: Target exchange hostname (e.g., fapi.binance.com)

This prevents unauthorized use of your proxy.

### Allowed Exchanges

The proxy only forwards requests to whitelisted exchanges:
- fapi.binance.com
- api.binance.com
- api.bybit.com
- api.phemex.com
- api.coinexx.com

All other hosts are blocked (403 Forbidden).

---

## Cost Estimates

### Cloudflare Workers

**Free Tier:**
- 100,000 requests/day
- Shared egress IP (not suitable for production)

**Paid Tier ($5/month):**
- Unlimited requests
- $0.50 per million requests after 10M
- Shared egress IP (not suitable for strict IP whitelisting)

**Enterprise (Custom Pricing):**
- Dedicated egress IP
- ~$200-500/month
- Contact Cloudflare Sales

### Estimated Monthly Cost for VerzekAutoTrader

Assuming:
- 1,000 active users
- 100 trades/day average
- 200 API calls per trade (DCA levels, monitoring, etc.)
- Total: 1,000 × 100 × 200 = 20,000,000 requests/month

**Cloudflare Workers Cost:**
- Base: $5/month (Unbound plan)
- Overage: (20M - 10M) × $0.50/million = $5
- **Total: $10/month** (without dedicated IP)

**With Dedicated IP:**
- Enterprise plan: ~$200-500/month
- **Total: $200-500/month**

---

## Alternatives (If Cloudflare Enterprise Too Expensive)

### Option A: AWS API Gateway + NAT Gateway

**Setup:**
1. Deploy lightweight Lambda proxy
2. Route through NAT Gateway (static IP)
3. Whitelist NAT Gateway IP on exchanges

**Cost:** ~$35-50/month (NAT Gateway + Lambda)

### Option B: Google Cloud Run + Cloud NAT

**Setup:**
1. Deploy proxy to Cloud Run
2. Configure Cloud NAT (static egress IP)
3. Whitelist Cloud NAT IP on exchanges

**Cost:** ~$30-40/month (Cloud NAT + Cloud Run)

### Option C: DigitalOcean Droplet

**Setup:**
1. Deploy lightweight proxy to $6/month Droplet
2. Droplet has static IP included
3. Whitelist Droplet IP on exchanges

**Cost:** $6/month (simplest, cheapest)

---

## Troubleshooting

### "Invalid X-Proxy-Signature header"

- Verify `PROXY_SECRET_KEY` matches in both Cloudflare and Replit
- Check HMAC signature calculation in exchange clients

### "Unauthorized exchange host"

- Verify exchange hostname is in `ALLOWED_EXCHANGES` array
- Update `worker.js` if using additional exchanges

### "Proxy request failed"

- Check Cloudflare Workers logs in dashboard
- Verify exchange API is reachable from Cloudflare
- Check for rate limiting on exchange side

---

## Support

For issues with:
- **Cloudflare Workers**: https://community.cloudflare.com/
- **Dedicated IP**: Contact Cloudflare Enterprise Sales
- **VerzekAutoTrader**: Check logs in Replit

---

## Next Steps

1. ✅ Deploy Cloudflare Workers proxy
2. ⚠️ **Contact Cloudflare Support** for dedicated egress IP (critical!)
3. ✅ Configure Replit secrets (PROXY_ENABLED, PROXY_URL, PROXY_SECRET_KEY)
4. ✅ Whitelist Cloudflare IP on all exchanges
5. ✅ Test trading with small amounts
6. ✅ Monitor for 24 hours before full production use

**IMPORTANT:** Do not enable production trading until you have a **dedicated static IP** from Cloudflare. The free tier shared IPs can change.
