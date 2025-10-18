"""
Bybit Exchange Client
Handles Bybit Futures and Spot trading with secure API key management
"""

import os
import time
import hmac
import hashlib
import requests
from typing import Dict, Optional, List
from exchanges.proxy_helper import get_proxy_helper


class BybitClient:
    """Bybit API client for futures and spot trading"""
    
    def __init__(self, testnet: bool = False):
        self.testnet = testnet
        
        # Load API keys from environment (Replit Secrets)
        self.api_key = os.getenv("BYBIT_API_KEY", "")
        self.api_secret = os.getenv("BYBIT_API_SECRET", "")
        
        # Set base URLs
        if testnet:
            self.base_url = "https://api-testnet.bybit.com"
        else:
            self.base_url = "https://api.bybit.com"
        
        # Market category
        self.category = "linear"  # linear (USDT futures), inverse, spot
    
    def _generate_signature(self, params: dict) -> str:
        """Generate HMAC SHA256 signature"""
        param_str = ""
        for key in sorted(params.keys()):
            param_str += f"{key}={params[key]}&"
        param_str = param_str[:-1]
        
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            param_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _request(self, method: str, endpoint: str, params: Optional[dict] = None, signed: bool = False) -> dict:
        """Make API request (with proxy support)"""
        if params is None:
            params = {}
        
        headers = {"X-BAPI-API-KEY": self.api_key}
        
        if signed:
            timestamp = str(int(time.time() * 1000))
            recv_window = "5000"
            
            params['api_key'] = self.api_key
            params['timestamp'] = timestamp
            params['recv_window'] = recv_window
            
            sign = self._generate_signature(params)
            params['sign'] = sign
        
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
    
    def get_account_balance(self) -> dict:
        """Get account balance"""
        endpoint = "/v5/account/wallet-balance"
        params = {"accountType": "UNIFIED"}
        return self._request("GET", endpoint, params=params, signed=True)
    
    def get_ticker_price(self, symbol: str) -> Optional[float]:
        """Get current price for symbol"""
        endpoint = "/v5/market/tickers"
        params = {"category": self.category, "symbol": symbol}
        result = self._request("GET", endpoint, params=params)
        
        if result.get("retCode") == 0:
            data = result.get("result", {}).get("list", [])
            if data:
                return float(data[0].get("lastPrice", 0))
        return None
    
    def create_market_order(self, symbol: str, side: str, quantity: float, **kwargs) -> dict:
        """Create market order"""
        endpoint = "/v5/order/create"
        params = {
            "category": self.category,
            "symbol": symbol,
            "side": side.capitalize(),
            "orderType": "Market",
            "qty": str(quantity)
        }
        return self._request("POST", endpoint, params=params, signed=True)
    
    def create_limit_order(self, symbol: str, side: str, quantity: float, price: float, **kwargs) -> dict:
        """Create limit order"""
        endpoint = "/v5/order/create"
        params = {
            "category": self.category,
            "symbol": symbol,
            "side": side.capitalize(),
            "orderType": "Limit",
            "qty": str(quantity),
            "price": str(price)
        }
        return self._request("POST", endpoint, params=params, signed=True)
    
    def create_stop_loss(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        """Create stop loss order"""
        endpoint = "/v5/order/create"
        close_side = "Sell" if side.upper() == "BUY" else "Buy"
        params = {
            "category": self.category,
            "symbol": symbol,
            "side": close_side,
            "orderType": "Market",
            "qty": str(quantity),
            "stopLoss": str(stop_price)
        }
        return self._request("POST", endpoint, params=params, signed=True)
    
    def create_take_profit(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        """Create take profit order"""
        endpoint = "/v5/order/create"
        close_side = "Sell" if side.upper() == "BUY" else "Buy"
        params = {
            "category": self.category,
            "symbol": symbol,
            "side": close_side,
            "orderType": "Market",
            "qty": str(quantity),
            "takeProfit": str(stop_price)
        }
        return self._request("POST", endpoint, params=params, signed=True)
    
    def cancel_order(self, symbol: str, order_id: str) -> dict:
        """Cancel an order"""
        endpoint = "/v5/order/cancel"
        params = {
            "category": self.category,
            "symbol": symbol,
            "orderId": order_id
        }
        return self._request("POST", endpoint, params=params, signed=True)
    
    def cancel_all_orders(self, symbol: str) -> dict:
        """Cancel all open orders for a symbol"""
        endpoint = "/v5/order/cancel-all"
        params = {
            "category": self.category,
            "symbol": symbol
        }
        return self._request("POST", endpoint, params=params, signed=True)
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[dict]:
        """Get all open orders"""
        endpoint = "/v5/order/realtime"
        params = {"category": self.category}
        if symbol:
            params["symbol"] = symbol
        
        result = self._request("GET", endpoint, params=params, signed=True)
        if result.get("retCode") == 0:
            return result.get("result", {}).get("list", [])
        return []
    
    def test_connection(self) -> bool:
        """Test API connection"""
        if not self.api_key or not self.api_secret:
            return False
        result = self.get_account_balance()
        return result.get("retCode") == 0


class BybitDemoClient:
    """Simulated Bybit client for paper trading"""
    
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
        if not price:
            return {"error": "Could not get price"}
        
        order = {
            "orderId": "demo_" + str(len(self.demo_orders) + 1),
            "symbol": symbol,
            "side": side,
            "orderType": "Market",
            "qty": quantity,
            "price": price,
            "status": "Filled"
        }
        self.demo_orders.append(order)
        return order
    
    def create_limit_order(self, symbol: str, side: str, quantity: float, price: float, **kwargs) -> dict:
        """Simulate limit order"""
        order = {
            "orderId": "demo_" + str(len(self.demo_orders) + 1),
            "symbol": symbol,
            "side": side,
            "orderType": "Limit",
            "qty": quantity,
            "price": price,
            "status": "New"
        }
        self.demo_orders.append(order)
        return order
    
    def create_stop_loss(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        """Simulate stop loss"""
        order = {
            "orderId": "demo_sl_" + str(len(self.demo_orders) + 1),
            "orderType": "Stop",
            "stopLoss": stop_price,
            "status": "New"
        }
        self.demo_orders.append(order)
        return order
    
    def create_take_profit(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        """Simulate take profit"""
        order = {
            "orderId": "demo_tp_" + str(len(self.demo_orders) + 1),
            "orderType": "TakeProfit",
            "takeProfit": stop_price,
            "status": "New"
        }
        self.demo_orders.append(order)
        return order
    
    def cancel_order(self, symbol: str, order_id: str) -> dict:
        """Simulate cancel order"""
        return {"orderId": order_id, "status": "Canceled"}
    
    def cancel_all_orders(self, symbol: str) -> dict:
        """Simulate cancel all orders"""
        return {"result": "success", "symbol": symbol}
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[dict]:
        """Get simulated open orders"""
        orders = [o for o in self.demo_orders if o.get("status") == "New"]
        if symbol:
            orders = [o for o in orders if o.get("symbol") == symbol]
        return orders
    
    def test_connection(self) -> bool:
        """Demo always connected"""
        return True
