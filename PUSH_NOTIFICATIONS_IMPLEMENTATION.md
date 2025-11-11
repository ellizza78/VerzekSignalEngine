# 📱 Push Notifications Implementation Guide - VerzekAutoTrader

## ✅ **COMPLETED:**
1. ✅ Installed `expo-notifications` and `expo-device` packages
2. ✅ Created `NotificationService.js` - Handles token registration & notification display
3. ✅ Updated `app.json` - Added notification plugin with sound/vibration config

---

## 🔧 **REMAINING IMPLEMENTATION STEPS:**

### **STEP 1: Update AuthContext.js (Mobile App)**

Add push token registration on login:

```javascript
// At the top of mobile_app/VerzekApp/src/context/AuthContext.js
import NotificationService from '../services/NotificationService';
import { userAPI } from '../services/api';

// Inside AuthContext, add this function:
const registerPushToken = async (userId) => {
  try {
    const token = await NotificationService.registerForPushNotifications();
    if (token) {
      // Send to backend
      await userAPI.registerPushToken(userId, token);
      console.log('Push token registered:', token);
    }
  } catch (error) {
    console.error('Failed to register push token:', error);
  }
};

// Update login function - add this after successful login:
const login = async (email, password, rememberMe = false) => {
  try {
    // ... existing login code ...
    
    if (result.success) {
      setUser(userData);
      setIsAuthenticated(true);
      
      // Register push notifications
      await registerPushToken(userData.id);
      
      return { success: true };
    }
  } catch (error) {
    // ... existing error handling ...
  }
};

// Export registerPushToken in context value
return (
  <AuthContext.Provider value={{ 
    user, 
    loading, 
    isAuthenticated, 
    login, 
    register, 
    logout, 
    refreshUser,
    loadRememberedCredentials,
    registerPushToken  // Add this
  }}>
    {children}
  </AuthContext.Provider>
);
```

---

### **STEP 2: Update api.js (Mobile App)**

Add push token API endpoint:

```javascript
// In mobile_app/VerzekApp/src/services/api.js
export const userAPI = {
  // ... existing methods ...
  
  registerPushToken: (userId, token) =>
    api.post(`/api/users/${userId}/push-token`, { push_token: token }),
  
  removePushToken: (userId) =>
    api.delete(`/api/users/${userId}/push-token`),
};
```

---

### **STEP 3: Create Backend Notification Service**

Create `backend/utils/notifications.py`:

```python
import requests
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

def send_push_notification(
    push_tokens: List[str],
    title: str,
    body: str,
    data: Optional[Dict] = None,
    sound: str = "default",
    channel_id: str = "default"
) -> Dict:
    """
    Send push notification to Expo devices
    
    Args:
        push_tokens: List of Expo push tokens
        title: Notification title
        body: Notification body
        data: Custom data payload
        sound: Sound to play (default, signal, trade)
        channel_id: Android notification channel
    """
    if not push_tokens:
        return {"success": False, "error": "No push tokens provided"}
    
    messages = []
    for token in push_tokens:
        if not token or not token.startswith('ExponentPushToken'):
            continue
            
        message = {
            "to": token,
            "sound": sound,
            "title": title,
            "body": body,
            "data": data or {},
            "channelId": channel_id,
            "priority": "high",
        }
        messages.append(message)
    
    if not messages:
        return {"success": False, "error": "No valid push tokens"}
    
    try:
        response = requests.post(
            EXPO_PUSH_URL,
            json=messages,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"Sent {len(messages)} push notifications")
            return {"success": True, "data": response.json()}
        else:
            logger.error(f"Push notification failed: {response.text}")
            return {"success": False, "error": response.text}
            
    except Exception as e:
        logger.error(f"Push notification error: {e}")
        return {"success": False, "error": str(e)}


def send_signal_notification(push_tokens: List[str], signal_data: Dict) -> Dict:
    """Send notification for new trading signal (VIP + PREMIUM)"""
    symbol = signal_data.get('symbol', 'Unknown')
    direction = signal_data.get('direction', 'BUY')
    
    return send_push_notification(
        push_tokens=push_tokens,
        title=f"🚨 New {direction} Signal",
        body=f"{symbol} - Entry: ${signal_data.get('entry', 'N/A')}",
        data={
            "type": "signal",
            "signal_id": signal_data.get('id'),
            "symbol": symbol,
            "direction": direction,
        },
        sound="default",
        channel_id="signals"
    )


def send_trade_start_notification(push_tokens: List[str], position_data: Dict) -> Dict:
    """Send notification when trade starts (PREMIUM only)"""
    symbol = position_data.get('symbol', 'Unknown')
    direction = position_data.get('direction', 'LONG')
    
    return send_push_notification(
        push_tokens=push_tokens,
        title=f"✅ Trade Started",
        body=f"{direction} {symbol} - Entry: ${position_data.get('entry_price', 'N/A')}",
        data={
            "type": "trade_start",
            "position_id": position_data.get('id'),
            "symbol": symbol,
        },
        sound="default",
        channel_id="trades"
    )


def send_trade_end_notification(push_tokens: List[str], position_data: Dict) -> Dict:
    """Send notification when trade ends (PREMIUM only)"""
    symbol = position_data.get('symbol', 'Unknown')
    pnl = position_data.get('pnl', 0)
    pnl_emoji = "🟢" if pnl > 0 else "🔴"
    
    return send_push_notification(
        push_tokens=push_tokens,
        title=f"{pnl_emoji} Trade Closed",
        body=f"{symbol} - PnL: ${pnl:.2f}",
        data={
            "type": "trade_end",
            "position_id": position_data.get('id'),
            "symbol": symbol,
            "pnl": pnl,
        },
        sound="default",
        channel_id="trades"
    )
```

---

### **STEP 4: Add Push Token Endpoint (Backend)**

Add to `backend/users_routes.py`:

```python
from backend.utils.notifications import send_push_notification

@bp.route('/<int:user_id>/push-token', methods=['POST', 'DELETE'])
@jwt_required()
def manage_push_token(user_id):
    """Register or remove push notification token"""
    try:
        current_user = get_jwt_identity()
        if current_user != user_id:
            return jsonify({"ok": False, "error": "Unauthorized"}), 403
        
        db: Session = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            db.close()
            return jsonify({"ok": False, "error": "User not found"}), 404
        
        if request.method == 'POST':
            data = request.get_json()
            push_token = data.get('push_token')
            
            if not push_token:
                db.close()
                return jsonify({"ok": False, "error": "Push token required"}), 400
            
            # Store push token (add push_token field to User model first)
            user.push_token = push_token
            db.commit()
            db.close()
            
            api_logger.info(f"User {user_id} registered push token")
            return jsonify({"ok": True, "message": "Push token registered"}), 200
        
        elif request.method == 'DELETE':
            user.push_token = None
            db.commit()
            db.close()
            
            api_logger.info(f"User {user_id} removed push token")
            return jsonify({"ok": True, "message": "Push token removed"}), 200
            
    except Exception as e:
        api_logger.error(f"Push token error: {e}")
        return jsonify({"ok": False, "error": "Failed to manage push token"}), 500
```

---

### **STEP 5: Add push_token to User Model**

Update `backend/models.py`:

```python
class User(Base):
    __tablename__ = "users"
    
    # ... existing fields ...
    
    push_token = Column(String, nullable=True)  # Add this field
    notifications_enabled = Column(Boolean, default=True)  # Add this field
```

**Then run migration:**
```bash
# Add push_token column to users table
ALTER TABLE users ADD COLUMN push_token VARCHAR;
ALTER TABLE users ADD COLUMN notifications_enabled BOOLEAN DEFAULT TRUE;
```

---

### **STEP 6: Integrate Notifications into Signal Routes**

Update `backend/signals_routes.py`:

```python
from backend.utils.notifications import send_signal_notification

@bp.route('', methods=['POST'])
@jwt_required()
def create_signal():
    """Create a new signal and send notifications to VIP + PREMIUM users"""
    try:
        # ... existing signal creation code ...
        
        # After signal is created successfully:
        
        # Get all VIP and PREMIUM users with notifications enabled
        db: Session = SessionLocal()
        users = db.query(User).filter(
            User.subscription_type.in_(['VIP', 'PREMIUM']),
            User.notifications_enabled == True,
            User.push_token != None
        ).all()
        
        if users:
            push_tokens = [u.push_token for u in users if u.push_token]
            
            signal_data = {
                "id": signal.id,
                "symbol": signal.symbol,
                "direction": signal.direction,
                "entry": signal.entry_price,
            }
            
            send_signal_notification(push_tokens, signal_data)
            api_logger.info(f"Sent signal notifications to {len(push_tokens)} users")
        
        db.close()
        
        # ... rest of existing code ...
        
    except Exception as e:
        api_logger.error(f"Signal creation error: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500
```

---

### **STEP 7: Integrate Notifications into Position Routes**

Update `backend/positions_routes.py`:

```python
from backend.utils.notifications import send_trade_start_notification, send_trade_end_notification

# When trade starts (PREMIUM only):
def notify_trade_start(position_id):
    db: Session = SessionLocal()
    position = db.query(Position).filter(Position.id == position_id).first()
    
    if position:
        user = db.query(User).filter(
            User.id == position.user_id,
            User.subscription_type == 'PREMIUM',
            User.notifications_enabled == True,
            User.push_token != None
        ).first()
        
        if user and user.push_token:
            position_data = {
                "id": position.id,
                "symbol": position.symbol,
                "direction": position.direction,
                "entry_price": position.entry_price,
            }
            
            send_trade_start_notification([user.push_token], position_data)
    
    db.close()


# When trade ends (PREMIUM only):
def notify_trade_end(position_id):
    db: Session = SessionLocal()
    position = db.query(Position).filter(Position.id == position_id).first()
    
    if position:
        user = db.query(User).filter(
            User.id == position.user_id,
            User.subscription_type == 'PREMIUM',
            User.notifications_enabled == True,
            User.push_token != None
        ).first()
        
        if user and user.push_token:
            position_data = {
                "id": position.id,
                "symbol": position.symbol,
                "pnl": position.pnl or 0,
            }
            
            send_trade_end_notification([user.push_token], position_data)
    
    db.close()
```

---

### **STEP 8: Update App.js with Notification Listeners**

Update `mobile_app/VerzekApp/App.js`:

```javascript
import { useEffect } from 'react';
import NotificationService from './src/services/NotificationService';
import { useNavigation } from '@react-navigation/native';

export default function App() {
  const navigation = useNavigation();
  
  useEffect(() => {
    // Setup notification listeners
    NotificationService.setupNotificationListeners(
      (notification) => {
        // Handle notification received while app is open
        console.log('Notification received:', notification);
      },
      (response) => {
        // Handle notification tapped
        const data = response.notification.request.content.data;
        
        if (data.type === 'signal') {
          navigation.navigate('Signals');
        } else if (data.type === 'trade_start' || data.type === 'trade_end') {
          navigation.navigate('Positions');
        }
      }
    );
    
    return () => {
      NotificationService.removeNotificationListeners();
    };
  }, []);
  
  // ... rest of App.js ...
}
```

---

### **STEP 9: Add Notification Toggle to SettingsScreen**

Add this to `mobile_app/VerzekApp/src/screens/SettingsScreen.js`:

```javascript
const [notificationsEnabled, setNotificationsEnabled] = useState(true);

// Add toggle in render:
<View style={styles.settingRow}>
  <View style={styles.settingInfo}>
    <Text style={styles.settingLabel}>Push Notifications</Text>
    <Text style={styles.settingDesc}>Receive alerts for signals and trades</Text>
  </View>
  <Switch
    value={notificationsEnabled}
    onValueChange={async (value) => {
      setNotificationsEnabled(value);
      // Update backend
      await userAPI.updatePreferences(user.user_id, { 
        notifications_enabled: value 
      });
    }}
    trackColor={{ false: COLORS.border, true: COLORS.tealBright }}
    thumbColor={notificationsEnabled ? COLORS.textPrimary : COLORS.textMuted}
  />
</View>
```

---

## 📋 **DEPLOYMENT CHECKLIST:**

### **Before Deploying:**
1. ⬜ Add `push_token` and `notifications_enabled` columns to database
2. ⬜ Test on physical Android/iOS device (notifications don't work on emulators)
3. ⬜ Verify Expo project ID in app.json matches your Expo account
4. ⬜ Build new APK with `eas build` (notification plugin requires native rebuild)
5. ⬜ Configure FCM credentials in Expo dashboard (for Android)
6. ⬜ Configure APNs credentials in Expo dashboard (for iOS)

### **After Deploying:**
1. ⬜ Test VIP user receives signal notifications
2. ⬜ Test PREMIUM user receives signal + trade notifications
3. ⬜ Test TRIAL user does NOT receive notifications
4. ⬜ Test notification toggle in settings
5. ⬜ Verify sound and vibration work correctly

---

## 🎯 **Feature Summary:**

### **TRIAL Users:**
- ❌ No push notifications

### **VIP Users ($50/month):**
- ✅ Signal arrival notifications (with sound + vibration)
- ❌ No trade notifications

### **PREMIUM Users ($120/month):**
- ✅ Signal arrival notifications (with sound + vibration)
- ✅ Trade start notifications (with sound + vibration)
- ✅ Trade end notifications (with sound + vibration)

---

## 🚀 **Next Steps:**

1. **Implement the code changes** from steps 1-9 above
2. **Add database columns** for push_token and notifications_enabled
3. **Rebuild APK** using `eas build` (notifications require native rebuild)
4. **Test on physical device** (emulators don't support push notifications)
5. **Deploy to production** after testing

---

## ⚠️ **Important Notes:**

- **Physical device required** - Push notifications DON'T work on emulators
- **APK rebuild required** - OTA updates alone won't enable notifications
- **FCM/APNs setup required** - Must configure credentials in Expo dashboard
- **Token format**: `ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]`
- **Rate limit**: 600 notifications/second/project max

---

**Questions?** Review Expo docs: https://docs.expo.dev/push-notifications/overview/
