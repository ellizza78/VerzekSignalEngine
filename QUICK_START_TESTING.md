# 🚀 Quick Start: Phase A Testing ($120 PREMIUM)

**Start Testing in 4 Simple Steps**

---

## ✅ STEP 1: Verify Backend is Live (2 minutes)

Your backend is deployed at: **https://verzek-auto-trader.replit.app**

Test it's working:

```bash
# Test 1: Health check
curl https://verzek-auto-trader.replit.app/health

# Expected: {"status":"healthy"}

# Test 2: CAPTCHA generation
curl https://verzek-auto-trader.replit.app/api/auth/captcha

# Expected: JSON with captcha data
```

**✅ If both work, proceed to Step 2**

---

## ✅ STEP 2: Build Test Mobile App (10 minutes)

```bash
# Navigate to mobile app folder
cd mobile_app/VerzekApp

# Login to Expo (if not logged in)
npx expo login

# Build preview/test version for Android
eas build --platform android --profile preview

# Or for iOS (if you have Apple Developer account)
eas build --platform ios --profile preview
```

**What happens:**
- EAS Build uploads your code to Expo servers
- Builds APK (Android) or IPA (iOS) in the cloud
- Takes ~10-15 minutes
- You'll get a download link when done

**While waiting:** Read the full test plan in `TEST_PLAN_PHASE_A.md`

---

## ✅ STEP 3: Install & Test App (30 minutes)

### Download & Install
1. When build completes, EAS gives you a download link
2. Open link on your phone
3. Download APK (Android) or install via TestFlight (iOS)
4. Install the app

### First Test - Registration
1. Open VerzekApp
2. Tap "Register"
3. Complete sliding puzzle CAPTCHA
4. Enter your email + password
5. Tap "Register"
6. Check email for verification link
7. Click verification link
8. Login to app

**✅ If you can login, registration works!**

---

## ✅ STEP 4: Test $120 PREMIUM Subscription (15 minutes)

### Navigate to Subscription
1. Tap Profile → Subscription
2. Select "PREMIUM" plan
3. Review features: Auto-trading, AI Assistant, Unlimited Positions
4. Tap "Subscribe"

### Make Payment
5. Copy USDT TRC20 address shown
6. Open your crypto wallet (TronLink, Trust Wallet, etc.)
7. Send **exactly $120 USDT** (TRC20 network)
8. Wait for blockchain confirmation (3-5 minutes)
9. Copy transaction hash from TronScan
10. Return to app → Submit payment proof
11. Wait for admin verification (I'll approve manually)

### Verify Upgrade
12. Refresh app
13. Check Profile → Subscription shows "PREMIUM"
14. Verify expiry date is 30 days from now
15. Check all PREMIUM features unlocked

**✅ If plan shows PREMIUM, payment system works!**

---

## 🎯 WHAT TO TEST NEXT (7-14 Days)

### Priority 1: Exchange Connection (Day 1-2)
- [ ] Connect Binance Testnet (free)
- [ ] Connect Binance/Bybit Live ($50-100)
- [ ] Verify balances show correctly

### Priority 2: Auto-Trading (Day 3-7)
- [ ] Enable auto-trading in settings
- [ ] Configure DCA (base: $10, max: $50)
- [ ] Wait for VIP signal
- [ ] Verify trade executes automatically
- [ ] Monitor DCA levels
- [ ] Test TP/SL execution

### Priority 3: Stress Testing (Day 7-14)
- [ ] Test multiple concurrent positions (5-10)
- [ ] Test daily trade limits
- [ ] Test daily loss limits
- [ ] Verify all safety rails work

**Full checklist:** See `TEST_PLAN_PHASE_A.md`

---

## 📊 Daily Monitoring

### Backend Health
```bash
# Check backend is running
curl https://verzek-auto-trader.replit.app/health

# Check database size
ls -lh database/verzek.db
```

### App Performance
- Open positions tracked: ___
- Trades executed today: ___
- Win rate: ___% 
- Total PNL: $___
- Issues found: ___

---

## 🚨 Emergency Stop

If you see ANY critical issue:
1. ❌ Disable auto-trading immediately (Settings → Auto-Trade OFF)
2. ❌ Close all open positions manually on exchange
3. ❌ Report issue to @VerzekSupport
4. ❌ Wait for fix before resuming

**Critical Issues:**
- Data loss (positions disappear)
- Wrong execution (trade at wrong price)
- Unauthorized trades (bot trades without signal)
- Money missing (balance incorrect)

---

## ✅ Success Criteria

**After 7-14 days, if:**
- ✅ No critical bugs found
- ✅ Auto-trading works reliably
- ✅ DCA executes correctly
- ✅ All payments processed
- ✅ Database stable (no corruption)

**Then:** Build production app and GO PUBLIC! 🚀

---

## 📞 Support

**Questions during testing?**
- Telegram: @VerzekSupport
- Email: support@vezekinnovative.com

**Your feedback shapes the final product!** 🎯
