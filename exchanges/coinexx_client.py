"""
Coinexx Exchange Client
Handles Coinexx trading with secure API key management
"""

import os
import time
import requests
from typing import Optional, List
from exchanges.proxy_helper import get_proxy_helper


class CoinexxClient:
    """Coinexx API client"""
    
    def __init__(self, testnet: bool = False):
        self.testnet = testnet
        
        # Load API keys from environment (Replit Secrets)
        self.api_key = os.getenv("COINEXX_API_KEY", "")
        self.api_secret = os.getenv("COINEXX_API_SECRET", "")
        
        # Set base URL
        self.base_url = "https://api.coinexx.com" if not testnet else "https://testnet.coinexx.com"
    
    def _request(self, method: str, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make API request (with proxy support)"""
        if params is None:
            params = {}
        
        headers = {"X-API-KEY": self.api_key}
        url = f"{self.base_url}{endpoint}"
        
        # Get proxy helper (automatically routes through proxy if enabled)
        proxy = get_proxy_helper()
        
        try:
            # Route through proxy (falls back to direct if proxy disabled/failed)
            if method == "POST":
                response = proxy.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json_data=params,
                    timeout=10
                )
            else:
                response = proxy.request(
                    method=method,
                    url=url,
                    params=params,
                    headers=headers,
                    timeout=10
                )
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_ticker_price(self, symbol: str) -> Optional[float]:
        """Get current price"""
        endpoint = f"/ticker/{symbol}"
        result = self._request("GET", endpoint)
        return float(result.get("price", 0)) if "price" in result else None
    
    def get_account_balance(self) -> dict:
        """Get account balance"""
        endpoint = "/account/balance"
        return self._request("GET", endpoint)
    
    def create_market_order(self, symbol: str, side: str, quantity: float, **kwargs) -> dict:
        """Create market order"""
        endpoint = "/orders"
        params = {
            "symbol": symbol,
            "side": side.lower(),
            "type": "market",
            "quantity": quantity
        }
        return self._request("POST", endpoint, params=params)
    
    def create_limit_order(self, symbol: str, side: str, quantity: float, price: float, **kwargs) -> dict:
        """Create limit order"""
        endpoint = "/orders"
        params = {
            "symbol": symbol,
            "side": side.lower(),
            "type": "limit",
            "quantity": quantity,
            "price": price
        }
        return self._request("POST", endpoint, params=params)
    
    def create_stop_loss(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        """Create stop loss order"""
        close_side = "sell" if side.upper() == "BUY" else "buy"
        endpoint = "/orders"
        params = {
            "symbol": symbol,
            "side": close_side,
            "type": "stop_loss",
            "quantity": quantity,
            "stopPrice": stop_price
        }
        return self._request("POST", endpoint, params=params)
    
    def create_take_profit(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        """Create take profit order"""
        close_side = "sell" if side.upper() == "BUY" else "buy"
        endpoint = "/orders"
        params = {
            "symbol": symbol,
            "side": close_side,
            "type": "take_profit",
            "quantity": quantity,
            "stopPrice": stop_price
        }
        return self._request("POST", endpoint, params=params)
    
    def cancel_order(self, symbol: str, order_id: str) -> dict:
        """Cancel an order"""
        endpoint = f"/orders/{order_id}"
        return self._request("DELETE", endpoint)
    
    def cancel_all_orders(self, symbol: str) -> dict:
        """Cancel all open orders for a symbol"""
        endpoint = f"/orders/all/{symbol}"
        return self._request("DELETE", endpoint)
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List:
        """Get all open orders"""
        endpoint = "/orders/open"
        params = {}
        if symbol:
            params["symbol"] = symbol
        result = self._request("GET", endpoint, params=params)
        return result.get("orders", []) if isinstance(result, dict) else []
    
    def test_connection(self) -> bool:
        """Test API connection"""
        if not self.api_key:
            return False
        result = self.get_account_balance()
        return "error" not in result


class CoinexxDemoClient:
    """Simulated Coinexx client for paper trading"""
    
    def __init__(self):
        self.demo_balance = 10000
        self.demo_orders = []
    
    def get_ticker_price(self, symbol: str) -> Optional[float]:
        """Get simulated price (deterministic for demo)"""
        # Deterministic demo pricing based on symbol
        base_prices = {
            "BTCUSDT": 43000.0,
            "ETHUSDT": 2300.0,
            "BNBUSDT": 310.0,
            "SOLUSDT": 98.0,
            "XRPUSDT": 0.52
        }
        return base_prices.get(symbol, 30000.0)
    
    def get_account_balance(self) -> dict:
        """Get demo balance"""
        return {"balance": self.demo_balance, "availableBalance": self.demo_balance}
    
    def create_market_order(self, symbol: str, side: str, quantity: float, **kwargs) -> dict:
        """Simulate market order"""
        price = self.get_ticker_price(symbol)
        order = {
            "orderId": "demo_" + str(len(self.demo_orders) + 1),
            "symbol": symbol,
            "side": side,
            "type": "market",
            "quantity": quantity,
            "price": price,
            "status": "filled"
        }
        self.demo_orders.append(order)
        return order
    
    def create_limit_order(self, symbol: str, side: str, quantity: float, price: float, **kwargs) -> dict:
        """Simulate limit order"""
        order = {
            "orderId": "demo_" + str(len(self.demo_orders) + 1),
            "symbol": symbol,
            "side": side,
            "type": "limit",
            "quantity": quantity,
            "price": price,
            "status": "open"
        }
        self.demo_orders.append(order)
        return order
    
    def create_stop_loss(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        """Simulate stop loss"""
        return {
            "orderId": "demo_sl_" + str(len(self.demo_orders) + 1),
            "type": "stop_loss",
            "stopPrice": stop_price,
            "status": "open"
        }
    
    def create_take_profit(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        """Simulate take profit"""
        return {
            "orderId": "demo_tp_" + str(len(self.demo_orders) + 1),
            "type": "take_profit",
            "stopPrice": stop_price,
            "status": "open"
        }
    
    def cancel_order(self, symbol: str, order_id: str) -> dict:
        """Simulate cancel order"""
        return {"orderId": order_id, "status": "canceled"}
    
    def cancel_all_orders(self, symbol: str) -> dict:
        """Simulate cancel all orders"""
        return {"result": "success", "symbol": symbol}
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List:
        """Get simulated open orders"""
        orders = [o for o in self.demo_orders if o.get("status") == "open"]
        if symbol:
            orders = [o for o in orders if o.get("symbol") == symbol]
        return orders
    
    def test_connection(self) -> bool:
        """Demo always connected"""
        return True
