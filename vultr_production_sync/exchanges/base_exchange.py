"""
Base Exchange Client Interface
All exchange clients must implement this interface
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple


class BaseExchange(ABC):
    """Abstract base class for exchange clients"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """
        Initialize exchange client
        
        Args:
            api_key: API key
            api_secret: API secret
            testnet: Use testnet (True) or live (False)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        self.exchange_name = "base"
    
    @abstractmethod
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test API connection and authentication
        
        Returns:
            (success, message) tuple
        """
        pass
    
    @abstractmethod
    def get_balance(self) -> Dict:
        """
        Get account balance
        
        Returns:
            {
                "ok": True/False,
                "total_usdt": float,
                "available_usdt": float,
                "currencies": {...}
            }
        """
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Dict]:
        """
        Get open positions
        
        Returns:
            List of position dicts
        """
        pass
    
    @abstractmethod
    def place_market_order(self, symbol: str, side: str, size: float, leverage: int = 1) -> Dict:
        """
        Place market order
        
        Args:
            symbol: Trading pair (e.g., "BTCUSDT")
            side: "BUY" or "SELL" (or "LONG"/"SHORT")
            size: Position size in base currency
            leverage: Leverage multiplier
        
        Returns:
            {
                "ok": True/False,
                "error": str (if failed),
                "exchange_order_id": str,
                "symbol": str,
                "side": str,
                "price": float,
                "size": float,
                "raw": {...}
            }
        """
        pass
    
    @abstractmethod
    def place_limit_order(self, symbol: str, side: str, size: float, limit_price: float, leverage: int = 1) -> Dict:
        """
        Place limit order
        
        Args:
            symbol: Trading pair
            side: "BUY" or "SELL"
            size: Position size
            limit_price: Limit price
            leverage: Leverage multiplier
        
        Returns:
            Same format as place_market_order
        """
        pass
    
    @abstractmethod
    def place_stop_loss(self, symbol: str, size: float, stop_price: float, side: str = None) -> Dict:
        """
        Place stop loss order
        
        Args:
            symbol: Trading pair
            size: Size to close
            stop_price: Stop price
            side: Optional side (auto-determined if None)
        
        Returns:
            Same format as place_market_order
        """
        pass
    
    @abstractmethod
    def close_position(self, symbol: str) -> Dict:
        """
        Close entire position for symbol
        
        Args:
            symbol: Trading pair
        
        Returns:
            {
                "ok": True/False,
                "error": str (if failed),
                "message": str
            }
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str, symbol: str = None) -> Dict:
        """
        Cancel an order
        
        Args:
            order_id: Exchange order ID
            symbol: Trading pair (required for some exchanges)
        
        Returns:
            {
                "ok": True/False,
                "error": str (if failed),
                "cancelled": bool
            }
        """
        pass
    
    @abstractmethod
    def set_leverage(self, symbol: str, leverage: int) -> Dict:
        """
        Set leverage for symbol
        
        Args:
            symbol: Trading pair
            leverage: Leverage value
        
        Returns:
            {
                "ok": True/False,
                "leverage": int
            }
        """
        pass
    
    def format_symbol(self, symbol: str) -> str:
        """
        Format symbol for exchange-specific requirements
        
        Args:
            symbol: Standard symbol (e.g., "BTCUSDT")
        
        Returns:
            Exchange-formatted symbol
        """
        return symbol.upper().replace("/", "")
