# Admin Notification System - Complete Guide

## 📱 Overview

The VerzekAutoTrader platform now includes a comprehensive admin notification system to keep you informed of all critical events, especially **referral payout requests** when you have thousands of users.

---

## 🔔 Notification Types

### 1. **Instant Payout Request Alerts** 🚨
Sent immediately when a user requests a referral payout.

**Triggers:**
- User requests payout from in-app wallet
- Minimum $10 USDT balance required

**Notification includes:**
- User ID
- Payout amount
- Wallet address (TRC20)
- Payout ID
- Priority indicator (🔴 for >$100, 🟢 for normal)

**Example:**
```
🔴 HIGH PRIORITY 💰 NEW PAYOUT REQUEST

User: whale_user_999
Amount: $250.00 USDT
Fee: $1.00 USDT
Net Payout: $250.00 USDT

Destination:
TWhaleWalletAddress1234567890abcdefghijk

Payout ID: PAYOUT_whale_user_999_1729540000

⏰ Requested: 2025-10-21T18:45:00

Action Required:
1. Verify wallet address is valid
2. Send $250.00 USDT to address above
3. Mark payout as completed in system
```

---

### 2. **Payment Verification Alerts** ✅
Sent when a subscription payment is successfully verified.

**Triggers:**
- User's USDT payment verified (automatic or manual)
- Subscription activated

**Notification includes:**
- User ID
- Plan (Pro/VIP)
- Payment amount
- Transaction hash
- Referral bonus (if applicable)
- Your net revenue

**Example:**
```
✅ PAYMENT VERIFIED

User: premium_user_123
Plan: PRO
Amount: $29.00 USDT

Referral Bonus: $2.90 credited to referrer

TX Hash:
9f2a1b3c4d5e6f7g8h9i0j1k2l3m...

💰 Revenue: $26.10 USDT
```

---

### 3. **Hourly Payout Summaries** 📊
Batched summary of all pending payouts (prevents spam with many users).

**Triggers:**
- Every hour on the hour (configurable)
- Only if there are pending payouts

**Notification includes:**
- Total pending requests
- Total payout amount
- Top 5 largest payouts
- Action reminder

**Example:**
```
📊 PENDING PAYOUTS SUMMARY

Total Requests: 15
Total Amount: $567.50 USDT
Total Fees: $15.00 USDT

Breakdown:
1. whale_user_999: $250.00
2. trader_pro_456: $89.50
3. affiliate_king_789: $65.00
4. crypto_guru_321: $45.00
5. moon_boy_654: $38.00

...and 10 more

⚠️ Action Required:
Process 15 payout request(s)
```

---

### 4. **Daily Platform Summary** 📈
Complete overview of platform activity (sent once daily).

**Triggers:**
- Every day at 9:00 AM UTC (configurable)

**Notification includes:**
- New user registrations
- Payments verified
- Total revenue
- Payouts processed/pending
- Active trading positions
- Referral commissions paid

**Example:**
```
📈 DAILY SUMMARY - 2025-10-21

💰 Revenue
• Payments Verified: 12
• Total Revenue: $348.00 USDT

👥 Users
• New Registrations: 8
• Active Positions: 45

💸 Payouts
• Processed: 5
• Pending: 3

📊 Referrals
• Commissions Paid: $34.80

─────────────────────────
VerzekAutoTrader Platform
```

---

### 5. **System Alerts** 🚨
Critical system errors or warnings.

**Triggers:**
- Exchange API failures
- Database errors
- Security incidents
- System restarts

---

## ⚙️ Setup Instructions

### Step 1: Create Telegram Bot

1. **Open Telegram and message @BotFather**
2. **Send:** `/newbot`
3. **Follow prompts:**
   - Bot name: "VerzekAdmin Notifier"
   - Username: "VerzekAdminBot" (must be unique)
4. **Copy the bot token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 2: Get Your Chat ID

1. **Message your new bot** (send any message)
2. **Message @userinfobot** on Telegram
3. **Copy your Chat ID** (looks like: `123456789`)

### Step 3: Configure Replit Secrets

Add these secrets to your Replit project:

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_CHAT_ID=123456789
```

**How to add secrets:**
1. Click "Tools" → "Secrets" in Replit
2. Add each secret with the values above
3. Save

### Step 4: Test Notifications

Run the test script:

```bash
python admin_notify_test.py
```

You should receive test notifications in your Telegram!

---

## 🔄 How Payout Flow Works

### User Side:
1. User earns referral commissions (10% of referee payments)
2. Commissions accumulate in **in-app wallet**
3. User requests payout (min $10 USDT)
4. **YOU GET INSTANT TELEGRAM NOTIFICATION** 📱
5. User's wallet balance cleared immediately

### Your Side:
1. **Receive Telegram notification** with all details
2. **Verify wallet address** is valid TRC20 address
3. **Send USDT** from your wallet to their address
4. **Get transaction hash** from TronScan
5. **Mark as completed** via API or admin panel

### API to Complete Payout:

```bash
POST /api/referral/payouts/{payout_id}/complete
Authorization: Bearer YOUR_ADMIN_TOKEN

{
  "tx_hash": "transaction_hash_from_tronscan"
}
```

**Example:**
```bash
curl -X POST https://your-domain.com/api/referral/payouts/PAYOUT_user_1234/complete \
  -H "Authorization: Bearer your_admin_token" \
  -H "Content-Type: application/json" \
  -d '{
    "tx_hash": "9f2a1b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Payout PAYOUT_user_1234 marked as completed",
  "amount": 14.00,
  "user_id": "user_123"
}
```

---

## 📊 Viewing Pending Payouts

### Via API:

```bash
GET /api/referral/payouts/pending
Authorization: Bearer YOUR_ADMIN_TOKEN
```

**Response:**
```json
{
  "count": 3,
  "payouts": [
    {
      "payout_id": "PAYOUT_user_123_1729540000",
      "user_id": "user_123",
      "amount_usdt": 14.00,
      "withdrawal_fee": 1.00,
      "total_deducted": 15.00,
      "wallet_address": "TUserWalletAddress...",
      "network": "TRC20",
      "status": "pending",
      "requested_at": "2025-10-21T18:00:00"
    }
  ]
}
```

---

## 🎯 Scaling for Thousands of Users

### Problem:
With 1,000+ users requesting payouts, you'd get spammed with notifications!

### Solution:
The system uses **intelligent batching**:

**Instant Alerts:**
- High-priority payouts (>$100) = Instant notification
- First payout of the hour = Instant notification

**Batched Alerts:**
- All other payouts = Included in hourly summary
- You get ONE notification per hour with all pending payouts

**Configuration:**
```python
# In services/admin_notifications.py
self.HIGH_AMOUNT_THRESHOLD = 100  # Change to adjust priority
self.BATCH_INTERVAL = 3600  # 1 hour (change if needed)
```

### Example with 50 Pending Payouts:

**Instead of 50 notifications, you get:**
1. ✅ 1 hourly summary with all 50 payouts listed
2. ✅ Sorted by amount (largest first)
3. ✅ Total amount clearly visible
4. ✅ Action reminder

---

## 🛠️ Advanced Configuration

### Schedule Configuration

Edit `scheduled_tasks.py` to change when summaries are sent:

```python
# Hourly summaries (default: every hour at :00)
schedule.every().hour.at(":00").do(send_hourly_payout_summary)

# Daily summary (default: 9 AM UTC)
schedule.every().day.at("09:00").do(send_daily_summary)

# Custom schedules:
schedule.every(30).minutes.do(send_hourly_payout_summary)  # Every 30 min
schedule.every().day.at("17:00").do(send_daily_summary)   # 5 PM UTC
```

### Notification Thresholds

Adjust when instant vs batched notifications are sent:

```python
# In services/admin_notifications.py
self.HIGH_AMOUNT_THRESHOLD = 100  # $100+ = instant alert
```

**Recommended settings:**
- Small platform (0-100 users): $50 threshold
- Medium platform (100-1000 users): $100 threshold
- Large platform (1000+ users): $200 threshold

---

## 📝 API Endpoints Summary

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/referral/payouts/pending` | GET | View pending payouts | Admin |
| `/api/referral/payouts/{id}/complete` | POST | Mark payout completed | Admin |
| `/api/referral/payout` | POST | Request payout (user) | User |
| `/api/wallet/balance` | GET | Check wallet balance | User |
| `/api/referral/stats` | GET | Get referral earnings | User |

---

## 🧪 Testing

### Test Instant Notification:
```bash
python admin_notify_test.py
```

### Test Hourly Summary:
```bash
python scheduled_tasks.py
```
(Will run in background and send summaries on schedule)

### Simulate Payout Request:
```bash
curl -X POST http://localhost:5000/api/referral/payout \
  -H "Authorization: Bearer user_token" \
  -H "Content-Type: application/json" \
  -d '{
    "wallet_address": "TTestWalletAddress123..."
  }'
```

You should immediately receive a Telegram notification! 📱

---

## 🚀 Production Deployment

### Option 1: Run Scheduler Separately
```bash
# In one process
python run_all_bots.py

# In another process
python scheduled_tasks.py
```

### Option 2: Integrate with Main Bot
Add to `run_all_bots.py`:
```python
import threading
from scheduled_tasks import run_scheduler

# Start scheduler in background thread
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()
```

---

## 💡 Best Practices

### For Small Scale (0-100 users):
- ✅ Enable instant notifications for all payouts
- ✅ Set threshold to $0 (all get instant alerts)
- ✅ Disable hourly summaries

### For Medium Scale (100-1000 users):
- ✅ Keep default settings ($100 threshold)
- ✅ Enable hourly summaries
- ✅ Daily summary at convenient time

### For Large Scale (1000+ users):
- ✅ Increase threshold to $200-$500
- ✅ Enable hourly summaries
- ✅ Consider 30-minute batches instead of hourly
- ✅ Daily summary essential

---

## 🔐 Security Notes

- ✅ Only admin users can view/complete payouts
- ✅ All payout completions are audit logged
- ✅ Transaction hash required for completion
- ✅ Wallet addresses validated before notification
- ✅ Telegram bot token never exposed in logs

---

## 📞 Support

**Telegram Bot Not Working?**
1. Check bot token is correct in secrets
2. Make sure you messaged the bot first
3. Verify chat ID is correct
4. Test with `admin_notify_test.py`

**Not Receiving Notifications?**
1. Check secrets are set correctly
2. Verify bot is running (`run_all_bots.py`)
3. Check logs: `tail -f database/logs.txt`

**Payout Not Completing?**
1. Verify you're admin user (plan = 'admin')
2. Check transaction hash is valid
3. Ensure payout is in 'pending' status

---

## ✅ Summary

**Instant Alerts For:**
- 🔴 High-value payouts (>$100)
- 💰 All payment verifications
- 🚨 System errors

**Batched Summaries For:**
- 📊 Regular payouts (hourly)
- 📈 Platform metrics (daily)

**Benefits:**
- ✅ Never miss a payout request
- ✅ Scales to thousands of users
- ✅ No spam with smart batching
- ✅ Mobile-friendly (Telegram)
- ✅ Instant action with all details

**Your Telegram becomes your admin dashboard!** 📱
