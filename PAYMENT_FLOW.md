# VerzekAutoTrader - Subscription Payment Flow

## 💰 Payment System Overview

VerzekAutoTrader uses **USDT TRC20** (TRON network) for all subscription payments. This provides fast, low-fee transactions with automatic verification.

---

## 🔄 Complete Payment Flow

### Step 1: User Requests Subscription Upgrade

**Mobile App → API:**
```
POST /api/users/{user_id}/subscription
{
  "plan": "pro",  // or "vip"
  "payment_method": "usdt_trc20"
}
```

**API Response:**
```json
{
  "payment_id": "PAY_demo_verzektrader_com_1729539600",
  "user_id": "demo_verzektrader_com",
  "plan": "pro",
  "amount_usdt": 29.00,
  "payment_method": "usdt_trc20",
  "status": "pending",
  "created_at": "2025-10-21T18:00:00",
  "expires_at": "2025-10-22T18:00:00",
  "wallet_address": "TYourWalletAddressHere",
  "network": "TRC20 (TRON)",
  "instructions": [
    "Send exactly 29 USDT",
    "Network: TRC20 (TRON)",
    "To wallet: TYourWalletAddressHere",
    "After payment, provide transaction hash for verification"
  ]
}
```

---

### Step 2: Where Does Payment Go?

**✅ Payment Destination:**
- **Wallet Address:** Set in Replit Secret `USDT_TRC20_WALLET`
- **Owned By:** Platform owner (YOU)
- **Network:** TRON (TRC20)
- **Currency:** USDT

**Configuration:**
```bash
# Set your USDT TRC20 wallet address in Replit Secrets
USDT_TRC20_WALLET=TYourActualWalletAddressHere
```

**Important:**
- This is YOUR wallet address
- You receive all subscription payments
- Users send USDT directly to your wallet
- No third-party payment processor involved

---

### Step 3: User Sends Payment

**User Actions:**
1. Opens TronLink/Trust Wallet/any TRON wallet
2. Sends exact amount (e.g., 29 USDT) to provided address
3. Uses TRC20 network (TRON)
4. Copies transaction hash after confirmation

**Example Transaction:**
```
From: TUserWalletAddress123...
To: TYourWalletAddressHere
Amount: 29.000000 USDT
Network: TRC20 (TRON)
TX Hash: 9f2a1b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7
Confirmations: 20
```

---

### Step 4: Payment Confirmation (2 Methods)

#### Method A: Automatic Verification (TronScan API)

**User submits transaction hash:**
```
POST /api/payments/{payment_id}/submit
{
  "tx_hash": "9f2a1b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7",
  "referral_code": "REF123" // optional
}
```

**System automatically verifies:**
1. ✅ Transaction exists on TRON blockchain
2. ✅ Status is SUCCESS
3. ✅ Recipient address matches your wallet
4. ✅ Amount matches subscription price (±$0.01 tolerance)
5. ✅ Minimum 19 confirmations (TRON finality)

**TronScan API Response:**
```json
{
  "verified": true,
  "amount": 29.00,
  "confirmations": 25,
  "tx_hash": "9f2a1b3c...",
  "from_address": "TUserWallet...",
  "to_address": "TYourWallet..."
}
```

#### Method B: Manual Admin Verification

**Admin reviews payment:**
```
POST /api/payments/{payment_id}/verify
{
  "is_valid": true,
  "verified_by": "admin_user_id"
}
```

**Manual verification used when:**
- TronScan API is down
- User sent slightly wrong amount
- Transaction needs manual review
- Testing in development

---

### Step 5: Subscription Activated

**After successful verification:**

1. **Subscription Updated:**
```json
{
  "user_id": "demo_verzektrader_com",
  "plan": "pro",
  "status": "active",
  "activated_at": "2025-10-21T18:05:00",
  "expires_at": "2025-11-21T18:05:00",
  "auto_renew": true
}
```

2. **Payment Status Updated:**
```json
{
  "payment_id": "PAY_demo_verzektrader_com_1729539600",
  "status": "verified",
  "verified_at": "2025-10-21T18:05:00",
  "tx_hash": "9f2a1b3c...",
  "verification_method": "automatic"
}
```

3. **User Notified:**
- Email confirmation sent
- Mobile app shows "Pro Plan Active"
- Trading features unlocked

---

### Step 6: Referral Bonuses (If Applicable)

**If user used a referral code:**

1. **Referrer earns 10% commission:**
```
Payment Amount: $29 USDT
Commission: $2.90 USDT (10%)
Credited to: Referrer's in-app wallet
```

2. **Bonus tracked in database:**
```json
{
  "referrer_id": "ref_user_123",
  "referee_id": "demo_verzektrader_com",
  "payment_amount": 29.00,
  "bonus_earned": 2.90,
  "date": "2025-10-21T18:05:00"
}
```

3. **Recurring monthly bonus:**
- Every month when user renews subscription
- Referrer continues earning 10%
- Tracked in `database/referrals.json`

---

### Step 7: Withdrawal System (For Referral Earnings)

**Users can withdraw referral bonuses:**

#### Request Payout
```
POST /api/referral/payout
{
  "wallet_address": "TUserWalletAddress123..."
}
```

**Requirements:**
- ✅ Minimum balance: $10 USDT
- ✅ Withdrawal fee: $1 USDT (goes to system)
- ✅ Network: TRC20 (TRON)
- ✅ Processing time: Within 24 hours

**Payout Flow:**
```
User Balance: $15.00 USDT
Withdrawal Fee: -$1.00 USDT
Payout Amount: $14.00 USDT
Destination: User's TRON wallet
Status: Pending (manual processing)
```

**Admin processes payout:**
1. Reviews payout request
2. Sends USDT from platform wallet to user's wallet
3. Marks payout as completed
4. User receives confirmation

---

## 🔐 Security & Verification

### Payment Security
- ✅ Transaction hash verification via TronScan API
- ✅ Minimum 19 confirmations required (TRON finality)
- ✅ Amount verification with tolerance (±$0.01)
- ✅ Wallet address verification
- ✅ Duplicate transaction prevention

### Data Protection
- ✅ Payment records stored in `database/payments.json`
- ✅ Referral data in `database/referrals.json`
- ✅ Transaction hashes logged for audit trail
- ✅ User subscription status encrypted

---

## 💵 Subscription Pricing

| Plan | Monthly Price | Features |
|------|---------------|----------|
| **Free** | $0 | Manual trading, basic features |
| **Pro** | $29 USDT | Auto-trading, 5 positions, advanced features |
| **VIP** | $99 USDT | Unlimited positions, AI assistant, priority signals |

---

## 🔄 Recurring Payments

### How It Works
1. User's subscription expires monthly
2. System sends renewal reminder via email/push notification
3. User creates new payment request
4. Sends USDT to same wallet address
5. Submits new transaction hash
6. Subscription automatically renewed
7. Referrer earns 10% commission again

### Auto-Renewal Flow
```
Month 1: User pays $29 → Referrer earns $2.90
Month 2: User pays $29 → Referrer earns $2.90
Month 3: User pays $29 → Referrer earns $2.90
...and so on
```

**Referrer Lifetime Value:**
```
1 referee × $29/month × 10% × 12 months = $34.80/year
10 referees × $29/month × 10% × 12 months = $348/year
100 referees × $29/month × 10% × 12 months = $3,480/year
```

---

## 📊 Payment Status Tracking

### Payment States
1. **pending** - Payment request created, awaiting user payment
2. **pending_verification** - TX hash submitted, awaiting verification
3. **verified** - Payment confirmed, subscription activated
4. **rejected** - Payment failed verification
5. **expired** - Payment request expired (24 hours)

### API Endpoints

**Create Payment Request:**
```
POST /api/users/{user_id}/subscription
```

**Submit Transaction Hash:**
```
POST /api/payments/{payment_id}/submit
```

**Check Payment Status:**
```
GET /api/payments/{payment_id}
```

**Admin Verify Payment:**
```
POST /api/payments/{payment_id}/verify
```

**Request Payout:**
```
POST /api/referral/payout
```

**Check Referral Earnings:**
```
GET /api/referral/earnings
```

---

## 🎯 Summary

**Where does money go?**
→ Your USDT TRC20 wallet (set in `USDT_TRC20_WALLET` secret)

**How is payment confirmed?**
→ Automatic: TronScan API (19+ confirmations)
→ Manual: Admin verification

**How to withdraw referral bonuses?**
→ Request payout to your TRON wallet (min $10, $1 fee)
→ Admin processes within 24 hours

**Who pays withdrawal fees?**
→ User pays $1 fee when withdrawing referral bonuses
→ Platform keeps subscription payments (minus referral commissions)

**Is it non-custodial?**
→ YES! Users never send funds to the platform
→ Payments go directly to your wallet
→ You control all funds

---

## 🚀 Production Setup

### Required Replit Secrets
```bash
# Your USDT TRC20 wallet address (REQUIRED)
USDT_TRC20_WALLET=TYourActualWalletAddressHere

# TronScan API key (optional, for higher rate limits)
TRONSCAN_API_KEY=your-api-key-here

# SMTP for payment confirmations (optional but recommended)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Testing Payment Flow
1. Set test wallet address in secrets
2. Create payment request via API
3. Send test amount (e.g., 1 USDT) to wallet
4. Submit TX hash
5. Verify automatic confirmation works
6. Check subscription activated

---

**Payment System Status:** ✅ Fully Functional

All payment infrastructure is ready for production use!
