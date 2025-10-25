# Trade Capacity & Limits Guide
**VerzekAutoTrader - Understanding System Limits**

## 📊 Maximum Concurrent Trades

### Per-User Limits
**Default Maximum:** 50 concurrent positions per user  
**Configurable:** Yes (via API or user settings)  
**Enforcement:** Checked before every trade execution

### How It Works

#### 1. Setting the Limit
```bash
# Via API endpoint
PUT /api/users/{userId}/risk
{
  "max_concurrent_positions": 50  # Set your limit
}
```

#### 2. System Checks Before Each Trade
```python
# From dca_orchestrator.py:106
if not self.user_manager.can_open_position(user_id):
    return {"success": False, "error": "Max concurrent positions reached"}
```

#### 3. Position Counting
- Counts all OPEN positions across all exchanges
- Includes DCA positions (each DCA entry = 1 position)
- Checked in real-time before every trade

---

## 🎯 DCA Trade Multiplication

When DCA is enabled, **one signal can create multiple positions**:

### Example Scenario
**User receives 1 signal for BTC/USDT LONG:**

| Event | Positions | Total |
|-------|-----------|-------|
| Initial entry at $50,000 | 1 position ($10) | 1 |
| Price drops 1.5% → DCA Level 1 | +1 position ($10) | 2 |
| Price drops 2.0% → DCA Level 2 | +1.2x position ($12) | 3 |
| Price drops 3.0% → DCA Level 3 | +1.5x position ($15) | 4 |

**Result:** 1 signal = 4 concurrent positions (if all DCA levels triggered)

### DCA Settings (Per User)
```json
{
  "dca_settings": {
    "enabled": true,
    "base_order": 10.0,          // $10 initial order
    "max_investment": 100.0,     // $100 max per symbol
    "levels": [
      {"drop_pct": 1.5, "multiplier": 1.0},  // DCA 1
      {"drop_pct": 2.0, "multiplier": 1.2},  // DCA 2
      {"drop_pct": 3.0, "multiplier": 1.5}   // DCA 3
    ]
  }
}
```

---

## 🔥 Maximum Theoretical Trades

### Scenario: PREMIUM User with Auto-Trading

#### Assumptions:
- User has `max_concurrent_positions = 50`
- DCA enabled with 3 levels
- Receives 50 priority signals simultaneously

#### Calculation:
**Without DCA:**  
- 50 signals × 1 position = **50 positions** ✅

**With DCA (all levels triggered):**  
- 50 signals × 4 positions (1 initial + 3 DCA) = **200 positions**  
- **LIMITED to 50** by max_concurrent_positions ⚠️

#### Result:
The system will:
1. Open initial positions until limit (50) is reached
2. Reject new signals with error: "Max concurrent positions reached"
3. Allow DCA entries for existing positions (within same symbol)
4. Block new symbols once limit is hit

---

## ⚡ Signal Processing Capacity

### Unlimited Parallel Processing
- **No queue limit** - All signals processed immediately
- **Parallel execution** - Multiple users trade simultaneously
- **Per-user limits** - Each user has independent position count

### Example: 100 Users, 10 Signals Each
| Metric | Value |
|--------|-------|
| Total signals received | 1,000 |
| Processed simultaneously | 1,000 |
| Per-user limit | 50 positions |
| Total system positions | Up to 5,000 (100 users × 50) |
| Bottleneck | Exchange API rate limits |

---

## 🛡️ Safety Rails

### 1. Max Concurrent Positions
```python
# Default: 50 per user
risk_settings = {
  "max_concurrent_positions": 50
}
```

### 2. Daily Trade Count
```python
# Default: 100 trades per day
risk_settings = {
  "max_daily_trades": 100
}
```

### 3. Daily Loss Limit
```python
# Default: 10% of account balance
risk_settings = {
  "daily_loss_limit_pct": 10.0
}
```

### 4. Max Investment Per Symbol
```python
# Default: $100 per symbol
dca_settings = {
  "max_investment": 100.0
}
```

### 5. Leverage Cap
```python
# Default: 20x, max: 125x
risk_settings = {
  "leverage_cap": 20
}
```

---

## 📈 Scaling Considerations

### Database Capacity
- **SQLite with WAL mode** - Handles 1000+ writes/second
- **Concurrent connections** - Thread-safe per-service
- **Position tracking** - Indexed by user_id and status

### API Rate Limits (Exchange Bottleneck)
| Exchange | Order Limit | Weight Limit |
|----------|-------------|--------------|
| Binance | 1200/min | 2400/min |
| Bybit | 600/min | - |
| Phemex | 300/min | - |

**System is NOT the bottleneck** - Exchange APIs are.

---

## 🎛️ Configuring Limits

### Via API (Recommended)
```bash
# Update risk settings
curl -X PUT https://your-domain.com/api/users/user123/risk \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "max_concurrent_positions": 100,
    "max_daily_trades": 200,
    "daily_loss_limit_pct": 15.0,
    "leverage_cap": 50
  }'
```

### Via Mobile App
1. Navigate to **Settings** → **Risk Management**
2. Adjust sliders for:
   - Max Concurrent Positions
   - Daily Trade Limit
   - Daily Loss Limit
   - Leverage Cap

---

## 🚨 What Happens When Limits Are Reached?

### Max Concurrent Positions Exceeded
```json
{
  "success": false,
  "error": "Max concurrent positions reached"
}
```
**Action:** Close existing positions or increase limit

### Daily Trade Limit Exceeded
```json
{
  "success": false,
  "error": "Daily trading limits exceeded"
}
```
**Action:** Wait until next day (UTC reset) or increase limit

### Daily Loss Limit Hit
```json
{
  "success": false,
  "error": "Daily loss limit reached - trading paused"
}
```
**Action:** Trading auto-paused, resumes next day

---

## 💡 Best Practices

### For Conservative Traders
```json
{
  "max_concurrent_positions": 10,
  "max_daily_trades": 20,
  "daily_loss_limit_pct": 5.0,
  "leverage_cap": 10,
  "dca_settings": {
    "enabled": true,
    "base_order": 5.0,
    "max_investment": 50.0
  }
}
```

### For Aggressive Traders
```json
{
  "max_concurrent_positions": 50,
  "max_daily_trades": 200,
  "daily_loss_limit_pct": 20.0,
  "leverage_cap": 50,
  "dca_settings": {
    "enabled": true,
    "base_order": 20.0,
    "max_investment": 200.0
  }
}
```

---

## 📞 Support

**Questions about trade limits?**  
Contact @VerzekSupport on Telegram

**Need custom limits?**  
Enterprise users can request custom configurations via support.
