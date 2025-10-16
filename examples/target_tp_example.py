"""
Target-Based Take Profit Example
---------------------------------
Demonstrates how the target-based TP system works
"""

from signal_parser import parse_signal

# Example signal with multiple targets
signal_text = """
BTCUSDT LONG
ENTRY: 45000
TARGET 1: 46000
TARGET 2: 47000
TARGET 3: 48000
TARGET 4: 49000
STOP LOSS: 44000
"""

# Parse the signal
signal_data = parse_signal(signal_text)

print("=" * 60)
print("TARGET-BASED TAKE PROFIT EXAMPLE")
print("=" * 60)
print(f"\n📊 Signal Parsed:")
print(f"   Symbol: {signal_data.get('symbol')}")
print(f"   Direction: {signal_data.get('direction')}")
print(f"   Entry: {signal_data.get('entry')}")
print(f"   Stop Loss: {signal_data.get('sl')}")
print(f"\n🎯 Targets:")
for target in signal_data.get('tp', []):
    print(f"   Target {target['target_num']}: ${target['price']}")

print(f"\n📈 Progressive TP Flow (Default 25% each):")
print(f"   1. Price hits $46,000 → Close 25% → Profit recorded")
print(f"   2. Price hits $47,000 → Close 25% → Profit added")
print(f"   3. Price hits $48,000 → Close 25% → Profit added")
print(f"   4. Price hits $49,000 → Close 25% (FINAL) → Position closed, total PnL recorded")

print(f"\n⚙️  User Settings:")
print(f"   - strategy_settings.target_based_tp: True/False")
print(f"   - strategy_settings.partial_tp_splits: [25, 25, 25, 25]")
print(f"     (Can customize: [30, 30, 40] or [20, 20, 20, 40], etc.)")

print(f"\n🔄 Background Monitor:")
print(f"   - Checks every 5 seconds")
print(f"   - Compares current price vs targets")
print(f"   - Auto-executes TP when target reached")

print("\n" + "=" * 60)
