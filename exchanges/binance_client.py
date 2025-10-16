"""
Binance Exchange Client
Handles Binance Futures and Spot trading with secure API key management
"""

import os
import time
import hmac
import hashlib
import requests
from typing import Dict, Optional, List
from datetime import datetime


class BinanceClient:
    """Binance API client for futures and spot trading"""
    
    def __init__(self, testnet: bool = False):
        self.testnet = testnet
        
        # Load API keys from environment (Replit Secrets)
        self.api_key = os.getenv("BINANCE_API_KEY", "")
        self.api_secret = os.getenv("BINANCE_API_SECRET", "")
        
        # Set base URLs
        if testnet:
            self.base_url = "https://testnet.binancefuture.com"
        else:
            self.base_url = "https://fapi.binance.com"
        
        self.spot_url = "https://api.binance.com"
        
        # Market type (futures or spot)
        self.market_type = "futures"  # default to futures
        
        # Headers
        self.headers = {
            "X-MBX-APIKEY": self.api_key
        }
    
    def _generate_signature(self, params: dict) -> str:
        """Generate HMAC SHA256 signature"""
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _request(self, method: str, endpoint: str, params: Optional[dict] = None, signed: bool = False) -> dict:
        """Make API request"""
        if params is None:
            params = {}
        
        # Add timestamp for signed requests
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._generate_signature(params)
        
        # Choose base URL based on market type
        base_url = self.base_url if self.market_type == "futures" else self.spot_url
        url = f"{base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, params=params, headers=self.headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, params=params, headers=self.headers, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, params=params, headers=self.headers, timeout=10)
            else:
                return {"error": f"Unsupported method: {method}"}
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_account_balance(self) -> dict:
        """Get account balance"""
        if self.market_type == "futures":
            endpoint = "/fapi/v2/balance"
        else:
            endpoint = "/api/v3/account"
        
        result = self._request("GET", endpoint, signed=True)
        return result
    
    def get_ticker_price(self, symbol: str) -> Optional[float]:
        """Get current price for symbol"""
        if self.market_type == "futures":
            endpoint = "/fapi/v1/ticker/price"
        else:
            endpoint = "/api/v3/ticker/price"
        
        result = self._request("GET", endpoint, params={"symbol": symbol})
        
        if "price" in result:
            return float(result["price"])
        return None
    
    def create_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        reduce_only: bool = False
    ) -> dict:
        """Create market order
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            side: BUY or SELL
            quantity: Order quantity
            reduce_only: For futures, close position only
        """
        if self.market_type == "futures":
            endpoint = "/fapi/v1/order"
            params = {
                "symbol": symbol,
                "side": side.upper(),
                "type": "MARKET",
                "quantity": quantity
            }
            if reduce_only:
                params["reduceOnly"] = "true"
        else:
            endpoint = "/api/v3/order"
            params = {
                "symbol": symbol,
                "side": side.upper(),
                "type": "MARKET",
                "quantity": quantity
            }
        
        result = self._request("POST", endpoint, params=params, signed=True)
        return result
    
    def create_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        time_in_force: str = "GTC"
    ) -> dict:
        """Create limit order"""
        if self.market_type == "futures":
            endpoint = "/fapi/v1/order"
        else:
            endpoint = "/api/v3/order"
        
        params = {
            "symbol": symbol,
            "side": side.upper(),
            "type": "LIMIT",
            "quantity": quantity,
            "price": price,
            "timeInForce": time_in_force
        }
        
        result = self._request("POST", endpoint, params=params, signed=True)
        return result
    
    def create_stop_loss(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float
    ) -> dict:
        """Create stop loss order (futures only)"""
        if self.market_type != "futures":
            return {"error": "Stop loss only available for futures"}
        
        endpoint = "/fapi/v1/order"
        params = {
            "symbol": symbol,
            "side": side.upper(),
            "type": "STOP_MARKET",
            "stopPrice": stop_price,
            "quantity": quantity,
            "closePosition": "false"
        }
        
        result = self._request("POST", endpoint, params=params, signed=True)
        return result
    
    def create_take_profit(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float
    ) -> dict:
        """Create take profit order (futures only)"""
        if self.market_type != "futures":
            return {"error": "Take profit only available for futures"}
        
        endpoint = "/fapi/v1/order"
        params = {
            "symbol": symbol,
            "side": side.upper(),
            "type": "TAKE_PROFIT_MARKET",
            "stopPrice": stop_price,
            "quantity": quantity,
            "closePosition": "false"
        }
        
        result = self._request("POST", endpoint, params=params, signed=True)
        return result
    
    def set_leverage(self, symbol: str, leverage: int) -> dict:
        """Set leverage for symbol (futures only)"""
        if self.market_type != "futures":
            return {"error": "Leverage only available for futures"}
        
        endpoint = "/fapi/v1/leverage"
        params = {
            "symbol": symbol,
            "leverage": leverage
        }
        
        result = self._request("POST", endpoint, params=params, signed=True)
        return result
    
    def get_position(self, symbol: Optional[str] = None) -> dict:
        """Get position information (futures only)"""
        if self.market_type != "futures":
            return {"error": "Position info only available for futures"}
        
        endpoint = "/fapi/v2/positionRisk"
        params = {}
        if symbol:
            params["symbol"] = symbol
        
        result = self._request("GET", endpoint, params=params, signed=True)
        return result
    
    def cancel_order(self, symbol: str, order_id: int) -> dict:
        """Cancel an order"""
        if self.market_type == "futures":
            endpoint = "/fapi/v1/order"
        else:
            endpoint = "/api/v3/order"
        
        params = {
            "symbol": symbol,
            "orderId": order_id
        }
        
        result = self._request("DELETE", endpoint, params=params, signed=True)
        return result
    
    def cancel_all_orders(self, symbol: str) -> dict:
        """Cancel all open orders for a symbol"""
        if self.market_type == "futures":
            endpoint = "/fapi/v1/allOpenOrders"
        else:
            endpoint = "/api/v3/openOrders"
        
        params = {"symbol": symbol}
        result = self._request("DELETE", endpoint, params=params, signed=True)
        return result
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[dict]:
        """Get all open orders"""
        if self.market_type == "futures":
            endpoint = "/fapi/v1/openOrders"
        else:
            endpoint = "/api/v3/openOrders"
        
        params = {}
        if symbol:
            params["symbol"] = symbol
        
        result = self._request("GET", endpoint, params=params, signed=True)
        return result if isinstance(result, list) else []
    
    def get_exchange_info(self, symbol: Optional[str] = None) -> dict:
        """Get exchange trading rules and symbol info"""
        if self.market_type == "futures":
            endpoint = "/fapi/v1/exchangeInfo"
        else:
            endpoint = "/api/v3/exchangeInfo"
        
        result = self._request("GET", endpoint)
        
        if symbol and "symbols" in result:
            for sym_info in result["symbols"]:
                if sym_info["symbol"] == symbol:
                    return sym_info
        
        return result
    
    def test_connection(self) -> bool:
        """Test API connection"""
        if not self.api_key or not self.api_secret:
            return False
        
        result = self.get_account_balance()
        return "error" not in result


# Demo/Paper Trading Client
class BinanceDemoClient:
    """Simulated Binance client for paper trading"""
    
    def __init__(self):
        self.demo_balance = 10000  # $10,000 demo balance
        self.demo_positions = {}
        self.demo_orders = []
    
    def get_ticker_price(self, symbol: str) -> Optional[float]:
        """Get simulated price (uses real Binance price)"""
        try:
            response = requests.get(
                "https://fapi.binance.com/fapi/v1/ticker/price",
                params={"symbol": symbol},
                timeout=5
            )
            if response.status_code == 200:
                return float(response.json()["price"])
        except:
            pass
        return None
    
    def create_market_order(self, symbol: str, side: str, quantity: float, **kwargs) -> dict:
        """Simulate market order"""
        price = self.get_ticker_price(symbol)
        if not price:
            return {"error": "Could not get price"}
        
        order = {
            "orderId": len(self.demo_orders) + 1,
            "symbol": symbol,
            "side": side.upper(),
            "type": "MARKET",
            "quantity": quantity,
            "price": price,
            "status": "FILLED",
            "executedQty": quantity,
            "timestamp": int(time.time() * 1000)
        }
        
        self.demo_orders.append(order)
        return order
    
    def create_stop_loss(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        """Simulate stop loss"""
        return {
            "orderId": len(self.demo_orders) + 1,
            "symbol": symbol,
            "side": side,
            "type": "STOP_MARKET",
            "stopPrice": stop_price,
            "quantity": quantity,
            "status": "NEW"
        }
    
    def create_take_profit(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        """Simulate take profit"""
        return {
            "orderId": len(self.demo_orders) + 1,
            "symbol": symbol,
            "side": side,
            "type": "TAKE_PROFIT_MARKET",
            "stopPrice": stop_price,
            "quantity": quantity,
            "status": "NEW"
        }
    
    def get_account_balance(self) -> dict:
        """Get demo balance"""
        return {
            "balance": self.demo_balance,
            "availableBalance": self.demo_balance
        }
    
    def test_connection(self) -> bool:
        """Demo always connected"""
        return True
