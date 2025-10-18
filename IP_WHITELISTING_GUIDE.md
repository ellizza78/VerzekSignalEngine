# IP Whitelisting Setup Guide

## ⚠️ IMPORTANT: Static IP Requirement for Production

**Binance Futures API keys REQUIRE IP whitelisting** to enable trading permissions. Without IP restrictions, Binance will **automatically delete** API keys with trading permissions for security.

### Problem: Replit Dynamic IPs
Replit Reserved VM deployments use **dynamic IP addresses** that can change on restart/redeploy. This makes direct IP whitelisting unreliable.

### Solution: Cloudflare Workers Proxy
VerzekAutoTrader includes a **Cloudflare Workers proxy** that provides a static egress IP address for all exchange API calls.

**Recommended Setup:**
1. ✅ Deploy Cloudflare Workers proxy (see `cloudflare_proxy/README.md`)
2. ✅ Get dedicated egress IP from Cloudflare Enterprise
3. ✅ Whitelist Cloudflare IP on all exchanges
4. ✅ Enable proxy in Replit (PROXY_ENABLED=true)

---

## 📍 Step 1: Get Server IP Address

### Option A: Cloudflare Workers Proxy (Recommended for Production)
**Best for: Production deployment requiring static IP**

1. Deploy Cloudflare Workers proxy (see `cloudflare_proxy/README.md`)
2. Contact Cloudflare to get dedicated egress IP (Enterprise plan)
3. Use Cloudflare IP for exchange whitelisting
4. Enable proxy in Replit:
   ```
   PROXY_ENABLED=true
   PROXY_URL=https://verzek-exchange-proxy.workers.dev/proxy
   PROXY_SECRET_KEY=your-secret-key
   ```

**Benefits:**
- ✅ Static IP (never changes)
- ✅ Meets Binance IP whitelisting requirement
- ✅ Production-ready reliability

**Cost:** ~$200-500/month (Cloudflare Enterprise for dedicated IP)

### Option B: Replit Direct IP (Testing/Development Only)
**Best for: Development and testing**

The server IP is **dynamically assigned** and can change.

**How to get it:**
1. Open VerzekAutoTrader mobile app
2. Go to **Exchange Setup** tab
3. Copy the displayed server IP (e.g., `34.182.71.28`)
4. Or visit: `https://your-app.replit.app/api/system/ip`

**⚠️ WARNING:** This IP can change on deployment restart. Not recommended for production.

### Recommendation
- **Development:** Use Replit direct IP (Option B)
- **Production:** Use Cloudflare Workers proxy (Option A)

---

## 🔐 Step 2: Create API Keys with IP Whitelist

### Binance
1. Login to Binance → **Account** → **API Management**
2. Click **Create API**
3. **IMPORTANT:** Select **"Restrict access to trusted IPs only"**
4. Add the server IP from Step 1
5. **Permissions:**
   - ✅ Enable Futures
   - ✅ Enable Reading
   - ❌ **NEVER** enable withdrawals
6. **Margin Type:** Set to **ISOLATED MARGIN** (critical!)
7. Save API Key + Secret

### Bybit
1. Login to Bybit → **Account & Security** → **API Management**
2. Click **Create New Key** → **System-generated API Keys**
3. **IP Restrictions:**
   - Select **"Restrict to IP addresses"**
   - Add the server IP from Step 1
4. **Permissions:**
   - ✅ Derivatives Trading (for futures)
   - ✅ Read-only
   - ❌ **NEVER** enable withdrawals
5. **Margin Type:** Set to **ISOLATED MARGIN** (critical!)
6. Save API Key + Secret

### Phemex
1. Login to Phemex → **Account** → **API Management**
2. Click **Create New API Key**
3. **IP Whitelist:**
   - Toggle **"IP Restrictions"** ON
   - Add the server IP from Step 1
4. **Permissions:**
   - ✅ Enable Contracts (futures)
   - ✅ Enable Reading
   - ❌ **NEVER** enable withdrawals
5. **Margin Type:** Set to **ISOLATED MARGIN** (critical!)
6. Save API Key + Secret

### Coinexx
1. Login to Coinexx → **Settings** → **API**
2. Generate new API credentials
3. **IP Whitelist:**
   - Enable IP filtering
   - Add the server IP from Step 1
4. **Permissions:**
   - ✅ Trading
   - ✅ Read-only
   - ❌ **NEVER** enable withdrawals
5. Save API Key + Secret

---

## 📱 Step 3: Add Exchange Account in Mobile App

1. Open VerzekAutoTrader app
2. Go to **Settings** → **Exchange Accounts**
3. Tap **Add Account**
4. Select exchange (Binance, Bybit, Phemex, or Coinexx)
5. Enter:
   - Account nickname (e.g., "Binance Main")
   - API Key
   - API Secret
6. Tap **Save**

**Security Note:** API keys are encrypted with AES-128 and stored ONLY on the backend server. The mobile app never stores credentials locally.

---

## ⚙️ Step 4: Configure Isolated Margin on Exchange

**CRITICAL:** You MUST set all trading pairs to **ISOLATED MARGIN** mode.

### Why Isolated Margin?
- ✅ Limits losses to individual positions
- ✅ Prevents entire account liquidation
- ✅ Better risk management per trade
- ❌ Cross Margin can liquidate your entire account

### How to Set Isolated Margin:

**Binance Futures:**
1. Go to Futures → USDⓈ-M Futures
2. For each trading pair, click **Cross** → Change to **Isolated**
3. Set max leverage (recommend 5x-10x max)

**Bybit:**
1. Go to Derivatives → USDT Perpetual
2. Click margin type → Select **Isolated**
3. Apply to all pairs you'll trade

**Phemex:**
1. Go to Contracts
2. Select **Isolated Margin** mode
3. Set leverage per position

**Coinexx:**
1. Navigate to Trading Settings
2. Enable **Isolated Margin** for all pairs

---

## 🔍 Step 5: Verify Connection

1. In VerzekAutoTrader app → **Dashboard**
2. Check **Exchange Status** section
3. Should show: ✅ Connected for each exchange
4. If ❌ Failed:
   - Verify IP is whitelisted correctly
   - Check API key permissions
   - Ensure isolated margin is set
   - Try refreshing the connection

---

## 🚨 Security Checklist

Before enabling auto-trading, verify:

- [ ] Server IP whitelisted on exchange
- [ ] API keys have **NO withdrawal permissions**
- [ ] All trading pairs set to **ISOLATED MARGIN**
- [ ] API keys stored securely (backend-only)
- [ ] 2FA enabled on exchange account
- [ ] API key expiry set (recommended: 90 days)
- [ ] Auto-trading settings configured in app
- [ ] Test with small amounts first

---

## 🛡️ What Makes This Secure?

### 1. IP Whitelisting
- API keys only work from our server IP
- Even if keys are compromised, attackers can't use them

### 2. Backend-Only Storage
- API keys never stored on mobile device
- Encrypted at rest with AES-128
- Decrypted only in-memory during trades

### 3. Isolated Margin
- Each position is independent
- Losses limited to position size
- Account balance protected

### 4. No Withdrawal Permissions
- API keys can only trade
- Cannot withdraw funds
- Maximum security

### 5. HTTPS/TLS Encryption
- All API communication encrypted
- JWT authentication
- Certificate pinning

---

## ❓ FAQ

**Q: What happens if the server IP changes?**
A: Rare on Reserved VM deployment. If it happens:
1. Get new IP from Exchange Setup tab
2. Update IP whitelist on each exchange
3. Reconnect accounts in app

**Q: Can I use the same API keys for multiple bots?**
A: Not recommended. Create separate API keys for VerzekAutoTrader.

**Q: Do I need different API keys for demo mode?**
A: Yes. Use testnet/demo API keys for demo mode, real API keys for live trading.

**Q: What if I see "IP not whitelisted" error?**
A: 
1. Double-check IP in Exchange Setup tab matches exchange whitelist
2. Wait 5-10 minutes after updating whitelist (propagation delay)
3. Try reconnecting the account

**Q: Is my account balance safe?**
A: Yes, with proper setup:
- ✅ Isolated margin = limited losses per trade
- ✅ No withdrawal permissions = funds can't leave account
- ✅ IP whitelist = only our server can trade
- ✅ Kill switch = emergency stop button

---

## 📊 Production IP History

For reference (IP may change with deployments):

| Date | Environment | IP Address |
|------|-------------|------------|
| 2025-10-18 | Development | 34.182.71.28 |
| Production | *Dynamic* | Fetch via /api/system/ip |

**Always get current IP from the mobile app or API endpoint.**

---

## 🆘 Emergency: IP Whitelist Issues

If you can't trade due to IP whitelist errors:

1. **Immediate:** Disable auto-trading in app
2. **Verify:** Current server IP via Exchange Setup tab
3. **Update:** Exchange whitelist with correct IP
4. **Wait:** 5-10 minutes for propagation
5. **Test:** Reconnect exchange account
6. **Enable:** Auto-trading when connection successful

---

## ✅ Setup Complete!

Once all steps are done:
1. ✅ IP whitelisted on all exchanges
2. ✅ API keys created with correct permissions
3. ✅ Accounts added to VerzekAutoTrader app
4. ✅ Isolated margin set on all pairs
5. ✅ Connection verified in app

You're ready to enable auto-trading! 🚀

**Recommended next steps:**
- Configure DCA settings in app
- Set risk parameters (leverage caps, position limits)
- Test with small amounts first
- Monitor trades closely for first 24 hours
