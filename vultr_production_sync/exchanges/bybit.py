"""
Bybit Contract Exchange Client
IMPORTANT: This is a DRY-RUN implementation for Phase 2 validation
NO REAL TRADING - All methods return mock responses
"""
from typing import Dict, List, Tuple
from .base_exchange import BaseExchange
import time


class BybitClient(BaseExchange):
    """Bybit Contract client (DRY-RUN only for Phase 2)"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        super().__init__(api_key, api_secret, testnet)
        self.exchange_name = "bybit"
        self.base_url = "https://api-testnet.bybit.com" if testnet else "https://api.bybit.com"
    
    def test_connection(self) -> Tuple[bool, str]:
        """Test API connection (MOCK for Phase 2)"""
        return (True, f"✅ Bybit API keys validated (MOCK - testnet={self.testnet})")
    
    def get_balance(self) -> Dict:
        """Get account balance (MOCK for Phase 2)"""
        return {
            "ok": True,
            "total_usdt": 10000.0,
            "available_usdt": 8500.0,
            "currencies": {
                "USDT": {"free": 8500.0, "locked": 1500.0}
            },
            "mock": True,
            "note": "Phase 2: Mock balance - no real API call"
        }
    
    def get_positions(self) -> List[Dict]:
        """Get open positions (MOCK for Phase 2)"""
        return []
    
    def place_market_order(self, symbol: str, side: str, size: float, leverage: int = 1) -> Dict:
        """Place market order (DRY-RUN only)"""
        return {
            "ok": True,
            "exchange_order_id": f"BYBIT_MOCK_{int(time.time())}",
            "symbol": self.format_symbol(symbol),
            "side": side.upper(),
            "price": 50000.0,
            "size": size,
            "leverage": leverage,
            "raw": {},
            "mock": True,
            "note": "Phase 2: DRY-RUN - NO REAL ORDER PLACED"
        }
    
    def place_limit_order(self, symbol: str, side: str, size: float, limit_price: float, leverage: int = 1) -> Dict:
        """Place limit order (DRY-RUN only)"""
        return {
            "ok": True,
            "exchange_order_id": f"BYBIT_LIMIT_{int(time.time())}",
            "symbol": self.format_symbol(symbol),
            "side": side.upper(),
            "price": limit_price,
            "size": size,
            "leverage": leverage,
            "raw": {},
            "mock": True,
            "note": "Phase 2: DRY-RUN - NO REAL ORDER PLACED"
        }
    
    def place_stop_loss(self, symbol: str, size: float, stop_price: float, side: str = None) -> Dict:
        """Place stop loss order (DRY-RUN only)"""
        return {
            "ok": True,
            "exchange_order_id": f"BYBIT_SL_{int(time.time())}",
            "symbol": self.format_symbol(symbol),
            "stop_price": stop_price,
            "size": size,
            "side": side or "SELL",
            "raw": {},
            "mock": True,
            "note": "Phase 2: DRY-RUN - NO REAL STOP LOSS PLACED"
        }
    
    def close_position(self, symbol: str) -> Dict:
        """Close position (DRY-RUN only)"""
        return {
            "ok": True,
            "message": f"Position closed for {self.format_symbol(symbol)} (MOCK)",
            "mock": True,
            "note": "Phase 2: DRY-RUN - NO REAL POSITION CLOSED"
        }
    
    def cancel_order(self, order_id: str, symbol: str = None) -> Dict:
        """Cancel order (DRY-RUN only)"""
        return {
            "ok": True,
            "cancelled": True,
            "order_id": order_id,
            "symbol": symbol,
            "mock": True,
            "note": "Phase 2: DRY-RUN - NO REAL ORDER CANCELLED"
        }
    
    def set_leverage(self, symbol: str, leverage: int) -> Dict:
        """Set leverage (DRY-RUN only)"""
        return {
            "ok": True,
            "leverage": leverage,
            "symbol": self.format_symbol(symbol),
            "mock": True,
            "note": "Phase 2: DRY-RUN - NO REAL LEVERAGE SET"
        }
    
    def format_symbol(self, symbol: str) -> str:
        """Format symbol for Bybit (e.g., BTCUSDT)"""
        return symbol.upper().replace("/", "").replace("-", "")
