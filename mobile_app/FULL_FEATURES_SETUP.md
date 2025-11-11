# VerzekApp - Full Features Setup Guide

## 🎯 Overview

This guide walks you through enabling all production features in the VerzekApp mobile application, connecting it to your live backend API, and starting real trading operations.

---

## 📱 Current Status

Your app is currently running in **development mode** with:
- ✅ Expo Dev Server active
- ✅ QR code for testing
- ✅ UI/UX complete with dark theme
- ✅ Authentication flow ready
- ⚠️ Backend pointing to development/local server

---

## 🚀 Enable Full Features - Step by Step

### **Step 1: Verify API Configuration**

**✅ Already configured!** The app is pointing to production:

Check `mobile_app/VerzekApp/src/config/api.js` (line 3):
```javascript
export const API_BASE_URL = 'https://api.verzekinnovative.com';
```

The app uses JWT authentication - no API key header validation on backend.

**For local development** (optional), you can change this to:
```javascript
export const API_BASE_URL = 'http://localhost:8050';  // Development
```

But the production build is already correctly configured!

### **Step 2: Configure Telegram Integration**

The app receives trading signals from Telegram. Ensure these are set:

**Backend Configuration** (already done):
- `TELEGRAM_BOT_TOKEN` - Main bot for signal monitoring
- `BROADCAST_BOT_TOKEN` - Bot for broadcasting to user groups
- `VIP_GROUP_ID` - VIP subscribers group
- `TRIAL_GROUP_ID` - Trial users group

**Mobile App** - Signals are automatically fetched via API:
- `/api/signals` - Get latest trading signals
- Real-time updates every 30 seconds when app is active

### **Step 3: Enable Push Notifications**

For trade alerts and signal notifications:

1. **Setup Firebase Cloud Messaging** (if not already done):
   ```bash
   cd mobile_app/VerzekApp
   expo install expo-notifications
   ```

2. **Add FCM Token Storage** in `src/services/auth.ts`:
   ```typescript
   import * as Notifications from 'expo-notifications';
   
   // After successful login
   const token = await Notifications.getExpoPushTokenAsync();
   // Send token to backend: POST /api/user/fcm-token
   ```

3. **Backend will automatically send notifications** for:
   - New trading signals
   - Position updates (TP hit, SL triggered)
   - Account alerts
   - System maintenance

### **Step 4: Configure Trading Modes**

The app supports two trading modes:

#### **Paper Trading (Risk-Free)**
- Uses simulated capital
- No real money at risk
- Perfect for testing strategies
- **Status**: ✅ Already enabled

#### **Live Trading (Real Money)**
- Connects to real exchange accounts
- Executes actual trades
- Requires verified email + exchange API keys
- **Status**: Disabled by default for safety

To enable live trading for your account:

```bash
# On Vultr VPS after deployment
cd /root/api_server/backend
source venv/bin/activate
source /root/api_server_env.sh

python << EOF
from db import SessionLocal
from models import User

db = SessionLocal()
user = db.query(User).filter(User.email == "YOUR_EMAIL").first()
if user:
    user.auto_trade_enabled = True
    user.subscription_type = "VIP"  # or PREMIUM
    db.commit()
    print(f"✅ Live trading enabled for {user.email}")
else:
    print("❌ User not found")
db.close()
EOF
```

### **Step 5: Add Exchange Accounts**

Users can add exchange API keys through the mobile app:

1. **Tap "Settings" → "Exchange Accounts"**
2. **Select Exchange** (Binance, Bybit, Phemex, Kraken)
3. **Enter API Credentials**:
   - API Key
   - API Secret
   - Enable Testnet (for testing first)
4. **App encrypts and sends to backend**

**Security Features**:
- ✅ Keys encrypted with Fernet (AES-128)
- ✅ Stored encrypted in database
- ✅ Never logged or exposed
- ✅ Can be deleted anytime

### **Step 6: Enable Advanced Features**

Edit backend `feature_flags` to enable:

```python
# Update AppConfig in database
config.feature_flags = {
    'paper_trading': True,        # ✅ Enabled
    'live_trading': True,          # Enable for production
    'ai_assistant': True,          # GPT-4o-mini trade advisor
    'telegram_signals': True,      # Auto-broadcast signals
    'multi_timeframe': True,       # Advanced charting
    'social_trading': False,       # Coming soon
    'portfolio_rebalance': True,   # Auto-rebalancing
    'webhook_integration': True,   # External signal sources
    'push_notifications': True,    # FCM alerts
}
```

---

## 🔐 Security Setup

### **Email Verification** (Required for Trading)

Users must verify email before:
- Connecting exchange accounts
- Enabling auto-trading
- Accessing live trading features

**Flow**:
1. User signs up → Receives verification email (Resend API)
2. Clicks link → Account verified
3. Can now add exchanges and trade

### **Two-Factor Authentication (2FA)** (Optional)

For extra security:
1. **User enables 2FA** in app settings
2. **Scans QR code** with authenticator app (Google Authenticator, Authy)
3. **Enters code** on every login

---

## 📊 Trading Features Breakdown

### **Automated Trading**
- ✅ Monitors Telegram signals 24/7
- ✅ Auto-executes trades based on signals
- ✅ DCA (Dollar Cost Averaging) support
- ✅ Progressive take-profit (ladder exit)
- ✅ Auto stop-loss management
- ✅ Risk management per trade
- ✅ Max concurrent positions limit

### **Position Management**
- ✅ Real-time P&L tracking
- ✅ Partial close support
- ✅ Update TP/SL on the fly
- ✅ Manual close positions
- ✅ Position history & analytics

### **Portfolio Overview**
- ✅ Total equity & available balance
- ✅ Active positions count
- ✅ Today's P&L
- ✅ Win rate & performance metrics
- ✅ Daily reports (email + Telegram)

### **AI Trade Assistant** (Premium)
- ✅ GPT-4o-mini powered analysis
- ✅ Market sentiment analysis
- ✅ Trade recommendations
- ✅ Risk scoring
- ✅ Smart entry/exit suggestions

---

## 🎨 App Features Already Built

### ✅ **Authentication**
- Sign up / Login with JWT
- Email verification
- Password reset
- Secure token storage

### ✅ **Dashboard**
- Account overview
- Quick stats
- Active positions list
- Recent trades

### ✅ **Settings**
- Profile management
- Trading preferences
- Risk settings
- DCA configuration
- Exchange accounts
- Notifications

### ✅ **Help & Support**
- FAQ section
- Contact support
- Tutorial videos
- Documentation

---

## 📲 Build & Distribute App

### **For Android (EAS Build)**

```bash
cd mobile_app/VerzekApp

# Login to Expo
expo login

# Build APK
eas build --platform android --profile preview

# Or build for production
eas build --platform android --profile production
```

**Build Profiles** (`eas.json`):
- `preview` - Testing build with dev settings
- `production` - Production build for Play Store

### **For iOS (Requires Apple Developer Account)**

```bash
eas build --platform ios --profile production
```

### **OTA Updates (No Rebuild Required)**

For JavaScript/UI changes only:

```bash
# Update the app instantly without rebuild
eas update --branch production --message "Fixed dashboard layout"
```

Users get the update automatically on next app restart!

---

## 🔔 User Subscription Plans

Configure in backend database:

### **TRIAL (Free)**
- ✅ Paper trading unlimited
- ✅ View signals
- ✅ Limited AI assistant (5 queries/day)
- ✅ Basic support
- ❌ No live trading
- **Duration**: 7 days

### **VIP**
- ✅ Everything in TRIAL
- ✅ Live trading enabled
- ✅ Up to 20 concurrent positions
- ✅ Unlimited AI assistant
- ✅ Priority support
- ✅ Telegram VIP group access
- **Price**: $50/month

### **PREMIUM**
- ✅ Everything in VIP
- ✅ Up to 50 concurrent positions
- ✅ Advanced analytics
- ✅ Custom strategies
- ✅ Dedicated account manager
- ✅ API access
- **Price**: $200/month

---

## 🎯 Go-Live Checklist

Before enabling live trading for users:

- [ ] Backend deployed to Vultr VPS
- [ ] SSL certificate installed
- [ ] Database initialized with AppConfig
- [ ] All environment variables set
- [ ] Watchdog monitoring active
- [ ] Email verification system tested
- [ ] Telegram broadcasting working
- [ ] Mobile app pointing to production API
- [ ] Test user account created
- [ ] Exchange API keys tested (testnet first)
- [ ] Paper trading verified working
- [ ] Daily reports generating correctly
- [ ] Push notifications working
- [ ] Payment processing tested
- [ ] Backup strategy in place

---

## 🆘 Support & Monitoring

### **User Support**
- Email: support@verzekinnovative.com
- Telegram: VIP/Trial group support
- In-app: Help & FAQ section

### **System Monitoring**
- Health endpoint: `/api/health` (every 5 mins)
- Watchdog auto-restart on failures
- Telegram admin alerts
- Daily performance reports

### **Logs**
- API logs: `journalctl -u verzek_api -f`
- Worker logs: `journalctl -u verzek_worker -f`
- Watchdog: `/root/api_server/logs/watchdog.log`

---

## 🚀 You're Ready to Trade!

Your VerzekAutoTrader platform is now production-ready with:

1. ✅ **Backend API** - Deployed on Vultr (api.verzekinnovative.com)
2. ✅ **Mobile App** - Connected to production backend
3. ✅ **Trading Engine** - Paper & live trading support
4. ✅ **Telegram Integration** - Signal monitoring & broadcasting
5. ✅ **Email System** - Verification & daily reports
6. ✅ **Monitoring** - Watchdog with auto-restart
7. ✅ **Security** - Encryption, JWT, 2FA ready

**Start trading with confidence! 🎉**

Need help? Contact support@verzekinnovative.com
