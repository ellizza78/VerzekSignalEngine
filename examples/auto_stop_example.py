"""
Auto-Stop Logic Example
-----------------------
Demonstrates how the auto-stop system detects and processes close signals
"""

from signal_parser import parse_close_signal

# Example close/cancel signals
test_signals = [
    "BTCUSDT - Signal Cancelled",
    "#ETHUSDT Stop Loss Hit",
    "SOLUSDT Trade Closed with 15% profit",
    "BNBUSDT POSITION CLOSED",
    "🛑 XRPUSDT - SL Hit"
]

print("=" * 60)
print("AUTO-STOP LOGIC EXAMPLE")
print("=" * 60)

print("\n📋 Supported Close Signal Patterns:")
print("   - 'Signal Cancelled' or 'Signal Canceled'")
print("   - 'Closed' or 'Close'")
print("   - 'Stop Loss Hit' or 'SL Hit'")
print("   - 'Position Closed' or 'Trade Closed'")

print("\n🔍 Parsing Example Signals:\n")

for signal in test_signals:
    result = parse_close_signal(signal)
    if result:
        print(f"✅ '{signal}'")
        print(f"   → Symbol: {result['symbol']}")
        print(f"   → Reason: {result['reason']}")
        print(f"   → Action: {result['action']}")
    else:
        print(f"❌ '{signal}' - Not recognized as close signal")
    print()

print("🔄 How Auto-Close Works:")
print("   1. Telegram signal detected by Broadcast Bot")
print("   2. parse_close_signal() checks for close keywords")
print("   3. If detected, extract symbol and reason")
print("   4. orchestrator.auto_close_positions() triggered")
print("   5. Finds all active positions for that symbol")
print("   6. Checks if user has auto_stop_on_cancel enabled")
print("   7. Places close orders at current market price")
print("   8. Updates position status to 'closed'")
print("   9. Records final PnL (including any partial TPs)")

print("\n⚙️  User Settings:")
print("   - strategy_settings.auto_stop_on_cancel: True/False (default: True)")
print("   - When disabled, user must manually close positions")

print("\n📊 Close Reasons:")
print("   - signal_cancelled: Signal was cancelled by provider")
print("   - stop_loss_hit: Stop loss was triggered")
print("   - closed: General position closure")
print("   - manual_close: User manually closed")

print("\n" + "=" * 60)
