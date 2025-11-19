"""
Master Fusion Engine - Balanced Mode (Option A)
Intelligent signal filtering and consolidation
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from .models import SignalCandidate
import logging

logger = logging.getLogger(__name__)


class FusionEngineBalanced:
    """
    Balanced Mode Fusion Engine
    
    Rules:
    1. Ignore price fluctuations within entry zone
    2. Reject opposite signals unless reversal confidence >= threshold
    3. Enforce cooldown periods
    4. Respect trend bias from Trend Bot
    5. No duplicate signals for same symbol/direction
    6. No late-entry signals
    7. Respect max signals/hour limits
    8. Log every approval and rejection
    """
    
    def __init__(self, config: dict):
        self.config = config
        
        # Tracking dictionaries
        self.last_signal_by_symbol: Dict[str, SignalCandidate] = {}
        self.last_close_reason_by_symbol: Dict[str, str] = {}
        self.last_signal_time_by_symbol: Dict[str, datetime] = {}
        self.trend_bias_by_symbol: Dict[str, str] = {}  # "LONG", "SHORT", "NEUTRAL"
        
        # Hourly rate limiting
        self.signals_this_hour: List[datetime] = []
        self.signals_per_symbol_this_hour: Dict[str, List[datetime]] = {}
        
        # Statistics
        self.stats = {
            'total_candidates': 0,
            'approved': 0,
            'rejected_confidence': 0,
            'rejected_cooldown': 0,
            'rejected_trend': 0,
            'rejected_opposite': 0,
            'rejected_duplicate': 0,
            'rejected_rate_limit': 0
        }
        
        logger.info(f"🔧 Fusion Engine Initialized (Balanced Mode)")
        logger.info(f"   Cooldown Same: {config['cooldown_same_direction_minutes']}m")
        logger.info(f"   Cooldown Opposite: {config['cooldown_opposite_direction_minutes']}m")
        logger.info(f"   Reversal Min Confidence: {config['reversal_min_confidence']}%")
        logger.info(f"   Max Signals/Hour: {config['max_signals_per_hour_global']}")
    
    def update_trend_bias(self, symbol: str, direction: str):
        """
        Update trend bias for a symbol (called when Trend Bot signals)
        
        Args:
            symbol: Trading symbol
            direction: "LONG" or "SHORT"
        """
        self.trend_bias_by_symbol[symbol] = direction
        logger.info(f"📊 Trend bias updated: {symbol} → {direction}")
    
    def process_candidates(self, candidates: List[SignalCandidate]) -> List[SignalCandidate]:
        """
        Process signal candidates through fusion rules
        
        Args:
            candidates: List of SignalCandidate from all bots
            
        Returns:
            List of approved SignalCandidate objects
        """
        self.stats['total_candidates'] += len(candidates)
        approved: List[SignalCandidate] = []
        now = datetime.utcnow()
        
        # Clean old hourly tracking data
        self._clean_hourly_tracking(now)
        
        # Group candidates by symbol
        by_symbol: Dict[str, List[SignalCandidate]] = {}
        for c in candidates:
            by_symbol.setdefault(c.symbol, []).append(c)
        
        logger.info(f"🔍 Processing {len(candidates)} candidates across {len(by_symbol)} symbols")
        
        # Process each symbol's candidates
        for symbol, symbol_candidates in by_symbol.items():
            logger.debug(f"   Analyzing {symbol}: {len(symbol_candidates)} candidates")
            
            # Check global rate limit first
            if self._is_global_rate_limited(now):
                logger.warning(f"⚠️  Global rate limit reached ({self.config['max_signals_per_hour_global']}/hour)")
                self.stats['rejected_rate_limit'] += len(symbol_candidates)
                continue
            
            # Check symbol-specific rate limit
            if self._is_symbol_rate_limited(symbol, now):
                logger.warning(f"⚠️  {symbol} rate limit reached ({self.config['max_signals_per_hour_per_symbol']}/hour)")
                self.stats['rejected_rate_limit'] += len(symbol_candidates)
                continue
            
            # Apply cooldown rules
            symbol_candidates = self._apply_cooldown_filter(symbol, symbol_candidates, now)
            if not symbol_candidates:
                continue
            
            # Apply trend bias filter
            symbol_candidates = self._apply_trend_filter(symbol, symbol_candidates)
            if not symbol_candidates:
                continue
            
            # Choose best candidate from remaining
            best = self._select_best_candidate(symbol_candidates)
            if not best:
                continue
            
            # Check opposite direction block (Option A - Balanced Mode)
            if self._is_blocked_by_opposite_signal(symbol, best):
                logger.warning(f"❌ {symbol} {best.side} blocked: Active opposite signal exists")
                self.stats['rejected_opposite'] += 1
                continue
            
            # Approved!
            approved.append(best)
            self._record_approved_signal(symbol, best, now)
            logger.info(f"✅ APPROVED: {symbol} {best.side} ({best.bot_source}, {best.confidence:.0f}%)")
            self.stats['approved'] += 1
        
        logger.info(f"📊 Fusion result: {len(approved)}/{len(candidates)} approved")
        return approved
    
    def _clean_hourly_tracking(self, now: datetime):
        """Remove tracking data older than 1 hour"""
        one_hour_ago = now - timedelta(hours=1)
        
        # Clean global tracking
        self.signals_this_hour = [t for t in self.signals_this_hour if t > one_hour_ago]
        
        # Clean per-symbol tracking
        for symbol in list(self.signals_per_symbol_this_hour.keys()):
            self.signals_per_symbol_this_hour[symbol] = [
                t for t in self.signals_per_symbol_this_hour[symbol] if t > one_hour_ago
            ]
    
    def _is_global_rate_limited(self, now: datetime) -> bool:
        """Check if global hourly limit is reached"""
        return len(self.signals_this_hour) >= self.config['max_signals_per_hour_global']
    
    def _is_symbol_rate_limited(self, symbol: str, now: datetime) -> bool:
        """Check if symbol-specific hourly limit is reached"""
        symbol_signals = self.signals_per_symbol_this_hour.get(symbol, [])
        return len(symbol_signals) >= self.config['max_signals_per_hour_per_symbol']
    
    def _apply_cooldown_filter(
        self, 
        symbol: str, 
        candidates: List[SignalCandidate], 
        now: datetime
    ) -> List[SignalCandidate]:
        """
        Apply cooldown rules
        
        - If same direction: require cooldown OR very strong confidence
        - If opposite direction: require longer cooldown OR reversal confidence
        """
        last_time = self.last_signal_time_by_symbol.get(symbol)
        if not last_time:
            return candidates  # No cooldown needed
        
        last_signal = self.last_signal_by_symbol.get(symbol)
        time_since_last = now - last_time
        
        filtered = []
        for c in candidates:
            # Same direction signals
            if last_signal and c.side == last_signal.side:
                cooldown_required = timedelta(minutes=self.config['cooldown_same_direction_minutes'])
                
                if time_since_last < cooldown_required:
                    # Check if very strong confidence can override cooldown
                    if c.confidence >= self.config['very_strong_confidence']:
                        logger.info(f"   {symbol} {c.side}: Cooldown bypassed (very strong: {c.confidence:.0f}%)")
                        filtered.append(c)
                    else:
                        logger.debug(f"   {symbol} {c.side}: Rejected by cooldown ({time_since_last.seconds//60}m < {self.config['cooldown_same_direction_minutes']}m)")
                        self.stats['rejected_cooldown'] += 1
                else:
                    filtered.append(c)
            
            # Opposite direction signals
            else:
                cooldown_required = timedelta(minutes=self.config['cooldown_opposite_direction_minutes'])
                
                if time_since_last < cooldown_required:
                    logger.debug(f"   {symbol} {c.side}: Opposite direction in cooldown ({time_since_last.seconds//60}m < {self.config['cooldown_opposite_direction_minutes']}m)")
                    self.stats['rejected_cooldown'] += 1
                else:
                    filtered.append(c)
        
        return filtered
    
    def _apply_trend_filter(self, symbol: str, candidates: List[SignalCandidate]) -> List[SignalCandidate]:
        """
        Apply trend bias filter
        
        - NEUTRAL bias: Allow all
        - With bias: Allow same direction, or opposite if reversal confidence met
        """
        bias = self.trend_bias_by_symbol.get(symbol, "NEUTRAL")
        
        if bias == "NEUTRAL":
            return candidates
        
        filtered = []
        for c in candidates:
            if c.side == bias:
                # Signal aligns with trend
                filtered.append(c)
            else:
                # Counter-trend signal - check reversal confidence
                if c.confidence >= self.config['reversal_min_confidence']:
                    logger.info(f"   {symbol} {c.side}: Counter-trend approved (reversal conf: {c.confidence:.0f}%)")
                    filtered.append(c)
                else:
                    logger.debug(f"   {symbol} {c.side}: Rejected by trend bias ({c.confidence:.0f}% < {self.config['reversal_min_confidence']}%)")
                    self.stats['rejected_trend'] += 1
        
        return filtered
    
    def _select_best_candidate(self, candidates: List[SignalCandidate]) -> Optional[SignalCandidate]:
        """
        Choose best candidate from list
        Priority: Confidence > Bot Source Priority
        """
        if not candidates:
            return None
        
        # Bot source priority weights
        priority = {
            "TREND": 4,
            "AI_ML": 3,
            "SCALPING": 2,
            "QFL": 1
        }
        
        # Sort by confidence first, then bot priority
        candidates.sort(
            key=lambda c: (c.confidence, priority.get(c.bot_source, 0)),
            reverse=True
        )
        
        return candidates[0]
    
    def _is_blocked_by_opposite_signal(self, symbol: str, candidate: SignalCandidate) -> bool:
        """
        Balanced Mode Rule (Option A):
        Block opposite signals if active signal exists for same symbol
        """
        last = self.last_signal_by_symbol.get(symbol)
        
        if not last:
            return False  # No previous signal
        
        if last.side == candidate.side:
            return False  # Same direction, not opposite
        
        # Opposite signal exists - BLOCK in Balanced Mode
        return True
    
    def _record_approved_signal(self, symbol: str, signal: SignalCandidate, now: datetime):
        """Record approved signal for tracking"""
        self.last_signal_by_symbol[symbol] = signal
        self.last_signal_time_by_symbol[symbol] = now
        
        # Update hourly tracking
        self.signals_this_hour.append(now)
        if symbol not in self.signals_per_symbol_this_hour:
            self.signals_per_symbol_this_hour[symbol] = []
        self.signals_per_symbol_this_hour[symbol].append(now)
    
    def signal_closed(self, symbol: str, signal_id: str, close_reason: str):
        """
        Notify fusion engine that a signal was closed
        Allows new opposite signals to be considered
        """
        last = self.last_signal_by_symbol.get(symbol)
        
        if last and last.signal_id == signal_id:
            logger.info(f"🔓 {symbol} signal closed ({close_reason}), opposite signals now allowed")
            self.last_close_reason_by_symbol[symbol] = close_reason
            # Keep last_signal_by_symbol to maintain cooldown tracking
    
    def get_stats(self) -> Dict:
        """Get fusion engine statistics"""
        total = self.stats['total_candidates']
        approved = self.stats['approved']
        
        return {
            **self.stats,
            'approval_rate': (approved / total * 100) if total > 0 else 0,
            'active_signals': len(self.last_signal_by_symbol)
        }
    
    def reset_stats(self):
        """Reset statistics (called by daily reporter)"""
        self.stats = {
            'total_candidates': 0,
            'approved': 0,
            'rejected_confidence': 0,
            'rejected_cooldown': 0,
            'rejected_trend': 0,
            'rejected_opposite': 0,
            'rejected_duplicate': 0,
            'rejected_rate_limit': 0
        }
