"""
Recurring Payments Service - Background service for processing monthly subscription renewals
"""

import time
import schedule
from modules.recurring_payments import recurring_handler
from utils.logger import log_event

def check_recurring_payments():
    """Check and process recurring subscription payments and referral bonuses"""
    try:
        recurring_handler.process_monthly_renewals()
    except Exception as e:
        log_event("ERROR", f"Recurring payments check failed: {str(e)}")

if __name__ == "__main__":
    log_event("RECURRING", "💰 Recurring Payments Service started")
    
    # Schedule daily check at 00:00
    schedule.every().day.at("00:00").do(check_recurring_payments)
    
    # Also run check on startup
    check_recurring_payments()
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute for scheduled tasks
