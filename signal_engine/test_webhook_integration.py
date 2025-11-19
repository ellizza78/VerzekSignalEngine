"""
Test Script: Webhook Integration for Signal Closure
Tests the complete flow: open signal → webhook call → close signal → verify
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import requests
from datetime import datetime
from services.tracker import SignalTracker
from core.models import SignalCandidate

def test_webhook_integration():
    """Test complete webhook integration flow"""
    print("=" * 60)
    print("🧪 TESTING WEBHOOK INTEGRATION")
    print("=" * 60)
    
    # Step 1: Initialize tracker
    print("\n1️⃣  Initializing Signal Tracker...")
    tracker = SignalTracker(db_path='./data/signals_test.db')
    print("✅ Tracker initialized")
    
    # Step 2: Create a test signal
    print("\n2️⃣  Creating test signal...")
    test_signal = SignalCandidate(
        signal_id="test-webhook-123",
        symbol="BTCUSDT",
        side="LONG",
        entry=50000.0,
        stop_loss=49500.0,
        take_profits=[51500.0],
        timeframe="5m",
        confidence=85.0,
        bot_source="TEST"
    )
    
    success = tracker.open_signal(test_signal)
    if not success:
        print("❌ Failed to open signal")
        return False
    
    print(f"✅ Signal opened: {test_signal.signal_id}")
    print(f"   Symbol: {test_signal.symbol}")
    print(f"   Entry: ${test_signal.entry}")
    print(f"   TP: ${test_signal.take_profits[0]}")
    print(f"   SL: ${test_signal.stop_loss}")
    
    # Step 3: Verify signal is ACTIVE
    print("\n3️⃣  Verifying signal is ACTIVE...")
    active_signals = tracker.get_active_signals()
    if not any(s['signal_id'] == test_signal.signal_id for s in active_signals):
        print("❌ Signal not found in active signals")
        return False
    print(f"✅ Signal confirmed ACTIVE (Total active: {len(active_signals)})")
    
    # Step 4: Call webhook to close signal
    print("\n4️⃣  Calling webhook to close signal...")
    webhook_payload = {
        'signal_id': test_signal.signal_id,
        'exit_price': 51500.0,  # Hit TP
        'close_reason': 'TP'
    }
    
    try:
        # Note: Start webhooks.py server first: python3 signal_engine/api/webhooks.py
        response = requests.post(
            'http://localhost:8050/api/signals/close',
            json=webhook_payload,
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Webhook successful!")
            print(f"   Status: {result['status']}")
            print(f"   Profit: {result['outcome']['profit_pct']:.2f}%")
            print(f"   Duration: {result['outcome']['duration_minutes']} minutes")
        else:
            print(f"❌ Webhook failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Webhook server not running!")
        print("   Start webhook server: python3 signal_engine/api/webhooks.py")
        return False
    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return False
    
    # Step 5: Verify signal is CLOSED
    print("\n5️⃣  Verifying signal is CLOSED...")
    active_signals_after = tracker.get_active_signals()
    if any(s['signal_id'] == test_signal.signal_id for s in active_signals_after):
        print("❌ Signal still ACTIVE after webhook")
        return False
    
    print(f"✅ Signal confirmed CLOSED")
    
    # Step 6: Check statistics
    print("\n6️⃣  Checking tracker statistics...")
    stats = tracker.get_stats()
    print(f"   Active Signals: {stats['active_signals']}")
    print(f"   Closed Signals: {stats['closed_signals']}")
    print(f"   Total Signals: {stats['total_signals']}")
    print(f"   Win Rate: {stats['win_rate']}%")
    print(f"   Avg Profit: {stats['avg_profit']}%")
    
    print("\n" + "=" * 60)
    print("✅ WEBHOOK INTEGRATION TEST PASSED!")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    test_webhook_integration()
