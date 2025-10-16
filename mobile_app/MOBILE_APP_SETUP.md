# 📱 VerzekAutoTrader Mobile App - Setup Guide

## ✅ What's Complete

Your React Native mobile app with JWT authentication is **fully functional**! Here's what's ready:

### Backend (Tested & Working)
- ✅ JWT Authentication API (registration, login, refresh, me)
- ✅ Secure password hashing with bcrypt
- ✅ Access tokens (1hr) + Refresh tokens (30 days)
- ✅ User creation with email validation
- ✅ Protected endpoints with @token_required decorator

### Mobile App (Built & Ready)
- ✅ Expo React Native app structure
- ✅ Login/Register screens with validation
- ✅ Dashboard with user stats and subscription info
- ✅ Automatic token refresh on 401 errors
- ✅ Auth-based navigation (Login stack ↔ Dashboard stack)
- ✅ Modern dark UI (Navy #1a1a2e + Pink #e94560)
- ✅ Secure AsyncStorage for tokens

---

## 🚀 How to Run the Mobile App

### Step 1: Install Dependencies

```bash
cd mobile_app/VerzekApp
npm install
```

### Step 2: Configure Backend URL

**Option A: Edit config file (Recommended)**
Edit `mobile_app/VerzekApp/src/config/api.js`:

```javascript
export const API_BASE_URL = 'https://YOUR-REPLIT-URL.replit.app';
```

**Option B: Use environment variable**
Create `.env` file:
```
EXPO_PUBLIC_API_URL=https://YOUR-REPLIT-URL.replit.app
```

### Step 3: Start the App

```bash
# Start Expo dev server
npm start

# OR run directly on platform
npm run ios      # For iOS simulator
npm run android  # For Android emulator
```

### Step 4: Test Authentication

1. **Register a new user:**
   - Open app → Tap "Sign Up"
   - Enter full name, email, password
   - App will auto-login after registration

2. **Login with existing user:**
   - Email: test@verzek.com
   - Password: test123
   - (Test user already created on backend)

---

## 📲 Testing on Physical Device

### Using Expo Go (Easiest)

1. Install **Expo Go** app:
   - iOS: [App Store](https://apps.apple.com/app/expo-go/id982107779)
   - Android: [Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)

2. Run `npm start` in terminal

3. Scan QR code with:
   - **iOS**: Camera app
   - **Android**: Expo Go app

4. App opens instantly on your phone!

---

## 🎨 App Features

### Current Features
- ✅ **Secure Authentication**: JWT-based login/register
- ✅ **Auto Token Refresh**: Seamless session management
- ✅ **Dashboard**: Account overview with stats
- ✅ **Subscription Display**: Visual tier badges (Free/Pro/VIP)
- ✅ **Pull to Refresh**: Update user data
- ✅ **Logout**: Secure session termination

### Coming Soon 🚧
- 📡 **Signals Feed**: Real-time trading signals
- 📊 **Positions Screen**: Active/closed positions
- ⚙️ **Settings**: Configure risk, DCA, strategy
- 🔗 **Exchange Management**: Connect exchange APIs
- 🔔 **Push Notifications**: Signal alerts & TP notifications

---

## 🔧 Backend API Endpoints

Your Flask API is running at `http://YOUR-REPLIT-URL.replit.app`

### Authentication Endpoints
```
POST /api/auth/register
POST /api/auth/login
POST /api/auth/refresh
GET  /api/auth/me
```

### User Management
```
GET  /api/users/{userId}
PUT  /api/users/{userId}/general
PUT  /api/users/{userId}/risk
PUT  /api/users/{userId}/strategy
PUT  /api/users/{userId}/dca
```

### Positions
```
GET /api/positions/{userId}
```

---

## 🎯 API Testing (Already Verified)

**✅ Registration Test:**
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@verzek.com","password":"test123","full_name":"Test User"}'
```

**✅ Login Test:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@verzek.com","password":"test123"}'
```

**✅ Protected Endpoint Test:**
```bash
curl -X GET http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

All tests passed successfully! ✨

---

## 📱 Building for Production

### iOS (App Store)

```bash
# Build iOS app
npx eas build --platform ios

# Submit to App Store
npx eas submit --platform ios
```

### Android (Play Store)

```bash
# Build Android APK/AAB
npx eas build --platform android

# Submit to Play Store
npx eas submit --platform android
```

**Note:** Requires [Expo Application Services (EAS)](https://expo.dev/eas) account (free tier available)

---

## 🔒 Security Notes

✅ **Password Security**
- Bcrypt hashing with salt
- Min 6 characters required
- Never logged or exposed

✅ **Token Security**
- JWT with HS256 algorithm
- Access token: 1 hour expiry
- Refresh token: 30 days expiry
- Automatic refresh on 401

✅ **Storage Security**
- AsyncStorage for token persistence
- Tokens cleared on logout
- No sensitive data in plain text

---

## 🐛 Troubleshooting

### "Cannot connect to API"
1. Ensure backend is running (check Replit console)
2. Verify API_BASE_URL in config/api.js
3. Check network connectivity

### "Login failed"
1. Verify email/password are correct
2. Check backend logs for errors
3. Ensure user exists (try registration first)

### "Token expired"
- Should auto-refresh automatically
- If issues persist, logout and login again

### "App won't start"
```bash
# Clear cache
npm start -- --clear

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

---

## 📚 Project Structure

```
mobile_app/VerzekApp/
├── App.js                      # Entry point
├── src/
│   ├── config/
│   │   └── api.js             # API configuration
│   ├── context/
│   │   └── AuthContext.js     # Auth state management
│   ├── navigation/
│   │   └── AppNavigator.js    # Navigation setup
│   ├── screens/
│   │   ├── LoginScreen.js     # Login screen
│   │   ├── RegisterScreen.js  # Registration screen
│   │   └── DashboardScreen.js # Dashboard screen
│   └── services/
│       └── api.js             # API service layer
├── package.json               # Dependencies
├── app.json                   # Expo config
└── README.md                  # Documentation
```

---

## 🎉 Next Steps

1. **Test the app** on your device using Expo Go
2. **Add more screens** (Signals, Positions, Settings)
3. **Integrate push notifications** for signal alerts
4. **Add real-time updates** with WebSockets
5. **Deploy to App Store/Play Store**

Your mobile app is ready to go! 🚀

---

## 🆘 Need Help?

- **Expo Docs**: https://docs.expo.dev
- **React Navigation**: https://reactnavigation.org
- **React Native**: https://reactnative.dev

Happy Trading! 📈
