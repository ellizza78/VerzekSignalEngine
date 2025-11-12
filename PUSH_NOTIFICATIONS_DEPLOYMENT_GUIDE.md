# 🚀 Push Notifications - Production Deployment Guide

## ✅ **COMPLETED IMPLEMENTATION**

### **Mobile App (React Native/Expo)**
- ✅ **NotificationService.js** - Multi-fallback projectId lookup for production builds
- ✅ **app.json** - expo-notifications plugin configured with sound/vibration
- ✅ **AuthContext.js** - Auto-registers push tokens on login
- ✅ **api.js** - Device token endpoints (POST/DELETE) + notification settings
- ✅ **App.js** - Notification listeners with navigation handling
- ✅ **Multi-device support** - Same user can receive notifications on multiple phones

### **Backend (Python/Flask)**
- ✅ **models.py** - DeviceToken model + notifications_enabled field on User
- ✅ **users_routes.py** - Device token management endpoints
- ✅ **utils/notifications.py** - Complete notification service with subscription filtering
- ✅ **Database migration** - SQL file ready (backend/database/migrations/add_device_tokens.sql)

---

## ⏳ **REMAINING TASKS**

### **1. Run Database Migration**
```bash
# SSH into VPS: 80.240.29.142
cd /root/VerzekBackend/backend
sqlite3 database/verzek_autotrader.db < database/migrations/add_device_tokens.sql
```

### **2. Integrate Notifications into Signal Routes**
Add this to `backend/signals_routes.py` after signal creation:

```python
from backend.utils.notifications import send_signal_notification, get_subscription_user_tokens

# Inside create_signal() after signal is saved:
try:
    # Get all VIP + PREMIUM users with notifications enabled
    user_tokens = get_subscription_user_tokens(db, ['VIP', 'PREMIUM'])
    
    if user_tokens:
        all_tokens = [token for tokens in user_tokens.values() for token in tokens]
        
        signal_data = {
            "id": signal.id,
            "symbol": signal.symbol,
            "direction": signal.side,
            "entry_price": signal.entry,
        }
        
        result = send_signal_notification(all_tokens, signal_data)
        api_logger.info(f"Sent signal notifications to {len(all_tokens)} devices")
except Exception as e:
    api_logger.error(f"Failed to send signal notifications: {e}")
```

### **3. Integrate Notifications into Position Routes**
Add this to `backend/positions_routes.py` for PREMIUM users:

```python
from backend.utils.notifications import send_trade_start_notification, send_trade_end_notification, get_user_push_tokens

# When trade starts (PREMIUM only):
def notify_trade_start(db, position):
    try:
        user = db.query(User).filter(User.id == position.user_id).first()
        
        if user and user.subscription_type == 'PREMIUM' and user.notifications_enabled:
            tokens = get_user_push_tokens(db, user.id)
            
            if tokens:
                position_data = {
                    "id": position.id,
                    "symbol": position.symbol,
                    "direction": position.side,
                    "entry_price": position.entry_price,
                }
                send_trade_start_notification(tokens, position_data)
    except Exception as e:
        api_logger.error(f"Trade start notification failed: {e}")

# When trade ends (PREMIUM only):
def notify_trade_end(db, position):
    try:
        user = db.query(User).filter(User.id == position.user_id).first()
        
        if user and user.subscription_type == 'PREMIUM' and user.notifications_enabled:
            tokens = get_user_push_tokens(db, user.id)
            
            if tokens:
                position_data = {
                    "id": position.id,
                    "symbol": position.symbol,
                    "pnl": position.pnl_usdt,
                    "pnl_percentage": position.pnl_pct,
                }
                send_trade_end_notification(tokens, position_data)
    except Exception as e:
        api_logger.error(f"Trade end notification failed: {e}")
```

### **4. Rebuild Mobile App (REQUIRED)**
**CRITICAL:** The `expo-notifications` plugin requires a **native rebuild** (OTA updates won't work):

```bash
# Build new APK with notification support
cd mobile_app/VerzekApp
eas build --profile production --platform android
```

**Why rebuild is required:**
- Added `expo-notifications` plugin to app.json
- Native Android/iOS code must be regenerated
- Cannot use OTA updates for this change

### **5. Configure FCM Credentials**
Before users can receive notifications, configure Firebase Cloud Messaging:

```bash
# Option 1: Via EAS CLI
eas credentials

# Option 2: Via Expo Dashboard
# Go to: https://expo.dev/accounts/ellizza/projects/verzek-app/credentials
# Upload FCM V1 service account JSON
```

**Get FCM credentials:**
1. Go to Firebase Console: https://console.firebase.google.com
2. Select your project (or create one)
3. Project Settings → Service Accounts
4. Generate new private key (JSON)
5. Upload to Expo

---

## 📊 **Feature Summary**

### **TRIAL Users (FREE)**
- ❌ No push notifications

### **VIP Users ($50/month)**
- ✅ Signal arrival notifications with sound/vibration
- ❌ No trade notifications

### **PREMIUM Users ($120/month)**
- ✅ Signal arrival notifications with sound/vibration
- ✅ Trade start notifications (when trade opens)
- ✅ Trade end notifications (when trade closes with PnL)

---

## 🧪 **Testing Checklist**

After deployment, test these scenarios:

### **1. Token Registration**
- [ ] User logs in → push token auto-registered
- [ ] Same user logs in on 2nd device → both devices receive notifications
- [ ] User logs out → notifications stop (token marked inactive)

### **2. Notification Delivery (VIP)**
- [ ] New signal created → VIP user receives notification
- [ ] Notification has correct symbol/direction/entry price
- [ ] Tapping notification navigates to Signals screen
- [ ] Sound + vibration work correctly

### **3. Notification Delivery (PREMIUM)**
- [ ] New signal created → PREMIUM user receives notification
- [ ] Trade opens → PREMIUM user receives "Trade Started" notification
- [ ] Trade closes → PREMIUM user receives "Trade Closed" with PnL
- [ ] Tapping trade notification navigates to Positions screen

### **4. Subscription Filtering**
- [ ] TRIAL user does NOT receive any notifications
- [ ] VIP user receives signal notifications only
- [ ] PREMIUM user receives signal + trade notifications
- [ ] User with notifications_enabled=false receives nothing

### **5. Settings Toggle**
- [ ] User can enable/disable notifications in SettingsScreen
- [ ] Disabled notifications are not sent even if subscription allows it

---

## 🔧 **Troubleshooting**

### **"No push token" error**
- Ensure app is running on **physical device** (not emulator)
- Check app.json has correct Expo project ID
- Verify user granted notification permissions

### **Notifications not received**
- Check FCM/APNs credentials are configured in Expo dashboard
- Verify backend API can reach `https://exp.host/--/api/v2/push/send`
- Check device token is active in `device_tokens` table
- Verify user has `notifications_enabled=true`

### **"DeviceNotRegistered" error**
- User uninstalled app or revoked permissions
- Backend auto-handles this by deactivating stale tokens

---

## 📚 **API Endpoints Reference**

### **Register Device Token**
```
POST /api/users/{user_id}/device-token
Authorization: Bearer {access_token}

{
  "push_token": "ExponentPushToken[xxxxxx]",
  "device_name": "Android Device",
  "device_platform": "android"
}
```

### **Remove Device Token**
```
DELETE /api/users/{user_id}/device-token
Authorization: Bearer {access_token}

{
  "push_token": "ExponentPushToken[xxxxxx]"  // Optional - omit to remove all
}
```

### **Update Notification Settings**
```
PUT /api/users/{user_id}/notifications/settings
Authorization: Bearer {access_token}

{
  "notifications_enabled": true
}
```

---

## ⚠️ **Important Notes**

1. **APK Rebuild Required** - OTA updates alone won't enable notifications
2. **Physical Device Only** - Emulators don't support push notifications
3. **FCM Configuration** - Must upload credentials before notifications work
4. **Rate Limits** - Expo allows 600 notifications/second/project max
5. **Multi-Device Support** - Same user can have unlimited active devices
6. **Token Cleanup** - Stale tokens automatically deactivated on error responses

---

## 🎯 **Next Steps**

1. **Run database migration** (Step 1 above)
2. **Add signal/position triggers** (Steps 2-3 above)
3. **Rebuild APK** (Step 4 above)
4. **Configure FCM** (Step 5 above)
5. **Test thoroughly** (Testing Checklist above)
6. **Deploy via OTA** for all JavaScript changes
7. **Monitor logs** for notification delivery success/failures

---

**Estimated Time to Complete:** 30-45 minutes

**Questions?** Review:
- Expo Push Notifications: https://docs.expo.dev/push-notifications/overview/
- Firebase Setup: https://console.firebase.google.com
