"""
Base Strategy Class
All trading bots inherit from this class
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional
from datetime import datetime
import logging
from ..data_feed.live_data import get_market_feed
from ..common.indicators import Indicators

logger = logging.getLogger(__name__)


class Signal:
    """Trading signal data structure"""
    
    def __init__(
        self,
        symbol: str,
        direction: str,  # 'LONG' or 'SHORT'
        entry_price: float,
        tp_price: float,
        sl_price: float,
        strategy_name: str,
        timeframe: str,
        confidence: float,
        metadata: Optional[Dict] = None
    ):
        self.symbol = symbol
        self.direction = direction.upper()
        self.entry_price = entry_price
        self.tp_price = tp_price
        self.sl_price = sl_price
        self.strategy_name = strategy_name
        self.timeframe = timeframe
        self.confidence = confidence
        self.metadata = metadata or {}
        self.timestamp = datetime.now()
        self.version = "SE.v1.0"
        
    def to_dict(self) -> Dict:
        """Convert signal to dictionary for API/broadcast"""
        return {
            'symbol': self.symbol,
            'direction': self.direction,
            'entry_price': self.entry_price,
            'tp_price': self.tp_price,
            'sl_price': self.sl_price,
            'strategy': self.strategy_name,
            'timeframe': self.timeframe,
            'confidence': round(self.confidence, 2),
            'timestamp': self.timestamp.isoformat(),
            'version': self.version,
            'metadata': self.metadata
        }
    
    def to_telegram_message(self) -> str:
        """Format signal for Telegram broadcast"""
        tp_pct = ((self.tp_price - self.entry_price) / self.entry_price * 100)
        sl_pct = ((self.sl_price - self.entry_price) / self.entry_price * 100)
        
        message = f"""
🔥 **VERZEK SIGNAL** — {self.strategy_name}

**PAIR:** {self.symbol}
**DIRECTION:** {'🟢 LONG' if self.direction == 'LONG' else '🔴 SHORT'}
**ENTRY:** {self.entry_price:.4f}
**TP:** {self.tp_price:.4f} (+{tp_pct:.2f}%)
**SL:** {self.sl_price:.4f} ({sl_pct:.2f}%)
**TIMEFRAME:** {self.timeframe}
**CONFIDENCE:** {self.confidence:.0f}%
**EXCHANGE:** Binance Futures
**VERSION:** {self.version}

⏰ {self.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}
        """
        return message.strip()


class BaseStrategy(ABC):
    """Abstract base class for all trading strategies"""
    
    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config
        self.market_feed = get_market_feed()
        self.indicators = Indicators()
        self.last_signal_time = {}
        
    @abstractmethod
    async def analyze(self, symbol: str) -> Optional[Signal]:
        """
        Analyze market data and generate signal if conditions met
        
        Args:
            symbol: Trading pair to analyze
            
        Returns:
            Signal object if signal generated, None otherwise
        """
        pass
    
    def fetch_market_data(self, symbol: str, timeframe: str, limit: int = 200):
        """Fetch OHLCV data for analysis"""
        try:
            df = self.market_feed.get_ohlcv(symbol, timeframe, limit)
            if df is None or len(df) < 50:
                logger.warning(f"Insufficient data for {symbol} {timeframe}")
                return None
            return df
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None
    
    def get_ticker_data(self, symbol: str):
        """Get current ticker information"""
        return self.market_feed.get_ticker(symbol)
    
    def should_generate_signal(self, symbol: str, cooldown_minutes: int = 15) -> bool:
        """
        Check if enough time has passed since last signal for this symbol
        Prevents signal spam
        """
        if symbol not in self.last_signal_time:
            return True
        
        time_diff = (datetime.now() - self.last_signal_time[symbol]).total_seconds() / 60
        return time_diff >= cooldown_minutes
    
    def record_signal(self, symbol: str):
        """Record that a signal was generated for this symbol"""
        self.last_signal_time[symbol] = datetime.now()
    
    def calculate_tp_sl(
        self,
        entry_price: float,
        direction: str,
        tp_pct: float,
        sl_pct: float
    ) -> tuple:
        """
        Calculate take profit and stop loss prices
        
        Args:
            entry_price: Entry price
            direction: 'LONG' or 'SHORT'
            tp_pct: Take profit percentage
            sl_pct: Stop loss percentage
            
        Returns:
            (tp_price, sl_price)
        """
        if direction == 'LONG':
            tp_price = entry_price * (1 + tp_pct / 100)
            sl_price = entry_price * (1 - sl_pct / 100)
        else:  # SHORT
            tp_price = entry_price * (1 - tp_pct / 100)
            sl_price = entry_price * (1 + sl_pct / 100)
        
        return tp_price, sl_price
    
    def validate_signal(self, signal: Signal) -> bool:
        """
        Validate signal meets minimum requirements
        
        Args:
            signal: Signal object to validate
            
        Returns:
            True if signal is valid, False otherwise
        """
        # Check confidence threshold
        min_confidence = self.config.get('confidence_threshold', 70)
        if signal.confidence < min_confidence:
            logger.debug(f"Signal rejected: confidence {signal.confidence} < {min_confidence}")
            return False
        
        # Check TP/SL are valid
        if signal.direction == 'LONG':
            if signal.tp_price <= signal.entry_price:
                logger.warning("Invalid LONG signal: TP <= Entry")
                return False
            if signal.sl_price >= signal.entry_price:
                logger.warning("Invalid LONG signal: SL >= Entry")
                return False
        else:  # SHORT
            if signal.tp_price >= signal.entry_price:
                logger.warning("Invalid SHORT signal: TP >= Entry")
                return False
            if signal.sl_price <= signal.entry_price:
                logger.warning("Invalid SHORT signal: SL <= Entry")
                return False
        
        # Check risk/reward ratio
        risk = abs(signal.entry_price - signal.sl_price)
        reward = abs(signal.tp_price - signal.entry_price)
        rr_ratio = reward / risk if risk > 0 else 0
        
        if rr_ratio < 1.0:
            logger.debug(f"Signal rejected: R/R ratio {rr_ratio:.2f} < 1.0")
            return False
        
        return True
    
    def log_signal(self, signal: Signal):
        """Log signal generation"""
        logger.info(
            f"📊 {self.name} SIGNAL: {signal.symbol} {signal.direction} "
            f"@ {signal.entry_price:.4f} | TP: {signal.tp_price:.4f} | "
            f"SL: {signal.sl_price:.4f} | Confidence: {signal.confidence:.0f}%"
        )
