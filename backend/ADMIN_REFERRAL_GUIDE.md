# Admin Guide: Referrals, Payments & Subscriptions

## 🎯 How Referrals Work

### For Users:
1. Each user gets unique `referral_code` on registration (e.g., "REF12345")
2. They share this code with friends
3. Friends enter code during registration
4. System tracks who referred whom in database

### Database Fields:
- `referral_code`: Unique code per user (based on their ID)
- `referred_by`: User ID of person who referred them
- `email`: Unique identifier (username not needed)
- `full_name`: Display name
- `subscription_type`: TRIAL, VIP, or PREMIUM

---

## 📊 Admin Endpoints (Authentication Required)

### **Payment & Subscription Management:**

#### 1. View Pending Payments
**GET** `/api/admin/payments/pending`

Returns all payments waiting for verification (sorted newest first).

**Response:**
```json
{
  "ok": true,
  "total_pending": 5,
  "payments": [
    {
      "payment_id": "VZK-ABC123",
      "user_email": "user@example.com",
      "amount_usdt": 50.0,
      "plan_type": "VIP",
      "status": "PENDING_VERIFICATION",
      "tx_hash": "0x123abc...",
      "waiting_hours": 2.5
    }
  ]
}
```

#### 2. View All Payments (With Filters)
**GET** `/api/admin/payments/all?status=VERIFIED&plan_type=VIP&limit=50`

Returns payment history with optional filters.

#### 3. Approve Payment
**POST** `/api/admin/payments/approve/<payment_id>`

Verifies payment and upgrades user subscription automatically.

**Response:**
```json
{
  "ok": true,
  "message": "Payment approved and user upgraded",
  "payment_id": "VZK-ABC123",
  "user_id": 42,
  "new_plan": "VIP"
}
```

#### 4. Reject Payment
**POST** `/api/admin/payments/reject/<payment_id>`

Marks payment as FAILED.

**Body:**
```json
{
  "reason": "Incorrect amount sent"
}
```

#### 5. Subscription Overview
**GET** `/api/admin/subscriptions/overview`

Returns complete subscription breakdown and revenue stats.

**Response:**
```json
{
  "ok": true,
  "subscriptions": {
    "trial": 45,
    "vip": 12,
    "premium": 8,
    "total": 65
  },
  "payments": {
    "total": 25,
    "verified": 20,
    "pending": 3,
    "failed": 2
  },
  "revenue": {
    "total_usdt": 1400.0,
    "vip_payments": 12,
    "premium_payments": 8
  }
}
```

---

### **Referral Tracking:**

#### 6. View All Referrals
**GET** `/api/admin/referrals`

Returns complete referral tree showing:
- Who each user referred
- Subscription types
- Email verification status
- Join dates

**Example Response:**
```json
{
  "ok": true,
  "total_users": 150,
  "referrals": [
    {
      "user_id": 5,
      "email": "john@example.com",
      "full_name": "John Doe",
      "referral_code": "REF00005",
      "subscription_type": "PREMIUM",
      "referred_count": 12,
      "referred_users": [
        {
          "id": 23,
          "email": "friend1@example.com",
          "subscription_type": "VIP",
          "is_verified": true
        }
      ]
    }
  ]
}
```

---

#### 7. Calculate Payouts
**GET** `/api/admin/referrals/payouts?bonus_per_vip=10&bonus_per_premium=20`

Calculates bonuses owed to referrers based on subscription types.

**Query Parameters:**
- `bonus_per_vip`: USDT bonus per VIP referral (default: 10)
- `bonus_per_premium`: USDT bonus per PREMIUM referral (default: 20)

**Example Response:**
```json
{
  "ok": true,
  "total_payouts_owed_usdt": 540.00,
  "bonus_per_vip": 10,
  "bonus_per_premium": 20,
  "payouts": [
    {
      "user_id": 5,
      "email": "john@example.com",
      "full_name": "John Doe",
      "referral_code": "REF00005",
      "vip_referrals": 8,
      "premium_referrals": 4,
      "bonus_owed_usdt": 160.00
    }
  ]
}
```

---

#### 8. System Stats
**GET** `/api/admin/stats`

Returns overall platform statistics including user counts and revenue estimates.

---

## 🔐 Authentication

Admin endpoints require:
1. **JWT Token**: Login as admin user
2. **Admin Email**: Set in `ADMIN_EMAIL` environment variable

**How to Login as Admin:**
```bash
# Mobile app login or API call:
POST /api/auth/login
{
  "email": "admin@verzekinnovative.com",
  "password": "your_admin_password"
}
```

Use returned `access_token` in headers:
```
Authorization: Bearer <access_token>
```

---

---

## 🔧 Daily Admin Workflow

### 1. Check Pending Payments (Morning Routine):
```bash
curl -H "Authorization: Bearer <token>" \
  "https://api.verzekinnovative.com/api/admin/payments/pending"
```

### 2. Verify Transaction on TronScan:
- Copy `tx_hash` from pending payment
- Visit https://tronscan.org/
- Search for transaction
- Verify: Amount matches, recipient wallet is yours, status confirmed

### 3. Approve or Reject:
```bash
# Approve (auto-upgrades user)
curl -X POST -H "Authorization: Bearer <token>" \
  "https://api.verzekinnovative.com/api/admin/payments/approve/VZK-ABC123"

# Reject (if fraud/wrong amount)
curl -X POST -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"reason":"Incorrect amount"}' \
  "https://api.verzekinnovative.com/api/admin/payments/reject/VZK-ABC123"
```

### 4. Weekly: Check Subscriptions Overview
```bash
curl -H "Authorization: Bearer <token>" \
  "https://api.verzekinnovative.com/api/admin/subscriptions/overview"
```

### 5. Monthly: Calculate Referral Payouts
```bash
curl -H "Authorization: Bearer <token>" \
  "https://api.verzekinnovative.com/api/admin/referrals/payouts"
```

---

## 💰 Referral Payout Process

### Manual Process:

1. **Get Payout Data:**
   ```bash
   curl -H "Authorization: Bearer <token>" \
     "https://api.verzekinnovative.com/api/admin/referrals/payouts?bonus_per_vip=10&bonus_per_premium=20"
   ```

2. **Export to Spreadsheet:**
   - Copy JSON response
   - Use tool like [JSON to CSV](https://www.convertcsv.com/json-to-csv.htm)
   - Review payouts in Excel/Google Sheets

3. **Send USDT Payments:**
   - Send TRC20 USDT to each user's wallet
   - Record transaction hashes

4. **Track Payments:**
   - Create spreadsheet: `[User Email, Amount, TX Hash, Date]`
   - Mark as paid in your records

---

## 📋 Direct Database Queries (Alternative)

If admin endpoints aren't accessible, query database directly:

### SSH into VPS:
```bash
ssh root@80.240.29.142
cd /root/VerzekBackend/backend
sqlite3 database/verzek_autotrader.db
```

### Query 1: See All Referrals
```sql
SELECT 
  u.id,
  u.email,
  u.full_name,
  u.referral_code,
  u.subscription_type,
  u.is_verified,
  COUNT(r.id) as referred_count
FROM users u
LEFT JOIN users r ON r.referred_by = u.id
GROUP BY u.id
ORDER BY referred_count DESC;
```

### Query 2: Referral Relationships
```sql
SELECT 
  referrer.email AS referrer_email,
  referrer.referral_code,
  referred.email AS referred_email,
  referred.subscription_type,
  referred.is_verified,
  referred.created_at AS join_date
FROM users referred
JOIN users referrer ON referred.referred_by = referrer.id
ORDER BY referrer.id;
```

### Query 3: Calculate Bonuses (10 USDT/VIP, 20 USDT/PREMIUM)
```sql
SELECT 
  referrer.email,
  referrer.full_name,
  referrer.referral_code,
  COUNT(CASE WHEN referred.subscription_type = 'VIP' THEN 1 END) as vip_count,
  COUNT(CASE WHEN referred.subscription_type = 'PREMIUM' THEN 1 END) as premium_count,
  (COUNT(CASE WHEN referred.subscription_type = 'VIP' THEN 1 END) * 10 + 
   COUNT(CASE WHEN referred.subscription_type = 'PREMIUM' THEN 1 END) * 20) as bonus_usdt
FROM users referrer
JOIN users referred ON referred.referred_by = referrer.id AND referred.is_verified = 1
GROUP BY referrer.id
HAVING bonus_usdt > 0
ORDER BY bonus_usdt DESC;
```

---

## ✅ Why Username Is NOT Needed

**Database uses:**
- ✅ `email` - Unique identifier, login credential
- ✅ `full_name` - Display name in app
- ✅ `referral_code` - Tracking referrals

**Username field:**
- ❌ Never sent to backend
- ❌ Not stored in database
- ❌ Not used anywhere in system
- ✅ **REMOVED** from registration flow

---

## 🚀 Next Steps

1. Deploy updated backend with admin routes
2. Login with admin account
3. Test `/api/admin/referrals` endpoint
4. Set your bonus amounts
5. Run `/api/admin/referrals/payouts` monthly
6. Export data and process payments
