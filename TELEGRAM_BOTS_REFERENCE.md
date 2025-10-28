# VerzekAutoTrader - Telegram Bots Reference

This document lists all Telegram bots working in the VerzekAutoTrader project, their duties, configurations, and IDs.

---

## 📋 **Bot Overview**

The project uses **2 Telegram bots** and **1 Telethon user client** for signal monitoring and broadcasting:

---

## 1️⃣ **Broadcast Bot** (@broadnews_bot)

### **Primary Duty:**
Broadcasts trading signals to VIP and TRIAL Telegram groups with "VERZEK TRADING SIGNALS" branding.

### **Configuration:**
- **Username:** `@broadnews_bot`
- **Bot ID:** *(To get: message the bot and check Telegram API response)*
- **Token:** Stored in `BROADCAST_BOT_TOKEN` environment variable
- **Operation Mode:** Webhook (for efficiency and to avoid polling conflicts)
- **Webhook URL:** `https://verzek-auto-trader.replit.app/webhook/broadcast`

### **Responsibilities:**
1. ✅ Receives signals from Telethon Forwarder via HTTP POST
2. ✅ Broadcasts signals to VIP Group (ID: -1002721581400)
3. ✅ Broadcasts signals to TRIAL Group (ID: -1002726167386)
4. ✅ Logs all signals to `database/broadcast_log.txt` for mobile app access
5. ✅ Triggers auto-trading for PREMIUM users via Signal Auto-Trader module
6. ✅ Cleans signal formatting (removes # symbols, leverage indicators)
7. ✅ Detects close/cancel signals and auto-closes positions for affected users
8. ✅ Prevents broadcast loops (ignores messages from VIP/TRIAL groups)

### **Target Groups:**
| Group | Group ID | Purpose |
|-------|----------|---------|
| VIP Group | `-1002721581400` | Paid VIP subscribers |
| TRIAL Group | `-1002726167386` | Trial users |

### **Files:**
- `broadcast_bot.py` - Main bot script (standalone mode)
- `broadcast_bot_webhook_handler.py` - Webhook handler (imported by Flask API)

### **How to Get Bot ID:**
```bash
# Use Telegram API to get bot info
curl "https://api.telegram.org/bot<BROADCAST_BOT_TOKEN>/getMe"
```

---

## 2️⃣ **Admin Notification Bot** (Username: Not Specified)

### **Primary Duty:**
Sends administrative alerts, financial summaries, and system notifications to admin.

### **Configuration:**
- **Username:** *(Not explicitly named - uses generic Telegram Bot API)*
- **Bot ID:** *(To get: use getMe API call)*
- **Token:** Stored in `TELEGRAM_BOT_TOKEN` environment variable
- **Admin Chat ID:** Stored in `ADMIN_CHAT_ID` environment variable
- **Operation Mode:** Direct API calls via `requests` library

### **Responsibilities:**
1. 🔔 Sends payout request notifications to admin
2. 🔔 Alerts admin about large payment amounts ($100+ USDT)
3. 🔔 Sends daily/hourly financial summaries
4. 🔔 System alerts and critical event notifications
5. 🔔 Batched notifications for scale (1-hour intervals for non-urgent alerts)

### **Notification Types:**
- **Payout Requests** - User referral commission withdrawals
- **High-Value Alerts** - Payments ≥ $100 USDT
- **System Alerts** - Critical errors, security events
- **Financial Summaries** - Daily revenue, subscription stats, referral payouts

### **Files:**
- `services/admin_notifications.py` - Notification service module
- `admin_notify_test.py` - Test script for notification system

### **How to Get Bot ID:**
```bash
# Use Telegram API to get bot info
curl "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getMe"
```

---

## 3️⃣ **Telethon Forwarder** (User Client - NOT a Bot)

### **Primary Duty:**
Monitors Telegram channels and personal chats for trading signals, then forwards them to Broadcast Bot.

### **Configuration:**
- **Type:** Telethon User Client (NOT a bot - runs as your personal Telegram account)
- **API ID:** Stored in `TELEGRAM_API_ID` environment variable
- **API Hash:** Stored in `TELEGRAM_API_HASH` environment variable
- **Session Files:**
  - Production: `telethon_session_prod.txt`
  - Development: `telethon_session_dev.txt`

### **Monitored Channels:**
| Channel Name | Channel ID | Type |
|--------------|------------|------|
| **Ai Golden Crypto (🔱VIP)** | `2249790469` | Paid VIP signal source |
| *(Future channels can be added)* | - | - |

### **Responsibilities:**
1. 📡 Monitors VIP signal channel (Ai Golden Crypto) 24/7
2. 📡 Smart filtering: Only forwards real trading signals, blocks promotional content
3. 📡 Detects signal types: Entry+Targets, Target Reached, Profit Collected, Stop Loss hit, Closed signals
4. 📡 Blocks spam: Setup guides, claim bonus ads, invite links
5. 📡 Sends filtered signals to Broadcast Bot via HTTP POST to Flask API
6. 📡 Prevents duplicate signals (rolling cache of 300 messages)
7. 📡 Blocks known spammers and promotional bots

### **Signal Detection Criteria:**
- ✅ Entry + Targets
- ✅ Entry + Stop Loss
- ✅ Target Reached notifications
- ✅ Profit Collected updates
- ✅ Stop Loss hit alerts
- ✅ Trade Closed/Cancelled signals
- ✅ #Signal format markers

### **Blocked Content:**
- 🚫 "Setup Auto-Trade" ads
- 🚫 "Claim Bonus" promotions
- 🚫 Invite links (T.ME/)
- 🚫 Tutorials and guides
- 🚫 Pinned messages

### **Files:**
- `telethon_forwarder.py` - Main forwarder script
- `setup_telethon.py` - Session setup script
- `recover_telethon_session.py` - Session recovery tool

---

## 🔑 **Required Environment Variables**

### **For Broadcast Bot:**
```bash
BROADCAST_BOT_TOKEN=<your_broadcast_bot_token>
ADMIN_CHAT_ID=<your_telegram_admin_user_id>
```

### **For Admin Notification Bot:**
```bash
TELEGRAM_BOT_TOKEN=<your_admin_notification_bot_token>
ADMIN_CHAT_ID=<your_telegram_admin_user_id>
```

### **For Telethon Forwarder:**
```bash
TELEGRAM_API_ID=<your_telegram_api_id>
TELEGRAM_API_HASH=<your_telegram_api_hash>
```

**Get Telegram API credentials:** https://my.telegram.org/apps

---

## 📊 **Bot Communication Flow**

```
┌─────────────────────────────────────────────────────┐
│  Ai Golden Crypto (🔱VIP) Channel                   │
│  ID: 2249790469                                     │
└───────────────────┬─────────────────────────────────┘
                    │
                    │ New Signal Posted
                    ▼
┌─────────────────────────────────────────────────────┐
│  Telethon Forwarder (User Client)                   │
│  - Monitors channel 24/7                            │
│  - Smart filtering (blocks spam)                    │
│  - Detects signal types                             │
└───────────────────┬─────────────────────────────────┘
                    │
                    │ HTTP POST to Flask API
                    │ Endpoint: /api/broadcast/signal
                    ▼
┌─────────────────────────────────────────────────────┐
│  Broadcast Bot (@broadnews_bot)                     │
│  - Receives via webhook                             │
│  - Adds "VERZEK TRADING SIGNALS" header             │
│  - Cleans formatting                                │
└───────────────────┬─────────────────────────────────┘
                    │
                    │ Broadcasts
                    ├─────────────┬──────────────┬─────────────┐
                    ▼             ▼              ▼             ▼
            ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
            │VIP Group │  │TRIAL Grp │  │Mobile App│  │Auto-Trade│
            │-10027... │  │-10027... │  │Log File  │  │Engine    │
            └──────────┘  └──────────┘  └──────────┘  └──────────┘
```

---

## 📱 **How to Get Bot IDs**

### **Method 1: Using Telegram Bot API (Recommended)**

```bash
# Get Broadcast Bot info
curl "https://api.telegram.org/bot<BROADCAST_BOT_TOKEN>/getMe"

# Get Admin Notification Bot info
curl "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getMe"
```

**Response Example:**
```json
{
  "ok": true,
  "result": {
    "id": 123456789,
    "is_bot": true,
    "first_name": "BroadNews Bot",
    "username": "broadnews_bot"
  }
}
```

### **Method 2: Using @userinfobot on Telegram**

1. Forward a message from the bot to @userinfobot
2. It will show you the bot's ID

### **Method 3: Using @getidsbot on Telegram**

1. Add the bot to a group
2. Forward a message from the bot to @getidsbot
3. It will display the bot's ID

---

## 🔧 **Testing Bots**

### **Test Broadcast Bot:**
```bash
# Send a test signal to the broadcast bot via webhook
curl -X POST https://verzek-auto-trader.replit.app/api/broadcast/signal \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Signal BTC/USDT Long Entry: 45000",
    "provider": "test"
  }'
```

### **Test Admin Notifications:**
```bash
# Run the admin notification test script
python admin_notify_test.py
```

---

## ⚠️ **Important Notes**

1. **Broadcast Bot vs Admin Bot:**
   - `BROADCAST_BOT_TOKEN` = Public-facing bot for signal broadcasting
   - `TELEGRAM_BOT_TOKEN` = Admin-only bot for private notifications

2. **Webhook vs Polling:**
   - Broadcast Bot uses **webhooks** (more efficient, no conflicts)
   - Admin Notification Bot uses **direct API calls** (simpler, no setup needed)

3. **Loop Prevention:**
   - Both bots ignore messages from VIP/TRIAL groups
   - Telethon ignores messages with "VERZEK TRADING SIGNALS" header
   - Prevents infinite broadcast loops

4. **Session Management:**
   - Telethon uses separate sessions for production and development
   - Prevents "dual IP" conflicts when running on multiple servers

---

## 📚 **Related Documentation**

- `ADMIN_NOTIFICATIONS_GUIDE.md` - Admin notification system guide
- `CHANNEL_MONITORING_FIXED.md` - Channel monitoring configuration
- `PRODUCTION_READINESS.md` - Production deployment checklist
- `replit.md` - Project overview and architecture

---

**Last Updated:** October 27, 2025
