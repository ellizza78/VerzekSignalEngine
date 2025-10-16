"""
Phemex Exchange Client
Handles Phemex trading with secure API key management
"""

import os
import time
import hmac
import hashlib
import requests
from typing import Optional, List


class PhemexClient:
    """Phemex API client"""
    
    def __init__(self, testnet: bool = False):
        self.testnet = testnet
        
        # Load API keys from environment (Replit Secrets)
        self.api_key = os.getenv("PHEMEX_API_KEY", "")
        self.api_secret = os.getenv("PHEMEX_API_SECRET", "")
        
        # Set base URL
        if testnet:
            self.base_url = "https://testnet-api.phemex.com"
        else:
            self.base_url = "https://api.phemex.com"
    
    def _generate_signature(self, path: str, params_str: str, timestamp: str) -> str:
        """Generate HMAC SHA256 signature"""
        message = path + params_str + timestamp
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _request(self, method: str, endpoint: str, params: Optional[dict] = None, signed: bool = False) -> dict:
        """Make API request"""
        if params is None:
            params = {}
        
        timestamp = str(int(time.time()))
        params_str = ""
        
        if signed:
            for key in sorted(params.keys()):
                params_str += f"{key}={params[key]}&"
            params_str = params_str[:-1] if params_str else ""
            
            signature = self._generate_signature(endpoint, params_str, timestamp)
            
            headers = {
                "x-phemex-access-token": self.api_key,
                "x-phemex-request-expiry": timestamp,
                "x-phemex-request-signature": signature
            }
        else:
            headers = {}
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, params=params, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=params, headers=headers, timeout=10)
            else:
                return {"error": f"Unsupported method: {method}"}
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_ticker_price(self, symbol: str) -> Optional[float]:
        """Get current price"""
        endpoint = "/md/ticker/24hr"
        params = {"symbol": symbol}
        result = self._request("GET", endpoint, params=params)
        
        if "result" in result and "lastEp" in result["result"]:
            return float(result["result"]["lastEp"]) / 10000
        return None
    
    def get_account_balance(self) -> dict:
        """Get account balance"""
        endpoint = "/accounts/accountPositions"
        return self._request("GET", endpoint, signed=True)
    
    def create_market_order(self, symbol: str, side: str, quantity: float, **kwargs) -> dict:
        """Create market order"""
        endpoint = "/orders"
        params = {
            "symbol": symbol,
            "side": side.capitalize(),
            "orderQty": int(quantity),
            "ordType": "Market"
        }
        return self._request("POST", endpoint, params=params, signed=True)
    
    def create_limit_order(self, symbol: str, side: str, quantity: float, price: float, **kwargs) -> dict:
        """Create limit order"""
        endpoint = "/orders"
        params = {
            "symbol": symbol,
            "side": side.capitalize(),
            "orderQty": int(quantity),
            "ordType": "Limit",
            "priceEp": int(price * 10000)
        }
        return self._request("POST", endpoint, params=params, signed=True)
    
    def create_stop_loss(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        """Create stop loss order"""
        close_side = "Sell" if side.upper() == "BUY" else "Buy"
        endpoint = "/orders"
        params = {
            "symbol": symbol,
            "side": close_side,
            "orderQty": int(quantity),
            "ordType": "Stop",
            "stopPxEp": int(stop_price * 10000)
        }
        return self._request("POST", endpoint, params=params, signed=True)
    
    def create_take_profit(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        """Create take profit order"""
        close_side = "Sell" if side.upper() == "BUY" else "Buy"
        endpoint = "/orders"
        params = {
            "symbol": symbol,
            "side": close_side,
            "orderQty": int(quantity),
            "ordType": "LimitIfTouched",
            "triggerType": "ByMarkPrice",
            "stopPxEp": int(stop_price * 10000),
            "priceEp": int(stop_price * 10000)
        }
        return self._request("POST", endpoint, params=params, signed=True)
    
    def cancel_order(self, symbol: str, order_id: str) -> dict:
        """Cancel an order"""
        endpoint = "/orders/cancel"
        params = {
            "symbol": symbol,
            "orderID": order_id
        }
        return self._request("DELETE", endpoint, params=params, signed=True)
    
    def cancel_all_orders(self, symbol: str) -> dict:
        """Cancel all open orders for a symbol"""
        endpoint = "/orders/all"
        params = {"symbol": symbol}
        return self._request("DELETE", endpoint, params=params, signed=True)
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[dict]:
        """Get all open orders"""
        endpoint = "/orders/activeList"
        params = {}
        if symbol:
            params["symbol"] = symbol
        result = self._request("GET", endpoint, params=params, signed=True)
        return result.get("data", {}).get("rows", []) if "data" in result else []
    
    def test_connection(self) -> bool:
        """Test API connection"""
        if not self.api_key or not self.api_secret:
            return False
        result = self.get_account_balance()
        return "error" not in result


class PhemexDemoClient:
    """Simulated Phemex client for paper trading"""
    
    def __init__(self):
        self.demo_balance = 10000
        self.demo_orders = []
        self.demo_positions = {}
    
    def get_ticker_price(self, symbol: str) -> Optional[float]:
        """Get simulated price (uses real Phemex price if available)"""
        try:
            response = requests.get(
                "https://api.phemex.com/md/ticker/24hr",
                params={"symbol": symbol},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                if "result" in data and "lastEp" in data["result"]:
                    return float(data["result"]["lastEp"]) / 10000
        except:
            pass
        return 30000.0
    
    def get_account_balance(self) -> dict:
        """Get demo balance"""
        return {"balance": self.demo_balance, "availableBalance": self.demo_balance}
    
    def create_market_order(self, symbol: str, side: str, quantity: float, **kwargs) -> dict:
        """Simulate market order"""
        price = self.get_ticker_price(symbol)
        order = {
            "orderID": "demo_" + str(len(self.demo_orders) + 1),
            "symbol": symbol,
            "side": side,
            "ordType": "Market",
            "orderQty": quantity,
            "priceEp": int(price * 10000),
            "ordStatus": "Filled"
        }
        self.demo_orders.append(order)
        return order
    
    def create_limit_order(self, symbol: str, side: str, quantity: float, price: float, **kwargs) -> dict:
        """Simulate limit order"""
        order = {
            "orderID": "demo_" + str(len(self.demo_orders) + 1),
            "symbol": symbol,
            "side": side,
            "ordType": "Limit",
            "orderQty": quantity,
            "priceEp": int(price * 10000),
            "ordStatus": "New"
        }
        self.demo_orders.append(order)
        return order
    
    def create_stop_loss(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        """Simulate stop loss"""
        return {
            "orderID": "demo_sl_" + str(len(self.demo_orders) + 1),
            "ordType": "Stop",
            "stopPxEp": int(stop_price * 10000),
            "ordStatus": "New"
        }
    
    def create_take_profit(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        """Simulate take profit"""
        return {
            "orderID": "demo_tp_" + str(len(self.demo_orders) + 1),
            "ordType": "LimitIfTouched",
            "stopPxEp": int(stop_price * 10000),
            "ordStatus": "New"
        }
    
    def cancel_order(self, symbol: str, order_id: str) -> dict:
        """Simulate cancel order"""
        return {"orderID": order_id, "ordStatus": "Canceled"}
    
    def cancel_all_orders(self, symbol: str) -> dict:
        """Simulate cancel all orders"""
        return {"result": "success", "symbol": symbol}
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[dict]:
        """Get simulated open orders"""
        orders = [o for o in self.demo_orders if o.get("ordStatus") == "New"]
        if symbol:
            orders = [o for o in orders if o.get("symbol") == symbol]
        return orders
    
    def test_connection(self) -> bool:
        """Demo always connected"""
        return True
