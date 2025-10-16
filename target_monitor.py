"""
Target Monitor
--------------
Continuously monitors all active positions for target hits
and executes progressive take profits automatically
"""

import time
from modules.dca_orchestrator import DCAOrchestrator
from utils.logger import log_event

def main():
    """Main target monitoring loop"""
    log_event("TARGET_MONITOR", "🎯 Target Monitor started")
    
    orchestrator = DCAOrchestrator()
    
    # Monitoring interval (check every 5 seconds)
    CHECK_INTERVAL = 5
    
    try:
        while True:
            try:
                # Monitor all positions for target hits
                orchestrator.monitor_targets()
                
            except Exception as e:
                log_event("TARGET_MONITOR", f"Error in monitoring loop: {e}")
            
            # Wait before next check
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        log_event("TARGET_MONITOR", "🛑 Target Monitor stopped")

if __name__ == "__main__":
    main()
