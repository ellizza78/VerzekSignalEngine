# 📚 Complete Exchange API Setup Guides

This document provides detailed step-by-step instructions for connecting each exchange to VerzekAutoTrader.

---

## 🔷 Binance API Setup Guide

### **Prerequisites:**
- Active Binance account
- Identity verification completed (KYC Level 2)
- Some USDT in your Spot or Futures wallet

### **Step-by-Step Instructions:**

#### **1. Login to Binance**
1. Go to [www.binance.com](https://www.binance.com)
2. Click "Log In" at the top right
3. Enter your email and password
4. Complete 2FA verification

#### **2. Navigate to API Management**
1. Click your profile icon (top right)
2. Select "API Management" from the dropdown
3. Or go directly to: Profile → Security → API Management

#### **3. Create New API Key**
1. Click "Create API" button
2. Choose "System Generated" (recommended)
3. Enter a label (e.g., "VerzekAutoTrader")
4. Click "Next"

#### **4. Complete Security Verification**
1. Enter Email verification code (check your email)
2. Enter SMS code (check your phone)
3. Enter Google Authenticator code (if enabled)
4. Click "Submit"

#### **5. Configure API Permissions** ⚠️ CRITICAL
**Enable these permissions:**
- ✅ **Enable Reading** (checked by default)
- ✅ **Enable Spot & Margin Trading** (CHECK THIS!)
- ✅ **Enable Futures** (CHECK THIS for futures trading)

**MUST DISABLE:**
- ❌ **Enable Withdrawals** (NEVER enable this!)

#### **6. Set Up IP Whitelisting** (Recommended)
1. In the API settings, find "IP Access Restrictions"
2. Select "Restrict access to trusted IPs"
3. Click "Edit" next to IP address field
4. **In your VerzekAutoTrader app:**
   - Go to Exchange Accounts → Binance
   - Copy the server IP address shown (e.g., 45.76.90.149)
5. **Back in Binance:**
   - Paste the IP address
   - Click "Confirm"
   - Complete 2FA verification again

#### **7. Save Your API Keys** 🔐
**IMPORTANT:** Your Secret Key is shown **ONLY ONCE**!

1. **Copy API Key:**
   - Click the copy icon next to API Key
   - Save it somewhere secure temporarily

2. **Copy Secret Key:**
   - Click "Show" next to Secret Key
   - Complete 2FA verification
   - Click copy icon
   - **This is your ONLY chance to copy it!**
   - Save it somewhere secure temporarily

#### **8. Connect to VerzekAutoTrader**
1. Open VerzekAutoTrader mobile app
2. Go to: **Dashboard → Exchange Accounts → Binance**
3. Scroll down to "API Key" section
4. Paste your **API Key** in the first field
5. Paste your **Secret Key** in the second field
6. Tap "Connect Exchange"
7. Wait for verification (5-10 seconds)
8. You'll see: ✅ "Binance account connected successfully!"

#### **9. Verify Connection**
1. Go back to Exchange Accounts screen
2. Binance should now show 🔗 (connected)
3. You can now use auto-trading on Binance!

---

### **Common Binance Errors & Solutions:**

| Error Message | Solution |
|--------------|----------|
| "Invalid API credentials" | Double-check you copied both keys correctly (no extra spaces) |
| "API key doesn't have permission" | Go back to Binance → Enable "Spot & Margin Trading" |
| "IP address not whitelisted" | Add our server IP (shown in app) to Binance API settings |
| "Timestamp for this request is outside" | Check your phone's time/date settings (must be accurate) |
| "Signature verification failed" | Re-create API keys and try again |

---

## 🔷 Bybit API Setup Guide

### **Prerequisites:**
- Active Bybit account
- Identity verification completed (Level 1 minimum)
- USDT in your Unified Trading Account or Derivatives wallet

### **Step-by-Step Instructions:**

#### **1. Login to Bybit**
1. Go to [www.bybit.com](https://www.bybit.com)
2. Click "Log In"
3. Enter credentials and complete 2FA

#### **2. Navigate to API Management**
1. Hover over your profile icon (top right)
2. Click "API" from the dropdown
3. Or: Account & Security → API Management

#### **3. Create New API Key**
1. Click "Create New Key"
2. Choose "System-generated API Keys"
3. **For API Key Type:** Select "API Transaction" (for trading)

#### **4. Configure Permissions** ⚠️ CRITICAL
**Select these permissions:**
- ✅ **Contract Trade** (for futures trading)
- ✅ **Spot Trade** (for spot trading)  
- ✅ **Read-Only** (checked by default)

**NEVER enable:**
- ❌ **Withdraw** (keep this unchecked!)

#### **5. Set IP Whitelist** (Recommended)
1. Enable "IP Restriction"
2. **In VerzekAutoTrader app:**
   - Go to: Exchange Accounts → Bybit
   - Copy the server IP (e.g., 45.76.90.149)
3. **Back in Bybit:**
   - Click "Add IP"
   - Paste the IP address
   - Click "Confirm"

#### **6. Complete Security Verification**
1. Enter Email verification code
2. Enter Google Authenticator code (if enabled)
3. Click "Submit"

#### **7. Save Your API Keys** 🔐
1. **Copy API Key** - shown immediately
2. **Copy Secret Key** - click "Copy" (only shown once!)
3. Save both securely

#### **8. Connect to VerzekAutoTrader**
1. Open app → Exchange Accounts → Bybit
2. Enter API Key and Secret Key
3. Tap "Connect Exchange"
4. Success! ✅

---

### **Common Bybit Errors & Solutions:**

| Error Message | Solution |
|--------------|----------|
| "Invalid signature" | Re-check Secret Key (copy again from Bybit) |
| "Permission denied" | Enable "Contract Trade" permission in Bybit API settings |
| "IP not whitelisted" | Add server IP to Bybit API whitelist |
| "API key expired" | Create new API key (Bybit keys expire after 90 days of inactivity) |

---

## ⚡ Phemex API Setup Guide

### **Prerequisites:**
- Active Phemex account
- KYC verification completed
- USDT in your Contract Account

### **Step-by-Step Instructions:**

#### **1. Login to Phemex**
1. Go to [www.phemex.com](https://www.phemex.com)
2. Log in with your credentials

#### **2. Navigate to API Management**
1. Click your profile icon (top right)
2. Select "API Management"
3. Or: Account & Security → API Management

#### **3. Create New API Key**
1. Click "Create New API Key"
2. Enter API key name (e.g., "VerzekAutoTrader")
3. Click "Create"

#### **4. Configure Permissions** ⚠️ CRITICAL
**Enable:**
- ✅ **Trade** (for executing orders)
- ✅ **Read** (for checking balances)

**NEVER enable:**
- ❌ **Transfer/Withdraw** (keep disabled!)

#### **5. Set IP Restriction** (Recommended)
1. Toggle "IP Restriction" to ON
2. **From VerzekAutoTrader app:**
   - Go to: Exchange Accounts → Phemex
   - Copy server IP address
3. **In Phemex:**
   - Click "Add IP"
   - Paste IP: 45.76.90.149
   - Click "Confirm"

#### **6. Complete Security Verification**
1. Enter email verification code
2. Enter 2FA code
3. Click "Submit"

#### **7. Save API Credentials** 🔐
1. **API Key** - copy immediately
2. **Secret Key** - click "Show" and copy (shown only once!)
3. Store securely

#### **8. Connect to VerzekAutoTrader**
1. Open app → Exchange Accounts → Phemex
2. Paste API Key and Secret Key
3. Tap "Connect Exchange"
4. ✅ Connected!

---

### **Common Phemex Errors & Solutions:**

| Error Message | Solution |
|--------------|----------|
| "Invalid API credentials" | Verify both keys copied correctly |
| "Permission denied" | Enable "Trade" permission in Phemex |
| "IP not allowed" | Add server IP to Phemex IP restriction list |
| "Insufficient balance" | Transfer USDT to your Contract Account |

---

## 🐙 Kraken Futures API Setup Guide

### **Prerequisites:**
- Active Kraken account with Futures enabled
- Intermediate or higher verification level
- Funding in Futures wallet

### **Step-by-Step Instructions:**

#### **1. Login to Kraken Futures**
1. Go to [futures.kraken.com](https://futures.kraken.com)
2. Log in with your Kraken credentials

#### **2. Navigate to API Settings**
1. Click "Settings" (gear icon, top right)
2. Select "API" tab

#### **3. Generate New API Key**
1. Click "Generate New API Key"
2. Enter key name: "VerzekAutoTrader"

#### **4. Configure Permissions** ⚠️ CRITICAL
**Enable:**
- ✅ **Access Futures** (required)
- ✅ **Trade** (place/cancel orders)
- ✅ **View** (read account data)

**NEVER enable:**
- ❌ **Withdraw** (keep unchecked!)

#### **5. Optional: IP Whitelisting**
1. Under "IP Whitelist", click "Add IP"
2. **From VerzekAutoTrader:**
   - Copy server IP: 45.76.90.149
3. Paste and save

#### **6. Save API Credentials** 🔐
1. **API Key** - copy and save
2. **Secret Key** - copy immediately (only shown once!)

#### **7. Connect to VerzekAutoTrader**
1. Open app → Exchange Accounts → Kraken Futures
2. Enter API Key and Secret Key
3. Tap "Connect Exchange"
4. ✅ Success!

---

### **Common Kraken Errors & Solutions:**

| Error Message | Solution |
|--------------|----------|
| "Invalid nonce" | System time issue - restart app and try again |
| "Permission denied" | Enable "Trade" and "Access Futures" permissions |
| "API key not found" | Re-create API key and try again |

---

## 🔐 Universal Security Best Practices

### **DO:**
✅ Use unique API keys for VerzekAutoTrader (don't reuse keys from other bots)  
✅ Enable IP whitelisting on all exchanges  
✅ Keep API keys and secrets in secure password manager  
✅ Check API permissions before connecting  
✅ Monitor your exchange account regularly  
✅ Revoke old/unused API keys immediately

### **DON'T:**
❌ Enable withdrawal permissions (NEVER!)  
❌ Share your API keys with anyone  
❌ Take screenshots of secret keys  
❌ Store keys in plain text files  
❌ Use the same API key on multiple platforms  
❌ Ignore email notifications from exchanges about API activity

---

## 📊 What VerzekAutoTrader Can Do With Your API Keys

✅ **CAN:**
- Read your account balance
- Check current positions
- Place buy/sell orders based on signals
- Close positions with DCA strategy
- Check order status
- View trade history

❌ **CANNOT:**
- Withdraw your funds
- Transfer funds out of exchange
- Change account settings
- Access your login credentials
- Share your data with third parties

**Your funds always stay on the exchange under your control!**

---

## 🆘 Troubleshooting Guide

### **Issue: "Connection Failed" Error**

**Try these steps:**
1. Check internet connection
2. Verify API key and secret copied correctly (no spaces)
3. Confirm exchange permissions are correct
4. Restart VerzekAutoTrader app
5. Wait 60 seconds and try again (rate limit cooldown)

### **Issue: "Invalid Signature" Error**

**Solutions:**
1. Re-create API keys on exchange
2. Make sure Secret Key was copied completely
3. Check your phone's date/time is automatic
4. Delete and re-enter keys in app

### **Issue: Exchange Connected But Trades Not Executing**

**Check:**
1. You have sufficient USDT balance
2. Leverage is set correctly (in Exchange screen)
3. Your subscription is active (Premium/VIP required for auto-trading)
4. Symbol is not in your blacklist

---

## 📱 Quick Setup Summary (For Each Exchange)

```
1. Login to exchange website
2. Go to API Management
3. Create new API key
4. Enable: Reading + Trading permissions
5. Disable: Withdrawals
6. Add IP whitelist: 45.76.90.149
7. Copy API Key + Secret Key
8. Open VerzekAutoTrader app
9. Go to: Exchange Accounts → [Exchange Name]
10. Paste both keys
11. Tap "Connect Exchange"
12. ✅ Done!
```

---

## 🎯 Next Steps After Connecting

Once your exchange is connected:

1. **Set Leverage** (recommended: 5x-10x for beginners)
2. **Configure DCA Settings** (in Settings → Strategy)
3. **Set Risk Limits** (in Settings → Risk Management)
4. **Enable Auto-Trading** (Dashboard → Toggle Auto-Trade)
5. **Monitor Positions** (Positions tab)
6. **Track Signals** (Signals Feed tab)

---

**Need help?** Contact support at support@verzekinnovative.com
