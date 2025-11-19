"""
Scalping Bot - Fast 1m/5m/15m Strategy
Detects quick momentum shifts and oversold/overbought bounces
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


class ScalpingBot(BaseStrategy):
    """
    Scalping strategy for quick 1-5 minute trades
    
    Entry Conditions (LONG):
    - RSI < 30 (oversold)
    - Stochastic %K crosses above %D
    - Price bounces off MA7 or MA25
    - Volume surge detected
    
    Entry Conditions (SHORT):
    - RSI > 70 (overbought)
    - Stochastic %K crosses below %D
    - Price rejects MA7 or MA25
    - Volume surge detected
    """
    
    def __init__(self, config: dict):
        super().__init__("Scalping Bot", config)
        self.timeframe = config.get('primary_timeframe', '5m')
        self.min_confidence = config.get('confidence_threshold', 70)
        
    async def analyze(self, symbol: str) -> Optional[SignalCandidate]:
        """Analyze symbol for scalping opportunities"""
        try:
            # Fetch market data
            df = self.fetch_market_data(symbol, self.timeframe, limit=100)
            if df is None:
                return None
            
            # Check if we should generate a signal (cooldown)
            if not self.should_generate_signal(symbol, cooldown_minutes=10):
                return None
            
            # Calculate indicators
            rsi = self.indicators.rsi(df, period=14)
            stoch_k, stoch_d = self.indicators.stochastic(df)
            ma7 = self.indicators.moving_average(df, 7, 'EMA')
            ma25 = self.indicators.moving_average(df, 25, 'EMA')
            volume_surge = self.indicators.volume_surge(df, lookback=20, multiplier=1.5)
            
            current_price = df['close'].iloc[-1]
            current_rsi = rsi.iloc[-1]
            current_k = stoch_k.iloc[-1]
            current_d = stoch_d.iloc[-1]
            prev_k = stoch_k.iloc[-2]
            prev_d = stoch_d.iloc[-2]
            
            # Check for LONG signal
            long_signal = self._check_long_conditions(
                current_price, current_rsi, current_k, current_d,
                prev_k, prev_d, ma7.iloc[-1], ma25.iloc[-1],
                volume_surge.iloc[-1]
            )
            
            if long_signal:
                confidence = self._calculate_confidence(
                    current_rsi, current_k, 'LONG', volume_surge.iloc[-1]
                )
                
                if confidence >= self.min_confidence:
                    candidate = self.create_signal_candidate(
                        symbol=symbol,
                        side='LONG',
                        entry_price=current_price,
                        confidence=confidence,
                        tp_pct=0.8,
                        sl_pct=0.5
                    )
                    
                    if self.validate_signal(candidate):
                        self.record_signal(symbol)
                        self.log_signal(candidate)
                        return candidate
            
            # Check for SHORT signal
            short_signal = self._check_short_conditions(
                current_price, current_rsi, current_k, current_d,
                prev_k, prev_d, ma7.iloc[-1], ma25.iloc[-1],
                volume_surge.iloc[-1]
            )
            
            if short_signal:
                confidence = self._calculate_confidence(
                    current_rsi, current_k, 'SHORT', volume_surge.iloc[-1]
                )
                
                if confidence >= self.min_confidence:
                    candidate = self.create_signal_candidate(
                        symbol=symbol,
                        side='SHORT',
                        entry_price=current_price,
                        confidence=confidence,
                        tp_pct=0.8,
                        sl_pct=0.5
                    )
                    
                    if self.validate_signal(candidate):
                        self.record_signal(symbol)
                        self.log_signal(candidate)
                        return candidate
            
            return None
            
        except Exception as e:
            logger.error(f"Scalping bot error analyzing {symbol}: {e}")
            return None
    
    def _check_long_conditions(
        self, price, rsi, k, d, prev_k, prev_d, ma7, ma25, volume_surge
    ) -> bool:
        """Check if LONG entry conditions are met"""
        # RSI oversold
        rsi_oversold = rsi < 35
        
        # Stochastic cross (bullish)
        stoch_cross = prev_k <= prev_d and k > d
        
        # Price near MA support
        near_ma7 = abs(price - ma7) / ma7 < 0.005  # Within 0.5%
        near_ma25 = abs(price - ma25) / ma25 < 0.01  # Within 1%
        ma_support = near_ma7 or near_ma25
        
        # Volume confirmation
        volume_ok = volume_surge
        
        # At least 3 conditions must be met
        conditions_met = sum([
            rsi_oversold,
            stoch_cross,
            ma_support,
            volume_ok
        ])
        
        return conditions_met >= 3
    
    def _check_short_conditions(
        self, price, rsi, k, d, prev_k, prev_d, ma7, ma25, volume_surge
    ) -> bool:
        """Check if SHORT entry conditions are met"""
        # RSI overbought
        rsi_overbought = rsi > 65
        
        # Stochastic cross (bearish)
        stoch_cross = prev_k >= prev_d and k < d
        
        # Price near MA resistance
        near_ma7 = abs(price - ma7) / ma7 < 0.005
        near_ma25 = abs(price - ma25) / ma25 < 0.01
        ma_resistance = near_ma7 or near_ma25
        
        # Volume confirmation
        volume_ok = volume_surge
        
        # At least 3 conditions must be met
        conditions_met = sum([
            rsi_overbought,
            stoch_cross,
            ma_resistance,
            volume_ok
        ])
        
        return conditions_met >= 3
    
    def _calculate_confidence(self, rsi, stoch_k, direction, volume_surge) -> float:
        """Calculate signal confidence score (0-100)"""
        confidence = 50.0  # Base confidence
        
        if direction == 'LONG':
            # More oversold = higher confidence
            if rsi < 20:
                confidence += 25
            elif rsi < 30:
                confidence += 15
            elif rsi < 35:
                confidence += 10
            
            # Low stochastic = higher confidence
            if stoch_k < 20:
                confidence += 15
        
        else:  # SHORT
            # More overbought = higher confidence
            if rsi > 80:
                confidence += 25
            elif rsi > 70:
                confidence += 15
            elif rsi > 65:
                confidence += 10
            
            # High stochastic = higher confidence
            if stoch_k > 80:
                confidence += 15
        
        # Volume surge adds confidence
        if volume_surge:
            confidence += 10
        
        return min(confidence, 95.0)  # Cap at 95%
    
    def _create_signal(self, symbol, direction, entry_price, confidence) -> Signal:
        """Create a signal object with TP/SL"""
        # Scalping uses small TP/SL percentages
        if direction == 'LONG':
            tp_pct = 0.8  # 0.8% profit
            sl_pct = 0.5  # 0.5% stop loss
        else:
            tp_pct = 0.8
            sl_pct = 0.5
        
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
                'strategy_type': 'scalping',
                'tp_pct': tp_pct,
                'sl_pct': sl_pct
            }
        )
