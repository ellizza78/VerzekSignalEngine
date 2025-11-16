# VerzekSignalEngine → VerzekAutoTrader Integration Guide

## 📡 Overview

This guide explains how to integrate VerzekSignalEngine with your existing VerzekAutoTrader backend.

---

## 🔗 Backend API Requirements

### 1. Create Signal Endpoint

Add this endpoint to your Flask backend:

```python
# backend/routes/signals.py

from flask import Blueprint, request, jsonify
from backend.auth.middleware import require_api_key
from backend.models import Signal
from backend.database import db
from datetime import datetime

signals_bp = Blueprint('signals', __name__)

@signals_bp.route('/api/signals', methods=['POST'])
@require_api_key
def receive_signal():
    """
    Receive trading signal from VerzekSignalEngine
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['symbol', 'direction', 'entry_price', 'tp_price', 'sl_price', 'strategy', 'confidence']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create signal record
        signal = Signal(
            symbol=data['symbol'],
            direction=data['direction'],
            entry_price=float(data['entry_price']),
            tp_price=float(data['tp_price']),
            sl_price=float(data['sl_price']),
            strategy=data['strategy'],
            timeframe=data.get('timeframe', '5m'),
            confidence=float(data['confidence']),
            version=data.get('version', 'SE.v1.0'),
            metadata=data.get('metadata', {}),
            source='VerzekSignalEngine',
            created_at=datetime.utcnow(),
            status='active'
        )
        
        db.session.add(signal)
        db.session.commit()
        
        # Broadcast to app subscribers (async task)
        broadcast_signal_to_app.delay(signal.id)
        
        return jsonify({
            'success': True,
            'signal_id': signal.id,
            'message': 'Signal received and processed'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Register blueprint
app.register_blueprint(signals_bp)
```

### 2. Create Signal Model

```python
# backend/models.py

class Signal(db.Model):
    __tablename__ = 'signals'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)
    direction = db.Column(db.String(10), nullable=False)  # LONG or SHORT
    entry_price = db.Column(db.Float, nullable=False)
    tp_price = db.Column(db.Float, nullable=False)
    sl_price = db.Column(db.Float, nullable=False)
    strategy = db.Column(db.String(50), nullable=False)
    timeframe = db.Column(db.String(10))
    confidence = db.Column(db.Float)
    version = db.Column(db.String(20))
    metadata = db.Column(db.JSON)
    source = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active')  # active, closed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'direction': self.direction,
            'entry_price': self.entry_price,
            'tp_price': self.tp_price,
            'sl_price': self.sl_price,
            'strategy': self.strategy,
            'timeframe': self.timeframe,
            'confidence': self.confidence,
            'version': self.version,
            'metadata': self.metadata,
            'source': self.source,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
```

### 3. API Key Authentication

```python
# backend/auth/middleware.py

from functools import wraps
from flask import request, jsonify
import os

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        # Validate API key
        valid_key = os.getenv('SIGNAL_ENGINE_API_KEY')
        if api_key != valid_key:
            return jsonify({'error': 'Invalid API key'}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function
```

### 4. Generate API Key

```bash
# On Vultr server
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Add to Replit Secrets:
- **Key**: `SIGNAL_ENGINE_API_KEY`
- **Value**: Generated token

---

## 📱 Mobile App Integration

### 1. Signals Screen

Create new screen to display signals:

```jsx
// mobile_app/VerzekApp/src/screens/SignalsScreen.js

import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, StyleSheet } from 'react-native';
import { api } from '../services/api';

export default function SignalsScreen() {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchSignals();
    const interval = setInterval(fetchSignals, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);
  
  const fetchSignals = async () => {
    try {
      const response = await api.get('/api/signals/recent');
      setSignals(response.data.signals);
    } catch (error) {
      console.error('Error fetching signals:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const renderSignal = ({ item }) => (
    <View style={styles.signalCard}>
      <Text style={styles.symbol}>{item.symbol}</Text>
      <Text style={[styles.direction, item.direction === 'LONG' ? styles.long : styles.short]}>
        {item.direction}
      </Text>
      <Text style={styles.entry}>Entry: {item.entry_price}</Text>
      <Text style={styles.tp}>TP: {item.tp_price}</Text>
      <Text style={styles.sl}>SL: {item.sl_price}</Text>
      <Text style={styles.confidence}>Confidence: {item.confidence}%</Text>
      <Text style={styles.strategy}>{item.strategy}</Text>
    </View>
  );
  
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Live Trading Signals</Text>
      <FlatList
        data={signals}
        renderItem={renderSignal}
        keyExtractor={item => item.id.toString()}
        refreshing={loading}
        onRefresh={fetchSignals}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0A0E27', padding: 15 },
  title: { fontSize: 24, color: '#FFD700', fontWeight: 'bold', marginBottom: 15 },
  signalCard: { backgroundColor: '#1A1F3A', padding: 15, borderRadius: 10, marginBottom: 10 },
  symbol: { fontSize: 18, color: '#FFF', fontWeight: 'bold' },
  direction: { fontSize: 16, fontWeight: 'bold', marginTop: 5 },
  long: { color: '#00FF00' },
  short: { color: '#FF0000' },
  entry: { fontSize: 14, color: '#AAA', marginTop: 3 },
  tp: { fontSize: 14, color: '#00FF00', marginTop: 3 },
  sl: { fontSize: 14, color: '#FF0000', marginTop: 3 },
  confidence: { fontSize: 14, color: '#FFD700', marginTop: 5 },
  strategy: { fontSize: 12, color: '#888', marginTop: 5 }
});
```

### 2. Backend Endpoint for App

```python
# backend/routes/signals.py

@signals_bp.route('/api/signals/recent', methods=['GET'])
@jwt_required()
def get_recent_signals():
    """Get recent signals for mobile app"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    # Check subscription tier
    if user.subscription_tier == 'FREE':
        return jsonify({'error': 'Upgrade to access signals'}), 403
    
    # Get recent active signals
    signals = Signal.query.filter_by(status='active').order_by(Signal.created_at.desc()).limit(20).all()
    
    return jsonify({
        'signals': [s.to_dict() for s in signals],
        'count': len(signals)
    }), 200
```

---

## 🔄 Deployment Steps

### 1. On Vultr Server

```bash
# Clone signal engine
cd /root
git clone https://github.com/your-repo/VerzekSignalEngine.git
cd VerzekSignalEngine

# Install dependencies
pip3 install -r requirements.txt

# Configure environment
cp config/.env.example config/.env
nano config/.env

# Setup systemd
sudo cp systemd/verzek-signalengine.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable verzek-signalengine
sudo systemctl start verzek-signalengine

# Check status
sudo systemctl status verzek-signalengine
```

### 2. On Replit (Backend)

```bash
# Add to backend/requirements.txt
# (No new dependencies needed if using existing Flask setup)

# Apply database migration
flask db upgrade

# Add API key to Secrets
# SIGNAL_ENGINE_API_KEY=your_generated_key

# Restart backend
```

### 3. Test Integration

```bash
# Test signal endpoint manually
curl -X POST https://api.verzekinnovative.com/api/signals \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "symbol": "BTCUSDT",
    "direction": "LONG",
    "entry_price": 51000,
    "tp_price": 51500,
    "sl_price": 50700,
    "strategy": "Test Signal",
    "confidence": 75,
    "timeframe": "5m"
  }'
```

---

## 📊 Monitoring

### Check Signal Flow

```bash
# On Vultr
tail -f /root/VerzekSignalEngine/logs/signal_engine.log

# On Replit
tail -f backend/logs/api.log

# In mobile app
console.log('Signals received:', signals.length)
```

---

## 🚨 Removing Old Telethon Code

### Files to Delete

```bash
# On Vultr server
rm -rf /root/old_telegram_listener/
rm -f backend/telethon_bot.py
rm -f backend/signal_monitor_telethon.py
```

### Update Backend

Remove Telethon imports and replace with:
```python
# backend/telegram_bot.py (NEW - using python-telegram-bot)
from telegram import Bot

# Use python-telegram-bot library instead of Telethon
```

---

## ✅ Verification Checklist

- [ ] Backend `/api/signals` endpoint created
- [ ] Signal model added to database
- [ ] API key authentication working
- [ ] VerzekSignalEngine deployed on Vultr
- [ ] Systemd service running
- [ ] Test signal received by backend
- [ ] Signals visible in database
- [ ] Mobile app can fetch signals
- [ ] Telegram broadcasting working
- [ ] Old Telethon code removed

---

## 📞 Support

Issues or questions? Contact: support@verzekinnovative.com
