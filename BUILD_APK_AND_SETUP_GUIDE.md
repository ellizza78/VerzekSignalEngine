# 🚀 Complete Setup Guide: APK Build + External Signals + Auto-Trading

## 📱 **STEP 1: Build Production APK**

### **Run This in Replit Shell** (NOT via agent):

```bash
cd mobile_app/VerzekApp
eas build --platform android --profile production
```

**What happens:**
- EAS will build your APK (~10-15 minutes)
- You'll get a download link when ready
- APK will be signed and production-ready

**Download Link**: Check your Expo dashboard at https://expo.dev/accounts/ellizza/projects/verzekapp/builds

**Note**: You've used 100% of free build credits. Additional builds are pay-as-you-go.

---

## 📡 **STEP 2: Setup External VIP Signal Listener** (CRITICAL)

Your system currently has **House Signals** (VerzekSignalEngine) working, but NOT external VIP group monitoring.

### **What You Need:**

1. **Your VIP Group Details:**
   - VIP Group ID or Username
   - Telegram API ID (from https://my.telegram.org/apps)
   - Telegram API Hash

2. **Two Options for Signal Listening:**

#### **Option A: Telethon (Recommended)** ✅
- Monitors your personal Telegram account
- Forwards signals from VIP group to your broadcast groups
- Auto-trading integration ready

#### **Option B: Pyrogram** 
- Similar but different library
- More lightweight

### **Setup Commands** (I'll run these for you):

#### **Configure Telethon Listener:**

I need you to provide:
```
TELEGRAM_API_ID=YOUR_API_ID
TELEGRAM_API_HASH=YOUR_API_HASH
VIP_SIGNAL_GROUP_ID=-100XXXXXXXXX  (Your VIP group ID)
```

Then I'll:
1. Configure `telethon_forwarder.py` to monitor your VIP group
2. Deploy it to Vultr as a systemd service
3. Connect it to backend for auto-trading
4. Set up heartbeat monitoring

---

## 🤖 **STEP 3: Enable Auto-Trading** (DCA Engine)

### **Current Status:**
- ✅ DCA Engine code exists
- ✅ Safety Manager ready
- ✅ Exchange adapters (Binance, Bybit, Phemex, Kraken) ready
- ⚠️ Needs configuration

### **What's Required:**

1. **Exchange API Keys** (I'll help you set these up securely):
   - Binance API Key + Secret
   - Bybit API Key + Secret (optional)
   - Phemex API Key + Secret (optional)

2. **Static IP Setup** (For exchange whitelisting):
   - Required if using Binance with IP restrictions
   - I have WireGuard VPN + HAProxy scripts ready
   - Static IP: 80.240.29.142 (Vultr)

3. **Trading Mode:**
   - Start in PAPER mode (simulation)
   - Test for 24-48 hours
   - Switch to LIVE when confident

---

## 🔐 **STEP 4: Static IP Proxy Setup** (If Needed)

### **When You Need This:**
- Using Binance Futures API (requires IP whitelisting)
- Want consistent IP for all exchanges

### **What I'll Deploy:**
1. WireGuard VPN mesh on Vultr
2. HAProxy load balancer
3. Nginx + SSL (HTTPS)
4. FastAPI proxy service
5. Automatic failover

### **Result:**
- All exchange API calls route through 80.240.29.142
- Whitelist this IP on Binance/Bybit
- No more "IP not whitelisted" errors

---

## ⚡ **PRIORITY ACTIONS**

### **Immediate (You need to do):**

1. **Build APK:**
   ```bash
   cd mobile_app/VerzekApp
   eas build --platform android --profile production
   ```

2. **Get Your VIP Group ID:**
   - Forward any message from your VIP group to @userinfobot
   - It will show you the group ID (format: -100XXXXXXXXX)

3. **Get Telegram API Credentials:**
   - Go to https://my.telegram.org/apps
   - Create an application
   - Copy API ID and API Hash

4. **Decide on Auto-Trading:**
   - Do you want auto-trading enabled?
   - Which exchanges will you use?
   - Start with PAPER mode or LIVE?

### **After You Provide Info (I'll do):**

1. Configure and deploy Telethon listener to Vultr
2. Set up exchange API keys (encrypted storage)
3. Deploy static IP proxy (if needed)
4. Enable auto-trading DCA engine
5. Test end-to-end signal flow
6. Monitor for 24 hours before LIVE mode

---

## 📊 **System Architecture After Full Setup**

```
┌─────────────────────────────────────────────────────┐
│          SIGNAL SOURCES                              │
├─────────────────────────────────────────────────────┤
│                                                      │
│  1. VerzekSignalEngine (House Signals) ✅ RUNNING   │
│     - Scalping Bot (15s)                            │
│     - Trend Bot (5m)                                │
│     - QFL Bot (20s)                                 │
│     - AI/ML Bot (30s)                               │
│                                                      │
│  2. External VIP Group ⚠️ NEEDS SETUP                │
│     - Telethon Listener                             │
│     - Monitors your VIP signal source               │
│     - Parses LONG/SHORT/ENTRY/TP/SL                 │
│                                                      │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│          BACKEND API (Vultr) ✅ RUNNING              │
├─────────────────────────────────────────────────────┤
│                                                      │
│  /api/house-signals/ingest  (House signals)         │
│  /api/broadcast/signal      (External signals)      │
│                                                      │
│  - DCA Orchestrator ⚠️ NEEDS CONFIG                  │
│  - Safety Manager                                   │
│  - Signal Quality Filter                            │
│  - Position Tracker                                 │
│                                                      │
└──────────┬──────────────────┬────────────────────────┘
           │                  │
           │                  ▼
           │         ┌────────────────────┐
           │         │  TELEGRAM GROUPS   │
           │         ├────────────────────┤
           │         │  VIP Group ✅      │
           │         │  TRIAL Group ✅    │
           │         └────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────┐
│          AUTO-TRADING ⚠️ NEEDS SETUP                 │
├─────────────────────────────────────────────────────┤
│                                                      │
│  DCA Engine → Exchange Adapters → Exchanges         │
│                                                      │
│  Supported Exchanges:                               │
│  - Binance Futures ⚠️                                │
│  - Bybit ⚠️                                          │
│  - Phemex ⚠️                                         │
│  - Kraken Futures ⚠️                                 │
│                                                      │
│  Static IP Proxy (80.240.29.142) ⚠️ NOT DEPLOYED    │
│  - WireGuard VPN                                    │
│  - HAProxy                                          │
│  - Nginx SSL                                        │
│                                                      │
└─────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────┐
│          MOBILE APP ✅ READY                         │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Version: 2.1.1 (versionCode 20)                    │
│  Backend: https://api.verzekinnovative.com          │
│  APK Build: Ready (run eas build command)           │
│                                                      │
│  Features:                                          │
│  - Live signal feed (House signals ✅)              │
│  - Auto-trading controls ⚠️                          │
│  - Position monitoring ⚠️                            │
│  - Push notifications ✅                             │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 **NEXT STEPS**

**Tell me:**

1. **VIP Group Details**:
   - What's your VIP signal group ID?
   - Do you have Telegram API credentials?

2. **Auto-Trading Preference**:
   - Which exchanges do you want to use?
   - Do you have API keys ready?
   - Start with PAPER or LIVE mode?

3. **Static IP Need**:
   - Do your exchanges require IP whitelisting?
   - Should I deploy the proxy infrastructure?

**Once you provide these, I'll:**
- Set up complete external signal monitoring
- Configure auto-trading with DCA
- Deploy proxy if needed
- Test everything end-to-end
- Give you final GO/NO-GO for production

---

## ⚠️ **Important Notes**

1. **Trading Mode**: ALWAYS start with PAPER mode for 24-48 hours minimum
2. **API Key Security**: I'll encrypt and store keys securely (Fernet AES-128)
3. **Position Limits**: Default 50 concurrent positions per user (configurable)
4. **Safety Features**: Stop-loss, take-profit, breakeven SL all working
5. **Monitoring**: 24/7 health checks, heartbeat monitoring, admin alerts

---

## ✅ **What's Already Working**

- ✅ Backend API (4 Gunicorn workers)
- ✅ VerzekSignalEngine (4 bots generating house signals)
- ✅ PostgreSQL database
- ✅ Telegram broadcasting (VIP + TRIAL groups)
- ✅ Mobile app push notifications
- ✅ Signal ingestion pipeline
- ✅ Complete signal flow (House signals only)

---

Ready to set this up? Provide the details above and I'll configure everything! 🚀
