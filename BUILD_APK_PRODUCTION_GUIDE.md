# 🏗️ VerzekAutoTrader Production APK Build Guide

**Version**: 1.2.0 (versionCode 16)  
**Backend**: https://api.verzekinnovative.com ✅ LIVE  
**Date**: November 7, 2025

---

## ⚡ QUICK BUILD (1 Command)

Open **Replit Shell** and run:

```bash
cd mobile_app/VerzekApp && EAS_SKIP_AUTO_FINGERPRINT=1 eas build --platform android --profile preview
```

**Expected Time**: 10-15 minutes  
**Result**: APK download link

---

## 📋 STEP-BY-STEP BUILD PROCESS

### Step 1: Open Replit Shell

Click on the **Shell** tab in Replit (bottom of screen).

### Step 2: Navigate to App Directory

```bash
cd mobile_app/VerzekApp
```

### Step 3: Verify Configuration

```bash
cat app.json | grep version
# Should show: "version": "1.2.0"

cat config_production.js | grep API_BASE_URL
# Should show: "https://api.verzekinnovative.com"
```

### Step 4: Start the Build

```bash
EAS_SKIP_AUTO_FINGERPRINT=1 eas build --platform android --profile preview
```

**Note**: The `EAS_SKIP_AUTO_FINGERPRINT=1` flag prevents fingerprint computation timeouts.

### Step 5: Wait for Build

You'll see:
```
✔ Uploaded to EAS
- Waiting for build to complete
```

**Do NOT close the Shell tab!** Keep it open until you see the download link.

### Step 6: Get APK Download Link

When build completes, you'll see:
```
✔ Build finished

APK: https://expo.dev/artifacts/eas/[build-id].apk
```

**Copy this URL** - it's your APK download link!

---

## 🔍 VERIFICATION STEPS

After getting the APK:

### 1. Download the APK
```bash
# The link will be provided in the build output
# Example: https://expo.dev/artifacts/eas/abc123.apk
```

### 2. Install on Android Device
- Transfer APK to Android device
- Enable "Install from Unknown Sources" in Settings
- Install the APK

### 3. Test Backend Connection

Open the app and check:
- ✅ Console shows: `✅ API Online: { status: "ok" }`
- ✅ Registration works
- ✅ Login returns JWT tokens
- ✅ Signals load from backend

---

## 🚨 TROUBLESHOOTING

### Build Failed with "Gradle error"

**Solution**: Retry with cache clearing:
```bash
eas build --platform android --profile preview --clear-cache
```

### Build Stuck at "Computing fingerprint"

**Solution**: Already handled by `EAS_SKIP_AUTO_FINGERPRINT=1` flag

### "Out of build credits" Error

**Current Usage**: 97% of monthly credits used

**Options**:
1. Wait until next billing cycle
2. Add payment method at: https://expo.dev/accounts/ellizza/settings/billing
3. Upgrade to paid plan for more credits

### Can't Find Download Link

**Solution**: Check build history:
```bash
eas build:list
```

Or visit: https://expo.dev/accounts/ellizza/projects/verzek-app/builds

---

## 📊 BUILD CONFIGURATION

### App Details:
- **Name**: Verzek AutoTrader
- **Package**: com.verzek.autotrader
- **Version**: 1.2.0
- **Version Code**: 16
- **Expo SDK**: 51

### Backend Configuration:
- **API URL**: https://api.verzekinnovative.com
- **API Key**: Verzek2025AutoTrader (auto-included in headers)
- **Timeout**: 10 seconds
- **Health Check**: Runs on app startup

### Build Profile (preview):
- **Type**: APK (for direct installation)
- **Distribution**: Internal
- **Keystore**: Expo managed (Build Credentials xtdLrgP6CC)

---

## ✅ PRE-BUILD CHECKLIST

Before running the build, verify:

- [x] Backend is live: https://api.verzekinnovative.com ✅
- [x] App version updated: 1.2.0 ✅
- [x] Version code incremented: 16 ✅
- [x] API config uses production: config_production.js ✅
- [x] All dependencies installed ✅
- [x] EAS CLI authenticated ✅
- [x] Build credits available: 3% remaining ⚠️

---

## 📱 POST-BUILD TESTING

After installing the APK on your device:

### 1. Initial Launch
- App should load without crashes
- Splash screen shows Verzek logo
- Console log: `✅ API Online`

### 2. Registration Test
- Go to Register screen
- Fill in: email, password, full name
- Complete CAPTCHA
- Tap "Register"
- **Expected**: Success message + verification email sent

### 3. Login Test
- Use registered credentials
- Complete CAPTCHA
- Tap "Login"
- **Expected**: JWT tokens received + redirect to Dashboard

### 4. Signals Feed Test
- Navigate to Signals tab
- **Expected**: Trading signals load from `/api/signals`
- Signals display: Symbol, entry, targets, SL

### 5. Settings Test
- Go to Settings
- Change any setting
- Save
- **Expected**: Settings persist to backend

### 6. Subscription Test
- Settings → Subscription
- **Expected**: Current plan shown
- Payment flow accessible

---

## 🎯 SUCCESS CRITERIA

Build is successful when:

1. ✅ EAS build completes without errors
2. ✅ APK download link is generated
3. ✅ APK installs on Android device
4. ✅ App launches without crashes
5. ✅ Console shows: `✅ API Online`
6. ✅ Registration works
7. ✅ Login returns JWT tokens
8. ✅ Signals load from backend
9. ✅ All API endpoints respond correctly
10. ✅ No CORS or authentication errors

---

## 📞 SUPPORT

### Build Issues:
- **EAS Dashboard**: https://expo.dev/accounts/ellizza/projects/verzek-app/builds
- **Expo Docs**: https://docs.expo.dev/build/setup/

### Backend Issues:
- **API Endpoint**: https://api.verzekinnovative.com
- **Health Check**: https://api.verzekinnovative.com/health
- **Email**: support@verzekinnovative.com

---

## 🎉 EXPECTED OUTPUT

After successful build:

```
✔ Build finished

Build Details:
  Platform: Android
  Status: Finished
  
APK: https://expo.dev/artifacts/eas/[unique-build-id].apk

You can monitor the build at:
https://expo.dev/accounts/ellizza/projects/verzek-app/builds/[build-id]
```

**Download the APK from the provided link and install on your Android device!**

---

## 📝 NOTES

- **Build Time**: Typically 10-15 minutes
- **Build Credits**: 97% used - may need to add payment method
- **Manual Build Required**: Automated builds fail in Replit due to git lock protection
- **Profile Used**: preview (generates APK, not AAB)
- **Credentials**: Managed by Expo (keystore xtdLrgP6CC)

---

**Ready to build? Run the command in Replit Shell and you'll have your APK in ~15 minutes!** 🚀
