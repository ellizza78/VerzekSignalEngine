# Payment Confirmation Guide for VerzekAutoTrader

## 🔐 Admin Access Required
All payment confirmation endpoints require **admin** plan access.

---

## 📋 View Pending Payments

**Endpoint:** `GET /api/payments/pending`

**Example:**
```bash
curl -X GET https://80.240.29.142:5000/api/payments/pending \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN"
```

**Response:**
```json
{
  "count": 2,
  "payments": [
    {
      "payment_id": "PAY_user123_1730304000",
      "user_id": "user123",
      "plan": "premium",
      "amount_usdt": 120,
      "tx_hash": "abc123def456...",
      "status": "pending_verification",
      "created_at": "2025-10-30T14:00:00",
      "submitted_at": "2025-10-30T14:05:00"
    }
  ]
}
```

---

## ✅ Option 1: Auto-Verify with TronScan (RECOMMENDED)

**Endpoint:** `POST /api/payments/auto-verify/<payment_id>`

**Example:**
```bash
curl -X POST https://80.240.29.142:5000/api/payments/auto-verify/PAY_user123_1730304000 \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

**What happens:**
1. Backend calls TronScan API with the TX hash
2. Verifies transaction on blockchain
3. Checks amount matches plan ($50 VIP or $120 PREMIUM)
4. If valid → **Auto-activates subscription**
5. Sends welcome email to user
6. Processes referral bonus (if applicable)

**Response (Success):**
```json
{
  "success": true,
  "message": "Payment verified via TronScan. premium subscription activated.",
  "verification": {
    "verified": true,
    "amount": 120,
    "from_address": "TUser123...",
    "to_address": "TBjfqimY...",
    "confirmations": 19
  },
  "user_id": "user123",
  "plan": "premium"
}
```

---

## 🔍 Option 2: Manual Confirmation

**Endpoint:** `POST /api/payments/confirm/<payment_id>`

**Example (Approve):**
```bash
curl -X POST https://80.240.29.142:5000/api/payments/confirm/PAY_user123_1730304000 \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN" \
  -H "X-Admin-Signature: YOUR_HMAC_SIGNATURE" \
  -H "Content-Type: application/json" \
  -d '{"is_valid": true}'
```

**Example (Reject):**
```bash
curl -X POST https://80.240.29.142:5000/api/payments/confirm/PAY_user123_1730304000 \
  -H "Authorization: Bearer YOUR_ADMIN_JWT_TOKEN" \
  -H "X-Admin-Signature: YOUR_HMAC_SIGNATURE" \
  -H "Content-Type: application/json" \
  -d '{"is_valid": false}'
```

---

## 🎯 What Happens After Confirmation

Once payment is confirmed (auto or manual):

1. ✅ User's plan upgraded (FREE → VIP or PREMIUM)
2. ✅ License key generated
3. ✅ Subscription expires in 30 days
4. ✅ Welcome email sent (if PREMIUM or VIP)
5. ✅ Referral bonus processed (10% to referrer)
6. ✅ Financial tracker updated
7. ✅ Admin notification sent via Telegram

---

## 💡 Recommended Workflow

**For BOTH $50 VIP and $120 PREMIUM:**

1. User pays USDT via TrustWallet/etc
2. User submits TX hash in mobile app
3. Payment shows as `pending_verification`
4. Admin checks: `GET /api/payments/pending`
5. Admin auto-verifies: `POST /api/payments/auto-verify/<payment_id>`
6. TronScan confirms → User activated automatically! ✅

**Fallback (if TronScan fails):**
- Manually verify TX on TronScan.org
- Use manual confirmation endpoint

---

## 📊 Payment Status Flow

```
pending → pending_verification → verified ✅
                               ↘ rejected ❌
```

- **pending**: Payment request created, waiting for TX hash
- **pending_verification**: TX hash submitted, awaiting admin review
- **verified**: Payment confirmed, subscription activated
- **rejected**: Payment invalid, subscription not activated

---

## 🔑 Environment Variables Required

```bash
USDT_TRC20_WALLET=TBjfqimYNsPecGxsk9kcX8GboPyZcWHNzb  # Your wallet
TRONSCAN_API_KEY=your_api_key_here                     # Optional but recommended
```

