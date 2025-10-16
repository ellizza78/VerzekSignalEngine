"""
Advanced Orders Monitor Service
Continuously monitors and executes trailing stops and OCO orders
"""

import schedule
import time
from modules.advanced_orders import advanced_order_manager
from modules import PositionTracker
from utils.logger import log_event
from typing import Dict


class AdvancedOrdersMonitor:
    """Background service to monitor and trigger advanced orders"""
    
    def __init__(self):
        self.position_tracker = PositionTracker()
        log_event("ADVANCED_ORDERS", "🎯 Advanced Orders Monitor initialized")
    
    def get_current_prices(self) -> Dict[str, float]:
        """Get current prices for all active positions"""
        positions = self.position_tracker.get_all_positions()
        prices = {}
        
        for pos in positions:
            if pos.get('status') == 'active' and pos.get('current_price'):
                prices[pos.get('symbol')] = pos.get('current_price')
        
        return prices
    
    def monitor_advanced_orders(self):
        """Check and execute advanced orders"""
        try:
            # Get current market prices
            current_prices = self.get_current_prices()
            
            if not current_prices:
                return
            
            # Check trailing stops
            triggered_trailing = advanced_order_manager.update_trailing_stops(current_prices)
            
            for trigger in triggered_trailing:
                log_event(
                    "ADVANCED_ORDERS", 
                    f"⚠️ Trailing stop triggered for {trigger['symbol']}: "
                    f"${trigger['stop_price']} (current: ${trigger['current_price']})"
                )
                # Position will be closed by DCA orchestrator or manual intervention
            
            # Check OCO orders
            triggered_oco = advanced_order_manager.check_oco_orders(current_prices)
            
            for trigger in triggered_oco:
                log_event(
                    "ADVANCED_ORDERS",
                    f"⚡ OCO order triggered for {trigger['symbol']}: "
                    f"{trigger['executed_side']} at ${trigger['execution_price']}"
                )
                # Order will be executed by trading system
            
        except Exception as e:
            log_event("ADVANCED_ORDERS", f"❌ Error in advanced orders monitor: {str(e)}")
    
    def run(self):
        """Run the monitoring service"""
        # Check advanced orders every 5 seconds
        schedule.every(5).seconds.do(self.monitor_advanced_orders)
        
        log_event("ADVANCED_ORDERS", "🚀 Advanced Orders Monitor started")
        
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == "__main__":
    monitor = AdvancedOrdersMonitor()
    monitor.run()
