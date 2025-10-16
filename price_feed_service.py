"""
price_feed_service.py
--------------------
Real-time WebSocket price feed service for VerzekAutoTrader
"""

from modules.realtime_price_feed import PriceFeedManager
from modules.position_tracker import PositionTracker
from utils.logger import log_event
import time

def main():
    log_event("PRICE_FEED", "📡 Starting Real-Time Price Feed Service...")
    
    position_tracker = PositionTracker()
    price_feed = PriceFeedManager(position_tracker)
    
    # Subscribe to price updates
    def on_price_update(symbol, price, exchange):
        log_event("PRICE_FEED", f"{exchange.upper()} | {symbol}: ${price:.2f}")
    
    price_feed.subscribe(on_price_update)
    
    # Start auto-feeds for all active positions
    price_feed.start_auto_feeds()
    
    log_event("PRICE_FEED", "✅ Price Feed Service running...")
    
    # Keep service alive
    while price_feed.running:
        time.sleep(1)

if __name__ == "__main__":
    main()
