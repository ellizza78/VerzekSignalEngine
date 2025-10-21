# VerzekAutoTrader - Testing Guide

## 📱 Test Credentials

### Demo Account
**Email:** `demo@verzektrader.com`  
**Password:** `Demo123!`  
**User ID:** `demo_verzektrader_com`  
**Status:** ✅ Email Verified  
**Plan:** Free (can be upgraded to Pro/VIP)

---

## 🔧 Building on Expo Go

### Prerequisites
1. Install Expo Go app on your mobile device:
   - **iOS:** Download from App Store
   - **Android:** Download from Play Store

2. Install dependencies (if not already done):
```bash
cd mobile_app/VerzekApp
npm install
```

### Method 1: Development Build (Expo Go)

1. **Start the Expo development server:**
```bash
cd mobile_app/VerzekApp
npx expo start
```

2. **Scan the QR code:**
   - **iOS:** Open Camera app and scan the QR code
   - **Android:** Open Expo Go app and scan the QR code

3. **App should load on your device!**

### Method 2: Build APK/IPA (For Distribution)

#### Android APK
```bash
cd mobile_app/VerzekApp
eas build --platform android --profile preview
```

#### iOS Build
```bash
cd mobile_app/VerzekApp
eas build --platform ios --profile preview
```

#### Production Builds
```bash
# Android App Bundle (for Play Store)
eas build --platform android --profile production

# iOS App (for App Store)
eas build --platform ios --profile production
```

---

## 🧪 Testing Features

### 1. Registration & Email Verification
- ✅ Register with any email
- ✅ Email verification link printed to console (dev mode)
- ✅ Click verification link or use API to verify
- ✅ Login after verification

### 2. Exchange Connection
- ✅ Navigate to Settings → Exchange Accounts
- ✅ Add exchange (Binance, Bybit, Phemex, Kraken)
- ✅ API keys are encrypted with AES-128
- ✅ Demo mode available for testing

### 3. Trading (Auto-DCA)
- ✅ System monitors Telegram signals
- ✅ Auto-executes DCA trades with risk management
- ✅ Position tracking and safety controls
- ✅ Progressive take-profit system

### 4. Subscription Plans

#### Free Plan
- ✅ Limited features
- ✅ Manual trading only
- ✅ Basic dashboard

#### Pro Plan ($29/month)
- ✅ Auto-trading enabled
- ✅ 5 active positions
- ✅ Advanced features

#### VIP Plan ($99/month)
- ✅ Unlimited positions
- ✅ Priority signals
- ✅ AI Trade Assistant
- ✅ Advanced analytics

### 5. Referral System
- ✅ Generate referral code
- ✅ Earn 10% recurring commission
- ✅ In-app wallet tracking
- ✅ Request payout (min $10 USDT)

---

## 🔐 API Endpoints (For Testing)

**Base URL:** `https://97d3a6c0-0cc4-488f-9056-f562cf567574-00-3d2bstza716gq.kirk.replit.dev`

### Register
```bash
curl -X POST https://97d3a6c0-0cc4-488f-9056-f562cf567574-00-3d2bstza716gq.kirk.replit.dev/api/auth/register \
  -H "Content-Type: application/json" \
  -H "User-Agent: VerzekAutoTrader/1.0 (Expo; React-Native)" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "full_name": "Test User"
  }'
```

### Login
```bash
curl -X POST https://97d3a6c0-0cc4-488f-9056-f562cf567574-00-3d2bstza716gq.kirk.replit.dev/api/auth/login \
  -H "Content-Type: application/json" \
  -H "User-Agent: VerzekAutoTrader/1.0 (Expo; React-Native)" \
  -d '{
    "email": "demo@verzektrader.com",
    "password": "Demo123!"
  }'
```

### Check Verification Status
```bash
curl -X GET https://97d3a6c0-0cc4-488f-9056-f562cf567574-00-3d2bstza716gq.kirk.replit.dev/api/auth/check-verification \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📊 System Status

### Backend Services Running:
- ✅ Flask API Server (Port 5000)
- ✅ DCA Orchestrator (Auto-trading engine)
- ✅ Target Monitor (Take-profit tracking)
- ✅ Broadcast Bot (Telegram signal distribution)
- ✅ Recurring Payments Handler
- ✅ Advanced Orders Monitor
- ✅ Price Feed Service (WebSocket)

### Database Files:
- `database/users_v2.json` - User accounts & settings
- `database/data.json` - Positions & trading data
- `database/logs.txt` - System logs
- `database/trades_log.json` - Trade history

---

## 🚨 Troubleshooting

### App won't connect to backend
1. Check API URL in `mobile_app/VerzekApp/src/config/api.js`
2. Ensure backend workflow is running
3. Test API endpoint with curl

### Email verification not working
1. Dev mode: Check console logs for verification link
2. Production: Configure SMTP secrets

### Exchange connection fails
1. Verify API keys are correct
2. Check IP whitelist (Binance requires static IP)
3. Cloudflare proxy handles IP whitelisting automatically

### Can't place trades
1. Ensure email is verified
2. Check subscription plan (Free plan = manual only)
3. Verify exchange account is connected
4. Check safety controls aren't blocking trades

---

## 📝 Next Steps

1. ✅ Test registration flow on mobile app
2. ✅ Verify email verification screen works
3. ✅ Connect a demo exchange account
4. ✅ Test subscription upgrade flow
5. ✅ Generate referral code and test commission tracking
6. ✅ Deploy to production (Replit Reserved VM)
7. ✅ Configure SMTP for production emails
8. ✅ Set up USDT TRC20 wallet for payments
9. ✅ Build and distribute app via EAS

---

## 🎯 Feature Checklist

- ✅ Multi-tenant user management
- ✅ Email verification system
- ✅ Encrypted API credentials (AES-128)
- ✅ Multi-exchange support (4 exchanges)
- ✅ DCA auto-trading engine
- ✅ Telegram signal monitoring
- ✅ Subscription payment system (USDT TRC20)
- ✅ Referral & commission system
- ✅ Mobile app (React Native + Expo)
- ✅ JWT authentication
- ✅ Rate limiting & security
- ✅ CAPTCHA (web only)
- ✅ Cloudflare proxy (static IP)
- ✅ Safety controls & risk management
- ✅ Real-time price feeds
- ✅ Advanced order types
- ✅ Position tracking
- ✅ Trading journal
- ✅ Leaderboards & social trading

**Project Status:** ✅ Production Ready!
