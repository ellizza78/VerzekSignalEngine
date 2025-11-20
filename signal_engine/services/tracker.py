"""
Signal Tracker - SQLite Database for Signal Performance Tracking
Tracks opened and closed signals for performance analysis
"""
import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Dict
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core.models import SignalCandidate, SignalOutcome

logger = logging.getLogger(__name__)


class SignalTracker:
    """Tracks signal performance using SQLite database"""
    
    def __init__(self, db_path='./data/signals.db'):
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()
        logger.info(f"✅ Signal Tracker initialized (DB: {db_path})")
    
    def _ensure_db_directory(self):
        """Create data directory if it doesn't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _init_database(self):
        """Initialize SQLite database with signals table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signals (
                signal_id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                entry_price REAL NOT NULL,
                tp_pct REAL NOT NULL,
                sl_pct REAL NOT NULL,
                confidence REAL NOT NULL,
                bot_source TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                opened_at TEXT NOT NULL,
                closed_at TEXT,
                exit_price REAL,
                profit_pct REAL,
                duration_seconds INTEGER,
                close_reason TEXT,
                status TEXT DEFAULT 'ACTIVE',
                current_tp_index INTEGER DEFAULT 0,
                total_tps INTEGER DEFAULT 5,
                partial_profits TEXT DEFAULT '[]'
            )
        ''')
        
        # Create indices for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_status ON signals(status)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_opened_at ON signals(opened_at)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_bot_source ON signals(bot_source)
        ''')
        
        # Migration: Add multi-TP columns if they don't exist
        try:
            cursor.execute("PRAGMA table_info(signals)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'current_tp_index' not in columns:
                cursor.execute('ALTER TABLE signals ADD COLUMN current_tp_index INTEGER DEFAULT 0')
                logger.info("✅ Added current_tp_index column to signals table")
            
            if 'total_tps' not in columns:
                cursor.execute('ALTER TABLE signals ADD COLUMN total_tps INTEGER DEFAULT 5')
                logger.info("✅ Added total_tps column to signals table")
            
            if 'partial_profits' not in columns:
                cursor.execute("ALTER TABLE signals ADD COLUMN partial_profits TEXT DEFAULT '[]'")
                logger.info("✅ Added partial_profits column to signals table")
        except Exception as e:
            logger.error(f"Migration error: {e}")
        
        conn.commit()
        conn.close()
    
    def open_signal(self, candidate: SignalCandidate) -> bool:
        """
        Record a new opened signal
        
        Args:
            candidate: SignalCandidate from fusion engine
            
        Returns:
            True if successfully recorded
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Validate take_profits list
            if not candidate.take_profits or len(candidate.take_profits) == 0:
                logger.error(f"Cannot track signal {candidate.signal_id[:8]}: empty take_profits list")
                conn.close()
                return False
            
            # Calculate TP/SL percentages from prices for tracking
            if candidate.side in ['LONG', 'BUY']:
                tp_pct = ((candidate.take_profits[0] - candidate.entry) / candidate.entry) * 100
                sl_pct = ((candidate.entry - candidate.stop_loss) / candidate.entry) * 100
            else:  # SHORT/SELL
                tp_pct = ((candidate.entry - candidate.take_profits[0]) / candidate.entry) * 100
                sl_pct = ((candidate.stop_loss - candidate.entry) / candidate.entry) * 100
            
            cursor.execute('''
                INSERT INTO signals (
                    signal_id, symbol, side, entry_price, tp_pct, sl_pct,
                    confidence, bot_source, timeframe, opened_at, status,
                    current_tp_index, total_tps, partial_profits
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                candidate.signal_id,
                candidate.symbol,
                candidate.side,
                candidate.entry,
                tp_pct,
                sl_pct,
                candidate.confidence,
                candidate.bot_source,
                candidate.timeframe,
                candidate.created_at.isoformat(),
                'ACTIVE',
                0,  # current_tp_index starts at 0
                len(candidate.take_profits),  # total_tps (should be 5)
                '[]'  # partial_profits starts empty
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"📊 Tracked signal: {candidate.signal_id[:8]} ({candidate.symbol} {candidate.side})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to track signal {candidate.signal_id}: {e}")
            return False
    
    def close_signal(
        self,
        signal_id: str,
        exit_price: float,
        close_reason: str
    ) -> Optional[SignalOutcome]:
        """
        Close an active signal and return outcome
        
        Args:
            signal_id: Signal ID to close
            exit_price: Exit price
            close_reason: Reason for closure (TP/SL/CANCEL)
            
        Returns:
            SignalOutcome if successful, None otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get signal data
            cursor.execute('''
                SELECT symbol, side, entry_price, opened_at, bot_source
                FROM signals WHERE signal_id = ? AND status = 'ACTIVE'
            ''', (signal_id,))
            
            row = cursor.fetchone()
            if not row:
                logger.warning(f"Signal {signal_id[:8]} not found or already closed")
                conn.close()
                return None
            
            symbol, side, entry_price, opened_at, bot_source = row
            
            # Calculate profit percentage
            if side in ['LONG', 'BUY']:
                profit_pct = ((exit_price - entry_price) / entry_price) * 100
            else:  # SHORT/SELL
                profit_pct = ((entry_price - exit_price) / entry_price) * 100
            
            # Calculate duration
            opened_time = datetime.fromisoformat(opened_at)
            closed_time = datetime.now()
            duration_seconds = int((closed_time - opened_time).total_seconds())
            
            # Update database
            cursor.execute('''
                UPDATE signals SET
                    closed_at = ?,
                    exit_price = ?,
                    profit_pct = ?,
                    duration_seconds = ?,
                    close_reason = ?,
                    status = 'CLOSED'
                WHERE signal_id = ?
            ''', (
                closed_time.isoformat(),
                exit_price,
                profit_pct,
                duration_seconds,
                close_reason,
                signal_id
            ))
            
            conn.commit()
            conn.close()
            
            # Create outcome
            outcome = SignalOutcome(
                signal_id=signal_id,
                symbol=symbol,
                side=side,
                entry=entry_price,
                exit_price=exit_price,
                profit_pct=profit_pct,
                close_reason=close_reason,
                opened_at=opened_time,
                closed_at=closed_time,
                bot_source=bot_source
            )
            
            logger.info(
                f"📈 Closed signal {signal_id[:8]}: {symbol} {side} "
                f"{profit_pct:+.2f}% ({close_reason})"
            )
            
            return outcome
            
        except Exception as e:
            logger.error(f"Failed to close signal {signal_id}: {e}")
            return None
    
    def on_target_hit(
        self,
        signal_id: str,
        hit_price: float,
        tp_number: int = None
    ) -> Optional[SignalOutcome]:
        """
        Record a take-profit target hit (partial or final) with sequential validation
        
        For TP1-TP4: Updates partial_profits and current_tp_index, keeps signal ACTIVE
        For TP5: Closes the signal completely
        
        Args:
            signal_id: Signal ID
            hit_price: Price at which TP was hit
            tp_number: Optional TP number (1-5) for validation
            
        Returns:
            SignalOutcome with is_final=False for partial TP, is_final=True for TP5
        """
        try:
            import json
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get signal data
            cursor.execute('''
                SELECT symbol, side, entry_price, opened_at, bot_source,
                       current_tp_index, total_tps, partial_profits
                FROM signals WHERE signal_id = ? AND status = 'ACTIVE'
            ''', (signal_id,))
            
            row = cursor.fetchone()
            if not row:
                logger.error(f"Signal {signal_id[:8]} not found or already closed - cannot record TP hit")
                conn.close()
                return None
            
            symbol, side, entry_price, opened_at, bot_source, current_tp_index, total_tps, partial_profits_json = row
            
            # Parse partial_profits list
            partial_profits = json.loads(partial_profits_json) if partial_profits_json else []
            
            # SEQUENTIAL VALIDATION: Enforce TP order
            expected_tp_number = current_tp_index + 1  # Next expected TP (1-based)
            
            if tp_number is not None and tp_number != expected_tp_number:
                logger.error(
                    f"⚠️  OUT-OF-ORDER TP HIT REJECTED: {signal_id[:8]} "
                    f"Expected TP{expected_tp_number}, got TP{tp_number}. "
                    f"TPs must be hit sequentially."
                )
                conn.close()
                return None
            
            # Validate we haven't already completed all TPs
            if current_tp_index >= total_tps:
                logger.error(
                    f"⚠️  INVALID TP HIT: {signal_id[:8]} already completed all {total_tps} TPs"
                )
                conn.close()
                return None
            
            # Calculate CUMULATIVE profit percentage from entry to THIS target
            # Note: partial_profits stores cumulative profit, not incremental
            # TP1: +2%, TP2: +4%, TP3: +6%, etc. (cumulative from entry)
            if side in ['LONG', 'BUY']:
                cumulative_profit_pct = ((hit_price - entry_price) / entry_price) * 100
            else:  # SHORT/SELL
                cumulative_profit_pct = ((entry_price - hit_price) / entry_price) * 100
            
            # Add to partial_profits list (stores cumulative profit at each TP)
            partial_profits.append(cumulative_profit_pct)
            new_tp_index = current_tp_index + 1
            
            # Use profit_pct as the variable name for consistency
            profit_pct = cumulative_profit_pct
            
            # Calculate duration
            opened_time = datetime.fromisoformat(opened_at)
            current_time = datetime.now()
            duration_seconds = int((current_time - opened_time).total_seconds())
            
            # CRITICAL: Only mark as final if this is truly the LAST TP
            is_final = new_tp_index >= total_tps
            
            if is_final:
                # TP5 - Close the signal completely
                cursor.execute('''
                    UPDATE signals SET
                        closed_at = ?,
                        exit_price = ?,
                        profit_pct = ?,
                        duration_seconds = ?,
                        close_reason = 'TP',
                        status = 'CLOSED',
                        current_tp_index = ?,
                        partial_profits = ?
                    WHERE signal_id = ?
                ''', (
                    current_time.isoformat(),
                    hit_price,
                    profit_pct,
                    duration_seconds,
                    new_tp_index,
                    json.dumps(partial_profits),
                    signal_id
                ))
                
                logger.info(
                    f"🎯 TP5 HIT (FINAL): {signal_id[:8]} ({symbol} {side}) "
                    f"{profit_pct:+.2f}% - SIGNAL CLOSED"
                )
            else:
                # TP1-TP4 - Partial TP, keep signal ACTIVE
                cursor.execute('''
                    UPDATE signals SET
                        current_tp_index = ?,
                        partial_profits = ?
                    WHERE signal_id = ?
                ''', (
                    new_tp_index,
                    json.dumps(partial_profits),
                    signal_id
                ))
                
                logger.info(
                    f"🎯 TP{new_tp_index} HIT (Partial): {signal_id[:8]} ({symbol} {side}) "
                    f"{profit_pct:+.2f}% - Signal still ACTIVE"
                )
            
            conn.commit()
            conn.close()
            
            # Create outcome (is_final flag determines if signal is fully closed)
            outcome = SignalOutcome(
                signal_id=signal_id,
                symbol=symbol,
                side=side,
                entry=entry_price,
                exit_price=hit_price,
                profit_pct=profit_pct,
                close_reason='TP',
                opened_at=opened_time,
                closed_at=current_time,
                bot_source=bot_source,
                current_tp_index=new_tp_index - 1,  # 0-indexed (0=TP1, 4=TP5)
                total_tps=total_tps,
                partial_profits=partial_profits
            )
            
            return outcome
            
        except Exception as e:
            logger.error(f"Failed to record TP hit for {signal_id}: {e}")
            return None
    
    def get_active_signals(self) -> List[Dict]:
        """Get all active signals"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM signals WHERE status = 'ACTIVE'
                ORDER BY opened_at DESC
            ''')
            
            rows = cursor.fetchall()
            conn.close()
            
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get active signals: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """
        Get overall signal statistics
        
        Returns:
            Dictionary with overall statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get counts
            cursor.execute('SELECT COUNT(*) FROM signals WHERE status = "ACTIVE"')
            active_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM signals WHERE status = "CLOSED"')
            closed_count = cursor.fetchone()[0]
            
            # Get win rate and avg profit for closed signals
            cursor.execute('''
                SELECT
                    SUM(CASE WHEN profit_pct > 0 THEN 1 ELSE 0 END) as winners,
                    AVG(profit_pct) as avg_profit
                FROM signals
                WHERE status = 'CLOSED'
            ''')
            
            row = cursor.fetchone()
            conn.close()
            
            winners = row[0] or 0
            avg_profit = row[1] or 0.0
            
            total_signals = active_count + closed_count
            win_rate = (winners / closed_count * 100) if closed_count > 0 else 0.0
            
            return {
                'active_signals': active_count,
                'closed_signals': closed_count,
                'total_signals': total_signals,
                'win_rate': round(win_rate, 2),
                'avg_profit': round(avg_profit, 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {
                'active_signals': 0,
                'closed_signals': 0,
                'total_signals': 0,
                'win_rate': 0.0,
                'avg_profit': 0.0
            }
    
    def get_daily_stats(self, date: Optional[str] = None) -> Dict:
        """
        Get performance statistics for a specific day with TP1-TP5 breakdown
        
        Args:
            date: Date in YYYY-MM-DD format (defaults to today)
            
        Returns:
            Dictionary with daily statistics including TP level breakdown
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all closed signals for the day
            cursor.execute('''
                SELECT
                    COUNT(*) as total_signals,
                    SUM(CASE WHEN close_reason = 'TP' THEN 1 ELSE 0 END) as tp_count,
                    SUM(CASE WHEN close_reason = 'SL' THEN 1 ELSE 0 END) as sl_count,
                    SUM(CASE WHEN close_reason = 'CANCEL' THEN 1 ELSE 0 END) as cancel_count,
                    AVG(profit_pct) as avg_profit,
                    MAX(profit_pct) as best_trade,
                    MIN(profit_pct) as worst_trade,
                    AVG(duration_seconds) as avg_duration,
                    SUM(CASE WHEN profit_pct > 0 THEN 1 ELSE 0 END) as winners,
                    SUM(CASE WHEN profit_pct < 0 THEN 1 ELSE 0 END) as losers
                FROM signals
                WHERE status = 'CLOSED'
                AND DATE(closed_at) = ?
            ''', (date,))
            
            row = cursor.fetchone()
            
            if not row or row[0] == 0:
                conn.close()
                return {
                    'date': date,
                    'total_signals': 0,
                    'tp_count': 0,
                    'sl_count': 0,
                    'cancel_count': 0,
                    'win_rate': 0.0,
                    'avg_profit': 0.0,
                    'best_trade': 0.0,
                    'worst_trade': 0.0,
                    'avg_duration_minutes': 0,
                    'tp_breakdown': {'TP1': 0, 'TP2': 0, 'TP3': 0, 'TP4': 0, 'TP5': 0},
                    'avg_tp_level': 0.0
                }
            
            total, tp, sl, cancel, avg_profit, best, worst, avg_dur, winners, losers = row
            
            # Get TP1-TP5 breakdown for signals closed with TP
            cursor.execute('''
                SELECT
                    SUM(CASE WHEN current_tp_index = 0 THEN 1 ELSE 0 END) as tp1_count,
                    SUM(CASE WHEN current_tp_index = 1 THEN 1 ELSE 0 END) as tp2_count,
                    SUM(CASE WHEN current_tp_index = 2 THEN 1 ELSE 0 END) as tp3_count,
                    SUM(CASE WHEN current_tp_index = 3 THEN 1 ELSE 0 END) as tp4_count,
                    SUM(CASE WHEN current_tp_index >= 4 THEN 1 ELSE 0 END) as tp5_count,
                    AVG(current_tp_index + 1) as avg_tp_level
                FROM signals
                WHERE status = 'CLOSED'
                AND close_reason = 'TP'
                AND DATE(closed_at) = ?
            ''', (date,))
            
            tp_row = cursor.fetchone()
            conn.close()
            
            # Parse TP breakdown
            if tp_row:
                tp1, tp2, tp3, tp4, tp5, avg_tp = tp_row
                tp_breakdown = {
                    'TP1': tp1 or 0,
                    'TP2': tp2 or 0,
                    'TP3': tp3 or 0,
                    'TP4': tp4 or 0,
                    'TP5': tp5 or 0
                }
                avg_tp_level = avg_tp or 0.0
            else:
                tp_breakdown = {'TP1': 0, 'TP2': 0, 'TP3': 0, 'TP4': 0, 'TP5': 0}
                avg_tp_level = 0.0
            
            win_rate = (winners / total * 100) if total > 0 else 0.0
            avg_duration_minutes = int(avg_dur / 60) if avg_dur else 0
            
            return {
                'date': date,
                'total_signals': total,
                'tp_count': tp or 0,
                'sl_count': sl or 0,
                'cancel_count': cancel or 0,
                'winners': winners or 0,
                'losers': losers or 0,
                'win_rate': win_rate,
                'avg_profit': avg_profit or 0.0,
                'best_trade': best or 0.0,
                'worst_trade': worst or 0.0,
                'avg_duration_minutes': avg_duration_minutes,
                'tp_breakdown': tp_breakdown,
                'avg_tp_level': avg_tp_level
            }
            
        except Exception as e:
            logger.error(f"Failed to get daily stats: {e}")
            return {}


# Singleton instance
_tracker_instance = None

def get_tracker() -> SignalTracker:
    """Get or create tracker instance"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = SignalTracker()
    return _tracker_instance
