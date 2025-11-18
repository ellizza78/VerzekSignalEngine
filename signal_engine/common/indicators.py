"""
Shared Technical Indicator Library
Used by all strategy bots for analysis
Based on SIGNAL RESEARCH formulas
"""
import pandas as pd
import numpy as np
import ta
from typing import Tuple, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class Indicators:
    """Technical indicator calculations"""
    
    @staticmethod
    def rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Relative Strength Index
        Returns: Series with RSI values (0-100)
        """
        return ta.momentum.RSIIndicator(df['close'], window=period).rsi()
    
    @staticmethod
    def stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """
        Stochastic Oscillator
        Returns: (K line, D line)
        """
        stoch = ta.momentum.StochasticOscillator(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=k_period,
            smooth_window=d_period
        )
        return stoch.stoch(), stoch.stoch_signal()
    
    @staticmethod
    def macd(df: pd.DataFrame, fast=12, slow=26, signal=9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        MACD Indicator
        Returns: (MACD line, Signal line, Histogram)
        """
        macd_indicator = ta.trend.MACD(
            close=df['close'],
            window_fast=fast,
            window_slow=slow,
            window_sign=signal
        )
        return macd_indicator.macd(), macd_indicator.macd_signal(), macd_indicator.macd_diff()
    
    @staticmethod
    def moving_average(df: pd.DataFrame, period: int, ma_type='SMA') -> pd.Series:
        """
        Moving Average (SMA or EMA)
        """
        if ma_type == 'EMA':
            return ta.trend.EMAIndicator(df['close'], window=period).ema_indicator()
        else:  # SMA
            return ta.trend.SMAIndicator(df['close'], window=period).sma_indicator()
    
    @staticmethod
    def bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Bollinger Bands
        Returns: (Upper band, Middle band, Lower band)
        """
        bb = ta.volatility.BollingerBands(
            close=df['close'],
            window=period,
            window_dev=std_dev
        )
        return bb.bollinger_hband(), bb.bollinger_mavg(), bb.bollinger_lband()
    
    @staticmethod
    def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Average True Range (volatility)
        """
        return ta.volatility.AverageTrueRange(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=period
        ).average_true_range()
    
    @staticmethod
    def volume_surge(df: pd.DataFrame, lookback: int = 20, multiplier: float = 1.5) -> pd.Series:
        """
        Detect volume surges
        Returns: Boolean series where True = volume surge
        """
        avg_volume = df['volume'].rolling(window=lookback).mean()
        return df['volume'] > (avg_volume * multiplier)
    
    @staticmethod
    def price_drop_pct(df: pd.DataFrame, lookback: int = 20) -> float:
        """
        Calculate percentage drop from recent high
        Returns: Negative percentage if price dropped
        """
        recent_high = df['high'].rolling(window=lookback).max().iloc[-1]
        current_price = df['close'].iloc[-1]
        drop_pct = ((current_price - recent_high) / recent_high) * 100
        return drop_pct
    
    @staticmethod
    def detect_qfl_base(df: pd.DataFrame, lookback: int = 100) -> Optional[float]:
        """
        Detect QFL base level
        Base = support level where price consolidated before drop
        Returns: Base price level or None
        """
        try:
            # Find recent consolidation zone (low volatility period)
            recent_data = df.tail(lookback)
            
            # Calculate rolling volatility
            volatility = recent_data['close'].pct_change().rolling(window=10).std()
            
            # Find lowest volatility period (consolidation)
            consolidation_idx = volatility.idxmin()
            consolidation_period = recent_data.loc[:consolidation_idx].tail(20)
            
            # Base = average price during consolidation
            base_level = consolidation_period['close'].mean()
            
            return base_level
            
        except Exception as e:
            logger.error(f"Error detecting QFL base: {e}")
            return None
    
    @staticmethod
    def detect_doji_candle(df: pd.DataFrame, threshold: float = 0.1) -> bool:
        """
        Detect Doji candle pattern (indecision)
        """
        last_candle = df.iloc[-1]
        body = abs(last_candle['close'] - last_candle['open'])
        range_size = last_candle['high'] - last_candle['low']
        
        if range_size == 0:
            return False
        
        body_ratio = body / range_size
        return body_ratio < threshold
    
    @staticmethod
    def detect_hammer(df: pd.DataFrame) -> bool:
        """
        Detect Hammer candle (bullish reversal)
        """
        last_candle = df.iloc[-1]
        
        body = abs(last_candle['close'] - last_candle['open'])
        upper_wick = last_candle['high'] - max(last_candle['open'], last_candle['close'])
        lower_wick = min(last_candle['open'], last_candle['close']) - last_candle['low']
        
        # Hammer: small body, long lower wick, small upper wick
        if body == 0:
            return False
        
        return (lower_wick > body * 2) and (upper_wick < body * 0.5)
    
    @staticmethod
    def detect_shooting_star(df: pd.DataFrame) -> bool:
        """
        Detect Shooting Star candle (bearish reversal)
        """
        last_candle = df.iloc[-1]
        
        body = abs(last_candle['close'] - last_candle['open'])
        upper_wick = last_candle['high'] - max(last_candle['open'], last_candle['close'])
        lower_wick = min(last_candle['open'], last_candle['close']) - last_candle['low']
        
        # Shooting star: small body, long upper wick, small lower wick
        if body == 0:
            return False
        
        return (upper_wick > body * 2) and (lower_wick < body * 0.5)
    
    @staticmethod
    def ma_cross(df: pd.DataFrame, fast_period: int = 7, slow_period: int = 25) -> str:
        """
        Detect moving average crossover
        Returns: 'bullish', 'bearish', or 'none'
        """
        ma_fast = Indicators.moving_average(df, fast_period)
        ma_slow = Indicators.moving_average(df, slow_period)
        
        if len(ma_fast) < 2 or len(ma_slow) < 2:
            return 'none'
        
        # Bullish cross: fast crosses above slow
        if ma_fast.iloc[-2] <= ma_slow.iloc[-2] and ma_fast.iloc[-1] > ma_slow.iloc[-1]:
            return 'bullish'
        
        # Bearish cross: fast crosses below slow
        if ma_fast.iloc[-2] >= ma_slow.iloc[-2] and ma_fast.iloc[-1] < ma_slow.iloc[-1]:
            return 'bearish'
        
        return 'none'
    
    @staticmethod
    def trend_direction(df: pd.DataFrame, ma_period: int = 50) -> str:
        """
        Determine overall trend direction
        Returns: 'uptrend', 'downtrend', or 'sideways'
        """
        ma = Indicators.moving_average(df, ma_period)
        
        if len(ma) < 10:
            return 'sideways'
        
        # Check if MA is rising or falling
        ma_slope = (ma.iloc[-1] - ma.iloc[-10]) / ma.iloc[-10] * 100
        
        if ma_slope > 1:
            return 'uptrend'
        elif ma_slope < -1:
            return 'downtrend'
        else:
            return 'sideways'
    
    @staticmethod
    def calculate_support_resistance(df: pd.DataFrame, lookback: int = 50) -> Tuple[float, float]:
        """
        Calculate nearest support and resistance levels
        Returns: (support_level, resistance_level)
        """
        recent_data = df.tail(lookback)
        
        support = recent_data['low'].min()
        resistance = recent_data['high'].max()
        
        return support, resistance
    
    @staticmethod
    def calculate_pivot_points(df: pd.DataFrame) -> Dict:
        """
        Calculate pivot points for the day
        Returns: Dict with pivot, r1, r2, s1, s2
        """
        last_candle = df.iloc[-1]
        
        pivot = (last_candle['high'] + last_candle['low'] + last_candle['close']) / 3
        r1 = (2 * pivot) - last_candle['low']
        r2 = pivot + (last_candle['high'] - last_candle['low'])
        s1 = (2 * pivot) - last_candle['high']
        s2 = pivot - (last_candle['high'] - last_candle['low'])
        
        return {
            'pivot': pivot,
            'r1': r1,
            'r2': r2,
            's1': s1,
            's2': s2
        }
