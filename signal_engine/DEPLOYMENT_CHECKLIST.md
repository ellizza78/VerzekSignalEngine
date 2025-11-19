# Master Fusion Engine v2.0 - Deployment Checklist

## ✅ **PRE-DEPLOYMENT CHECKS** (Complete)

- [x] Phase 1: SSH automation configured
- [x] Phase 2: Core models (SignalCandidate, SignalOutcome) created
- [x] Phase 3: FusionEngineBalanced implemented
- [x] Phase 4: All 4 bots updated to return SignalCandidate
- [x] Phase 5: Scheduler wired to fusion engine
- [x] Phase 6: Dispatcher updated for SignalCandidate support
- [x] Phase 7: master_engine config added to engine_settings.json
- [x] Phase 8: Signal tracker (SQLite) implemented
- [x] Phase 9: Daily reporter implemented
- [x] Phase 10: Integration ready for deployment

---

## 📋 **DEPLOYMENT STEPS**

### **Step 1: Authorize SSH Key on Vultr**

```bash
# On Vultr server (80.240.29.142), run as root:
cat >> /root/.ssh/authorized_keys << 'EOF'
[Copy content from ~/.ssh/agent_key.pub on Replit]
EOF
chmod 600 /root/.ssh/authorized_keys
```

### **Step 2: Test SSH Connection**

```bash
# From Replit:
ssh -i ~/.ssh/agent_key root@80.240.29.142 "echo Connection successful"
```

### **Step 3: Deploy Using Automated Script**

```bash
cd signal_engine
./QUICK_DEPLOY.sh
```

**OR Manual Deployment:**

```bash
# Commit and push
git add -A
git commit -m "Deploy Master Fusion Engine v2.0"
git push origin main

# Deploy to Vultr
ssh root@80.240.29.142 << 'ENDSSH'
  cd /root/VerzekSignalEngine
  git pull origin main
  pip3 install -r requirements.txt
  systemctl restart verzek-signalengine
  systemctl status verzek-signalengine --no-pager
ENDSSH
```

### **Step 4: Monitor Logs**

```bash
# From Vultr server:
journalctl -u verzek-signalengine -f

# Look for:
# - "Master Fusion Engine v2.0 initialized"
# - "All bots initialized"
# - "Fusion Engine approved X/Y signals"
```

### **Step 5: Verify Fusion Engine Statistics**

After 5 minutes, check logs for:
```
📊 SIGNAL ENGINE STATISTICS (Fusion Engine v2.0)
Signals Sent: X
Success Rate: Y%
─────────────────────────────────────────────
🔥 FUSION ENGINE STATISTICS
Total Candidates: X
Approved Signals: Y
Approval Rate: Z%
Rejected (Confidence): A
Rejected (Cooldown): B
Rejected (Trend Bias): C
Rejected (Opposite Signal): D
Rejected (Rate Limit): E
Active Signals: F
```

---

## 🧪 **TESTING CHECKLIST**

### **Functional Tests**

- [ ] All 4 bots start successfully
- [ ] Bots generate signal candidates
- [ ] Fusion engine receives candidates
- [ ] Rate limiting works (max 12/hour global, 4/hour per symbol)
- [ ] Cooldown enforcement works (10min same, 20min opposite)
- [ ] Trend bias filtering works
- [ ] Opposite signal blocking works (Balanced Mode)
- [ ] Signals dispatched to backend API
- [ ] Telegram broadcasts working
- [ ] Signal tracker recording opened signals
- [ ] SQLite database created at ./data/signals.db

### **Integration Tests**

- [ ] Scalping Bot (15s interval) → Fusion Engine → Dispatcher
- [ ] Trend Bot (5m interval) → Fusion Engine → Dispatcher
- [ ] QFL Bot (20s interval) → Fusion Engine → Dispatcher
- [ ] AI/ML Bot (30s interval) → Fusion Engine → Dispatcher
- [ ] Backend API receives signals with metadata
- [ ] Telegram VIP/TRIAL groups receive formatted signals

### **Performance Tests**

- [ ] 59 symbols processed across all bots
- [ ] No memory leaks after 1 hour
- [ ] No crashes or exceptions
- [ ] Statistics logging every 5 minutes
- [ ] Fusion engine approval rate 20-40% (healthy filtering)

---

## 🔍 **MONITORING**

### **Key Metrics to Track**

1. **Fusion Engine Stats** (every 5 min):
   - Total candidates generated
   - Approval rate (target: 20-40%)
   - Rejection breakdown
   - Active signals count

2. **Dispatcher Stats**:
   - Signals sent successfully
   - Failed dispatches
   - Success rate (target: >95%)

3. **Signal Tracker**:
   - Active signals count
   - Daily closed signals
   - Win rate (tracked daily)

### **Logs to Monitor**

```bash
# Fusion Engine approvals
grep "Fusion Engine approved" /var/log/syslog

# Signal dispatches
grep "Signal dispatched" /var/log/syslog

# Errors
grep "ERROR" /var/log/syslog | grep verzek

# Rejection reasons
grep "Rejected" /var/log/syslog
```

---

## 🚨 **ROLLBACK PLAN**

If critical issues occur:

### **Option 1: Revert to Previous Version**

```bash
# On Vultr:
cd /root/VerzekSignalEngine
git log --oneline -5  # Find previous commit
git reset --hard <COMMIT_HASH_BEFORE_FUSION>
systemctl restart verzek-signalengine
```

### **Option 2: Disable Fusion Engine**

Temporarily disable by modifying scheduler to bypass fusion engine (emergency only).

---

## 📊 **SUCCESS CRITERIA**

### **Deployment Successful If:**

- ✅ All 4 bots running without crashes
- ✅ Fusion engine processes candidates
- ✅ Approval rate between 20-40%
- ✅ Signals delivered to backend + Telegram
- ✅ No memory leaks or performance degradation
- ✅ Statistics logging working
- ✅ Signal tracker database created and populating

### **Expected Behavior:**

- **Scalping Bot**: Generates 3-5 candidates per cycle (15s)
- **Trend Bot**: Generates 0-2 candidates per cycle (5m)
- **QFL Bot**: Generates 0-1 candidates per cycle (20s)
- **AI/ML Bot**: Generates 0-2 candidates per cycle (30s)
- **Fusion Engine**: Approves ~25% of candidates
- **Rate Limits**: Blocks excessive signals (>12/hour globally, >4/hour per symbol)

---

## 📝 **POST-DEPLOYMENT TASKS**

1. Monitor for 24 hours
2. Review daily performance report (automated)
3. Analyze fusion engine rejection patterns
4. Tune confidence thresholds if needed
5. Adjust rate limits based on real performance
6. Update replit.md with deployment date and results

---

## 🔗 **RELATED DOCUMENTATION**

- **README_FUSION_ENGINE.md** - Technical overview
- **FUSION_ENGINE_UPGRADE_PROGRESS.md** - Implementation phases
- **IMPLEMENTATION_STATUS.md** - Architect review and status
- **QUICK_DEPLOY.sh** - Automated deployment script

---

**Deployment Date**: TBD  
**Deployed By**: Replit AI Agent  
**Version**: Master Fusion Engine v2.0  
**Status**: Ready for Deployment
