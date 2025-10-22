# 📱 Expo Go - Quick Start Guide

## 🔑 TEST LOGIN CREDENTIALS

```
Email:    demo@verzektrader.com
Password: Demo123!
```

**Account Status:**
✅ Email verified
✅ Pro subscription (active)
✅ All features unlocked
✅ Ready to use immediately

---

## 🚀 3-STEP TESTING PROCESS

### **STEP 1: Install Expo Go on Your Phone**

Download and install the Expo Go app:

**📱 iOS (iPhone/iPad):**
- Open App Store
- Search "Expo Go"
- Install: [Direct Link](https://apps.apple.com/app/expo-go/id982107779)

**📱 Android:**
- Open Google Play Store
- Search "Expo Go"
- Install: [Direct Link](https://play.google.com/store/apps/details?id=host.exp.exponent)

---

### **STEP 2: Start the Development Server**

Open your terminal and run:

```bash
cd mobile_app/VerzekApp
npx expo start
```

**You'll see:**
```
Starting Metro Bundler...
Metro waiting on exp://192.168.x.x:8081

› Press s │ switch to Expo Go
› Press a │ open Android
› Press i │ open iOS simulator
› Press w │ open web

› Scan QR code to open in Expo Go
```

---

### **STEP 3: Scan QR Code**

**On iOS:**
1. Open **Camera app**
2. Point at the QR code in terminal
3. Tap the notification that appears
4. App opens in Expo Go!

**On Android:**
1. Open **Expo Go app**
2. Tap **"Scan QR Code"**
3. Point at the QR code in terminal
4. App opens!

---

## 📲 ALTERNATIVE: Use Tunnel Mode (For Network Issues)

If you have network/firewall issues, use tunnel mode:

```bash
cd mobile_app/VerzekApp
npx expo start --tunnel
```

This creates a public URL that works from anywhere!

---

## 🎮 TESTING FEATURES

Once the app loads on your phone:

### **1. Login**
```
Email:    demo@verzektrader.com
Password: Demo123!
```

Tap "Login" - you'll see the Dashboard!

### **2. Dashboard**
- View your profile information
- Check subscription status (Pro)
- See account balance
- View trading stats
- Quick action buttons

### **3. Exchange Accounts**
- Tap "Exchange Accounts" in bottom navigation
- See connected exchanges
- Tap "+" to add new exchange
- Choose: Binance, Bybit, Phemex, or Kraken
- Enter API keys (encrypted storage)
- Test connection

### **4. Positions**
- Tap "Positions" tab
- View active trades
- See entry price, take-profit, stop-loss
- Check P&L (profit/loss)

### **5. Signals Feed**
- Tap "Signals" tab
- See real-time trading signals
- View quality scores (0-100)
- Priority signals highlighted
- Toggle auto-trade on/off

### **6. Settings**
- Tap "Settings" tab
- Configure risk management
- Set DCA preferences
- Update strategy settings
- Adjust notifications

---

## 🔄 LIVE RELOAD

**The app supports live reload!**

While testing:
1. Keep the app open on your phone
2. Edit files in `mobile_app/VerzekApp/src/`
3. Save changes
4. App automatically refreshes on your phone!

**Try it:**
- Edit a screen in `src/screens/`
- Change colors in `src/constants/colors.js`
- Update API calls in `src/services/api.js`

---

## 🛠️ DEVELOPMENT MENU

**Shake your phone** to open the Expo development menu:

Options:
- Reload
- Go Home
- Debug Remote JS
- Show Performance Monitor
- Toggle Inspector

---

## 📊 BACKEND STATUS

**Backend API:** ✅ Running
```
https://97d3a6c0-0cc4-488f-9056-f562cf567574-00-3d2bstza716gq.kirk.replit.dev
```

The mobile app is already configured to connect to this backend!

---

## 💡 PRO TIPS

### **Faster Testing:**
```bash
# Clear cache if issues
npx expo start -c

# LAN mode (default, fastest)
npx expo start

# Tunnel mode (works anywhere)
npx expo start --tunnel

# Web preview
npx expo start --web
```

### **View Logs:**
Check terminal for:
- API requests
- Console logs
- Errors
- Network activity

### **Hot Reload:**
- Edit code → Auto-refresh
- No need to rebuild
- See changes instantly

---

## 🐛 TROUBLESHOOTING

### **QR Code Won't Scan?**

**Solution 1:** Use manual URL
1. Note the `exp://192.168.x.x:8081` URL in terminal
2. Type it manually in Expo Go

**Solution 2:** Use tunnel mode
```bash
npx expo start --tunnel
```

### **"Network Error" or "Unable to Connect"?**

**Check:**
1. ✅ Phone and computer on same WiFi
2. ✅ Backend is running (check URL in browser)
3. ✅ Firewall not blocking port 8081

**Fix:** Use tunnel mode (bypasses network issues)

### **App Crashes on Launch?**

**Solution:**
```bash
# Clear cache and restart
cd mobile_app/VerzekApp
npx expo start -c
```

### **"Login Failed" Error?**

**Verify:**
1. ✅ Using correct credentials: demo@verzektrader.com / Demo123!
2. ✅ Backend is running
3. ✅ API URL is correct in `src/config/api.js`

**Test backend:**
```bash
curl https://97d3a6c0-0cc4-488f-9056-f562cf567574-00-3d2bstza716gq.kirk.replit.dev/api/auth/login \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@verzektrader.com","password":"Demo123!"}'
```

Should return user data and tokens.

---

## 🎨 APP DESIGN

**VZK Branding:**
- 🌙 Dark theme (modern)
- 🎨 Teal/Gold gradients
- ✨ Smooth animations
- 📱 Responsive layout

**Colors:**
- Primary: Teal (#0A4A5C → #1B9AAA)
- Accent: Gold (#F9C74F)
- Background: Dark Navy (#1a1a2e)
- Text: White/Gray

---

## 📱 DEVICE COMPATIBILITY

**Tested On:**
- ✅ iOS 13+
- ✅ Android 5.0+
- ✅ iPhone 6s and newer
- ✅ Most Android phones

**Screen Sizes:**
- ✅ Phone (small/medium/large)
- ✅ Tablet
- ✅ iPad

---

## 🚀 NEXT STEPS AFTER TESTING

Once you're happy with testing:

1. **Build for Production:**
```bash
# Android APK
eas build --platform android --profile preview

# iOS IPA
eas build --platform ios --profile production
```

2. **Submit to Stores:**
```bash
eas submit --platform all
```

---

## ✅ QUICK CHECKLIST

Before testing:
- [ ] Expo Go installed on phone
- [ ] Backend running (check URL in browser)
- [ ] Terminal open in `mobile_app/VerzekApp/`

To start:
- [ ] Run `npx expo start`
- [ ] Scan QR code with phone
- [ ] Login with demo account
- [ ] Test all features!

---

## 🎉 YOU'RE READY!

**Just run:**
```bash
cd mobile_app/VerzekApp
npx expo start
```

**Then scan and test!** 📱✨

**Login:**
- Email: demo@verzektrader.com
- Password: Demo123!
