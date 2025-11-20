# ✅ VerzekAutoTrader - Complete Testing Checklist

**Version:** 2.0 - Multi-TP System + Trial Timer + Exchange Balance  
**Date:** November 20, 2025

---

## 🎯 TESTING STRATEGY

Test in this order:
1. **Backend Health** → Ensures API is responding
2. **Signal Engine** → Ensures signals generate correctly
3. **Mobile App (Expo Go)** → Fastest testing without APK
4. **Integration** → End-to-end flow verification
5. **Production APK** → Final user experience

---

## 📋 PHASE 1: Backend Testing (Vultr)

### **Test 1.1: Basic Health Checks**

```bash
# Health endpoint
curl http://80.240.29.142:8000/api/health
# ✅ Expected: {"status": "ok"}

# Ping endpoint
curl http://80.240.29.142:8000/api/ping
# ✅ Expected: {"message": "pong"}
```

**Pass Criteria:** Both return HTTP 200

---

### **Test 1.2: New Exchange Balance Endpoint**

**Setup:**
1. Get JWT token (login via Postman/curl)
2. Get user_id and exchange_id from database

```bash
# Test endpoint (replace placeholders)
curl -X GET \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://80.240.29.142:8000/api/users/1/exchanges/1/balance

# ✅ Expected Response:
{
  "ok": true,
  "exchange": "binance",
  "testnet": true,
  "balance": {
    "ok": true,
    "total_usdt": 10000.0,
    "available_usdt": 8500.0,
    "currencies": {
      "USDT": {
        "free": 8500.0,
        "locked": 1500.0
      }
    },
    "mock": true,
    "note": "Phase 2: Mock balance - no real API call"
  }
}
```

**Pass Criteria:**
- ✅ Returns HTTP 200
- ✅ `ok: true`
- ✅ `mock: true` (Phase 2)
- ✅ Balance amounts correct

---

### **Test 1.3: Authentication Still Works**

```bash
# Register new user
curl -X POST http://80.240.29.142:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "full_name": "Test User"
  }'

# ✅ Expected: User created (check email for verification)

# Login
curl -X POST http://80.240.29.142:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!"
  }'

# ✅ Expected: Returns JWT token
```

**Pass Criteria:** Authentication flow works end-to-end

---

## 📋 PHASE 2: Signal Engine Testing (Vultr)

### **Test 2.1: Service Status**

```bash
ssh root@80.240.29.142

# Check service
sudo systemctl status signal-engine

# ✅ Expected: Active (running)
```

---

### **Test 2.2: Multi-TP Signal Generation**

```bash
# Check logs for TP1-TP5 signals
grep -E "TP[1-5]" /root/signal_engine/signal_engine.log | tail -20

# ✅ Expected: See signals with TP1, TP2, TP3, TP4, TP5 mentioned
```

**Example Output:**
```
[INFO] BTCUSDT LONG: TP1=$50200, TP2=$50400, TP3=$50600, TP4=$50800, TP5=$51200
```

---

### **Test 2.3: Daily Reporter TP Breakdown**

**Option A: Wait for midnight UTC daily report**
- Check VIP Telegram group

**Option B: Trigger manual report**

```bash
ssh root@80.240.29.142
cd /root/signal_engine

python3 -c "
import asyncio
from services.daily_reporter import get_reporter
asyncio.run(get_reporter().generate_and_send_report('2025-11-20'))
"
```

**Check Telegram for message with:**
```
🎯 TAKE-PROFIT BREAKDOWN (Multi-TP System)
• TP1 Hits: X (Partial)
• TP2 Hits: X (Partial)
• TP3 Hits: X (Partial)
• TP4 Hits: X (Partial)
• TP5 Hits: X (Final - All Targets)
• Avg TP Level: X.X
```

**Pass Criteria:**
- ✅ TP breakdown section appears
- ✅ Shows individual counts for each TP level
- ✅ Footer says "🚀 5-Level Progressive Take-Profit System Active"

---

## 📋 PHASE 3: Mobile App Testing (Expo Go)

### **Test 3.1: Install and Connect**

1. **Install Expo Go** on Android phone (Play Store)
2. **Open Replit** → Check "Expo Dev Server" workflow
3. **Scan QR code** with Expo Go app
4. **App loads** → Should see login screen

**Pass Criteria:** App loads without errors

---

### **Test 3.2: Authentication**

1. **Login** with test credentials
2. **Verify** user dashboard loads
3. **Logout** and login again

**Pass Criteria:** Auth flow works smoothly

---

### **Test 3.3: Trial Subscription Timer** ⏰

**For Trial Users Only:**

1. **Dashboard loads** → TrialBanner should appear at top
2. **Verify countdown displays:**
   - Format: "Xd Yh Zm" (e.g., "3d 12h 45m")
   - Updates every 60 seconds
3. **Test Telegram link:**
   - Tap "📱 Join Trial Group" button
   - Should open: https://t.me/+JObDSp1HOuxmMWQ0
4. **Test expiry warning:**
   - If trial < 2 days: Red border + warning message appears
   - Otherwise: Green/teal border

**Pass Criteria:**
- ✅ Banner displays for trial users only
- ✅ Countdown shows correct time remaining
- ✅ Telegram link opens correctly
- ✅ Warning appears when < 2 days

---

### **Test 3.4: Exchange Balance Display** 💰

**Prerequisites:** User must have connected exchange account

1. **Navigate:** Dashboard → Settings (gear icon) → Exchange Accounts
2. **Select an exchange** (e.g., Binance, Bybit)
3. **Verify balance card appears:**
   - **Available USDT:** $8,500.00
   - **Total USDT:** $10,000.00
   - **Mock Data indicator:** "⚠️ Mock Data (Phase 2)"
4. **Test refresh:**
   - Tap refresh button (🔃)
   - Balance should reload
   - Loading spinner appears briefly
5. **Test auto-load:**
   - Go back and select exchange again
   - Balance loads automatically (no manual refresh needed)

**Pass Criteria:**
- ✅ Balance displays correctly
- ✅ Refresh button works
- ✅ Auto-loads when exchange selected
- ✅ Mock data indicator visible

---

### **Test 3.5: Navigation & Stability**

**Test all screens:**
- ✅ Dashboard
- ✅ Signals Feed
- ✅ Positions
- ✅ Settings
  - ✅ Trade Settings
  - ✅ Exchange Accounts
  - ✅ Risk Settings
- ✅ Subscription
- ✅ Help

**Pass Criteria:**
- No crashes
- No blank screens
- Smooth navigation
- No console errors in Expo

---

## 📋 PHASE 4: Integration Testing

### **Test 4.1: Backend ↔ Signal Engine**

**Simulate signal flow:**

1. **Signal Engine generates signal** (check logs)
2. **Backend receives webhook** (check backend logs)
3. **Signal stored in database**
4. **Mobile app fetches signal** via `/api/signals`

**Pass Criteria:** Complete signal lifecycle works

---

### **Test 4.2: Mobile App ↔ Backend**

**Test API calls from mobile:**

1. **Login** → Backend returns JWT
2. **Fetch user data** → Backend returns user info
3. **Fetch exchange balance** → Backend returns mock balance
4. **Fetch signals** → Backend returns signal list

**Pass Criteria:** All API calls succeed

---

### **Test 4.3: Multi-TP Webhook Flow** (When Position Closes)

**This tests the complete TP hit flow:**

1. **Backend detects TP1 hit** → Calls `/api/signals/tp-hit` webhook
2. **Signal Engine updates tracker** → Marks TP1 hit, keeps signal ACTIVE
3. **Telegram notification sent** → "TP1 HIT! Partial profit"
4. **Backend detects TP5 hit** → Calls webhook
5. **Signal Engine closes signal** → Returns `is_final: true`
6. **Final Telegram notification** → "TP5 HIT! All targets achieved"

**Pass Criteria:**
- ✅ TP1-TP4 webhook returns `is_final: false`
- ✅ TP5 webhook returns `is_final: true`
- ✅ Telegram messages sent for each TP

---

## 📋 PHASE 5: Production APK Testing

### **Test 5.1: Build APK**

```bash
cd mobile_app/VerzekApp
eas build -p android --profile production --clear-cache
```

**Pass Criteria:**
- ✅ Build completes without errors
- ✅ Download link provided

---

### **Test 5.2: Install & Launch**

1. **Download APK** from EAS link
2. **Install on Android device**
3. **Launch app**
4. **Grant permissions** (notifications, storage if needed)

**Pass Criteria:**
- App installs without errors
- App launches to login screen

---

### **Test 5.3: Full Feature Test (APK)**

**Run all Phase 3 tests again on APK:**
- ✅ Authentication
- ✅ Trial timer (if trial user)
- ✅ Exchange balance
- ✅ Navigation
- ✅ Signals loading
- ✅ Settings working

**Pass Criteria:** All features work identically to Expo Go version

---

## 📊 FINAL VERIFICATION

**Complete this checklist before considering deployment DONE:**

### **Backend (Vultr)**
- [ ] `/api/health` returns 200
- [ ] `/api/users/<id>/exchanges/<id>/balance` works
- [ ] Authentication endpoints working
- [ ] No critical errors in logs

### **Signal Engine (Vultr)**
- [ ] Service running (`systemctl status signal-engine`)
- [ ] Multi-TP signals generating (TP1-TP5 in logs)
- [ ] Daily reporter includes TP breakdown
- [ ] Telegram notifications sending

### **Mobile App**
- [ ] Trial timer displays and counts down
- [ ] Exchange balance loads and refreshes
- [ ] All screens functional
- [ ] No crashes or console errors
- [ ] APK builds successfully
- [ ] APK installs and runs

### **Integration**
- [ ] Signal flow: Engine → Backend → Mobile
- [ ] TP webhooks: Backend → Engine
- [ ] Telegram notifications working
- [ ] All Replit workflows running

---

## 🎯 PASS/FAIL CRITERIA

**PASS:** All checkboxes above marked ✅  
**FAIL:** Any critical feature broken → Must fix before production

---

**🎉 Testing Complete - Ready for Production!**
