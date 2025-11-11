#!/usr/bin/env python3
"""
Verzek AutoTrader Worker
Continuously monitors signals and executes trades for users with auto_trade_enabled=True
"""
import os
import sys
import time

# Add current directory to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from db import SessionLocal
from trading.executor import run_once
from utils.logger import worker_logger

POLL_SECONDS = int(os.getenv("WORKER_POLL_SECONDS", "10"))


def main():
    """Main worker loop"""
    worker_logger.info("=" * 60)
    worker_logger.info(f"🚀 Verzek AutoTrader Worker v2.1 started")
    worker_logger.info(f"⏱️  Poll interval: {POLL_SECONDS} seconds")
    worker_logger.info(f"💾 Database: {os.getenv('DATABASE_URL', 'sqlite:///')}")
    worker_logger.info(f"🔧 Exchange mode: {os.getenv('EXCHANGE_MODE', 'paper')}")
    worker_logger.info("=" * 60)
    
    cycle_count = 0
    
    while True:
        try:
            cycle_count += 1
            worker_logger.info(f"📊 Starting execution cycle #{cycle_count}")
            
            db = SessionLocal()
            run_once(db)
            db.close()
            
            worker_logger.info(f"✅ Cycle #{cycle_count} completed successfully")
            
        except KeyboardInterrupt:
            worker_logger.info("⛔ Worker stopped by user (Ctrl+C)")
            break
            
        except Exception as e:
            worker_logger.error(f"❌ Worker error in cycle #{cycle_count}: {e}", exc_info=True)
        
        finally:
            time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
