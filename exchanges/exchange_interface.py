"""
Unified Exchange Interface
Provides a consistent API across all exchange adapters
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List


class ExchangeInterface(ABC):
    """Abstract base class for all exchange clients"""
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test API connection"""
        pass
    
    @abstractmethod
    def get_account_balance(self) -> dict:
        """Get account balance"""
        pass
    
    @abstractmethod
    def get_ticker_price(self, symbol: str) -> Optional[float]:
        """Get current price for symbol"""
        pass
    
    @abstractmethod
    def create_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        **kwargs
    ) -> dict:
        """Create market order"""
        pass
    
    @abstractmethod
    def create_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        **kwargs
    ) -> dict:
        """Create limit order"""
        pass
    
    @abstractmethod
    def create_stop_loss(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float
    ) -> dict:
        """Create stop loss order"""
        pass
    
    @abstractmethod
    def create_take_profit(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float
    ) -> dict:
        """Create take profit order"""
        pass
    
    @abstractmethod
    def cancel_order(self, symbol: str, order_id: int) -> dict:
        """Cancel an order"""
        pass
    
    @abstractmethod
    def cancel_all_orders(self, symbol: str) -> dict:
        """Cancel all open orders for a symbol"""
        pass
    
    @abstractmethod
    def get_open_orders(self, symbol: Optional[str] = None) -> List[dict]:
        """Get all open orders"""
        pass


class ExchangeFactory:
    """Factory for creating exchange clients"""
    
    @staticmethod
    def create_client(exchange_name: str, mode: str = "demo", api_key: Optional[str] = None, api_secret: Optional[str] = None, **kwargs):
        """Create exchange client
        
        Args:
            exchange_name: binance, bybit, phemex, kraken
            mode: demo or live
            api_key: User's API key (optional, falls back to env vars)
            api_secret: User's API secret (optional, falls back to env vars)
            **kwargs: Additional config (testnet, etc.)
        """
        exchange_name = exchange_name.lower()
        
        if exchange_name == "binance":
            from .binance_client import BinanceClient, BinanceDemoClient
            if mode == "demo":
                return BinanceDemoClient()
            else:
                return BinanceClient(api_key=api_key, api_secret=api_secret, **kwargs)
        
        elif exchange_name == "bybit":
            from .bybit_client import BybitClient, BybitDemoClient
            if mode == "demo":
                return BybitDemoClient()
            else:
                return BybitClient(api_key=api_key, api_secret=api_secret, **kwargs)
        
        elif exchange_name == "phemex":
            from .phemex_client import PhemexClient, PhemexDemoClient
            if mode == "demo":
                return PhemexDemoClient()
            else:
                return PhemexClient(api_key=api_key, api_secret=api_secret, **kwargs)
        
        elif exchange_name == "kraken":
            from .kraken_client import KrakenClient, KrakenDemoClient
            if mode == "demo":
                return KrakenDemoClient()
            else:
                return KrakenClient(api_key=api_key, api_secret=api_secret, **kwargs)
        
        else:
            raise ValueError(f"Unsupported exchange: {exchange_name}")
    
    @staticmethod
    def get_supported_exchanges() -> List[str]:
        """Get list of supported exchanges"""
        return ["binance", "bybit", "phemex", "kraken"]
    
    def get_client(self, exchange_name: str, api_key: Optional[str] = None, api_secret: Optional[str] = None, testnet: bool = False):
        """Get exchange client instance (convenience method)
        
        Args:
            exchange_name: binance, bybit, phemex, kraken
            api_key: User's API key (optional)
            api_secret: User's API secret (optional)
            testnet: Use testnet (default: False)
        """
        mode = "demo" if testnet else "live"
        return self.create_client(
            exchange_name=exchange_name,
            mode=mode,
            api_key=api_key,
            api_secret=api_secret,
            testnet=testnet
        )
