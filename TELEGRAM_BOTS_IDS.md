# 📱 Telegram Bots & IDs Reference

Complete reference for all Telegram bot tokens and chat IDs used in VerzekAutoTrader.

---

## 🤖 Bot Tokens

### **1. Admin Bot (Payment & Management)**
- **Bot Username:** `@verzekpayflowbot`
- **Bot ID:** `8351047055`
- **Token:** `8351047055:AAEqBFx5g0NJpEvUOCP_DCPD0VsGpEAjvRE`
- **Purpose:** Payment processing, subscription management, admin alerts
- **Environment Variable:** `TELEGRAM_BOT_TOKEN`

### **2. Broadcast Bot (Signal Distribution)**
- **Bot Username:** `@broadnews_bot`
- **Bot ID:** `8479454611`
- **Token:** `7888348351:AAGQwdP0Bg5xFOQjxF6p5OPDZTLbUnp5IbU`
- **Purpose:** Broadcasting signals to VIP and TRIAL groups
- **Environment Variable:** `BROADCAST_BOT_TOKEN`

---

## 👤 Admin Chat IDs

### **Primary Admin**
- **Chat ID:** `572038606`
- **Environment Variable:** `ADMIN_CHAT_ID`
- **Receives:** Watchdog alerts, payment notifications, system errors

---

## 📢 Telegram Groups

### **VIP Group**
- **Group Name:** 🔥 VERZEK TRADING SIGNALS 🔥 (VIP)
- **Chat ID:** `-1002721581400`
- **Purpose:** Premium trading signals for VIP subscribers
- **Members:** Paid VIP subscribers only

### **TRIAL Group**
- **Group Name:** 🔥 VERZEK TRADING SIGNALS 🔥 (TRIAL)
- **Chat ID:** `-1002726167386`
- **Purpose:** Demo signals for trial users
- **Members:** Trial users (limited access)

---

## 📡 Monitored Signal Channels

### **Ai Golden Crypto (🔱VIP)**
- **Channel ID:** `-1002249790469`
- **Numeric ID:** `2249790469`
- **Purpose:** Primary signal source
- **Subscribers:** 15
- **Auto-forward:** ✅ Enabled (forwards to VIP + TRIAL groups)

---

## ⚙️ Environment Variables Setup

Add these to your `.env` file or Replit Secrets:

```bash
# Admin Bot (Payment Processing)
TELEGRAM_BOT_TOKEN="8351047055:AAEqBFx5g0NJpEvUOCP_DCPD0VsGpEAjvRE"

# Broadcast Bot (Signal Distribution)
BROADCAST_BOT_TOKEN="7888348351:AAGQwdP0Bg5xFOQjxF6p5OPDZTLbUnp5IbU"

# Admin Chat ID (Alert Recipient)
ADMIN_CHAT_ID="572038606"
```

---

## 🔔 Watchdog Alert Configuration

The watchdog script uses:
```bash
ADMIN_CHAT_ID="572038606"
TELEGRAM_BOT_TOKEN="8351047055:AAEqBFx5g0NJpEvUOCP_DCPD0VsGpEAjvRE"
```

When a service crashes, you receive:
> ⚠️ Watchdog Alert: Service verzekapi was restarted on vultr-server at 2025-10-28 14:30:00

---

## 🧪 Testing Bot Connectivity

### **Test Admin Bot:**
```bash
curl -X POST "https://api.telegram.org/bot8351047055:AAEqBFx5g0NJpEvUOCP_DCPD0VsGpEAjvRE/sendMessage" \
  -d chat_id="572038606" \
  -d text="✅ Admin Bot Test Message"
```

### **Test Broadcast Bot:**
```bash
curl -X POST "https://api.telegram.org/bot7888348351:AAGQwdP0Bg5xFOQjxF6p5OPDZTLbUnp5IbU/sendMessage" \
  -d chat_id="-1002721581400" \
  -d text="✅ Broadcast Bot Test Message"
```

---

## 📋 Bot Permissions

### **Admin Bot Permissions:**
- ✅ Send messages to admin
- ✅ Receive payment confirmations
- ✅ Handle subscription commands
- ✅ Process /start, /subscribe, /cancel

### **Broadcast Bot Permissions:**
- ✅ Send messages to VIP group
- ✅ Send messages to TRIAL group
- ✅ Post signals automatically
- ✅ No user interaction needed

---

## 🔒 Security Notes

- **Never commit bot tokens to Git** - Use environment variables only
- **Tokens stored in:** Replit Secrets + Vultr server `.env`
- **Admin Chat ID is public** (not sensitive)
- **Bot tokens are sensitive** - Never expose in logs or frontend

---

**Last Updated:** October 28, 2025  
**Status:** All bots verified and operational
