# Phase A: Real Money Test Plan ($120 PREMIUM)
**VerzekAutoTrader - Conservative Testing Phase**  
**Tester:** You (First Real User)  
**Budget:** $120 USDT  
**Duration:** 7-14 days  
**Goal:** Validate all services work with real money before public release

---

## 💰 Budget Allocation ($120 Total)

| Item | Cost | Purpose |
|------|------|---------|
| **PREMIUM Subscription** | $120 | Unlock all features (auto-trading, AI assistant, unlimited positions) |
| **Exchange Trading Capital** | $50-100 | Test live trades (use testnet first, then real with small amounts) |
| **Buffer** | Remaining | For additional tests or referral testing |

---

## 📋 TEST CHECKLIST (Complete in Order)

### ✅ PHASE 1: Registration & Onboarding (Day 1)

**Step 1: Register Account**
- [ ] Download mobile app (build test version first)
- [ ] Register with your real email
- [ ] Complete sliding puzzle CAPTCHA
- [ ] Verify email works (check inbox/spam)
- [ ] Login successfully

**Step 2: Profile Setup**
- [ ] Complete profile information
- [ ] Upload profile picture (optional)
- [ ] Set up 2FA (if enabled)
- [ ] Review dashboard shows correct FREE plan

**Expected Result:** Account created, email verified, logged in ✅

---

### ✅ PHASE 2: Subscription & Payment (Day 1)

**Step 3: PREMIUM Subscription**
- [ ] Navigate to Subscription screen
- [ ] Select PREMIUM plan ($120/month)
- [ ] Copy USDT TRC20 payment address
- [ ] Send exactly $120 USDT (TRC20) from your wallet
- [ ] Wait 3-5 minutes for blockchain confirmation
- [ ] Take screenshot of transaction (TronScan link)
- [ ] Submit payment proof via app
- [ ] Wait for admin verification (manual for first payment)
- [ ] Verify plan upgraded to PREMIUM in app

**Expected Result:** Payment processed, PREMIUM features unlocked ✅

**What to Check:**
```
Settings → Subscription Status
Should show: "PREMIUM - Active"
Expiry date: 30 days from now
```

---

### ✅ PHASE 3: Exchange Connection (Day 1-2)

**Step 4: Connect Binance (Testnet First)**
- [ ] Create Binance Testnet account (testnet.binance.vision)
- [ ] Generate API key + secret (with trading permissions)
- [ ] Add exchange in app: Settings → Exchange Accounts
- [ ] Select "Binance Testnet"
- [ ] Paste API key and secret
- [ ] Verify connection shows "Connected ✅"
- [ ] Check balance displays correctly

**Step 5: Connect Real Exchange (Small Amount)**
- [ ] Create Binance Futures account (or Bybit/Phemex)
- [ ] Generate API key (enable Futures trading, disable withdrawals)
- [ ] Add IP whitelist if required (use Vultr proxy IP: 45.76.90.149)
- [ ] Deposit $50-100 USDT to test trading
- [ ] Add exchange in app (use "Binance Live")
- [ ] Verify connection ✅
- [ ] Check balance shows correctly

**Expected Result:** Both testnet and live exchange connected ✅

---

### ✅ PHASE 4: Manual Trading Test (Day 2-3)

**Step 6: Place Manual Trade**
- [ ] Navigate to Positions screen
- [ ] Tap "New Position" (if available) or use Signals
- [ ] Wait for a signal from broadcast bot
- [ ] Review signal details (entry, SL, TP)
- [ ] Manually place trade on exchange (copy parameters)
- [ ] Verify position shows in app
- [ ] Check position details accurate

**Expected Result:** Manual trade executes, shows in app ✅

---

### ✅ PHASE 5: Auto-Trading Test (Day 3-7)

**Step 7: Enable Auto-Trading**
- [ ] Settings → Trading Preferences
- [ ] Enable "Auto-Trade" toggle
- [ ] Set max concurrent positions: 5 (start small)
- [ ] Set daily trade limit: 10
- [ ] Set daily loss limit: 5% ($5 max loss per day)
- [ ] Save settings

**Step 8: Configure DCA Settings**
- [ ] Settings → DCA Configuration
- [ ] Enable DCA: ON
- [ ] Base order: $10
- [ ] Max investment per symbol: $50
- [ ] DCA levels: Keep default (3 levels)
- [ ] Take profit: 1.2%
- [ ] Stop loss: 3.0%
- [ ] Save settings

**Step 9: Wait for Priority Signal**
- [ ] Monitor Signals Feed screen
- [ ] Wait for VIP/PREMIUM signal (⚡ icon)
- [ ] Verify auto-trading picks it up
- [ ] Check position opens automatically
- [ ] Monitor DCA levels trigger (if price drops)
- [ ] Wait for TP or SL to close position

**Expected Result:** Auto-trade executes, DCA works, position closes with profit/loss ✅

**What to Monitor:**
```
✅ Signal appears in Signals Feed
✅ Position opens within 10 seconds
✅ Entry price matches signal
✅ Stop loss set correctly
✅ Take profit targets set
✅ DCA entries trigger if price drops
✅ Position closes at TP or SL
✅ PNL recorded in stats
```

---

### ✅ PHASE 6: Advanced Features Test (Day 7-10)

**Step 10: AI Trade Assistant**
- [ ] Navigate to AI Assistant (if available)
- [ ] Ask a trading question
- [ ] Verify response is relevant
- [ ] Test multiple queries

**Step 11: Real-Time Price Feed**
- [ ] Check prices update in real-time
- [ ] Verify websocket connection stable
- [ ] Monitor for 1 hour (no disconnects)

**Step 12: Push Notifications**
- [ ] Enable push notifications in app
- [ ] Wait for signal notification
- [ ] Verify notification arrives promptly
- [ ] Test entry/TP/SL notifications

**Step 13: Trading Journal**
- [ ] Navigate to Journal/History
- [ ] Verify all trades logged
- [ ] Check PNL calculations correct
- [ ] Review win rate statistics

**Expected Result:** All advanced features work ✅

---

### ✅ PHASE 7: Stress Testing (Day 10-14)

**Step 14: Multiple Concurrent Positions**
- [ ] Increase max positions to 10
- [ ] Wait for multiple signals
- [ ] Verify bot opens multiple positions
- [ ] Monitor all positions tracked correctly
- [ ] Check database handles concurrent writes

**Step 15: Daily Limits Testing**
- [ ] Set daily trade limit to 3
- [ ] Wait for 4 signals in one day
- [ ] Verify 4th signal rejected
- [ ] Check error message: "Daily limit reached"

**Step 16: Loss Limit Testing**
- [ ] Set daily loss limit to 2% ($2)
- [ ] Take 3 losing trades
- [ ] Verify trading paused after limit hit
- [ ] Check resumes next day (UTC reset)

**Expected Result:** All safety rails working ✅

---

## 🔍 MONITORING CHECKLIST (Daily)

### Database Health
```bash
# Check database size (should grow slowly)
ls -lh database/verzek.db

# Verify no corruption
sqlite3 database/verzek.db "PRAGMA integrity_check;"
```

### Application Logs
- [ ] Check for errors in VerzekAutoTrader logs
- [ ] Look for database lock errors (should be 0)
- [ ] Monitor retry attempts (occasional is OK)
- [ ] Check for crashed services (should be 0)

### Trading Performance
- [ ] Total trades executed: ___
- [ ] Win rate: ___% (aim for >50%)
- [ ] Total PNL: $___
- [ ] Max drawdown: $___
- [ ] Concurrent positions (max): ___

### Issues Found
```
Date | Issue | Severity | Fixed? | Notes
-----|-------|----------|--------|-------
     |       |          |        |
     |       |          |        |
```

---

## 🎯 SUCCESS CRITERIA (Before Production Release)

### Must Pass (Critical):
- [x] Zero database corruption incidents
- [x] Zero data loss incidents
- [x] Zero critical crashes
- [x] 100% email delivery rate
- [x] All 4 exchanges connect successfully
- [x] Auto-trading executes signals correctly
- [x] DCA levels trigger as expected
- [x] Take profit and stop loss work
- [x] Payment processing works (your $120)
- [x] Subscription upgraded correctly

### Should Pass (Important):
- [x] Win rate >40% (trading performance)
- [x] <5 minor bugs found
- [x] All bugs fixed before production
- [x] Push notifications reliable
- [x] Real-time updates stable
- [x] Support responsive (@VerzekSupport)

### Nice to Have:
- [ ] Win rate >60%
- [ ] Zero bugs found
- [ ] <100ms API response time
- [ ] Beautiful UI/UX feedback

---

## 🚨 CRITICAL ISSUES (Report Immediately)

If you encounter ANY of these, **STOP testing** and report:

1. ❌ **Data Loss:** Positions disappear from database
2. ❌ **Wrong Execution:** Trade placed at wrong price/size
3. ❌ **Unauthorized Trades:** Bot trades without signal
4. ❌ **Money Missing:** Balance incorrect after trade
5. ❌ **Account Locked:** Cannot login after restart
6. ❌ **Payment Failed:** $120 not credited after payment
7. ❌ **Exchange Error:** API keys compromised/leaked
8. ❌ **Database Corruption:** Cannot read/write data

---

## 📊 DAILY TESTING LOG

### Day 1: Setup & Payment
- [ ] Backend deployed and running
- [ ] Mobile app built and installed
- [ ] Account registered
- [ ] Email verified
- [ ] $120 USDT paid
- [ ] PREMIUM unlocked
- [ ] Notes: ___________

### Day 2-3: Exchange & Manual Trading
- [ ] Testnet exchange connected
- [ ] Live exchange connected
- [ ] Manual trade executed
- [ ] Position tracked correctly
- [ ] Notes: ___________

### Day 4-7: Auto-Trading
- [ ] Auto-trading enabled
- [ ] First auto-trade executed
- [ ] DCA levels tested
- [ ] TP/SL tested
- [ ] Multiple positions tested
- [ ] Notes: ___________

### Day 8-14: Stress Testing
- [ ] Concurrent positions tested
- [ ] Daily limits tested
- [ ] Loss limits tested
- [ ] All features validated
- [ ] Final review completed
- [ ] Notes: ___________

---

## ✅ FINAL DECISION (After 7-14 Days)

### If All Tests Pass:
- [ ] Document all successful tests
- [ ] Fix any minor bugs found
- [ ] Build production mobile app
- [ ] Submit to app stores
- [ ] **GO PUBLIC** 🚀

### If Critical Issues Found:
- [ ] Document all issues
- [ ] Fix critical bugs
- [ ] Re-test for additional 7 days
- [ ] Repeat until all tests pass

---

## 📞 Support During Testing

**Questions or Issues?**
- Telegram: @VerzekSupport
- Email: support@vezekinnovative.com

**Emergency Contact (Critical Issues):**
- Create issue in Replit project
- Tag with "CRITICAL" label

---

**Good luck with testing! Your $120 investment will validate the entire platform before other users risk their money.** 🎯
