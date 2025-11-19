# Signal Closure Mechanism - Integration Guide

## 🎯 **PURPOSE**

The Signal Tracker tracks opened signals in SQLite database. To complete the performance monitoring loop, signals must be closed when they hit TP, SL, or get cancelled. This document outlines the mechanism for closing signals.

---

## 🔄 **CURRENT STATE**

### **What's Working**:
- ✅ Signals are tracked when approved by Fusion Engine
- ✅ `tracker.open_signal(candidate)` called in scheduler
- ✅ SQLite database stores ACTIVE signals
- ✅ Daily reporter queries for statistics

### **What's Missing**:
- ❌ No automatic signal closure mechanism
- ❌ `tracker.close_signal()` never called
- ❌ All signals remain ACTIVE indefinitely
- ❌ Performance statistics always return 0

---

## 📊 **CLOSURE MECHANISM OPTIONS**

### **Option 1: Backend Webhook (RECOMMENDED)**

**How it works**:
1. VerzekAutoTrader backend receives signals via `/api/house-signals/ingest`
2. Backend tracks position lifecycle (TP/SL/Cancel events)
3. Backend sends webhook to Signal Engine when position closes:
   ```
   POST http://signal-engine-host:8050/api/signals/close
   {
     "signal_id": "abc-123-def",
     "exit_price": 50200.50,
     "close_reason": "TP"  // or "SL", "CANCEL", "REVERSAL"
   }
   ```
4. Signal Engine receives webhook and calls `tracker.close_signal()`

**Pros**:
- ✅ Real-time closure based on actual trading events
- ✅ Accurate profit calculations
- ✅ Backend is source of truth for position state
- ✅ No polling required

**Cons**:
- ⚠️ Requires Signal Engine to run HTTP endpoint
- ⚠️ Network dependency (webhook delivery)

**Implementation**:
```python
# In signal_engine/api/webhooks.py (CREATE NEW FILE)
from flask import Flask, request, jsonify
from services.tracker import get_tracker

app = Flask(__name__)
tracker = get_tracker()

@app.route('/api/signals/close', methods=['POST'])
def close_signal():
    data = request.json
    signal_id = data.get('signal_id')
    exit_price = float(data.get('exit_price'))
    close_reason = data.get('close_reason')
    
    outcome = tracker.close_signal(signal_id, exit_price, close_reason)
    
    if outcome:
        return jsonify({'status': 'success', 'outcome': outcome.__dict__})
    else:
        return jsonify({'status': 'error', 'message': 'Signal not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050)
```

**Backend Integration** (VerzekAutoTrader):
```python
# In backend/trading/executor.py (MODIFY)
async def close_position(position_id, exit_price, close_reason):
    # Existing code to close position...
    
    # NEW: Send webhook to Signal Engine
    if position.signal_id:
        webhook_url = os.getenv('SIGNAL_ENGINE_WEBHOOK_URL')
        payload = {
            'signal_id': position.signal_id,
            'exit_price': exit_price,
            'close_reason': close_reason
        }
        try:
            requests.post(webhook_url, json=payload, timeout=5)
        except Exception as e:
            logger.error(f"Failed to notify Signal Engine: {e}")
```

---

### **Option 2: Polling Backend API**

**How it works**:
1. Signal Engine polls backend API every 5 minutes
2. Queries for closed positions with signal_ids
3. Calls `tracker.close_signal()` for each closure

**Pros**:
- ✅ No HTTP endpoint required on Signal Engine
- ✅ Simpler implementation

**Cons**:
- ⚠️ Delayed closure (up to 5 min lag)
- ⚠️ More network traffic
- ⚠️ Requires backend API endpoint

**Implementation**:
```python
# In signal_engine/services/scheduler.py (ADD METHOD)
async def sync_closures_task(self):
    """Poll backend for closed positions every 5 minutes"""
    while self.running:
        try:
            await asyncio.sleep(300)  # 5 minutes
            
            # Get active signals from tracker
            active_signals = self.tracker.get_active_signals()
            
            for signal in active_signals:
                # Query backend for signal status
                url = f"{backend_url}/api/positions/status/{signal['signal_id']}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data['status'] == 'CLOSED':
                        # Close signal in tracker
                        self.tracker.close_signal(
                            signal['signal_id'],
                            data['exit_price'],
                            data['close_reason']
                        )
                        
        except Exception as e:
            logger.error(f"Sync closures task error: {e}")
```

---

### **Option 3: Manual Signal Closure API**

**How it works**:
1. Signal Engine exposes REST API for manual closure
2. Admin/automated script calls API when positions close

**Pros**:
- ✅ Full control over closure timing
- ✅ Can be scripted/automated

**Cons**:
- ⚠️ Manual intervention required
- ⚠️ Not real-time

**Implementation**:
```python
# In signal_engine/api/admin.py
@app.route('/api/admin/signals/<signal_id>/close', methods=['POST'])
def admin_close_signal(signal_id):
    data = request.json
    exit_price = float(data.get('exit_price'))
    close_reason = data.get('close_reason')
    
    outcome = tracker.close_signal(signal_id, exit_price, close_reason)
    
    return jsonify({'status': 'success', 'outcome': outcome.__dict__})
```

---

## 🚀 **RECOMMENDED IMPLEMENTATION**

**Phase 1: Backend Webhook (Primary)**
- Deploy Option 1 for real-time closure
- Highest data accuracy
- Best for production

**Phase 2: Polling Backup (Fallback)**
- Add Option 2 as redundancy
- Catches any missed webhooks
- Runs every 30 minutes as safety net

**Phase 3: Manual API (Admin)**
- Add Option 3 for emergency overrides
- Useful during debugging
- Required for testing

---

## 📋 **DEPLOYMENT STEPS**

### **Step 1: Create Webhook Endpoint**

```bash
# Create new file
signal_engine/api/webhooks.py
```

### **Step 2: Run Webhook Server**

```bash
# Add to systemd or run separately
python3 signal_engine/api/webhooks.py &
```

### **Step 3: Update Backend to Send Webhooks**

Modify `backend/trading/executor.py` to send webhook on position closure.

### **Step 4: Test Integration**

```bash
# Test webhook manually
curl -X POST http://localhost:8050/api/signals/close \
  -H "Content-Type: application/json" \
  -d '{
    "signal_id": "test-123",
    "exit_price": 50200.50,
    "close_reason": "TP"
  }'
```

### **Step 5: Verify Database**

```sql
-- Check closed signals
SELECT * FROM signals WHERE status = 'CLOSED';

-- Verify daily stats
SELECT COUNT(*), AVG(profit_pct) 
FROM signals 
WHERE status = 'CLOSED' 
AND DATE(closed_at) = CURRENT_DATE;
```

---

## ⚠️ **CRITICAL NOTES**

1. **Signal IDs Must Match**:
   - Backend must store `signal_id` from Signal Engine
   - Backend must include `signal_id` in webhook payload

2. **Exit Price Accuracy**:
   - Use actual fill price, not limit price
   - Include slippage if applicable

3. **Close Reason Values**:
   - Valid values: "TP", "SL", "CANCEL", "REVERSAL"
   - Must match exactly (case-sensitive)

4. **Error Handling**:
   - If webhook fails, signal stays ACTIVE
   - Polling backup will eventually close it
   - Monitor for signals stuck in ACTIVE state

---

## 🧪 **TESTING CHECKLIST**

- [ ] Webhook endpoint responds correctly
- [ ] Backend sends webhook on TP hit
- [ ] Backend sends webhook on SL hit
- [ ] Backend sends webhook on manual cancel
- [ ] Signal is closed in tracker database
- [ ] Profit percentage calculated correctly
- [ ] Daily stats query returns accurate data
- [ ] Daily reporter generates correct report

---

## 📊 **MONITORING**

```bash
# Check active vs closed signals
sqlite3 signal_engine/data/signals.db "SELECT status, COUNT(*) FROM signals GROUP BY status"

# Recent closures
sqlite3 signal_engine/data/signals.db "SELECT * FROM signals WHERE status='CLOSED' ORDER BY closed_at DESC LIMIT 10"

# Win rate
sqlite3 signal_engine/data/signals.db "SELECT 
  COUNT(*) as total,
  SUM(CASE WHEN profit_pct > 0 THEN 1 ELSE 0 END) as winners,
  ROUND(100.0 * SUM(CASE WHEN profit_pct > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as win_rate
FROM signals WHERE status='CLOSED'"
```

---

## 🎯 **NEXT STEPS**

1. **Immediate**: Decide on closure mechanism (webhook recommended)
2. **Short-term**: Implement webhook endpoint in Signal Engine
3. **Medium-term**: Update backend to send webhooks
4. **Long-term**: Add polling backup + manual API

---

**Status**: MECHANISM DEFINED, IMPLEMENTATION PENDING  
**Priority**: HIGH (Required for production monitoring)  
**Estimated Implementation Time**: 2-4 hours
