# ⚡ PRIORITY SIGNAL SYSTEM

## Overview
VerzekAutoTrader now supports **Priority Auto-Trade Signals** - special signals marked by signal providers (like Ai Golden Crypto) that bypass quality filters and get priority processing for immediate auto-trading.

## What Are Priority Signals?

Priority signals are trading signals marked with special indicators by the signal provider, such as:
- **"⚡ Setup Auto-Trade ⚡"** (green banner)
- Text containing "PRIORITY SIGNAL"
- Text containing "AUTO-TRADE SETUP"

These signals are pre-vetted by trusted signal providers and should be executed immediately without additional quality scoring.

## How It Works

### 1. **Signal Detection**
When a signal is received (from monitored channels or admin):
```
- System checks for priority keywords
- Detects: "SETUP AUTO-TRADE", "PRIORITY SIGNAL", "AUTO-TRADE SETUP"
- Marks signal with priority flag
```

### 2. **Broadcasting with Priority Indicator**
Priority signals are broadcast with a special header:

**Regular Signal:**
```
🔥 Signal Alert (Verzek Trading Signals)
━━━━━━━━━━━━━━━━━━

#WLFI/USDT LONG
Entry: 0.1304 - Stop Loss: 0.129
Targets: 0.1311 - 0.1318 - 0.1325
```

**Priority Signal:**
```
⚡ PRIORITY AUTO-TRADE SIGNAL ⚡
🔥 Signal Alert (Verzek Trading Signals)
━━━━━━━━━━━━━━━━━━

WLFI/USDT LONG
Entry: 0.1304 - Stop Loss: 0.129
Targets: 0.1311 - 0.1318 - 0.1325
```

### 3. **Auto-Trading with Priority**
When users have auto-trading enabled:

**Priority Signals:**
- ✅ **Bypass quality filter** (always trusted)
- ✅ **Immediate execution** (no quality scoring delay)
- ✅ **Logged as priority** in system logs
- ✅ **Still respect user safety settings** (leverage caps, position limits)

**Regular Signals:**
- Quality filter applies (if enabled)
- Scored based on risk/reward, targets, stop loss
- Must meet quality threshold (default 60/100)

## Priority Keywords

The system detects these keywords (case-insensitive):
```python
PRIORITY_KEYWORDS = [
    "SETUP AUTO-TRADE",
    "SETUP AUTOTRADE",
    "AUTO-TRADE SETUP",
    "AUTOTRADE SETUP",
    "PRIORITY SIGNAL",
    "HIGH PRIORITY"
]
```

## Example: Ai Golden Crypto Signal

### Signal Received:
```
#Signal #WLFI/USDT $WLFI
Long 🚀 Lev x28 #Crypto

Entry: 0.1304 - Stop Loss: 0.129

Targets: 0.1311 - 0.1318 - 0.1325 - 0.1332 - 0.1339

⚡ Setup Auto-Trade ⚡  <--- PRIORITY MARKER
```

### What Happens:
1. **Telethon Forwarder** detects priority keyword
2. **Broadcast Bot** adds priority header: `⚡ PRIORITY AUTO-TRADE SIGNAL ⚡`
3. **Broadcasts** to VIP/TRIAL groups with priority indicator
4. **DCA Orchestrator** receives signal for users with auto-trade enabled
5. **Bypasses** quality filter (trusted source)
6. **Executes** trade immediately for all auto-trade users
7. **Logs**: `⚡ PRIORITY signal for WLFIUSDT - bypassing quality filter`

## Technical Implementation

### Files Modified:
1. **broadcast_bot_webhook_handler.py**
   - Added `is_priority_signal()` function
   - Modified `broadcast_admin_message()` to detect priority
   - Modified `auto_forward_signal()` to detect priority
   - Added priority header formatting

2. **modules/dca_orchestrator.py**
   - Added `is_priority` parameter to `execute_signal()`
   - Priority signals bypass quality filter
   - Logged as priority execution

3. **modules/priority_signal_queue.py** (NEW)
   - Queue system for managing signals
   - Priority queue + regular queue
   - Persistent storage in `database/signal_queue.json`

### Priority Signal Flow:
```
Channel/Admin → Telegram
       ↓
Telethon Forwarder (detects "Setup Auto-Trade")
       ↓
Broadcast Bot (adds ⚡ PRIORITY header)
       ↓
VIP/TRIAL Groups
       ↓
DCA Orchestrator (bypasses quality filter)
       ↓
Exchange Execution (immediate)
```

## User Benefits

### For VIP Users:
- ✅ See priority signals clearly marked
- ✅ Know which signals are pre-vetted by providers
- ✅ Faster execution for trusted signals
- ✅ No quality filter delays

### For Signal Providers:
- ✅ Can mark high-confidence signals
- ✅ Users get immediate execution
- ✅ Better tracking of priority trades
- ✅ Clear visual distinction

## Safety Considerations

**Priority signals STILL respect:**
- ✅ Kill Switch (if activated)
- ✅ Circuit Breaker thresholds
- ✅ Trading pause status
- ✅ User leverage caps
- ✅ Max concurrent positions
- ✅ Daily trading limits
- ✅ Symbol whitelist/blacklist

**Priority signals BYPASS:**
- ❌ Quality scoring filter
- ❌ Risk/reward ratio checks
- ❌ Signal clarity scoring

## Configuration

### Enable/Disable for Users:
Users can still control auto-trading via their settings:
```json
{
  "dca_settings": {
    "enabled": true  // Must be true for ANY auto-trading
  },
  "strategy_settings": {
    "signal_quality_filter": true,  // Priority signals bypass this
    "signal_quality_threshold": 60.0  // Ignored for priority signals
  }
}
```

### Adding More Priority Keywords:
Edit `broadcast_bot_webhook_handler.py`, line 83-90:
```python
priority_keywords = [
    "SETUP AUTO-TRADE",
    "YOUR NEW KEYWORD",  # Add here
]
```

## Logs & Monitoring

### Priority Signal Logs:
```
[BROADCAST] ⚡ Broadcasting PRIORITY signal
[BROADCAST] ⚡ Auto-forwarding PRIORITY signal from Ai Golden Crypto
[ORCHESTRATOR] ⚡ PRIORITY signal for WLFIUSDT - bypassing quality filter
```

### Regular Signal Logs:
```
[BROADCAST] 📡 Auto-forwarded signal from Ai Golden Crypto
[ORCHESTRATOR] Signal quality check passed for BTCUSDT: 75.0/100
```

## API Integration (Future)

Priority signal queue can be accessed via API:
```python
from modules.priority_signal_queue import PrioritySignalQueue

queue = PrioritySignalQueue()

# Add priority signal
queue.add_signal({
    "symbol": "BTCUSDT",
    "side": "LONG",
    "entry_price": 50000
}, is_priority=True)

# Get stats
stats = queue.get_queue_stats()
# {'priority_count': 5, 'regular_count': 12, 'total_count': 17}

# Process next (priority first)
signal = queue.get_next_signal()
```

## Testing

### Test Priority Signal:
1. Send message to monitored channel: "BTCUSDT LONG Entry: 50000 ⚡ Setup Auto-Trade ⚡"
2. Check broadcast includes: `⚡ PRIORITY AUTO-TRADE SIGNAL ⚡`
3. Check logs for: `⚡ PRIORITY signal for BTCUSDT - bypassing quality filter`
4. Verify immediate execution (no quality delay)

### Test Regular Signal:
1. Send message: "BTCUSDT LONG Entry: 50000"
2. Check broadcast has regular header only
3. Check logs for: `Signal quality check passed for BTCUSDT: XX.X/100`

## Summary

✅ **What's New:**
- Priority signal detection system
- Visual indicators in broadcasts
- Quality filter bypass for priority signals
- Immediate execution for trusted signals

✅ **What Stays the Same:**
- All safety controls still apply
- User must enable auto-trading
- Regular signals still use quality filter
- Manual trading unaffected

✅ **Benefits:**
- Faster execution for pre-vetted signals
- Clear visual distinction for users
- Provider flexibility to mark high-confidence trades
- Maintains all safety protections

---

**Version:** 1.0  
**Last Updated:** October 18, 2025  
**Status:** ✅ Ready for Production (after session recovery)
