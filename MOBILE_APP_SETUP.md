# 📱 VerzekAutoTrader Mobile App - Quick Start Guide

## ✅ Status: READY TO TEST

Your mobile app is fully configured and ready to run!

---

## 🔑 Test Account Credentials

**Use these credentials to login and test all features:**

```
Email: demo@verzektrader.com
Password: Demo123!
```

**Account Features:**
- ✅ Email verified
- ✅ Pro subscription (active)
- ✅ Full access to all features
- ✅ Exchange accounts can be connected
- ✅ Auto-trading enabled

---

## 🚀 How to Run the App

### **Option 1: Run in Expo Go (Easiest - Recommended)**

1. **Install Expo Go on your phone:**
   - iOS: [Download from App Store](https://apps.apple.com/app/expo-go/id982107779)
   - Android: [Download from Google Play](https://play.google.com/store/apps/details?id=host.exp.exponent)

2. **Start the Expo server:**
   ```bash
   cd mobile_app/VerzekApp
   npx expo start
   ```

3. **Scan the QR code:**
   - iOS: Open Camera app → Scan QR code → Tap notification
   - Android: Open Expo Go app → Scan QR code

4. **App will load on your phone!** 📱

---

### **Option 2: Run in Simulator/Emulator**

**For iOS Simulator (Mac only):**
```bash
cd mobile_app/VerzekApp
npx expo start --ios
```

**For Android Emulator:**
```bash
cd mobile_app/VerzekApp
npx expo start --android
```

**For Web Browser:**
```bash
cd mobile_app/VerzekApp
npx expo start --web
```

---

## 🎯 What You Can Test

### **1. Authentication**
- ✅ Login with test account
- ✅ JWT token refresh (automatic)
- ✅ Secure token storage
- ✅ Logout functionality

### **2. Dashboard**
- ✅ User profile information
- ✅ Subscription status (Pro)
- ✅ Account balance display
- ✅ Trading statistics
- ✅ Quick action buttons

### **3. Email Verification**
- ✅ Verification status check
- ✅ Resend verification email
- ✅ Beautiful verification emails with VZK branding

### **4. Exchange Accounts**
- ✅ View connected exchanges
- ✅ Add new exchange (Binance, Bybit, Phemex, Kraken)
- ✅ Encrypted API key storage
- ✅ Test connection
- ✅ Remove exchange

### **5. Settings**
- ✅ View/update user settings
- ✅ Risk management settings
- ✅ DCA configuration
- ✅ Strategy preferences

### **6. Positions**
- ✅ Active positions list
- ✅ Position details (entry, TP, SL)
- ✅ Real-time P&L updates
- ✅ Position history

### **7. Signals Feed**
- ✅ Real-time trading signals
- ✅ Signal quality scores
- ✅ Priority signals highlighted
- ✅ Auto-trade toggle

---

## 🎨 App Design

**VZK Branding:**
- 🎨 Teal/Gold gradient theme
- 🌙 Modern dark mode design
- ✨ Smooth animations
- 📱 Responsive layout

**Color Scheme:**
- Primary: Teal gradient (#0A4A5C → #1B9AAA)
- Accent: Gold (#F9C74F)
- Background: Dark Navy (#1a1a2e)
- Text: White/Gray for readability

---

## 📊 Backend Connection

**API URL (already configured):**
```
https://97d3a6c0-0cc4-488f-9056-f562cf567574-00-3d2bstza716gq.kirk.replit.dev
```

**Status:** ✅ Backend running and ready

**Available APIs:**
- ✅ Authentication endpoints
- ✅ User management
- ✅ Exchange accounts
- ✅ Positions tracking
- ✅ Settings management
- ✅ Subscription management
- ✅ Payment processing

---

## 🔧 Troubleshooting

### **Can't connect to backend?**
```bash
# Check if backend is running
curl https://97d3a6c0-0cc4-488f-9056-f562cf567574-00-3d2bstza716gq.kirk.replit.dev/health

# Should return: {"status": "healthy"}
```

### **Dependencies missing?**
```bash
cd mobile_app/VerzekApp
npm install
```

### **Expo not installed?**
```bash
npm install -g expo-cli
# or use npx: npx expo start
```

### **Metro bundler issues?**
```bash
# Clear cache and restart
cd mobile_app/VerzekApp
npx expo start -c
```

---

## 📱 Building for Production

### **Android APK (Preview Build)**
```bash
cd mobile_app/VerzekApp
eas build --platform android --profile preview
```

### **Android AAB (Production)**
```bash
eas build --platform android --profile production
```

### **iOS IPA (TestFlight)**
```bash
eas build --platform ios --profile production
```

**Note:** You'll need an Expo account (free) to build. Run `eas login` first.

---

## 🧪 Complete Testing Flow

**Test this complete user journey:**

1. **Open app** → See Login screen ✅
2. **Login** with demo@verzektrader.com / Demo123! ✅
3. **Dashboard** loads with user info ✅
4. **Tap "Exchange Accounts"** → See exchanges screen ✅
5. **Add exchange** → Test API key encryption ✅
6. **Tap "Positions"** → See trading positions ✅
7. **Tap "Signals"** → See real-time signals feed ✅
8. **Tap "Settings"** → Configure trading preferences ✅
9. **Logout** → Returns to login screen ✅
10. **Login again** → Auto-loads previous session ✅

---

## 🎯 Features Overview

### **Implemented:**
- ✅ JWT Authentication
- ✅ Email Verification System
- ✅ Dashboard with stats
- ✅ Exchange Account Management
- ✅ Position Tracking
- ✅ Settings Configuration
- ✅ Secure Token Storage
- ✅ Auto Token Refresh
- ✅ Beautiful UI with VZK branding
- ✅ Onboarding Modal

### **Coming Soon:**
- 🚧 Push Notifications (FCM)
- 🚧 Real-time WebSocket Updates
- 🚧 Advanced Charts
- 🚧 Trade History
- 🚧 Referral Dashboard
- 🚧 Payment Integration

---

## 📋 Quick Commands Reference

```bash
# Start development server
cd mobile_app/VerzekApp && npx expo start

# Run on iOS simulator
npx expo start --ios

# Run on Android emulator
npx expo start --android

# Run in web browser
npx expo start --web

# Clear cache
npx expo start -c

# Install dependencies
npm install

# Build for Android
eas build --platform android --profile preview

# Build for iOS
eas build --platform ios --profile production
```

---

## 🎉 You're All Set!

**Everything is ready:**
1. ✅ Backend API running
2. ✅ Mobile app configured
3. ✅ Test account created
4. ✅ Dependencies installed
5. ✅ Database ready

**Just run:**
```bash
cd mobile_app/VerzekApp && npx expo start
```

**Then scan the QR code with Expo Go app on your phone!**

---

## 💡 Pro Tips

1. **Shake your phone** to open Expo dev menu
2. **Enable Fast Refresh** for instant updates
3. **Use Expo Go** for fastest testing
4. **Build APK** for sharing with testers
5. **Hot reload** works automatically - just save files!

---

## 🆘 Need Help?

**Common Issues:**

**Q: QR code not scanning?**
A: Make sure phone and computer are on same WiFi network

**Q: App won't load?**
A: Check backend is running, clear Expo cache with `-c` flag

**Q: Login fails?**
A: Verify backend URL is correct in `src/config/api.js`

**Q: Can't build?**
A: Run `eas login` and `eas build:configure` first

---

## 📞 Test Account Info

```
Email: demo@verzektrader.com
Password: Demo123!

Subscription: Pro (active)
Email Verified: Yes
Features: All unlocked
```

**Happy Testing! 🎉**
