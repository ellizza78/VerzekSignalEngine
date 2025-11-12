# Telegram Notifications Setup Guide

## 🎯 Overview

The system automatically sends real-time notifications to your Telegram subscribers group for:
- ✅ **New Subscriptions** - VIP & PREMIUM upgrades
- ✅ **Payment Submissions** - When users submit USDT payments
- ✅ **Referral Activity** - When users refer new members
- ✅ **Platform Milestones** - User count, subscriber count achievements

---

## 🔧 Configuration

### Required Environment Variables

```bash
# In /root/api_server_env.sh (VPS) or .env (local)
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export SUBSCRIBERS_CHAT_ID="-1002721581400"  # Already configured
```

**Note:** The bot token (`TELEGRAM_BOT_TOKEN`) is already configured in your Replit secrets.

---

## 📲 Notification Types

### 1. New Subscription Notification

**Triggers:** When admin approves a payment

**Message Format:**
```
⭐ NEW VIP SUBSCRIBER! ⭐

👤 Welcome: John Doe
💰 Amount: $50.00 USDT
📅 Date: 2025-11-12 09:50 UTC

🎉 Welcome to the Verzek family! Happy trading!
```

### 2. Payment Received Notification

**Triggers:** When user submits TX hash for verification

**Message Format:**
```
💸 PAYMENT RECEIVED!

💰 Amount: $50.00 USDT
📦 Plan: VIP
🔗 TX: 0x12345...abc678
📅 Date: 2025-11-12 09:45 UTC

⏳ Pending admin verification...
```

### 3. Referral Success Notification

**Triggers:** When someone registers using a referral code

**Message Format:**
```
🤝 NEW REFERRAL!

👥 Referred by: Sarah Smith
🆕 New member: Mike Johnson
📊 Plan: TRIAL
📅 Date: 2025-11-12 09:40 UTC

💪 Keep spreading the word! Referral bonuses coming soon!
```

### 4. Platform Milestones

**Manual trigger** - For celebrating achievements:

```
👥 MILESTONE ACHIEVED! 👥

We just reached 100 USERS!

Thank you to our amazing community! 🚀

📈 Verzek AutoTrader - Growing Together!
```

---

## 🧪 Testing Telegram Notifications

### Method 1: Admin Test Endpoint

```bash
# Login as admin and get JWT token
curl -X POST https://api.verzekinnovative.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@verzekinnovative.com","password":"your_password"}'

# Send test notification
curl -X POST https://api.verzekinnovative.com/api/admin/telegram/test \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Expected response:
{
  "ok": true,
  "message": "Test notification sent to Telegram group successfully"
}
```

**Check your Telegram group** - You should see:
```
🤖 VERZEK AUTOTRADER BOT ONLINE!

✅ Notifications system activated
📢 You will receive updates about:
  • New subscriptions
  • Referral bonuses
  • Payment confirmations
  • Platform milestones

🚀 Let's trade smart together!
```

### Method 2: Trigger Real Events

**Test Payment Notification:**
1. Register a test account via mobile app
2. Create payment request (VIP or PREMIUM)
3. Submit a fake TX hash
4. Check Telegram group for "Payment Received" notification

**Test Subscription Notification:**
1. Login as admin
2. Approve the test payment
3. Check Telegram group for "New Subscriber" notification

**Test Referral Notification:**
1. Get your referral code from any existing user
2. Register a new account with that referral code
3. Check Telegram group for "New Referral" notification

---

## 🛠️ Troubleshooting

### Issue: No notifications appearing

**Check 1: Bot Token**
```bash
# SSH into VPS
ssh root@80.240.29.142

# Verify token is set
grep TELEGRAM_BOT_TOKEN /root/api_server_env.sh
```

**Check 2: Bot Permissions**
- Open Telegram group
- Check bot is a member
- Verify bot has permission to send messages

**Check 3: Chat ID**
```bash
# Verify chat ID
grep SUBSCRIBERS_CHAT_ID /root/api_server_env.sh

# Should be: -1002721581400
```

**Check 4: API Logs**
```bash
# Check for errors
tail -f /root/VerzekBackend/backend/logs/api.log | grep -i telegram
```

### Issue: "Telegram notification failed" in logs

**Possible causes:**
1. Bot token invalid or revoked
2. Bot removed from group
3. Network connectivity issues
4. Rate limiting (too many messages)

**Solution:**
```bash
# Test bot token manually
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getMe"

# Should return bot info if token is valid
```

---

## 🔐 Privacy & Security

### What Gets Sent to Group:
- ✅ User's full name (first + last)
- ✅ Subscription plan type (VIP/PREMIUM)
- ✅ Payment amount
- ✅ Truncated TX hash (first 8 + last 6 chars)
- ✅ Timestamps

### What's Protected (NOT Sent):
- ❌ User emails
- ❌ Complete TX hashes
- ❌ User IDs
- ❌ Password information
- ❌ API keys

---

## 📊 Notification Flow

```
User Action → Backend Endpoint → Telegram Notification
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Registration (with referral code)
  └→ /api/auth/register
     └→ notify_referral_success()
        └→ Telegram Group

Payment Submission
  └→ /api/payments/verify
     └→ notify_payment_received()
        └→ Telegram Group

Payment Approval
  └→ /api/admin/payments/approve/<id>
     └→ notify_new_subscription()
        └→ Telegram Group
```

---

## 💡 Best Practices

1. **Test Before Deployment**
   - Always run `/api/admin/telegram/test` after deployment
   - Verify notifications in group before going live

2. **Monitor Logs**
   - Check logs for "Telegram notification" messages
   - Warning logs won't stop payment processing

3. **Graceful Degradation**
   - If Telegram fails, payment/subscription logic continues
   - Notifications are **non-blocking** - failures are logged but don't stop operations

4. **Rate Limits**
   - Telegram allows ~20 messages/minute
   - System has no throttling - be cautious with bulk operations

---

## 🎨 Message Customization

To customize notification messages, edit:
```
backend/utils/telegram_notifications.py
```

**Available functions:**
- `notify_new_subscription()` - Subscription upgrades
- `notify_payment_received()` - Payment submissions
- `notify_referral_success()` - Referrals
- `notify_milestone()` - Achievements
- `test_notification()` - Test message

**Example customization:**
```python
def notify_new_subscription(user_name, plan_type, amount_usdt):
    emoji = "💎" if plan_type == "PREMIUM" else "⭐"
    
    # Customize this message:
    message = f"""
{emoji} <b>NEW {plan_type} SUBSCRIBER!</b> {emoji}

👤 <b>Welcome:</b> {user_name}
💰 <b>Amount:</b> ${amount_usdt:.2f} USDT

🎉 Custom welcome message here!
    """.strip()
    
    return send_telegram_message(message)
```

---

## 📞 Support

**Telegram Group:**
- Name: VERZEK SUBSCRIBERS
- Chat ID: `-1002721581400`
- Bot must be admin or have send message permissions

**Common Questions:**

**Q: Can I send to multiple groups?**
A: Yes, modify `telegram_notifications.py` to send to multiple chat IDs.

**Q: Can I disable certain notifications?**
A: Yes, comment out the `notify_*()` calls in the respective endpoints.

**Q: Are notifications sent for TRIAL users?**
A: Referral notifications yes, subscription notifications only for VIP/PREMIUM.

---

## ✅ Deployment Checklist

- [ ] TELEGRAM_BOT_TOKEN configured in environment
- [ ] SUBSCRIBERS_CHAT_ID set to `-1002721581400`
- [ ] Bot added to Telegram group
- [ ] Bot has message sending permissions
- [ ] Test endpoint returns success: `/api/admin/telegram/test`
- [ ] Test notification appears in Telegram group
- [ ] API logs show no Telegram errors
