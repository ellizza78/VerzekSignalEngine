"""
Price feed for paper trading mode
Fetches real-time cryptocurrency prices from public APIs
"""
import requests
from typing import Dict, Optional
from utils.logger import api_logger


class PriceFeed:
    """Fetch cryptocurrency prices from Binance or CoinGecko"""
    
    def __init__(self):
        self.binance_base = "https://api.binance.com/api/v3"
        self.cache = {}
    
    def get_price(self, symbol: str) -> Optional[float]:
        """
        Get current price for a symbol
        Symbol format: BTCUSDT, ETHUSDT, etc.
        """
        try:
            # Try Binance first
            url = f"{self.binance_base}/ticker/price"
            response = requests.get(url, params={"symbol": symbol.upper()}, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                price = float(data.get("price", 0))
                self.cache[symbol] = price
                return price
            
            # Fallback to cache
            return self.cache.get(symbol)
            
        except Exception as e:
            api_logger.error(f"Price feed error for {symbol}: {e}")
            return self.cache.get(symbol)
    
    def get_multiple_prices(self, symbols: list) -> Dict[str, float]:
        """Get prices for multiple symbols"""
        prices = {}
        for symbol in symbols:
            price = self.get_price(symbol)
            if price:
                prices[symbol] = price
        return prices


# Global price feed instance
price_feed = PriceFeed()
