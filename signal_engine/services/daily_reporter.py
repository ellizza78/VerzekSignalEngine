"""
Daily Performance Reporter
Generates and sends daily signal performance reports to Telegram
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import os
from services.tracker import get_tracker
from services.telegram_broadcaster import get_broadcaster

logger = logging.getLogger(__name__)


class DailyReporter:
    """Generates daily performance reports"""
    
    def __init__(self):
        self.tracker = get_tracker()
        self.broadcaster = get_broadcaster()
        logger.info("✅ Daily Reporter initialized")
    
    async def generate_and_send_report(self, date: Optional[str] = None):
        """
        Generate daily report and send to VIP Telegram group
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to yesterday)
        """
        if date is None:
            # Default to yesterday's report
            yesterday = datetime.now() - timedelta(days=1)
            date = yesterday.strftime('%Y-%m-%d')
        
        try:
            logger.info(f"📊 Generating daily report for {date}")
            
            # Get statistics from tracker
            stats = self.tracker.get_daily_stats(date)
            
            if stats.get('total_signals', 0) == 0:
                logger.info(f"No closed signals for {date}, skipping report")
                return
            
            # Generate report message
            report = self._format_report(stats)
            
            # Send to VIP and Admin groups
            await self.broadcaster.broadcast_signal(
                report,
                to_groups=['vip', 'admin']
            )
            
            logger.info(f"✅ Daily report sent for {date}")
            
        except Exception as e:
            logger.error(f"Failed to generate daily report: {e}")
    
    def _format_report(self, stats: Dict) -> str:
        """
        Format statistics into Telegram message
        
        Args:
            stats: Statistics dictionary from tracker
            
        Returns:
            Formatted Telegram message
        """
        date = stats['date']
        total = stats['total_signals']
        tp_count = stats['tp_count']
        sl_count = stats['sl_count']
        cancel_count = stats['cancel_count']
        winners = stats['winners']
        losers = stats['losers']
        win_rate = stats['win_rate']
        avg_profit = stats['avg_profit']
        best_trade = stats['best_trade']
        worst_trade = stats['worst_trade']
        avg_duration = stats['avg_duration_minutes']
        
        # Determine performance emoji
        if win_rate >= 70:
            performance_emoji = "🔥"
        elif win_rate >= 60:
            performance_emoji = "✅"
        elif win_rate >= 50:
            performance_emoji = "⚡"
        else:
            performance_emoji = "⚠️"
        
        # Build report message
        report = f"""
{performance_emoji} **DAILY SIGNAL REPORT** {performance_emoji}
📅 **Date:** {date}

**📊 OVERVIEW**
• Total Signals: {total}
• Take-Profit Hits: {tp_count} 🎯
• Stop-Loss Hits: {sl_count} 🛑
• Cancelled: {cancel_count} ❌

**💰 PERFORMANCE**
• Win Rate: {win_rate:.1f}%
• Winners: {winners} ✅
• Losers: {losers} ❌
• Avg Profit: {avg_profit:+.2f}%

**🏆 BEST/WORST**
• Best Trade: {best_trade:+.2f}%
• Worst Trade: {worst_trade:+.2f}%

**⏱️ DURATION**
• Avg Signal Duration: {avg_duration} minutes

━━━━━━━━━━━━━━━━━━
📊 **VerzekSignalEngine v2.0 - Master Fusion Engine**
""".strip()
        
        return report
    
    def _get_performance_summary(self, win_rate: float, avg_profit: float) -> str:
        """Get performance summary text"""
        if win_rate >= 70 and avg_profit > 0:
            return "🔥 Excellent performance! Keep it up!"
        elif win_rate >= 60:
            return "✅ Strong performance today!"
        elif win_rate >= 50:
            return "⚡ Moderate performance."
        else:
            return "⚠️ Review signals and adjust strategies."


# Singleton instance
_reporter_instance = None

def get_reporter() -> DailyReporter:
    """Get or create reporter instance"""
    global _reporter_instance
    if _reporter_instance is None:
        _reporter_instance = DailyReporter()
    return _reporter_instance
