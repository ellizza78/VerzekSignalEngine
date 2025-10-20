# 📱 Verzek AutoTrader - Mobile App Deployment Guide

## 🚀 Complete Guide: APK, Google Play Store & iOS App Store

---

## 📋 **Prerequisites**

### 1. **Expo Account** (Free)
- Sign up at: https://expo.dev/signup
- Required for building apps

### 2. **Google Play Developer Account** ($25 one-time fee)
- Sign up at: https://play.google.com/console/signup
- Required for Google Play Store

### 3. **Apple Developer Account** ($99/year)
- Sign up at: https://developer.apple.com/programs/
- Required for iOS App Store

---

## 🔧 **Step 1: Install Required Tools**

Open terminal in the `mobile_app/VerzekApp/` directory and run:

```bash
# Install dependencies
npm install

# Install EAS CLI globally
npm install -g eas-cli

# Login to your Expo account
eas login
```

---

## 📱 **Step 2: Configure Your Project**

### Initialize EAS Build:
```bash
eas build:configure
```

This creates `eas.json` (already provided in your project).

### Update app.json:
Edit `app.json` and replace:
- `YOUR_EAS_PROJECT_ID` with your actual project ID (get it after running `eas build:configure`)

---

## 🤖 **Step 3: Build Android APK (for Testing)**

### Quick Test APK:
```bash
eas build --platform android --profile preview
```

**What happens:**
1. ✅ Code is uploaded to Expo cloud
2. ✅ APK is built (takes 10-20 minutes)
3. ✅ You get a download link
4. ✅ Install on any Android device

**Download & Install:**
- Click the download link from EAS dashboard
- Transfer APK to your phone
- Enable "Install from Unknown Sources" in Android settings
- Install the APK

---

## 🏪 **Step 4: Build for Google Play Store**

### Build Production AAB:
```bash
eas build --platform android --profile production
```

**What you get:**
- `.aab` file (Android App Bundle)
- Optimized for Google Play Store

### Submit to Google Play:
```bash
eas submit --platform android
```

**Or manually:**
1. Go to https://play.google.com/console
2. Create new app
3. Upload the `.aab` file
4. Fill in app details:
   - App name: **Verzek AutoTrader**
   - Description: Your trading platform description
   - Screenshots (Android phone/tablet)
   - Privacy policy URL
   - Content rating questionnaire
5. Submit for review (takes 1-7 days)

---

## 🍎 **Step 5: Build for iOS App Store**

### Build Production IPA:
```bash
eas build --platform ios --profile production
```

**First time setup:**
- EAS will prompt for Apple ID
- It will automatically create certificates and provisioning profiles
- You need an active Apple Developer account ($99/year)

### Submit to App Store:
```bash
eas submit --platform ios
```

**Or manually via App Store Connect:**
1. Go to https://appstoreconnect.apple.com
2. Create new app
3. Upload IPA file
4. Fill in app metadata:
   - App name: **Verzek AutoTrader**
   - Subtitle, description, keywords
   - Screenshots (iPhone/iPad)
   - Privacy policy URL
   - App category: Finance
5. Submit for review (takes 1-7 days)

---

## ⚡ **Step 6: Build Both Platforms at Once**

```bash
eas build --platform all --profile production
```

Builds both Android AAB and iOS IPA simultaneously!

---

## 🔄 **Step 7: Update Your App (Future Releases)**

### Increment Version Numbers:

**In app.json:**
```json
{
  "expo": {
    "version": "1.0.1",  // Update this
    "android": {
      "versionCode": 2    // Increment this
    },
    "ios": {
      "buildNumber": "2"  // Increment this
    }
  }
}
```

### Rebuild:
```bash
eas build --platform all --profile production
eas submit --platform all
```

---

## 🎨 **App Store Assets Needed**

### **Android (Google Play)**
- App icon: 512x512 PNG
- Feature graphic: 1024x500 PNG
- Screenshots: At least 2 (phone + tablet)
- Short description (80 chars)
- Full description (4000 chars)
- Privacy policy URL

### **iOS (App Store)**
- App icon: 1024x1024 PNG
- Screenshots: iPhone (6.5", 5.5") + iPad (12.9")
- App preview video (optional)
- Description (4000 chars)
- Keywords
- Privacy policy URL

---

## 💡 **Environment Variables for Production**

### Update API URL in your app:

**In `mobile_app/VerzekApp/src/config/api.js`:**
```javascript
const API_BASE_URL = __DEV__ 
  ? 'http://localhost:5000'  // Development
  : 'https://verzek-auto-trader.replit.app';  // Production

export default API_BASE_URL;
```

---

## 🐛 **Common Issues & Solutions**

### **Issue: "No bundle identifier"**
**Solution:** Make sure `bundleIdentifier` (iOS) and `package` (Android) are set in `app.json`

### **Issue: "Build failed - credentials"**
**Solution:** Run `eas credentials` to reset/configure signing credentials

### **Issue: "APK won't install"**
**Solution:** Enable "Install from Unknown Sources" in Android Settings → Security

### **Issue: "iOS build needs paid developer account"**
**Solution:** You must have an active Apple Developer account ($99/year)

---

## 📊 **Build Profiles Explained**

| Profile | Purpose | Output | Use Case |
|---------|---------|--------|----------|
| **preview** | Internal testing | APK (Android) | Quick testing on devices |
| **production** | Store release | AAB (Android), IPA (iOS) | Official app store releases |

---

## 🔐 **Security Checklist Before Release**

- ✅ Remove all console.log() statements
- ✅ Use production API URL (not localhost)
- ✅ Enable ProGuard/R8 for Android
- ✅ Test on real devices
- ✅ Set up crash reporting (optional: Sentry)
- ✅ Add privacy policy
- ✅ Add terms of service

---

## 📞 **Quick Command Reference**

```bash
# Build APK for testing
eas build --platform android --profile preview

# Build for Google Play
eas build --platform android --profile production

# Build for App Store
eas build --platform ios --profile production

# Build both platforms
eas build --platform all --profile production

# Submit to stores
eas submit --platform android
eas submit --platform ios

# Check build status
eas build:list

# Manage credentials
eas credentials
```

---

## 🎯 **Recommended Flow**

1. ✅ **Week 1:** Build preview APK → Test on Android devices
2. ✅ **Week 2:** Build iOS preview → Test on iPhone/iPad
3. ✅ **Week 3:** Build production builds → Submit to both stores
4. ✅ **Week 4:** Wait for review approval → Launch! 🚀

---

## 📚 **Official Documentation**

- Expo EAS Build: https://docs.expo.dev/build/introduction/
- Google Play Console: https://play.google.com/console
- App Store Connect: https://appstoreconnect.apple.com

---

## 🆘 **Need Help?**

- Expo Forums: https://forums.expo.dev
- Discord: https://chat.expo.dev
- Stack Overflow: Tag `expo` or `react-native`

---

**Your app bundle ID: `com.verzek.autotrader`**

Good luck with your launch! 🎉
