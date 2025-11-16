#!/bin/bash
# One-time script to fix the metadata column bug and deploy

SERVER="root@80.240.29.142"

echo "🔧 Fixing metadata column bug on server..."

ssh $SERVER bash << 'REMOTE_FIX'
cd /root/VerzekBackend/backend

echo "1️⃣ Fixing models.py..."
sed -i 's/metadata = Column(JSON, default=dict)/meta_data = Column(JSON, default=dict)/' models.py
grep -n "meta_data = Column" models.py

echo ""
echo "2️⃣ Fixing house_signals_routes.py..."
sed -i "s/metadata=data.get('metadata', {})/meta_data=data.get('metadata', {})/" house_signals_routes.py
grep -n "meta_data=data" house_signals_routes.py

echo ""
echo "3️⃣ Clearing cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo ""
echo "4️⃣ Restarting API..."
systemctl stop verzek_api
killall -9 gunicorn 2>/dev/null || true
sleep 2
systemctl start verzek_api
sleep 5

echo ""
echo "5️⃣ Checking status..."
systemctl status verzek_api --no-pager | head -15

echo ""
echo "6️⃣ Testing endpoint..."
curl -s -X POST http://localhost:8050/api/house-signals/ingest \
  -H "Content-Type: application/json" \
  -H "X-INTERNAL-TOKEN: $(grep HOUSE_ENGINE_TOKEN .env | cut -d= -f2)" \
  -d '{
    "source": "TEST",
    "symbol": "BTCUSDT",
    "side": "LONG",
    "entry": 50000.0,
    "stop_loss": 49500.0,
    "take_profits": [50500],
    "timeframe": "M5",
    "confidence": 85
  }' | python3 -m json.tool

echo ""
echo "✅ Fix complete!"
REMOTE_FIX

echo ""
echo "🚀 Now uploading fixed files from Replit..."
bash deploy_all.sh

echo ""
echo "✅ All done!"
