"""
Rate limiter for Verzek AutoTrader API
Prevents signal spam and abuse
"""
import time
from collections import defaultdict
from threading import Lock


class RateLimiter:
    """Simple in-memory rate limiter for signal endpoints"""
    
    def __init__(self):
        self.signals_per_symbol = defaultdict(list)  # {symbol: [timestamp1, timestamp2, ...]}
        self.lock = Lock()
    
    def check_signal_rate(self, symbol: str, limit_per_minute: int = 1) -> tuple[bool, str]:
        """
        Check if a signal for the given symbol can be processed
        
        Args:
            symbol: Trading pair symbol (e.g., "BTCUSDT")
            limit_per_minute: Max signals allowed per symbol per minute
            
        Returns:
            (allowed, reason) tuple
        """
        with self.lock:
            now = time.time()
            one_minute_ago = now - 60
            
            # Clean up old entries
            self.signals_per_symbol[symbol] = [
                ts for ts in self.signals_per_symbol[symbol]
                if ts > one_minute_ago
            ]
            
            # Check if limit exceeded
            if len(self.signals_per_symbol[symbol]) >= limit_per_minute:
                return False, f"Rate limit exceeded for {symbol}. Max {limit_per_minute} signal/minute."
            
            # Record this signal
            self.signals_per_symbol[symbol].append(now)
            return True, "OK"
    
    def get_stats(self) -> dict:
        """Get current rate limiter statistics"""
        with self.lock:
            now = time.time()
            one_minute_ago = now - 60
            
            active_symbols = {}
            for symbol, timestamps in self.signals_per_symbol.items():
                recent = [ts for ts in timestamps if ts > one_minute_ago]
                if recent:
                    active_symbols[symbol] = {
                        "count": len(recent),
                        "last_signal": max(recent)
                    }
            
            return {
                "active_symbols": len(active_symbols),
                "details": active_symbols
            }
    
    def reset(self):
        """Clear all rate limit data"""
        with self.lock:
            self.signals_per_symbol.clear()


# Global rate limiter instance
rate_limiter = RateLimiter()
