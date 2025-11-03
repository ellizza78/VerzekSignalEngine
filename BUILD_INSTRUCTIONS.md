# VerzekAutoTrader Build Instructions
## Version 1.1.5 - API Updated to api.verzekinnovative.com

### ✅ Changes in This Build:
1. **API Base URL Updated**: Now using `https://api.verzekinnovative.com`
2. **All URLs Secured**: Replaced all `http://` with `https://`
3. **Help Resources Updated**: All guide links now use HTTPS
4. **Build Caches Cleared**: Fresh build with no cached URLs
5. **Backend Tested**: Registration and health endpoints confirmed working

### 📱 Build Android APK (From Replit Shell)

**Step 1: Navigate to app directory**
```bash
cd mobile_app/VerzekApp
```

**Step 2: Build Android APK**
```bash
eas build --platform android --profile preview --non-interactive
```

**Step 3: Wait for build to complete**
- Build typically takes 10-15 minutes
- You'll get a download link when it's done
- Download URL will be shown in terminal

### 📲 Build iOS Preview (For iPhone Testing)

**Step 1: Build iOS Simulator Build**
```bash
eas build --platform ios --profile preview --non-interactive
```

**Step 2: Or create QR code for physical iPhone testing**
```bash
npx expo publish --release-channel preview
```

Then scan the QR code with the Expo Go app on your iPhone.

### 🧪 Alternative: Quick Update via OTA (No APK Rebuild)

If you only changed JavaScript code (not native configs), you can push an OTA update:

```bash
cd mobile_app/VerzekApp
eas update --branch preview --message "Updated API to api.verzekinnovative.com"
```

This will update existing app installations within 5 minutes without needing a new APK.

### 📊 Build Status Check

**Check build status:**
```bash
eas build:list
```

**View specific build:**
```bash
eas build:view [BUILD_ID]
```

### 🔗 Expected Build Artifacts

After successful build, you'll receive:

**Android APK:**
- Download URL: `https://expo.dev/artifacts/[artifact-id]`
- File: `verzek-autotrader-v1.1.5.apk`
- Size: ~40-50 MB

**iOS Preview:**
- QR Code for Expo Go app
- Or TestFlight link if using internal distribution

### ✅ Backend API Verification

Before testing the app, confirm backend is responding:

```bash
# Test health endpoint
curl https://api.verzekinnovative.com/api/health

# Test registration endpoint
curl -X POST https://api.verzekinnovative.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"Test1234!"}'
```

Both should return `200 OK` with JSON responses.

### 🎯 Post-Build Testing Checklist

After installing the new APK:

- [ ] App opens without crashes
- [ ] Registration creates new account
- [ ] Verification email is received (check spam)
- [ ] Login works after verification
- [ ] Dashboard loads user data
- [ ] Help resources links open correctly
- [ ] No console errors about API connections

### 📝 Version Info

- **App Version**: 1.1.5
- **Android Version Code**: 15
- **API Endpoint**: https://api.verzekinnovative.com
- **Build Date**: November 3, 2025
- **Build Profile**: preview (internal testing)

---

## 🚨 Troubleshooting

**If build fails:**
1. Check EXPO_TOKEN is set in Replit Secrets
2. Run `eas whoami` to confirm authentication
3. Clear node_modules: `rm -rf node_modules && npm install`
4. Try again with `--clear-cache` flag

**If app doesn't connect to API:**
1. Verify DNS: `nslookup api.verzekinnovative.com`
2. Test SSL: `curl -v https://api.verzekinnovative.com/api/health`
3. Check app logs in Expo dev tools
4. Ensure backend is running on Vultr

---

**Need help?** Contact support@verzekinnovative.com
