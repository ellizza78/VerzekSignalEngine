# 🚀 PRODUCTION DEPLOYMENT GUIDE
**VerzekAutoTrader - Production Operations Manual**

---

## 📋 QUICK STATUS CHECK

### Current Production Status
- **Server:** Vultr 80.240.29.142:8050
- **Database:** PostgreSQL (verzek_db) - LIVE
- **Trading Mode:** PAPER (simulation)
- **Auto-Trading:** Disabled (0 users enabled)
- **Daily Reports:** Not scheduled
- **Worker Service:** ✅ RUNNING

---

## 🔧 DEPLOYMENT TASKS

### 1️⃣ Deploy Daily Report System

**Purpose:** Send trading summary to Telegram at 9 AM UTC daily

**Command:**
```bash
./vultr_infrastructure/deploy_daily_report.sh
```

**What it does:**
- Installs systemd timer (verzek_daily_report.timer)
- Schedules daily execution at 9:00 AM UTC
- Broadcasts report to VIP + TRIAL Telegram groups
- Sends summary to mobile app

**Verify deployment:**
```bash
ssh root@80.240.29.142 "systemctl list-timers verzek_daily_report.timer"
```

**Manual test run:**
```bash
ssh root@80.240.29.142 "systemctl start verzek_daily_report.service"
ssh root@80.240.29.142 "journalctl -u verzek_daily_report.service -n 50"
```

---

### 2️⃣ Enable Auto-Trading for Premium Users

**Purpose:** Allow PREMIUM/VIP users to auto-trade signals

**Command:**
```bash
./vultr_infrastructure/enable_auto_trading.sh
```

**Interactive Menu:**
```
1) Enable auto-trading for specific user (by email)
2) Enable auto-trading for all PREMIUM users
3) Disable auto-trading for specific user (by email)
4) List all users with auto-trading enabled
5) Check auto-trading status for user (by email)
```

**Requirements for Auto-Trading:**
- ✅ Subscription tier: VIP or PREMIUM
- ✅ Email verified: `is_verified = true`
- ✅ Exchange account connected
- ✅ Sufficient balance on exchange
- ✅ `auto_trade_enabled = true` (set via script)

**Example Usage:**
```bash
# Check specific user status
./vultr_infrastructure/enable_auto_trading.sh
# Select: 5
# Enter email: user@example.com

# Enable for specific user
./vultr_infrastructure/enable_auto_trading.sh
# Select: 1
# Enter email: user@example.com

# List all enabled users
./vultr_infrastructure/enable_auto_trading.sh
# Select: 4
```

---

### 3️⃣ Switch to LIVE TRADING MODE

**⚠️ CRITICAL: This enables REAL MONEY trading!**

**Pre-Flight Checklist:**
- [ ] Daily reports deployed and tested
- [ ] At least 1 premium user enabled for auto-trading
- [ ] Premium user has exchange account connected
- [ ] Premium user has verified sufficient exchange balance
- [ ] House signals monitoring confirmed working (5 positions tracked)
- [ ] Worker service running smoothly (no errors in logs)
- [ ] Telegram broadcasting tested
- [ ] Mobile app tested end-to-end

**Command:**
```bash
./vultr_infrastructure/switch_to_live_trading.sh
```

**Confirmation required:** Type `ENABLE LIVE TRADING` to proceed

**What it changes:**
```bash
LIVE_TRADING_ENABLED=false  →  true
EXCHANGE_MODE=paper         →  live
USE_TESTNET=true            →  false
```

**Verify mode:**
```bash
ssh root@80.240.29.142 "grep -E 'LIVE_TRADING|EXCHANGE_MODE|USE_TESTNET' /root/VerzekBackend/.env"
```

---

### 4️⃣ Switch BACK to Paper Trading (If Needed)

**Purpose:** Revert to simulation mode

**Command:**
```bash
./vultr_infrastructure/switch_to_paper_trading.sh
```

**Use cases:**
- Testing new features
- Debugging issues
- System maintenance
- Emergency stop

---

## 🚨 EMERGENCY PROCEDURES

### Emergency Stop (IMMEDIATE)

**Stop all trading instantly:**
```bash
ssh root@80.240.29.142 'echo "EMERGENCY_STOP=true" >> /root/VerzekBackend/.env && systemctl restart verzek_worker.service'
```

**Verify stopped:**
```bash
ssh root@80.240.29.142 "grep EMERGENCY_STOP /root/VerzekBackend/.env"
```

**Resume trading:**
```bash
ssh root@80.240.29.142 'sed -i "s/EMERGENCY_STOP=true/EMERGENCY_STOP=false/" /root/VerzekBackend/.env && systemctl restart verzek_worker.service'
```

---

## 📊 MONITORING & LOGS

### Check Worker Status
```bash
ssh root@80.240.29.142 "systemctl status verzek_worker.service"
```

### View Worker Logs (Real-time)
```bash
ssh root@80.240.29.142 "journalctl -u verzek_worker.service -f"
```

### View API Server Logs
```bash
ssh root@80.240.29.142 "journalctl -u verzek_api.service -f"
```

### Check Daily Report Timer
```bash
ssh root@80.240.29.142 "systemctl list-timers verzek_daily_report.timer"
```

### Database Query (Position Monitoring)
```bash
ssh root@80.240.29.142 'psql -U verzek_user -d verzek_db -c "SELECT id, signal_id, symbol, status, entry_price, pnl_pct FROM house_signal_positions ORDER BY id DESC LIMIT 10;"'
```

### Check Auto-Trading Users
```bash
ssh root@80.240.29.142 'psql -U verzek_user -d verzek_db -c "SELECT email, subscription_tier, auto_trade_enabled, capital_usdt FROM users WHERE auto_trade_enabled = true;"'
```

---

## 🔐 SECURITY CHECKLIST

### Before Going Live:
- [ ] All API keys encrypted in database (Fernet AES-128)
- [ ] JWT tokens working correctly
- [ ] Email verification enforced
- [ ] CAPTCHA active on login/register
- [ ] Admin endpoints protected
- [ ] Environment variables secured (no hard-coded secrets)
- [ ] Database backups configured
- [ ] SSL/TLS certificates valid

---

## 📱 MOBILE APP BUILD

### Production APK Build

**Command (from Replit):**
```bash
cd mobile_app/VerzekApp
eas build --platform android --profile production
```

**OTA Update (JavaScript changes only):**
```bash
cd mobile_app/VerzekApp
eas update --branch production --message "Update description"
```

**When to rebuild vs OTA:**
- **Rebuild APK:** Native changes, new packages, SDK updates
- **OTA Update:** JavaScript/React changes, UI updates, bug fixes

---

## 📈 PERFORMANCE METRICS

### Key Metrics to Monitor:
1. **Active Users:** Users with auto-trading enabled
2. **Position Count:** Open positions across all users
3. **Win Rate:** Closed positions with profit
4. **Daily PnL:** Total profit/loss per day
5. **API Response Time:** Average request latency
6. **Worker Health:** Uptime percentage
7. **Telegram Broadcasting:** Message delivery rate
8. **Email Delivery:** Verification/reset email success rate

### Database Performance:
```bash
ssh root@80.240.29.142 'psql -U verzek_user -d verzek_db -c "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'"'.'"'||tablename)) AS size FROM pg_tables WHERE schemaname = '"'public'"' ORDER BY pg_total_relation_size(schemaname||'"'.'"'||tablename) DESC;"'
```

---

## 🎯 DEPLOYMENT SEQUENCE

**Recommended order for going live:**

```
1. Deploy Daily Reports
   └─ ./vultr_infrastructure/deploy_daily_report.sh
   └─ Test: systemctl start verzek_daily_report.service

2. Enable Auto-Trading for Test User
   └─ ./vultr_infrastructure/enable_auto_trading.sh
   └─ Verify user has exchange account + balance

3. Monitor Paper Trading (24-48 hours)
   └─ Watch logs: journalctl -u verzek_worker.service -f
   └─ Check positions: SELECT * FROM house_signal_positions;
   └─ Verify Telegram broadcasts

4. Switch to Live Trading
   └─ ./vultr_infrastructure/switch_to_live_trading.sh
   └─ Monitor closely for 24 hours

5. Gradually Enable More Users
   └─ Add 1-2 users per day
   └─ Monitor each user's performance
   └─ Ensure no issues before scaling
```

---

## 📞 SUPPORT CONTACTS

**Telegram Groups:**
- VIP Signals: VERZEK SUBSCRIBERS
- Trial Signals: VERZEK TRIAL SIGNALS
- Admin Alerts: Configured in ADMIN_CHAT_ID

**Email:**
- Support: support@verzekinnovative.com
- Admin: Configured in ADMIN_EMAIL

---

## 🔄 BACKUP & RECOVERY

### Database Backup
```bash
ssh root@80.240.29.142 "pg_dump -U verzek_user verzek_db > /root/backups/verzek_db_$(date +%Y%m%d_%H%M%S).sql"
```

### Download Backup to Local
```bash
scp -i ~/.ssh/vultr_verzek root@80.240.29.142:/root/backups/verzek_db_*.sql ./backups/
```

### Restore Database
```bash
ssh root@80.240.29.142 "psql -U verzek_user -d verzek_db < /root/backups/verzek_db_TIMESTAMP.sql"
```

---

## ✅ POST-DEPLOYMENT CHECKLIST

After deploying to production:

- [ ] Daily report timer running
- [ ] Worker service healthy (no errors)
- [ ] API server responding (port 8050)
- [ ] Database connections stable
- [ ] Telegram broadcasting working
- [ ] Email delivery working
- [ ] Position monitoring active
- [ ] Auto-trading users configured
- [ ] Mobile app connecting to API
- [ ] Push notifications working
- [ ] Logs clean (no critical errors)
- [ ] Trading mode confirmed (paper/live)

---

**System Ready for Production! 🚀**
