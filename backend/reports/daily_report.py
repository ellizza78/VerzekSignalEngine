"""
Daily Trading Report
Generates and broadcasts daily performance summary to Trial group + API endpoint
"""
import os
import sys
from datetime import datetime, timedelta
from sqlalchemy import func

# Add parent directory to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from db import SessionLocal
from models import TradeLog, Position
from broadcast import broadcast_event
from utils.logger import api_logger


def generate_daily_report():
    """Generate daily trading report for last 24 hours"""
    try:
        db = SessionLocal()
        
        # Get timestamp for 24 hours ago
        yesterday = datetime.utcnow() - timedelta(hours=24)
        
        # Get trade logs from last 24h
        trades = db.query(TradeLog).filter(TradeLog.created_at >= yesterday).all()
        
        # Get positions closed in last 24h
        closed_positions = db.query(Position).filter(
            Position.closed_at >= yesterday,
            Position.status.in_(['CLOSED', 'STOPPED'])
        ).all()
        
        # Calculate stats
        total_trades = len(closed_positions)
        winning_trades = len([p for p in closed_positions if p.pnl_usdt > 0])
        losing_trades = len([p for p in closed_positions if p.pnl_usdt < 0])
        
        total_pnl = sum(p.pnl_usdt for p in closed_positions)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Count TP hits and SL hits
        tp_hits = len([t for t in trades if t.type == 'TP_HIT'])
        sl_hits = len([t for t in trades if t.type == 'SL_HIT'])
        
        report_data = {
            "date": datetime.utcnow().strftime("%Y-%m-%d"),
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "total_pnl_usdt": round(total_pnl, 2),
            "win_rate_pct": round(win_rate, 2),
            "tp_hits": tp_hits,
            "sl_hits": sl_hits
        }
        
        db.close()
        
        return report_data
        
    except Exception as e:
        api_logger.error(f"Generate daily report error: {e}")
        return None


def broadcast_daily_report():
    """Generate and broadcast daily report to Telegram"""
    report = generate_daily_report()
    
    if not report:
        api_logger.error("Failed to generate daily report")
        return
    
    message = f"""
📊 <b>VERZEK DAILY TRADING REPORT</b>
📅 {report['date']}

<b>Performance Summary:</b>
• Total Trades: {report['total_trades']}
• Win Rate: {report['win_rate_pct']}%
• Wins: {report['winning_trades']} | Losses: {report['losing_trades']}

<b>Profit/Loss:</b>
• Total PnL: {report['total_pnl_usdt']:.2f} USDT

<b>Events:</b>
• Take-Profit Hits: {report['tp_hits']}
• Stop-Loss Hits: {report['sl_hits']}

🚀 <i>Auto-trading available for Premium users</i>
    """.strip()
    
    # Broadcast to Trial group (visible to all)
    broadcast_event(message, target="trial")
    
    api_logger.info("Daily report broadcasted to Telegram")


# Store latest report for API access
_latest_report = None


def get_latest_report():
    """Get the latest daily report"""
    global _latest_report
    if not _latest_report or datetime.utcnow().hour == 0:  # Refresh at midnight
        _latest_report = generate_daily_report()
    return _latest_report


if __name__ == "__main__":
    # Run report generation and broadcast
    broadcast_daily_report()
