# VerzekSignalEngine v2.0 - Production Runbook

## 🎯 **PURPOSE**

Operational guide for running, monitoring, and troubleshooting the Master Fusion Engine v2.0 in production.

---

## 📋 **PRE-DEPLOYMENT CHECKLIST**

### **Environment Variables**
```bash
# Required for Signal Engine
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_VIP_CHAT_ID="your_vip_chat_id"
export TELEGRAM_TRIAL_CHAT_ID="your_trial_chat_id"
export TELEGRAM_ADMIN_CHAT_ID="your_admin_chat_id"

# Required for Backend
export SIGNAL_ENGINE_WEBHOOK_URL="http://signal-engine-host:8050"
export DATABASE_URL="postgresql://user:pass@host:port/db"
```

### **Python Dependencies**
```bash
cd signal_engine
pip install -r requirements.txt
```

### **Database Setup**
```bash
# Signal Tracker creates SQLite database automatically
# Verify directory exists
mkdir -p signal_engine/data
ls -la signal_engine/data/signals.db  # Should exist after first run
```

### **Watchlist Configuration**
```bash
# Verify watchlist.json has 59 symbols
cat signal_engine/config/watchlist.json | jq '.futures | length'
# Should output: 59
```

---

## 🚀 **DEPLOYMENT**

### **1. Start Webhook Server First**
```bash
cd signal_engine/api
python3 webhooks.py &

# Verify webhook server is running
curl http://localhost:8050/health
# Expected: {"status": "healthy", ...}
```

### **2. Start Signal Engine Scheduler**
```bash
cd signal_engine
python3 main.py &

# Monitor startup logs
tail -f logs/signal_engine.log
```

### **3. Verify Backend Integration**
```bash
# Check backend worker is running
ps aux | grep worker.py

# Verify webhook URL is configured
echo $SIGNAL_ENGINE_WEBHOOK_URL
```

### **4. Test Signal Flow**
```bash
# Monitor live signals
tail -f signal_engine/logs/signals.log

# Check SQLite database
sqlite3 signal_engine/data/signals.db "SELECT COUNT(*) FROM signals WHERE status='ACTIVE'"
```

---

## 📊 **MONITORING**

### **Health Checks**

```bash
# Webhook server health
curl http://localhost:8050/health

# Signal statistics
curl http://localhost:8050/api/signals/stats

# Tracker database health
sqlite3 signal_engine/data/signals.db "SELECT 
  status, 
  COUNT(*) as count 
FROM signals 
GROUP BY status"
```

### **Key Metrics to Monitor**

| Metric | Command | Normal Range | Alert If |
|--------|---------|--------------|----------|
| Active Signals | `SELECT COUNT(*) FROM signals WHERE status='ACTIVE'` | 10-50 | >100 or stuck |
| Closed Signals (24h) | `SELECT COUNT(*) FROM signals WHERE status='CLOSED' AND DATE(closed_at) = CURRENT_DATE` | 20-150 | <5 or >500 |
| Win Rate (24h) | See query below | 55-75% | <40% or >90% |
| Avg Duration | `SELECT AVG(duration_seconds)/60 FROM signals WHERE status='CLOSED' AND DATE(closed_at) = CURRENT_DATE` | 30-180 min | >360 min |

**Win Rate Query**:
```sql
SELECT 
  ROUND(100.0 * SUM(CASE WHEN profit_pct > 0 THEN 1 ELSE 0 END) / COUNT(*), 2) as win_rate
FROM signals 
WHERE status='CLOSED' 
AND DATE(closed_at) = CURRENT_DATE;
```

### **Log Files**

```bash
# Signal Engine logs
tail -f signal_engine/logs/signal_engine.log

# Webhook server logs
tail -f signal_engine/logs/webhooks.log

# Backend worker logs
tail -f backend/logs/worker.log

# Fusion Engine statistics (every 5 min)
grep "FUSION ENGINE STATISTICS" signal_engine/logs/signal_engine.log | tail -20
```

---

## ⚠️ **COMMON ISSUES & TROUBLESHOOTING**

### **Issue 1: Signals Not Closing (Stuck ACTIVE)**

**Symptoms**:
- Active signal count keeps growing
- No closed signals in last 24 hours
- Win rate shows 0%

**Root Cause**: Backend webhook not reaching Signal Engine

**Diagnosis**:
```bash
# Check webhook server is running
curl http://localhost:8050/health

# Check backend logs for webhook errors
grep "Signal Engine webhook" backend/logs/worker.log | tail -20

# Test webhook manually
curl -X POST http://localhost:8050/api/signals/close \
  -H "Content-Type: application/json" \
  -d '{"signal_id": "test-123", "exit_price": 50000, "close_reason": "TP"}'
```

**Resolution**:
1. Restart webhook server: `python3 signal_engine/api/webhooks.py &`
2. Verify SIGNAL_ENGINE_WEBHOOK_URL in backend environment
3. Check firewall rules allow backend → webhook server connection
4. If many stuck signals, use manual closure (see Manual Operations)

---

### **Issue 2: Tracker Database Errors**

**Symptoms**:
- "Failed to track signal" errors in logs
- SQLite database locked errors
- Signals not appearing in database

**Diagnosis**:
```bash
# Check database file permissions
ls -la signal_engine/data/signals.db

# Check for database locks
lsof signal_engine/data/signals.db

# Verify table structure
sqlite3 signal_engine/data/signals.db ".schema signals"
```

**Resolution**:
```bash
# If database corrupted, backup and recreate
mv signal_engine/data/signals.db signal_engine/data/signals.db.backup
python3 -c "from services.tracker import SignalTracker; SignalTracker()"

# Fix permissions
chmod 664 signal_engine/data/signals.db
chown signal-engine-user:signal-engine-user signal_engine/data/signals.db
```

---

### **Issue 3: Fusion Engine Rejecting All Signals**

**Symptoms**:
- Approval rate < 10%
- "Rejected (Rate Limit)" or "Rejected (Cooldown)" in logs
- No signals dispatched for hours

**Diagnosis**:
```bash
# Check Fusion Engine stats
grep "FUSION ENGINE STATISTICS" signal_engine/logs/signal_engine.log | tail -5

# Check rejection reasons
grep "Rejected:" signal_engine/logs/signal_engine.log | tail -50
```

**Resolution**:
1. **Rate Limit Hit**: Normal if market is choppy. Wait 1 hour for cooldown reset.
2. **Trend Bias Blocking**: Check if Trend Bot is running
3. **Opposite Signal Blocking**: Expected behavior in Balanced Mode

**Temporary Override** (Emergency Only):
```bash
# Edit config temporarily
vim signal_engine/config/engine_settings.json

# Increase rate limits
"max_signals_per_hour": 20,  # from 12
"max_signals_per_symbol_per_hour": 6,  # from 4

# Restart signal engine
pkill -f "python3 main.py"
python3 signal_engine/main.py &
```

---

### **Issue 4: Dispatcher Failures (Signals Not Sent to Backend)**

**Symptoms**:
- "Failed to dispatch signal" in logs
- Signals tracked in DB but not appearing in backend
- Success rate < 80%

**Diagnosis**:
```bash
# Check dispatcher stats
grep "Signals Sent:" signal_engine/logs/signal_engine.log | tail -10

# Check backend API health
curl http://backend-host:8000/health

# Test manual dispatch
curl -X POST http://backend-host:8000/api/house-signals/ingest \
  -H "Content-Type: application/json" \
  -H "X-House-Engine-Token: $HOUSE_ENGINE_TOKEN" \
  -d '{"symbol": "BTCUSDT", "side": "LONG", ...}'
```

**Resolution**:
1. Verify HOUSE_ENGINE_TOKEN is correct
2. Check backend API is running and accessible
3. Verify network connectivity between signal engine and backend
4. Check backend logs for rejection reasons

---

### **Issue 5: Telegram Broadcasting Failures**

**Symptoms**:
- "Telegram broadcast failed" in logs
- VIP/Trial groups not receiving signals
- Messages sent count = 0

**Diagnosis**:
```bash
# Check broadcaster stats
grep "Telegram Messages:" signal_engine/logs/signal_engine.log | tail -10

# Verify bot token
echo $TELEGRAM_BOT_TOKEN

# Test manual broadcast
python3 -c "
from services.telegram_broadcaster import get_broadcaster
import asyncio
async def test():
    b = get_broadcaster()
    await b.broadcast_signal('TEST MESSAGE', ['admin'])
asyncio.run(test())
"
```

**Resolution**:
1. Verify TELEGRAM_BOT_TOKEN is valid
2. Check bot has permission to post in VIP/TRIAL groups
3. Verify TELEGRAM_VIP_CHAT_ID and TELEGRAM_TRIAL_CHAT_ID are correct
4. Test with admin group first

---

## 🔧 **MANUAL OPERATIONS**

### **Close Stuck Signal Manually**

```bash
# Method 1: Via webhook API
curl -X POST http://localhost:8050/api/signals/close \
  -H "Content-Type: application/json" \
  -d '{
    "signal_id": "abc-123-def",
    "exit_price": 50200.50,
    "close_reason": "TP"
  }'

# Method 2: Direct SQL
sqlite3 signal_engine/data/signals.db "
UPDATE signals SET
  closed_at = datetime('now'),
  exit_price = 50200.50,
  profit_pct = 2.5,
  duration_seconds = 3600,
  close_reason = 'MANUAL',
  status = 'CLOSED'
WHERE signal_id = 'abc-123-def';
"
```

### **Clear Old Signals (Cleanup)**

```bash
# Archive signals older than 30 days
sqlite3 signal_engine/data/signals.db "
INSERT INTO signals_archive SELECT * FROM signals WHERE DATE(closed_at) < DATE('now', '-30 days');
DELETE FROM signals WHERE DATE(closed_at) < DATE('now', '-30 days');
VACUUM;
"
```

### **Reset Fusion Engine Cooldowns (Emergency)**

```bash
# Stop signal engine
pkill -f "python3 main.py"

# Clear cooldown state (if using Redis/file cache)
rm -f signal_engine/data/cooldowns.json

# Restart
python3 signal_engine/main.py &
```

### **Force Close All Active Signals**

```bash
# Use with caution - only during emergency shutdown
sqlite3 signal_engine/data/signals.db "
UPDATE signals SET
  status = 'CLOSED',
  closed_at = datetime('now'),
  close_reason = 'EMERGENCY_STOP'
WHERE status = 'ACTIVE';
"
```

---

## 📈 **PERFORMANCE OPTIMIZATION**

### **Database Optimization**

```sql
-- Run daily vacuum
VACUUM;

-- Rebuild indices
REINDEX;

-- Analyze for query optimization
ANALYZE;
```

### **Log Rotation**

```bash
# Add to crontab
0 0 * * * find /path/to/signal_engine/logs -name "*.log" -mtime +7 -delete
```

### **Resource Monitoring**

```bash
# CPU usage
top -p $(pgrep -f "python3 main.py")

# Memory usage
ps aux | grep "main.py" | awk '{print $6/1024 "MB"}'

# Disk usage (database size)
du -h signal_engine/data/signals.db
```

---

## 🔄 **BACKUP & RECOVERY**

### **Daily Automated Backup**

```bash
#!/bin/bash
# backup_signals.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="/backup/signal_engine"

# Backup SQLite database
cp signal_engine/data/signals.db "$BACKUP_DIR/signals_$DATE.db"

# Backup configuration
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" signal_engine/config/

# Keep only last 7 days
find $BACKUP_DIR -name "signals_*.db" -mtime +7 -delete
```

### **Recovery from Backup**

```bash
# Stop signal engine
pkill -f "python3 main.py"

# Restore database
cp /backup/signal_engine/signals_20250119.db signal_engine/data/signals.db

# Verify integrity
sqlite3 signal_engine/data/signals.db "PRAGMA integrity_check;"

# Restart
python3 signal_engine/main.py &
```

---

## 📞 **EMERGENCY CONTACTS**

| Issue Type | Action | Contact |
|------------|--------|---------|
| System Down | Restart services | DevOps Team |
| Database Corruption | Restore from backup | Database Admin |
| Telegram API Issues | Check Telegram status | https://status.telegram.org |
| High Rejection Rate | Review market conditions | Trading Team |
| Stuck Signals | Manual closure | Operations Team |

---

## 📊 **DAILY OPERATIONS CHECKLIST**

### **Morning Check (9:00 AM)**
- [ ] Verify all services running
- [ ] Check active signal count (should be 10-50)
- [ ] Review overnight statistics
- [ ] Check for any error logs

### **Midday Check (2:00 PM)**
- [ ] Review win rate (should be 55-75%)
- [ ] Check Fusion Engine approval rate
- [ ] Verify Telegram broadcasts working
- [ ] Monitor dispatcher success rate

### **Evening Check (8:00 PM)**
- [ ] Review daily performance report
- [ ] Check for stuck signals
- [ ] Backup database
- [ ] Clear old logs

### **Weekly Tasks**
- [ ] Database vacuum and optimization
- [ ] Review and archive old signals (>30 days)
- [ ] Check disk usage
- [ ] Update watchlist if needed

---

## 🎯 **SUCCESS CRITERIA**

Production deployment is successful if:

1. ✅ **Signal Flow**: Signals generate → filter → track → dispatch → close
2. ✅ **Closure Rate**: >95% of signals close within 24 hours
3. ✅ **Dispatch Success**: >90% success rate
4. ✅ **Win Rate**: Between 50-80% (depends on market)
5. ✅ **No Stuck Signals**: <5 signals stuck ACTIVE for >24 hours
6. ✅ **Database Health**: No corruption, <1GB size
7. ✅ **Telegram Broadcasting**: 100% delivery to all groups

---

## 📝 **CHANGELOG & VERSIONING**

- **v2.0.0** (Nov 19, 2025): Master Fusion Engine with intelligent filtering
- **v2.0.1**: Added signal closure webhook integration
- **v2.0.2**: Added SQLite tracking and daily reporter

---

**Last Updated**: November 19, 2025  
**Maintained By**: VerzekAutoTrader DevOps Team  
**Documentation Version**: 2.0
