"""
Trend-Following Bot - 1H/4H Strong Moves
Captures sustained directional movements
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from engine.base_strategy import BaseStrategy
from core.models import SignalCandidate
from common.indicators import Indicators
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TrendBot(BaseStrategy):
    """
    Trend-following strategy for larger 1-4 hour moves
    
    Entry Conditions (LONG):
    - MA50 > MA100 > MA200 (aligned bullish)
    - MACD crosses above signal line
    - Price making higher highs and higher lows
    - Strong volume confirmation
    
    Entry Conditions (SHORT):
    - MA50 < MA100 < MA200 (aligned bearish)
    - MACD crosses below signal line
    - Price making lower highs and lower lows
    - Strong volume confirmation
    """
    
    def __init__(self, config: dict):
        super().__init__("Trend Bot", config)
        self.timeframe = config.get('primary_timeframe', '1h')
        self.min_confidence = config.get('confidence_threshold', 75)
        
    async def analyze(self, symbol: str) -> Optional[SignalCandidate]:
        """Analyze symbol for trend-following opportunities"""
        try:
            # Fetch market data
            df = self.fetch_market_data(symbol, self.timeframe, limit=250)
            if df is None:
                return None
            
            # Check cooldown (longer for trend bot)
            if not self.should_generate_signal(symbol, cooldown_minutes=30):
                return None
            
            # Calculate indicators
            ma50 = self.indicators.moving_average(df, 50, 'EMA')
            ma100 = self.indicators.moving_average(df, 100, 'EMA')
            ma200 = self.indicators.moving_average(df, 200, 'SMA')
            macd_line, signal_line, histogram = self.indicators.macd(df)
            atr = self.indicators.atr(df, period=14)
            
            current_price = df['close'].iloc[-1]
            
            # Check trend alignment
            trend_direction = self._detect_trend_alignment(
                ma50.iloc[-1], ma100.iloc[-1], ma200.iloc[-1], current_price
            )
            
            if trend_direction == 'NONE':
                return None
            
            # Check for MACD confirmation
            macd_signal = self._check_macd_cross(
                macd_line.iloc[-1], signal_line.iloc[-1],
                macd_line.iloc[-2], signal_line.iloc[-2]
            )
            
            # Check price structure (higher highs/lows or lower highs/lows)
            price_structure = self._analyze_price_structure(df, lookback=20)
            
            # Generate signal if conditions align
            if trend_direction == 'BULLISH' and macd_signal == 'BULLISH' and price_structure == 'BULLISH':
                confidence = self._calculate_confidence(
                    trend_direction, macd_signal, price_structure, histogram.iloc[-1]
                )
                
                if confidence >= self.min_confidence:
                    signal = self._create_signal(
                        symbol, 'LONG', current_price, confidence, atr.iloc[-1]
                    )
                    
                    if self.validate_signal(signal):
                        self.record_signal(symbol)
                        self.log_signal(signal)
                        return signal
            
            elif trend_direction == 'BEARISH' and macd_signal == 'BEARISH' and price_structure == 'BEARISH':
                confidence = self._calculate_confidence(
                    trend_direction, macd_signal, price_structure, histogram.iloc[-1]
                )
                
                if confidence >= self.min_confidence:
                    signal = self._create_signal(
                        symbol, 'SHORT', current_price, confidence, atr.iloc[-1]
                    )
                    
                    if self.validate_signal(signal):
                        self.record_signal(symbol)
                        self.log_signal(signal)
                        return signal
            
            return None
            
        except Exception as e:
            logger.error(f"Trend bot error analyzing {symbol}: {e}")
            return None
    
    def _detect_trend_alignment(self, ma50, ma100, ma200, price) -> str:
        """
        Detect if MAs are aligned for strong trend
        Returns: 'BULLISH', 'BEARISH', or 'NONE'
        """
        # Bullish alignment: MA50 > MA100 > MA200 and price > MA50
        if ma50 > ma100 > ma200 and price > ma50:
            return 'BULLISH'
        
        # Bearish alignment: MA50 < MA100 < MA200 and price < MA50
        if ma50 < ma100 < ma200 and price < ma50:
            return 'BEARISH'
        
        return 'NONE'
    
    def _check_macd_cross(self, macd_now, signal_now, macd_prev, signal_prev) -> str:
        """
        Check for MACD crossover
        Returns: 'BULLISH', 'BEARISH', or 'NONE'
        """
        # Bullish cross: MACD crosses above signal
        if macd_prev <= signal_prev and macd_now > signal_now:
            return 'BULLISH'
        
        # Bearish cross: MACD crosses below signal
        if macd_prev >= signal_prev and macd_now < signal_now:
            return 'BEARISH'
        
        # No cross but check if already in favorable position
        if macd_now > signal_now and macd_now > 0:
            return 'BULLISH'
        
        if macd_now < signal_now and macd_now < 0:
            return 'BEARISH'
        
        return 'NONE'
    
    def _analyze_price_structure(self, df, lookback=20) -> str:
        """
        Analyze if price is making higher highs/lows or lower highs/lows
        Returns: 'BULLISH', 'BEARISH', or 'NEUTRAL'
        """
        recent = df.tail(lookback)
        
        # Find swing highs and lows
        highs = recent['high'].values
        lows = recent['low'].values
        
        # Simple structure: compare first half vs second half
        mid_point = lookback // 2
        first_half_high = max(highs[:mid_point])
        second_half_high = max(highs[mid_point:])
        first_half_low = min(lows[:mid_point])
        second_half_low = min(lows[mid_point:])
        
        # Higher highs and higher lows = bullish structure
        if second_half_high > first_half_high and second_half_low > first_half_low:
            return 'BULLISH'
        
        # Lower highs and lower lows = bearish structure
        if second_half_high < first_half_high and second_half_low < first_half_low:
            return 'BEARISH'
        
        return 'NEUTRAL'
    
    def _calculate_confidence(self, trend, macd_signal, structure, histogram) -> float:
        """Calculate signal confidence score"""
        confidence = 60.0  # Base confidence
        
        # All indicators aligned = high confidence
        if trend != 'NONE' and macd_signal != 'NONE' and structure != 'NEUTRAL':
            confidence += 20
        
        # Strong MACD histogram adds confidence
        if abs(histogram) > 0.5:
            confidence += 10
        
        # Triple confirmation
        if (trend == 'BULLISH' and macd_signal == 'BULLISH' and structure == 'BULLISH') or \
           (trend == 'BEARISH' and macd_signal == 'BEARISH' and structure == 'BEARISH'):
            confidence += 15
        
        return min(confidence, 92.0)
    
    def _create_signal(self, symbol, direction, entry_price, confidence, atr) -> Signal:
        """Create a signal object with TP/SL based on ATR"""
        # Trend bot uses larger TP/SL
        if direction == 'LONG':
            tp_pct = 3.0  # 3% profit target
            sl_pct = 1.5  # 1.5% stop loss
        else:
            tp_pct = 3.0
            sl_pct = 1.5
        
        tp_price, sl_price = self.calculate_tp_sl(
            entry_price, direction, tp_pct, sl_pct
        )
        
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
                'strategy_type': 'trend_following',
                'tp_pct': tp_pct,
                'sl_pct': sl_pct,
                'atr': float(atr)
            }
        )
