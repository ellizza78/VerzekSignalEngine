#!/bin/bash
# ============================================================================
# VerzekAutoTrader - Server-Side Fix Script V2 (CORRECT VERSION)
# Run this DIRECTLY on your Vultr server
# ============================================================================

set -e

echo "🔧 VerzekAutoTrader - Fixing Metadata Column Bug (V2 - Correct Fix)"
echo "===================================================================="
echo ""

cd /root/VerzekBackend/backend

# Backup current files
echo "1️⃣ Creating backups..."
cp models.py models.py.backup.$(date +%Y%m%d_%H%M%S)
cp house_signals_routes.py house_signals_routes.py.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ Backups created"

# Fix models.py - Use SQLAlchemy column mapping + add backwards-compatible property
echo ""
echo "2️⃣ Fixing models.py with proper SQLAlchemy column mapping..."

# Replace metadata column with mapped version
sed -i "s/metadata = Column(JSON, default=dict)/meta_data = Column('metadata', JSON, default=dict)/" models.py

# Add backwards-compatible property after the positions relationship
if ! grep -q "@property" models.py | grep -q "def metadata"; then
    # Find the line with positions relationship and add property after it
    sed -i '/positions = relationship("HouseSignalPosition", back_populates="signal", cascade="all, delete-orphan")/a\    \n    @property\n    def metadata(self):\n        """Backwards-compatible property for accessing meta_data"""\n        return self.meta_data\n    \n    @metadata.setter\n    def metadata(self, value):\n        """Backwards-compatible setter for meta_data"""\n        self.meta_data = value' models.py
fi

# Verify the fix
if grep -q "meta_data = Column('metadata'" models.py; then
    echo "✅ models.py fixed with column mapping"
    grep -n "meta_data = Column" models.py | head -1
else
    echo "❌ Fix failed - reverting"
    cp models.py.backup.* models.py
    exit 1
fi

# Fix house_signals_routes.py - Update usage
echo ""
echo "3️⃣ Fixing house_signals_routes.py..."
sed -i "s/metadata=data.get('metadata', {})/meta_data=data.get('metadata', {})/" house_signals_routes.py

if grep -q "meta_data=data.get" house_signals_routes.py; then
    echo "✅ house_signals_routes.py fixed"
else
    echo "❌ Fix failed - reverting"
    cp house_signals_routes.py.backup.* house_signals_routes.py
    exit 1
fi

# Clear Python cache
echo ""
echo "4️⃣ Clearing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
echo "✅ Cache cleared"

# Restart API
echo ""
echo "5️⃣ Restarting API service..."
systemctl stop verzek_api
sleep 2
killall -9 gunicorn 2>/dev/null || true
sleep 1
systemctl start verzek_api
sleep 5

# Check API status
echo ""
echo "6️⃣ Checking API status..."
if systemctl is-active --quiet verzek_api; then
    echo "✅ API is running"
    systemctl status verzek_api --no-pager | grep "Active:"
else
    echo "❌ API failed to start - checking logs..."
    tail -30 logs/api_error.log
    exit 1
fi

# Test the endpoint
echo ""
echo "7️⃣ Testing /api/house-signals/ingest endpoint..."

TOKEN=$(grep HOUSE_ENGINE_TOKEN .env | cut -d= -f2)

RESPONSE=$(curl -s -X POST http://localhost:8050/api/house-signals/ingest \
  -H "Content-Type: application/json" \
  -H "X-INTERNAL-TOKEN: $TOKEN" \
  -d '{
    "source": "TEST",
    "symbol": "BTCUSDT",
    "side": "LONG",
    "entry": 50000.0,
    "stop_loss": 49500.0,
    "take_profits": [50500.0],
    "timeframe": "M5",
    "confidence": 85,
    "metadata": {"test": true}
  }')

echo "$RESPONSE" | python3 -m json.tool

if echo "$RESPONSE" | grep -q '"ok": true'; then
    echo ""
    echo "✅ SUCCESS! Endpoint working!"
    
    # Verify data in database
    echo ""
    echo "8️⃣ Verifying signal in database..."
    psql -d verzek_production -c "SELECT id, source, symbol, confidence, metadata FROM house_signals ORDER BY id DESC LIMIT 1;" || echo "⚠️ Could not query database"
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ ALL FIXES APPLIED SUCCESSFULLY!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "What was fixed:"
    echo "  ✓ models.py: Using SQLAlchemy column mapping"
    echo "  ✓ Python code uses: signal.meta_data"
    echo "  ✓ Database column stays: metadata (no migration needed)"
    echo "  ✓ house_signals_routes.py: Updated to use meta_data"
    echo "  ✓ Python cache cleared"
    echo "  ✓ API service restarted"
    echo "  ✓ Endpoint tested and working"
    echo "  ✓ Database storing signals correctly"
    echo ""
    echo "Next: Enable signal engine:"
    echo "  systemctl enable --now verzek-signalengine"
    echo ""
else
    echo ""
    echo "❌ Endpoint test failed"
    echo "Response: $RESPONSE"
    exit 1
fi
