# Verzek Auto Trader - Referral System Guide

## 🎁 Overview
Complete referral system allowing users to earn $10 for every friend who joins using their referral code.

## ✅ What's Implemented

###  1. Backend (Vultr - 80.240.29.142)
- ✅ Database schema (already existed): `referral_code`, `referred_by`, `referral_earnings`
- ✅ `referral_handler.py` - Processes referrals and sends Telegram notifications
- ✅ Registration endpoint updated to accept `referral_code` parameter
- ✅ Validates referral codes and links users
- ✅ `/api/referrals/<user_id>` endpoint to fetch referral stats
- ✅ Telegram notifications to `ADMIN_CHAT_ID` when new referral registers

### 2. Mobile App (React Native + Expo)
- ✅ RegisterScreen: Added optional "Referral Code" input field
- ✅ AuthContext: Updated to pass referral code to backend
- ✅ API Service: Added `referralAPI.getReferrals()` function
- ✅ ReferralsScreen: Complete referral dashboard with:
  - User's unique referral code (shareable)
  - Copy & Share functionality
  - Total referrals count
  - Total earnings display
  - List of referred users
  - "How It Works" guide

## 🚀 How It Works

### For Referrers:
1. User gets unique referral code upon registration
2. Share code with friends via Copy or Share button
3. When friend registers with the code:
   - Telegram notification sent to @VerzekSupport
   - Referrer's earnings updated (+$10)
4. Contact @VerzekSupport to claim earnings

### For New Users:
1. During registration, enter referrer's code (optional)
2. Code is validated on backend
3. If valid, referral link is created
4. Referrer gets notified

## 📱 User Journey

### Registration with Referral Code:
```
RegisterScreen
  ├─ User enters email, password, full name
  ├─ User enters referral code (OPTIONAL)
  ├─ Backend validates referral code
  ├─ If valid: Creates referral link
  └─ Sends Telegram notification to support
```

### Viewing Referrals:
```
Settings → My Referrals
  ├─ Display referral code
  ├─ Copy/Share buttons
  ├─ Stats: Total referrals & earnings
  ├─ List of referred users
  └─ Instructions to claim earnings
```

## 🔧 Technical Implementation

### Backend Files:
- `/var/www/VerzekAutoTrader/referral_handler.py` - Core referral logic
- `/var/www/VerzekAutoTrader/api_server.py` - Updated registration & new endpoint

### Mobile App Files:
- `src/screens/RegisterScreen.js` - Added referral code input
- `src/screens/ReferralsScreen.js` - New referral dashboard
- `src/context/AuthContext.js` - Updated registration function
- `src/services/api.js` - Added `referralAPI`

## 📊 Database Schema

```sql
users table:
  - referral_code TEXT UNIQUE      -- User's unique code (e.g., "VZK12AB34")
  - referred_by TEXT               -- User ID of referrer
  - referral_earnings REAL         -- Total earnings from referrals
```

## 🔔 Telegram Notifications

When a new user registers with a referral code, the admin receives:

```
🎁 NEW REFERRAL!

Referrer:
• Name: John Doe
• User ID: usr_123
• Email: john@example.com
• Earnings: $20.00

New User:
• Name: Jane Smith
• User ID: usr_456
• Email: jane@example.com

Bonus: $10.00
```

## 🎯 Next Steps

### 1. Add Referrals Screen to Navigation
**File:** `mobile_app/VerzekApp/src/navigation/*`

Add ReferralsScreen to Settings menu or main navigation.

### 2. Add Vultr Backend Endpoint
**Run on Vultr:**
```bash
ssh root@80.240.29.142
cd /var/www/VerzekAutoTrader

# Add the endpoint (see vultr_add_referral_endpoint.sh)
bash vultr_add_referral_endpoint.sh
```

### 3. Test the Flow
1. Register new user with referral code
2. Check Telegram for notification
3. Open Referrals screen
4. Verify stats are correct

## 💰 Bonus Structure

- **Per Referral:** $10.00
- **Payment Method:** Manual (contact @VerzekSupport)
- **Eligibility:** All registered users
- **Tracking:** Automatic via database

## 🔐 Security

- Referral codes are unique and validated on backend
- Invalid codes are rejected silently (no error to user)
- Earnings tracked in database
- Manual payout verification prevents fraud

## 📞 Support

Users contact @VerzekSupport on Telegram to:
- Verify referral bonuses
- Request payout
- Resolve referral issues

---

**Status:** ✅ Backend integration complete | 📱 Mobile app ready | 🧪 Ready for testing
