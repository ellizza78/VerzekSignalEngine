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
    worker_logger.info(f"🚀 Verzek AutoTrader Worker started (poll interval: {POLL_SECONDS}s)")
    
    while True:
        try:
            db = SessionLocal()
            run_once(db)
            db.close()
            
        except KeyboardInterrupt:
            worker_logger.info("Worker stopped by user")
            break
            
        except Exception as e:
            worker_logger.error(f"Worker error: {e}")
        
        finally:
            time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
