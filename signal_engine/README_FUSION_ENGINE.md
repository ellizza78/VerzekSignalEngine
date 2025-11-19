# VerzekSignalEngine v2.0 - Master Fusion Engine

## 🎯 Overview

The Master Fusion Engine upgrade transforms VerzekSignalEngine from 4 independent bots into an intelligent, coordinated signal generation system. All signals now pass through a central fusion engine that applies sophisticated filtering, cooldown management, and trend-aware decision making.

---

## ✅ **COMPLETED IMPLEMENTATION** (November 19, 2025)

### **Phase 1: SSH Automation ✅**
- Created SSH keypair: `~/.ssh/agent_key`
- Configured SSH config file with `verzek_vultr` host
- **Action Required**: Add public key to Vultr server

### **Phase 2: Core Models ✅**
**File**: `signal_engine/core/models.py`

- `SignalCandidate` dataclass - Standardized format for all bot signals
- `SignalOutcome` dataclass - Track closed signals with profit/loss
- UUID-based signal IDs
- Telegram message formatting
- Profit percentage calculations

### **Phase 3: Fusion Engine ✅**
**File**: `signal_engine/core/fusion_engine.py`

**FusionEngineBalanced** class implements:
- ✅ Cooldown enforcement (same: 10m, opposite: 20m)
- ✅ Trend bias filtering (follows Trend Bot direction)
- ✅ Reversal confidence threshold (90%)
- ✅ Rate limiting (12/hour global, 4/hour per symbol)
- ✅ Opposite signal blocking (Balanced Mode - Option A)
- ✅ Bot priority weighting (TREND > AI_ML > SCALPING > QFL)
- ✅ Comprehensive statistics and logging

### **Phase 4: Bot Updates ✅**
**Updated Files**:
- `signal_engine/engine/base_strategy.py` - Added `SignalCandidate` support
- `signal_engine/bots/scalper/scalping_bot.py` - Returns `SignalCandidate`
- `signal_engine/bots/trend/trend_bot.py` - Returns `SignalCandidate`
- `signal_engine/bots/qfl/qfl_bot.py` - Returns `SignalCandidate`
- `signal_engine/bots/ai_ml/ai_bot.py` - Returns `SignalCandidate`

All bots now use `create_signal_candidate()` helper method with appropriate TP/SL percentages.

---

## 🔄 **REMAINING WORK**

### **Phase 5: Wire Fusion Engine into Scheduler**
**File to Update**: `signal_engine/services/scheduler.py`

**Required Changes**:
```python
from core.fusion_engine import FusionEngineBalanced

class BotScheduler:
    def __init__(self):
        # ... existing init ...
        self.fusion_engine = FusionEngineBalanced(self.config['master_engine'])
    
    async def run_cycle(self):
        # Collect candidates from all bots
        raw_candidates = []
        raw_candidates.extend(await self.scalping_bot.generate_signals(symbols))
        raw_candidates.extend(await self.trend_bot.generate_signals(symbols))
        raw_candidates.extend(await self.qfl_bot.generate_signals(symbols))
        raw_candidates.extend(await self.ai_bot.generate_signals(symbols))
        
        # Update trend bias
        for c in raw_candidates:
            if c.bot_source == "TREND":
                self.fusion_engine.update_trend_bias(c.symbol, c.side)
        
        # Process through fusion engine
        approved = self.fusion_engine.process_candidates(raw_candidates)
        
        # Dispatch approved signals
        if approved:
            await self.dispatcher.send_signals(approved)
```

### **Phase 6: Update Dispatcher**
**File to Update**: `signal_engine/services/dispatcher.py`

**Required Changes**:
```python
async def send_signals(self, candidates: List[SignalCandidate]):
    for candidate in candidates:
        # Send to backend
        await self._send_to_backend(candidate)
        
        # Broadcast to Telegram
        await self._broadcast_to_telegram(candidate)
        
        # Track signal (Phase 8)
        # tracker.open_signal(candidate)
```

### **Phase 7: Extend Configuration**
**File to Update**: `signal_engine/config/engine_settings.json`

**Add**:
```json
{
  "master_engine": {
    "mode": "BALANCED",
    "cooldown_same_direction_minutes": 10,
    "cooldown_opposite_direction_minutes": 20,
    "reversal_min_confidence": 90,
    "very_strong_confidence": 92,
    "max_signals_per_hour_per_symbol": 4,
    "max_signals_per_hour_global": 12
  }
}
```

### **Phase 8: Signal Tracking**
**File to Create**: `signal_engine/services/tracker.py`

**Requirements**:
- SQLite database for signal tracking
- `open_signal(candidate: SignalCandidate)` - Record opened signals
- `close_signal(signal_id, exit_price, close_reason)` - Record closures, return `SignalOutcome`
- Calculate profit percentages: `(exit - entry) / entry * 100` (adjust for SHORT)
- Store in SQLite: `signals.db`

### **Phase 9: Daily Reporter**
**File to Create**: `signal_engine/services/daily_reporter.py`

**Requirements**:
- Query tracker for daily statistics
- Calculate:
  - Total signals
  - TP/SL/Cancel counts
  - Win rate percentage
  - Average profit
  - Best/worst trade
  - Average duration
- Send daily report to VIP Telegram group
- Schedule in scheduler (once per day)

### **Phase 10: Deployment & Testing**
- Run `signal_engine/QUICK_DEPLOY.sh`
- Test SSH connection to Vultr
- Deploy updated code
- Restart verzek-signalengine service
- Monitor logs for errors
- Verify fusion engine statistics

---

## 📊 **HOW IT WORKS**

### **Signal Flow**

```
┌─────────────────────────────────────────────────────────┐
│              4 Independent Bots                         │
│   Scalping │ Trend │ QFL │ AI/ML                       │
└──────┬──────────┬────────┬──────────┬──────────────────┘
       │          │        │          │
       └──────────┴────────┴──────────┘
                  │
                  ▼
       ┌──────────────────────┐
       │  Fusion Engine       │
       │  (Balanced Mode)     │
       └──────────┬───────────┘
                  │
       ┌──────────┴───────────┐
       │   Apply Filters:     │
       │  - Rate Limits       │
       │  - Cooldowns         │
       │  - Trend Bias        │
       │  - Opposite Block    │
       │  - Select Best       │
       └──────────┬───────────┘
                  │
                  ▼
       ┌──────────────────────┐
       │   Approved Signals   │
       └──────────┬───────────┘
                  │
       ┌──────────┴───────────┐
       ▼                      ▼
┌──────────────┐      ┌──────────────┐
│  Dispatcher  │      │  Telegram    │
│  → Backend   │      │  Broadcast   │
└──────────────┘      └──────────────┘
```

### **Fusion Engine Rules (Balanced Mode)**

1. **Rate Limiting**
   - Max 12 signals/hour globally
   - Max 4 signals/hour per symbol

2. **Cooldown Management**
   - Same direction: 10 minutes (bypass with 92%+ confidence)
   - Opposite direction: 20 minutes (strict)

3. **Trend Bias**
   - Trend Bot sets bias for each symbol
   - Counter-trend signals require 90%+ confidence

4. **Opposite Signal Blocking** (Option A - Balanced)
   - BLOCK opposite signals if active signal exists
   - ALLOW after signal closes (TP/SL/Cancel)

5. **Bot Priority** (when confidence equal)
   - TREND: 4
   - AI_ML: 3
   - SCALPING: 2
   - QFL: 1

---

## 🚀 **DEPLOYMENT**

### **Option 1: Automated Deploy Script**
```bash
cd signal_engine
./QUICK_DEPLOY.sh
```

### **Option 2: Manual Deploy**
```bash
# 1. Commit and push changes
git add -A
git commit -m "Fusion Engine v2.0 implementation"
git push origin main

# 2. Deploy to Vultr
ssh root@80.240.29.142 "cd /root/VerzekSignalEngine && git pull && systemctl restart verzek-signalengine"

# 3. Monitor logs
ssh root@80.240.29.142 "journalctl -u verzek-signalengine -f"
```

---

## 📈 **MONITORING & STATISTICS**

### **Fusion Engine Stats**
```python
stats = fusion_engine.get_stats()
# Returns:
# - total_candidates
# - approved
# - rejected_confidence
# - rejected_cooldown
# - rejected_trend
# - rejected_opposite
# - rejected_rate_limit
# - approval_rate
# - active_signals
```

### **Signal Tracking Stats** (Phase 8)
```python
tracker.get_daily_stats()
# Returns:
# - total_signals
# - tp_count
# - sl_count
# - cancel_count
# - win_rate
# - avg_profit
# - best_trade
# - worst_trade
# - avg_duration
```

---

## 🛠️ **CONFIGURATION**

### **Master Engine Config**
`signal_engine/config/engine_settings.json`

```json
{
  "master_engine": {
    "mode": "BALANCED",
    "cooldown_same_direction_minutes": 10,
    "cooldown_opposite_direction_minutes": 20,
    "reversal_min_confidence": 90,
    "very_strong_confidence": 92,
    "max_signals_per_hour_per_symbol": 4,
    "max_signals_per_hour_global": 12
  }
}
```

### **Bot-Specific TP/SL**
- **Scalping**: TP 0.8%, SL 0.5% (fast exits)
- **Trend**: TP 2-5%, SL 1-2% (larger moves)
- **QFL**: TP to base level, SL below crash (variable)
- **AI/ML**: TP 1-2%, SL 0.5-1% (ML predictions)

---

## 📝 **TESTING CHECKLIST**

- [ ] All 4 bots return SignalCandidate objects
- [ ] Fusion engine filters work correctly
- [ ] Scheduler collects and processes candidates
- [ ] Dispatcher sends approved signals
- [ ] Telegram broadcasts formatted correctly
- [ ] Backend API receives signals with metadata
- [ ] Rate limits enforced
- [ ] Cooldowns working
- [ ] Trend bias respected
- [ ] Opposite signals blocked correctly
- [ ] Statistics logging working
- [ ] Signal tracking implemented (Phase 8)
- [ ] Daily reporter implemented (Phase 9)

---

## 📚 **FILES MODIFIED/CREATED**

### **Core Infrastructure**
- `signal_engine/core/__init__.py` - Core module exports
- `signal_engine/core/models.py` - SignalCandidate, SignalOutcome
- `signal_engine/core/fusion_engine.py` - FusionEngineBalanced

### **Base Strategy**
- `signal_engine/engine/base_strategy.py` - Updated for SignalCandidate

### **Bots (All Updated)**
- `signal_engine/bots/scalper/scalping_bot.py`
- `signal_engine/bots/trend/trend_bot.py`
- `signal_engine/bots/qfl/qfl_bot.py`
- `signal_engine/bots/ai_ml/ai_bot.py`

### **Documentation**
- `signal_engine/FUSION_ENGINE_UPGRADE_PROGRESS.md`
- `signal_engine/README_FUSION_ENGINE.md` (this file)
- `signal_engine/QUICK_DEPLOY.sh`

### **To Be Modified**
- `signal_engine/services/scheduler.py` (Phase 5)
- `signal_engine/services/dispatcher.py` (Phase 6)
- `signal_engine/config/engine_settings.json` (Phase 7)

### **To Be Created**
- `signal_engine/services/tracker.py` (Phase 8)
- `signal_engine/services/daily_reporter.py` (Phase 9)

---

## 🎯 **SUCCESS CRITERIA**

✅ **Foundation Complete** (Phases 1-4):
- Core models implemented
- Fusion engine logic complete
- All bots updated to new format
- SSH automation ready

🔄 **Integration Pending** (Phases 5-7):
- Wire fusion into scheduler
- Update dispatcher
- Add master_engine config

📊 **Features Pending** (Phases 8-9):
- Signal tracking with SQLite
- Daily performance reporting

🚀 **Deployment Ready** (Phase 10):
- Deploy script created
- Documentation complete
- Testing checklist defined

---

## 📞 **SUPPORT**

For issues or questions:
1. Check `FUSION_ENGINE_UPGRADE_PROGRESS.md` for status
2. Review LSP diagnostics: `get_latest_lsp_diagnostics`
3. Test locally before deploying
4. Monitor Vultr logs: `journalctl -u verzek-signalengine -f`

---

**Version**: 2.0.0
**Status**: Foundation Complete, Integration Pending
**Last Updated**: November 19, 2025
