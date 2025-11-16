"""
VerzekSignalEngine v1.0 - Main Entry Point
Multi-bot signal generation system
"""
import sys
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Setup logging
def setup_logging():
    """Configure comprehensive logging"""
    log_dir = './logs'
    os.makedirs(log_dir, exist_ok=True)
    
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (rotating)
    file_handler = RotatingFileHandler(
        f'{log_dir}/signal_engine.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Error log file
    error_handler = RotatingFileHandler(
        f'{log_dir}/errors.log',
        maxBytes=10*1024*1024,
        backupCount=3
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    logger.addHandler(error_handler)
    
    return logger


def print_banner():
    """Print startup banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║           🔥 VERZEK SIGNAL ENGINE v1.0 🔥                ║
    ║                                                           ║
    ║   Multi-Bot Trading Signal Generation System             ║
    ║                                                           ║
    ║   • Scalping Bot    (15s interval - Quick momentum)      ║
    ║   • Trend Bot       (5m interval - Strong moves)         ║
    ║   • QFL Bot         (20s interval - Crash recovery)      ║
    ║   • AI/ML Bot       (30s interval - ML predictions)      ║
    ║                                                           ║
    ║   Integrated with VerzekAutoTrader Backend               ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """Main entry point"""
    # Setup logging
    logger = setup_logging()
    
    # Print banner
    print_banner()
    
    # Log startup info
    logger.info("=" * 80)
    logger.info("VerzekSignalEngine v1.0 Starting...")
    logger.info(f"Backend API: {os.getenv('BACKEND_API_URL', 'Not configured')}")
    logger.info(f"Telegram Bot: {'Configured' if os.getenv('TELEGRAM_BOT_TOKEN') else 'Not configured'}")
    logger.info("=" * 80)
    
    try:
        # Import and run scheduler
        from services.scheduler import run_signal_engine
        run_signal_engine()
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ Shutdown initiated by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
