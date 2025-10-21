#!/usr/bin/env python3
"""
Scheduled Tasks - Background tasks for notifications and summaries
Run this alongside the main bot to send periodic admin notifications
"""

import schedule
import time
from datetime import datetime
from utils.admin_dashboard import send_batch_payout_notification, send_daily_platform_summary
from utils.logger import log_event


def send_hourly_payout_summary():
    """Send summary every hour if there are pending payouts"""
    try:
        log_event("SCHEDULER", "Running hourly payout summary check...")
        result = send_batch_payout_notification()
        if result:
            log_event("SCHEDULER", "✅ Hourly payout summary sent")
        else:
            log_event("SCHEDULER", "⏭️ No pending payouts, skipping notification")
    except Exception as e:
        log_event("SCHEDULER", f"❌ Error in hourly summary: {e}")


def send_daily_summary():
    """Send daily platform summary at 9 AM UTC"""
    try:
        log_event("SCHEDULER", "Running daily platform summary...")
        result = send_daily_platform_summary()
        if result:
            log_event("SCHEDULER", "✅ Daily summary sent")
        else:
            log_event("SCHEDULER", "❌ Failed to send daily summary")
    except Exception as e:
        log_event("SCHEDULER", f"❌ Error in daily summary: {e}")


def run_scheduler():
    """Run the scheduled task manager"""
    log_event("SCHEDULER", "🕐 Starting scheduled task manager...")
    
    # Schedule hourly payout summaries (every hour)
    schedule.every().hour.at(":00").do(send_hourly_payout_summary)
    
    # Schedule daily summary at 9 AM UTC
    schedule.every().day.at("09:00").do(send_daily_summary)
    
    log_event("SCHEDULER", "✅ Tasks scheduled:")
    log_event("SCHEDULER", "  • Hourly payout summary: Every hour at :00")
    log_event("SCHEDULER", "  • Daily platform summary: Every day at 09:00 UTC")
    
    # Run the scheduler loop
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            log_event("SCHEDULER", "⏹️ Scheduler stopped by user")
            break
        except Exception as e:
            log_event("SCHEDULER", f"❌ Scheduler error: {e}")
            time.sleep(60)  # Wait a minute before retry


if __name__ == "__main__":
    run_scheduler()
