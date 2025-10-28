# VerzekAutoTrader - Telegram Bots & IDs (ACTUAL VALUES)

**Generated:** October 27, 2025

---

## 🤖 **Your Telegram Bots**

### **1️⃣ Broadcast Bot (Signal Broadcasting)**

| Property | Value |
|----------|-------|
| **Bot Name** | VerzekBroadcaster |
| **Username** | `@broadnews_bot` |
| **Bot ID** | **8479454611** |
| **Token Variable** | `BROADCAST_BOT_TOKEN` |
| **Purpose** | Broadcasts trading signals to VIP/TRIAL groups |

**Responsibilities:**
- Broadcasts signals to VIP Group (ID: -1002721581400)
- Broadcasts signals to TRIAL Group (ID: -1002726167386)
- Adds "VERZEK TRADING SIGNALS" branding
- Triggers auto-trading for PREMIUM users
- Logs signals for mobile app access

---

### **2️⃣ Admin Notification Bot (Private Admin Alerts)**

| Property | Value |
|----------|-------|
| **Bot Name** | Verzek Finances |
| **Username** | `@verzekpayflowbot` |
| **Bot ID** | **8351047055** |
| **Token Variable** | `TELEGRAM_BOT_TOKEN` |
| **Purpose** | Sends admin notifications, payout requests, financial summaries |

**Responsibilities:**
- Payout request notifications
- Large payment alerts ($100+ USDT)
- Daily/hourly financial summaries
- System alerts and critical events

---

### **👤 Your Admin Chat ID**

| Property | Value |
|----------|-------|
| **Admin Chat ID** | **572038606** |
| **Variable Name** | `ADMIN_CHAT_ID` |
| **Purpose** | Receives all admin notifications from @verzekpayflowbot |

---

## 📋 **Complete Bot Configuration Summary**

```
┌──────────────────────────────────────────────────────────────┐
│  Bot #1: BROADCAST BOT                                       │
├──────────────────────────────────────────────────────────────┤
│  Name:     VerzekBroadcaster                                 │
│  Username: @broadnews_bot                                    │
│  Bot ID:   8479454611                                        │
│  Role:     Public signal broadcasting to VIP/TRIAL groups    │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  Bot #2: ADMIN NOTIFICATION BOT                              │
├──────────────────────────────────────────────────────────────┤
│  Name:     Verzek Finances                                   │
│  Username: @verzekpayflowbot                                 │
│  Bot ID:   8351047055                                        │
│  Role:     Private admin alerts and financial notifications  │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  ADMIN CONFIGURATION                                         │
├──────────────────────────────────────────────────────────────┤
│  Admin Chat ID: 572038606                                    │
│  Receives notifications from: @verzekpayflowbot              │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔗 **Direct Bot Links**

- **Broadcast Bot:** https://t.me/broadnews_bot
- **Admin Bot:** https://t.me/verzekpayflowbot

---

## 📱 **How to Use These IDs**

### **For Webhook Configuration:**
```bash
# Set webhook for Broadcast Bot
curl -X POST "https://api.telegram.org/bot${BROADCAST_BOT_TOKEN}/setWebhook" \
  -d "url=https://verzek-auto-trader.replit.app/webhook/broadcast"
```

### **For Sending Messages:**
```python
# Send message via Broadcast Bot
import requests

bot_id = 8479454611
chat_id = -1002721581400  # VIP Group

requests.post(f"https://api.telegram.org/bot{BROADCAST_BOT_TOKEN}/sendMessage", 
  json={"chat_id": chat_id, "text": "Test message"})
```

### **For Admin Notifications:**
```python
# Send admin notification
import requests

admin_chat_id = 572038606

requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
  json={"chat_id": admin_chat_id, "text": "Admin alert!"})
```

---

## 🎯 **Target Groups (VIP/TRIAL)**

| Group | Chat ID | Purpose |
|-------|---------|---------|
| **VIP Group** | `-1002721581400` | Paid VIP subscribers - Full signal details |
| **TRIAL Group** | `-1002726167386` | Trial users - Limited access |

---

## ⚙️ **Environment Variables (Reference)**

```bash
# Broadcast Bot
BROADCAST_BOT_TOKEN=<your_token_here>

# Admin Notification Bot
TELEGRAM_BOT_TOKEN=<your_token_here>

# Admin Chat ID
ADMIN_CHAT_ID=572038606

# Telethon Forwarder
TELEGRAM_API_ID=<your_api_id>
TELEGRAM_API_HASH=<your_api_hash>
```

---

## 🔍 **Verification**

You can verify these IDs anytime by running:

```bash
# Check Broadcast Bot
curl "https://api.telegram.org/bot${BROADCAST_BOT_TOKEN}/getMe"

# Check Admin Bot
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"

# Check your Chat ID (send /start to @userinfobot on Telegram)
```

---

**🔒 SECURITY NOTE:** Keep these IDs and tokens secure. Never commit them to public repositories.

---

**Last Updated:** October 27, 2025  
**Project:** VerzekAutoTrader v2.0
