"""
QFL (Quick Fingers Luc) Bot - Deep Dip Sniper
Catches price crashes and bounces back to base
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from engine.base_strategy import BaseStrategy, Signal
from common.indicators import Indicators
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class QFLBot(BaseStrategy):
    """
    QFL strategy for catching deep dips
    
    Entry Conditions (LONG ONLY):
    - Price drops 6-15% from recent base level
    - Volume spike during the drop
    - Quick reversal (hammer candle or strong bounce)
    - Base level identified (consolidation zone)
    
    Exit:
    - TP: Return to base level
    - SL: Below crash low
    """
    
    def __init__(self, config: dict):
        super().__init__("QFL Bot", config)
        self.timeframe = config.get('primary_timeframe', '15m')
        self.min_drop = config.get('drop_threshold_min', 6.0)
        self.max_drop = config.get('drop_threshold_max', 15.0)
        self.base_lookback = config.get('base_lookback_candles', 100)
        self.min_confidence = config.get('confidence_threshold', 80)
        
    async def analyze(self, symbol: str) -> Optional[Signal]:
        """Analyze symbol for QFL opportunities (crashes)"""
        try:
            # Fetch market data
            df = self.fetch_market_data(symbol, self.timeframe, limit=self.base_lookback + 50)
            if df is None:
                return None
            
            # Check cooldown
            if not self.should_generate_signal(symbol, cooldown_minutes=30):
                return None
            
            current_price = df['close'].iloc[-1]
            
            # Step 1: Detect base level
            base_level = self.indicators.detect_qfl_base(df, self.base_lookback)
            if base_level is None:
                return None
            
            # Step 2: Calculate drop percentage from base
            drop_pct = self.indicators.price_drop_pct(df, lookback=50)
            
            # Step 3: Check if drop is within QFL range
            if not (self.min_drop <= abs(drop_pct) <= self.max_drop):
                return None
            
            # Step 4: Check for volume spike
            volume_surge = self.indicators.volume_surge(df, lookback=20, multiplier=2.0)
            if not volume_surge.iloc[-1]:
                return None
            
            # Step 5: Check for reversal signal
            is_hammer = self.indicators.detect_hammer(df)
            is_bounce = self._check_bounce_signal(df)
            
            if not (is_hammer or is_bounce):
                return None
            
            # All QFL conditions met - generate LONG signal
            confidence = self._calculate_confidence(
                drop_pct, volume_surge.iloc[-1], is_hammer, is_bounce
            )
            
            if confidence >= self.min_confidence:
                signal = self._create_qfl_signal(
                    symbol, current_price, base_level, confidence, drop_pct
                )
                
                if self.validate_signal(signal):
                    self.record_signal(symbol)
                    self.log_signal(signal)
                    return signal
            
            return None
            
        except Exception as e:
            logger.error(f"QFL bot error analyzing {symbol}: {e}")
            return None
    
    def _check_bounce_signal(self, df) -> bool:
        """
        Check if price is bouncing (recent low followed by strong green candle)
        """
        if len(df) < 3:
            return False
        
        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]
        
        # Last candle is green and closes in upper 50% of range
        is_green = last_candle['close'] > last_candle['open']
        body_size = abs(last_candle['close'] - last_candle['open'])
        candle_range = last_candle['high'] - last_candle['low']
        
        if candle_range == 0:
            return False
        
        close_in_upper_half = (last_candle['close'] - last_candle['low']) / candle_range > 0.6
        strong_body = body_size / candle_range > 0.5
        
        # Previous candle was red (selling)
        prev_was_red = prev_candle['close'] < prev_candle['open']
        
        return is_green and close_in_upper_half and strong_body and prev_was_red
    
    def _calculate_confidence(self, drop_pct, volume_surge, is_hammer, is_bounce) -> float:
        """Calculate QFL signal confidence"""
        confidence = 70.0  # Base confidence for QFL
        
        # Deeper drop = higher confidence (to a point)
        drop_magnitude = abs(drop_pct)
        if 8 <= drop_magnitude <= 12:
            confidence += 15  # Sweet spot
        elif drop_magnitude > 12:
            confidence += 10  # Very deep, slightly riskier
        else:
            confidence += 5
        
        # Volume surge = higher confidence
        if volume_surge:
            confidence += 10
        
        # Reversal candle patterns
        if is_hammer:
            confidence += 10
        if is_bounce:
            confidence += 5
        
        return min(confidence, 95.0)
    
    def _create_qfl_signal(self, symbol, entry_price, base_level, confidence, drop_pct) -> Signal:
        """Create QFL signal with TP at base level"""
        direction = 'LONG'  # QFL is always LONG
        
        # TP = base level (where price was before the crash)
        tp_price = base_level
        
        # SL = below recent low
        sl_price = entry_price * 0.97  # 3% below entry
        
        # Calculate actual percentages
        tp_pct = ((tp_price - entry_price) / entry_price) * 100
        sl_pct = ((entry_price - sl_price) / entry_price) * 100
        
        return Signal(
            symbol=symbol.replace('/', ''),
            direction=direction,
            entry_price=entry_price,
            tp_price=tp_price,
            sl_price=sl_price,
            strategy_name=f"{self.name} v1",
            timeframe=self.timeframe,
            confidence=confidence,
            metadata={
                'strategy_type': 'qfl',
                'base_level': float(base_level),
                'drop_pct': float(drop_pct),
                'tp_pct': float(tp_pct),
                'sl_pct': float(sl_pct)
            }
        )
