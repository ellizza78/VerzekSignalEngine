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
    def create_client(exchange_name: str, mode: str = "demo", **kwargs):
        """Create exchange client
        
        Args:
            exchange_name: binance, bybit, phemex, kraken
            mode: demo or live
            **kwargs: Additional config (testnet, etc.)
        """
        exchange_name = exchange_name.lower()
        
        if exchange_name == "binance":
            from .binance_client import BinanceClient, BinanceDemoClient
            if mode == "demo":
                return BinanceDemoClient()
            else:
                return BinanceClient(**kwargs)
        
        elif exchange_name == "bybit":
            from .bybit_client import BybitClient, BybitDemoClient
            if mode == "demo":
                return BybitDemoClient()
            else:
                return BybitClient(**kwargs)
        
        elif exchange_name == "phemex":
            from .phemex_client import PhemexClient, PhemexDemoClient
            if mode == "demo":
                return PhemexDemoClient()
            else:
                return PhemexClient(**kwargs)
        
        elif exchange_name == "kraken":
            from .kraken_client import KrakenClient, KrakenDemoClient
            if mode == "demo":
                return KrakenDemoClient()
            else:
                return KrakenClient(**kwargs)
        
        else:
            raise ValueError(f"Unsupported exchange: {exchange_name}")
    
    @staticmethod
    def get_supported_exchanges() -> List[str]:
        """Get list of supported exchanges"""
        return ["binance", "bybit", "phemex", "kraken"]
