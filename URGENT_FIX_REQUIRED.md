# 🚨 URGENT: VerzekAutoTrader Server Fix Required

## Current Status

❌ **API is DOWN** - Not responding at https://api.verzekinnovative.com  
❌ **Metadata column bug** causing SQLAlchemy crash  
❌ **SSH deployment blocked** - Key authentication not working from Replit

## Root Cause

The `HouseSignal` model has a column named `metadata` which is a **reserved word** in SQLAlchemy, causing the API to crash on startup with:

```
sqlalchemy.exc.InvalidRequestError: Attribute name 'metadata' is reserved when using the Declarative API.
```

---

## 🔧 IMMEDIATE FIX (Copy/Paste This - CORRECTED VERSION)

### Run this command in your Vultr SSH session:

```bash
cd /root/VerzekBackend/backend && \
cp models.py models.py.backup.$(date +%Y%m%d_%H%M%S) && \
cp house_signals_routes.py house_signals_routes.py.backup.$(date +%Y%m%d_%H%M%S) && \
sed -i "s/metadata = Column(JSON, default=dict)/meta_data = Column('metadata', JSON, default=dict)/" models.py && \
sed -i "s/metadata=data.get('metadata', {})/meta_data=data.get('metadata', {})/" house_signals_routes.py && \
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
find . -type f -name "*.pyc" -delete 2>/dev/null || true && \
systemctl stop verzek_api && \
killall -9 gunicorn 2>/dev/null || true && \
sleep 2 && \
systemctl start verzek_api && \
sleep 5 && \
echo "✅ Fix applied - testing endpoint..." && \
curl -s -X POST http://localhost:8050/api/house-signals/ingest \
  -H "Content-Type: application/json" \
  -H "X-INTERNAL-TOKEN: $(grep HOUSE_ENGINE_TOKEN .env | cut -d= -f2)" \
  -d '{"source":"TEST","symbol":"BTCUSDT","side":"LONG","entry":50000,"stop_loss":49500,"take_profits":[50500],"timeframe":"M5","confidence":85}' | python3 -m json.tool
```

**What Changed in V2:**
- Uses SQLAlchemy column mapping: `Column('metadata', ...)` 
- Python code uses: `signal.meta_data` (not reserved)
- Database column stays: `metadata` (NO migration needed!)
- This is the **CORRECT** approach - no schema changes required

### Expected Output:

```json
{
  "ok": true,
  "signal_id": 1,
  "message": "House signal ingested and position opened"
}
```

---

## What This Fix Does:

1. ✅ Backs up current files with timestamp
2. ✅ Changes `metadata` → `meta_data` in `models.py`
3. ✅ Updates `house_signals_routes.py` to use `meta_data`
4. ✅ Clears all Python cache
5. ✅ Stops and kills all Gunicorn processes
6. ✅ Starts API fresh
7. ✅ Tests the endpoint immediately

---

## After Fix Succeeds:

Run this to enable Signal Engine:

```bash
systemctl enable --now verzek-signalengine
systemctl status verzek-signalengine
```

---

## Verification Commands:

```bash
# Check API status
systemctl status verzek_api

# Check latest signals in database
psql -d verzek_production -c "SELECT id, source, symbol, side, confidence, created_at FROM house_signals ORDER BY id DESC LIMIT 5;"

# Monitor signal engine logs
tail -f /root/signal_engine/logs/signal_engine.log

# Test public endpoint
curl https://api.verzekinnovative.com/api/ping
```

---

## Next Steps After Fix:

1. ✅ API will be running
2. ✅ Signal engine can send signals
3. ✅ Signals stored in database
4. ✅ Mobile app receives signals
5. ✅ End-to-end flow working

---

## Why SSH Deployment Isn't Working:

The SSH key in `VULTR_SSH_PRIVATE_KEY` environment variable doesn't match the server's authorized_keys. This needs to be configured manually by:

1. Generating a new SSH key pair on Replit
2. Adding the public key to `/root/.ssh/authorized_keys` on Vultr
3. Then `deploy_all.sh` will work automatically

**For now: Run the fix command above manually, then we'll set up automated deployment.**

---

**STATUS: Waiting for you to run the fix command above** ⏳
