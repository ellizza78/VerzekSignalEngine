"""
Quick test script for VerzekSignalEngine
Tests individual bot functionality
"""
import sys
import asyncio
from bots.scalper.scalping_bot import ScalpingBot
from bots.trend.trend_bot import TrendBot
from bots.qfl.qfl_bot import QFLBot
from bots.ai_ml.ai_bot import AIBot

def test_config():
    return {
        'enabled': True,
        'primary_timeframe': '5m',
        'confidence_threshold': 70,
        'drop_threshold_min': 6.0,
        'drop_threshold_max': 15.0,
        'base_lookback_candles': 100,
        'model_path': './models/signal_predictor_v1.joblib',
        'prediction_threshold': 0.65
    }

async def test_scalping_bot():
    """Test Scalping Bot"""
    print("\n" + "="*60)
    print("🧪 Testing Scalping Bot...")
    print("="*60)
    
    bot = ScalpingBot(test_config())
    signal = await bot.analyze('BTC/USDT')
    
    if signal:
        print("✅ Signal Generated:")
        print(signal.to_telegram_message())
    else:
        print("ℹ️ No signal generated (conditions not met)")

async def test_trend_bot():
    """Test Trend Bot"""
    print("\n" + "="*60)
    print("🧪 Testing Trend Bot...")
    print("="*60)
    
    bot = TrendBot(test_config())
    signal = await bot.analyze('BTC/USDT')
    
    if signal:
        print("✅ Signal Generated:")
        print(signal.to_telegram_message())
    else:
        print("ℹ️ No signal generated (conditions not met)")

async def test_qfl_bot():
    """Test QFL Bot"""
    print("\n" + "="*60)
    print("🧪 Testing QFL Bot...")
    print("="*60)
    
    bot = QFLBot(test_config())
    signal = await bot.analyze('BTC/USDT')
    
    if signal:
        print("✅ Signal Generated:")
        print(signal.to_telegram_message())
    else:
        print("ℹ️ No signal generated (conditions not met)")

async def test_ai_bot():
    """Test AI/ML Bot"""
    print("\n" + "="*60)
    print("🧪 Testing AI/ML Bot...")
    print("="*60)
    
    bot = AIBot(test_config())
    signal = await bot.analyze('BTC/USDT')
    
    if signal:
        print("✅ Signal Generated:")
        print(signal.to_telegram_message())
    else:
        print("ℹ️ No signal generated (conditions not met)")

async def test_all_bots():
    """Test all bots"""
    print("\n🔥 VerzekSignalEngine - Bot Testing Suite\n")
    
    await test_scalping_bot()
    await test_trend_bot()
    await test_qfl_bot()
    await test_ai_bot()
    
    print("\n" + "="*60)
    print("✅ Testing Complete")
    print("="*60 + "\n")

if __name__ == "__main__":
    asyncio.run(test_all_bots())
