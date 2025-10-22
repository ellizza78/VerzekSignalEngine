# 🔑 VerzekAutoTrader - Test Account Credentials

## Mobile App Test Account

**Use these credentials to login and test the mobile app:**

```
Email:    demo@verzektrader.com
Password: Demo123!
```

---

## Account Details

**Status:** ✅ Active and Ready
- ✅ Email verified
- ✅ Pro subscription (active)
- ✅ All features unlocked
- ✅ Can connect exchange accounts
- ✅ Auto-trading enabled

---

## How to Test

### **1. Start the Mobile App**

**Option A: Use startup script (easiest):**
```bash
./start_mobile_app.sh
```

**Option B: Manual start:**
```bash
cd mobile_app/VerzekApp
npx expo start
```

### **2. Install Expo Go on Your Phone**

- **iOS:** [App Store - Expo Go](https://apps.apple.com/app/expo-go/id982107779)
- **Android:** [Play Store - Expo Go](https://play.google.com/store/apps/details?id=host.exp.exponent)

### **3. Scan QR Code**

- **iOS:** Open Camera app → Scan QR code → Tap notification
- **Android:** Open Expo Go app → Tap "Scan QR code"

### **4. Login with Test Account**

```
Email:    demo@verzektrader.com
Password: Demo123!
```

---

## What You Can Test

### ✅ **Authentication**
- Login/Logout
- JWT token refresh
- Secure storage

### ✅ **Dashboard**
- User profile
- Subscription status
- Account stats
- Quick actions

### ✅ **Exchange Accounts**
- View connected exchanges
- Add new exchange (Binance, Bybit, Phemex, Kraken)
- Test connection
- Encrypted API keys

### ✅ **Positions**
- Active positions
- Position details
- P&L tracking
- History

### ✅ **Settings**
- User preferences
- Risk management
- DCA configuration
- Strategy settings

### ✅ **Signals Feed**
- Real-time signals
- Quality scores
- Priority indicators
- Auto-trade toggle

---

## Backend API

**Base URL:**
```
https://97d3a6c0-0cc4-488f-9056-f562cf567574-00-3d2bstza716gq.kirk.replit.dev
```

**Status:** ✅ Running and accessible

---

## Additional Test Accounts

If you need more test accounts, you can create them in the app:

**Registration is open** - Just tap "Sign Up" on login screen and create a new account with any email.

**Note:** Mobile app bypasses CAPTCHA for better UX (CAPTCHA only required for web-based registration).

---

## Troubleshooting

**Can't login?**
- ✅ Verify email: demo@verzektrader.com
- ✅ Verify password: Demo123! (case-sensitive)
- ✅ Check internet connection
- ✅ Restart Expo server

**App won't load?**
- ✅ Make sure phone and computer are on same WiFi
- ✅ Try tunnel mode: `npx expo start --tunnel`
- ✅ Clear cache: `npx expo start -c`

**Backend not responding?**
- ✅ Check backend is running (it's configured to auto-start)
- ✅ Verify API URL in `mobile_app/VerzekApp/src/config/api.js`

---

## Quick Start Commands

```bash
# Start mobile app
./start_mobile_app.sh

# Or manually
cd mobile_app/VerzekApp && npx expo start

# Clear cache and restart
cd mobile_app/VerzekApp && npx expo start -c

# Run on iOS simulator (Mac only)
npx expo start --ios

# Run on Android emulator
npx expo start --android
```

---

## 🎉 Ready to Test!

Everything is configured and ready. Just run the startup script and scan the QR code with your phone!

```bash
./start_mobile_app.sh
```

**Happy Testing! 📱✨**
