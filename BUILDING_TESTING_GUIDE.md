# 📱 Building & Testing Guide - Expo Go

## 🔑 **TEST ACCOUNT CREDENTIALS**

```
Email:    demo@verzektrader.com
Password: Demo123!
```

**Account Details:**
- ✅ Email verified
- ✅ Pro subscription (active)
- ✅ All features unlocked
- ✅ Can connect exchanges
- ✅ Auto-trading enabled

---

## 🚀 **QUICK START (3 Steps)**

### **Step 1: Install Expo Go**

Download Expo Go on your phone:

**📱 iOS (iPhone/iPad):**
```
App Store → Search "Expo Go" → Install
Direct: https://apps.apple.com/app/expo-go/id982107779
```

**📱 Android:**
```
Play Store → Search "Expo Go" → Install
Direct: https://play.google.com/store/apps/details?id=host.exp.exponent
```

---

### **Step 2: Start Development Server**

**Option A: Use Quick Start Script (Easiest)**
```bash
./TEST_APP_NOW.sh
```

**Option B: Manual Command**
```bash
cd mobile_app/VerzekApp
npx expo start
```

**What You'll See:**
```
Starting Metro Bundler...
Metro waiting on exp://192.168.x.x:8081

› Press s │ switch to Expo Go
› Press a │ open Android
› Press i │ open iOS simulator

› Scan the QR code above with Expo Go (Android) or the Camera app (iOS)
```

---

### **Step 3: Scan QR Code**

**On iOS:**
1. Open **Camera app** (built-in)
2. Point at the QR code in your terminal
3. Tap the notification that appears
4. App opens in Expo Go! 🎉

**On Android:**
1. Open **Expo Go app**
2. Tap **"Scan QR Code"** button
3. Point at the QR code in your terminal
4. App opens! 🎉

---

## 🎯 **TESTING WORKFLOW**

### **1. First Launch**

App loads → See Login Screen

**Login with:**
```
Email:    demo@verzektrader.com
Password: Demo123!
```

Tap **"Login"** → Dashboard appears!

---

### **2. Dashboard Screen**

You'll see:
- ✅ User profile (demo@verzektrader.com)
- ✅ Subscription badge (Pro)
- ✅ Account balance
- ✅ Trading stats (win rate, total trades)
- ✅ Quick action buttons

---

### **3. Exchange Accounts**

Tap **"Exchange Accounts"** in bottom nav:

**Features:**
- View connected exchanges
- Add new exchange (Binance, Bybit, Phemex, Kraken)
- Enter API keys (encrypted storage)
- Test connection
- Enable/disable auto-trading
- Remove exchange

**To Add Exchange:**
1. Tap **"+" button**
2. Select exchange (e.g., Binance)
3. Enter API Key
4. Enter API Secret
5. Tap **"Test Connection"**
6. Tap **"Save"** if test passes

---

### **4. Positions**

Tap **"Positions"** tab:

**View:**
- Active positions
- Entry price
- Current price
- Take-profit levels
- Stop-loss
- Profit/Loss (P&L)
- Position size

---

### **5. Signals Feed**

Tap **"Signals"** tab:

**Features:**
- Real-time trading signals
- Quality scores (0-100)
- Priority signals highlighted (⚡)
- Signal details (entry, TP, SL)
- Auto-trade toggle
- Manual execute button

---

### **6. Settings**

Tap **"Settings"** tab:

**Configure:**
- **General Settings**
  - Email notifications
  - Push notifications
  - Default exchange
  
- **Risk Management**
  - Max leverage
  - Position size limits
  - Daily loss limit
  - Kill switch
  
- **DCA Settings**
  - Enable/disable DCA
  - DCA levels
  - Level multipliers
  - Take-profit mode
  
- **Strategy**
  - Signal quality threshold
  - Symbol whitelist/blacklist
  - Timeframe preferences

---

## 🔄 **LIVE RELOAD (Development)**

While the app is running on your phone:

**Make changes:**
1. Edit any file in `mobile_app/VerzekApp/src/`
2. Save the file
3. **App auto-refreshes on your phone!** ✨

**Example:**
```javascript
// Edit: src/screens/DashboardScreen.js
// Change some text or colors
// Save
// → App instantly updates on phone!
```

**No need to:**
- ❌ Rebuild
- ❌ Restart server
- ❌ Rescan QR code

Just edit and save! 🚀

---

## 🛠️ **DEVELOPMENT MENU**

**Open Dev Menu:**
- **iOS:** Shake your phone
- **Android:** Shake your phone (or press hardware menu button)

**Options:**
- **Reload** - Refresh the app
- **Go Home** - Return to Expo Go home
- **Debug Remote JS** - Use Chrome DevTools
- **Show Performance Monitor** - See FPS, memory
- **Toggle Inspector** - Inspect elements

---

## 💡 **EXPO START MODES**

### **Default Mode (LAN)**
```bash
npx expo start
```
- ✅ Fastest
- ✅ Phone and computer must be on same WiFi
- ✅ Best for normal development

### **Tunnel Mode**
```bash
npx expo start --tunnel
```
- ✅ Works from anywhere (public URL)
- ✅ Bypasses network/firewall issues
- ✅ Use if QR code won't scan
- ⚠️ Slightly slower

### **Clear Cache**
```bash
npx expo start -c
```
- ✅ Clears Metro bundler cache
- ✅ Use if seeing old code
- ✅ Fixes most bundling issues

### **Web Preview**
```bash
npx expo start --web
```
- ✅ Opens in browser
- ✅ Quick preview without phone
- ⚠️ Some features may not work (camera, etc.)

---

## 🐛 **TROUBLESHOOTING**

### **Problem: QR Code Won't Scan**

**Solution 1:** Make sure phone and computer on same WiFi

**Solution 2:** Use tunnel mode
```bash
npx expo start --tunnel
```

**Solution 3:** Enter URL manually
1. Note the `exp://192.168.x.x:8081` in terminal
2. In Expo Go, tap "Enter URL manually"
3. Type the URL

---

### **Problem: "Unable to Connect to Metro"**

**Solution 1:** Clear cache
```bash
npx expo start -c
```

**Solution 2:** Restart server
```bash
# Press Ctrl+C to stop
npx expo start
```

**Solution 3:** Check firewall
- Allow port 8081
- Or use tunnel mode

---

### **Problem: "Login Failed" or Network Error**

**Check Backend:**
```bash
# Test if backend is running
curl https://97d3a6c0-0cc4-488f-9056-f562cf567574-00-3d2bstza716gq.kirk.replit.dev/api/auth/login \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@verzektrader.com","password":"Demo123!","skip_captcha":true}'
```

Should return user data with tokens.

**Check API URL:**
```bash
# Verify API URL is correct
cat mobile_app/VerzekApp/src/config/api.js
```

Should show current Replit domain.

---

### **Problem: App Shows Old Code**

**Solution:** Clear cache and reload
```bash
# Stop server (Ctrl+C)
npx expo start -c
```

On phone:
1. Shake device
2. Tap "Reload"

---

### **Problem: "Couldn't Install Dependencies"**

**Solution:** Install manually
```bash
cd mobile_app/VerzekApp
npm install
```

Then restart Expo:
```bash
npx expo start
```

---

## 📊 **BACKEND STATUS**

**Backend API:** ✅ Running 24/7

**URL:**
```
https://97d3a6c0-0cc4-488f-9056-f562cf567574-00-3d2bstza716gq.kirk.replit.dev
```

**Status Check:**
Open in browser:
```
https://97d3a6c0-0cc4-488f-9056-f562cf567574-00-3d2bstza716gq.kirk.replit.dev
```

Should show Flask welcome or "Not Found" (means it's running).

---

## 🎨 **APP FEATURES TO TEST**

### **✅ Authentication**
- [x] Login with demo account
- [x] JWT token storage
- [x] Auto token refresh
- [x] Logout
- [x] Stay logged in (persistent)

### **✅ Dashboard**
- [x] User profile display
- [x] Subscription status
- [x] Account balance
- [x] Trading statistics
- [x] Quick actions

### **✅ Email Verification**
- [x] Verification status
- [x] Resend email button
- [x] Email sent confirmation

### **✅ Exchange Accounts**
- [x] List connected exchanges
- [x] Add new exchange
- [x] Test connection
- [x] Edit API keys
- [x] Delete exchange
- [x] Encrypted storage

### **✅ Positions**
- [x] Active positions list
- [x] Position details
- [x] Real-time P&L
- [x] Entry/TP/SL prices
- [x] Close position

### **✅ Signals Feed**
- [x] Real-time signals
- [x] Quality scores
- [x] Priority indicators
- [x] Signal details
- [x] Auto-trade toggle

### **✅ Settings**
- [x] General preferences
- [x] Risk management
- [x] DCA configuration
- [x] Strategy settings
- [x] Save changes

---

## 🚀 **BUILDING FOR PRODUCTION**

Once you're happy with testing:

### **Build Android APK (Preview)**
```bash
cd mobile_app/VerzekApp
eas build --platform android --profile preview
```

### **Build iOS IPA**
```bash
eas build --platform ios --profile production
```

### **Submit to Stores**
```bash
eas submit --platform all
```

**Note:** Requires Expo account (free to sign up)

---

## 📝 **EXPO GO vs PRODUCTION BUILD**

| Feature | Expo Go | Production Build |
|---------|---------|------------------|
| Testing | ✅ Best for development | ⚠️ For final testing |
| Speed | ✅ Instant reload | ❌ Rebuild needed |
| Libraries | ⚠️ Limited to Expo SDK | ✅ All libraries |
| Installation | ✅ Just scan QR | ❌ Need to install APK/IPA |
| Sharing | ✅ Share QR code | ❌ Need to send file |
| Performance | ⚠️ Slightly slower | ✅ Full speed |

**For testing: Use Expo Go** ✅  
**For production: Build standalone app** ✅

---

## 🎯 **NEXT STEPS**

1. **✅ Test with Expo Go** (you are here!)
2. **✅ Verify all features work**
3. **✅ Test on both iOS and Android** (if possible)
4. **🚀 Build for production** (when ready)
5. **🚀 Submit to App Store/Play Store**

---

## 📚 **DOCUMENTATION**

**Created for you:**
- `EXPO_QUICK_START.md` - Quick reference
- `TEST_CREDENTIALS.md` - Account details
- `MOBILE_APP_SETUP.md` - Complete setup guide
- `COMPLETE_SYSTEM_SUMMARY.md` - Full platform overview

---

## ✅ **YOU'RE ALL SET!**

**To start testing right now:**

```bash
./TEST_APP_NOW.sh
```

**Then:**
1. Install Expo Go on your phone
2. Scan the QR code
3. Login with demo account
4. Test all features!

**Login:**
- Email: demo@verzektrader.com
- Password: Demo123!

🎉 **Happy Testing!** 📱✨
