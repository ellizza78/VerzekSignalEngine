"""
Environment Variable Loader for VerzekSignalEngine
Loads secrets from Replit environment or .env file
"""
import os
from pathlib import Path
from dotenv import load_dotenv

def load_environment():
    """Load environment variables with fallback to .env file"""
    
    # Try loading from .env file
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment from {env_file}")
    
    # Verify required variables
    required_vars = [
        'BACKEND_API_URL',
        'HOUSE_ENGINE_TOKEN',
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_VIP_CHAT_ID',
        'TELEGRAM_TRIAL_CHAT_ID'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please set them in Replit Secrets or create a .env file")
        return False
    
    # Set defaults for optional variables
    os.environ.setdefault('ENABLE_SCALPING_BOT', 'true')
    os.environ.setdefault('ENABLE_TREND_BOT', 'true')
    os.environ.setdefault('ENABLE_QFL_BOT', 'true')
    os.environ.setdefault('ENABLE_AI_BOT', 'true')
    os.environ.setdefault('TRADING_SYMBOLS', 'BTCUSDT,ETHUSDT,BNBUSDT,SOLUSDT,XRPUSDT')
    os.environ.setdefault('LOG_LEVEL', 'INFO')
    os.environ.setdefault('SCALPING_INTERVAL', '15')
    os.environ.setdefault('TREND_INTERVAL', '300')
    os.environ.setdefault('QFL_INTERVAL', '20')
    os.environ.setdefault('AI_INTERVAL', '30')
    
    print("✅ All required environment variables loaded")
    return True

if __name__ == "__main__":
    load_environment()
