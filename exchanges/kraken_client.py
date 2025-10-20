"""
Kraken Futures Exchange Client
Handles Kraken Futures trading with secure API key management
"""

import os
import time
import hmac
import hashlib
import base64
import requests
from typing import Optional, List
from exchanges.proxy_helper import get_proxy_helper


class KrakenClient:
    """Kraken Futures API client"""
    
    def __init__(self, testnet: bool = False):
        self.testnet = testnet
        
        # Load API keys from environment (Replit Secrets)
        self.api_key = os.getenv("KRAKEN_API_KEY", "")
        self.api_secret = os.getenv("KRAKEN_API_SECRET", "")
        
        # Set base URL
        if testnet:
            self.base_url = "https://demo-futures.kraken.com/derivatives/api/v3"
        else:
            self.base_url = "https://futures.kraken.com/derivatives/api/v3"
    
    def _generate_signature(self, endpoint: str, nonce: str, data: str = "") -> str:
        """Generate authentication signature for Kraken API"""
        if not self.api_secret:
            return ""
        
        # Kraken uses SHA256 HMAC
        message = data + nonce + endpoint
        secret_decoded = base64.b64decode(self.api_secret)
        signature = hmac.new(secret_decoded, message.encode(), hashlib.sha256)
        return base64.b64encode(signature.digest()).decode()
    
    def _request(self, method: str, endpoint: str, params: Optional[dict] = None, authenticated: bool = False) -> dict:
        """Make API request (with proxy support)"""
        if params is None:
            params = {}
        
        url = f"{self.base_url}{endpoint}"
        headers = {}
        
        # Add authentication headers if needed
        if authenticated:
            nonce = str(int(time.time() * 1000))
            data_string = ""
            if params:
                data_string = "&".join([f"{k}={v}" for k, v in params.items()])
            
            signature = self._generate_signature(endpoint, nonce, data_string)
            headers["APIKey"] = self.api_key
            headers["Authent"] = signature
            headers["Nonce"] = nonce
        
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        
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
            return {"error": str(e), "result": "error"}
    
    def get_ticker_price(self, symbol: str) -> Optional[float]:
        """Get current price"""
        endpoint = "/tickers"
        result = self._request("GET", endpoint)
        
        if "tickers" in result:
            # Find matching symbol in tickers array
            for ticker in result["tickers"]:
                if ticker.get("symbol") == symbol:
                    return float(ticker.get("last", 0))
        return None
    
    def get_account_balance(self) -> dict:
        """Get account balance"""
        endpoint = "/accounts"
        return self._request("GET", endpoint, authenticated=True)
    
    def create_market_order(self, symbol: str, side: str, quantity: float, **kwargs) -> dict:
        """Create market order"""
        endpoint = "/sendorder"
        params = {
            "orderType": "mkt",
            "symbol": symbol,
            "side": side.lower(),
            "size": quantity
        }
        return self._request("POST", endpoint, params=params, authenticated=True)
    
    def create_limit_order(self, symbol: str, side: str, quantity: float, price: float, **kwargs) -> dict:
        """Create limit order"""
        endpoint = "/sendorder"
        params = {
            "orderType": "lmt",
            "symbol": symbol,
            "side": side.lower(),
            "size": quantity,
            "limitPrice": price
        }
        return self._request("POST", endpoint, params=params, authenticated=True)
    
    def create_stop_loss(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        """Create stop loss order"""
        close_side = "sell" if side.upper() == "BUY" else "buy"
        endpoint = "/sendorder"
        params = {
            "orderType": "stp",
            "symbol": symbol,
            "side": close_side,
            "size": quantity,
            "stopPrice": stop_price
        }
        return self._request("POST", endpoint, params=params, authenticated=True)
    
    def create_take_profit(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        """Create take profit order"""
        close_side = "sell" if side.upper() == "BUY" else "buy"
        endpoint = "/sendorder"
        params = {
            "orderType": "take_profit",
            "symbol": symbol,
            "side": close_side,
            "size": quantity,
            "limitPrice": stop_price
        }
        return self._request("POST", endpoint, params=params, authenticated=True)
    
    def cancel_order(self, symbol: str, order_id: str) -> dict:
        """Cancel an order"""
        endpoint = "/cancelorder"
        params = {"order_id": order_id}
        return self._request("POST", endpoint, params=params, authenticated=True)
    
    def cancel_all_orders(self, symbol: str) -> dict:
        """Cancel all open orders for a symbol"""
        endpoint = "/cancelallorders"
        params = {"symbol": symbol}
        return self._request("POST", endpoint, params=params, authenticated=True)
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List:
        """Get all open orders"""
        endpoint = "/openorders"
        result = self._request("GET", endpoint, authenticated=True)
        
        if "openOrders" in result:
            orders = result["openOrders"]
            if symbol:
                orders = [o for o in orders if o.get("symbol") == symbol]
            return orders
        return []
    
    def test_connection(self) -> bool:
        """Test API connection"""
        if not self.api_key:
            return False
        result = self.get_account_balance()
        return "error" not in result


class KrakenDemoClient:
    """Simulated Kraken client for paper trading"""
    
    def __init__(self):
        self.demo_balance = 10000
        self.demo_orders = []
    
    def get_ticker_price(self, symbol: str) -> Optional[float]:
        """Get simulated price (deterministic for demo)"""
        # Deterministic demo pricing based on symbol
        base_prices = {
            "PI_XBTUSD": 43000.0,  # Bitcoin
            "PI_ETHUSD": 2300.0,   # Ethereum
            "PF_SOLUSD": 98.0,     # Solana
            "PF_XRPUSD": 0.52,     # XRP
            "PI_LTCUSD": 72.0      # Litecoin
        }
        return base_prices.get(symbol, 30000.0)
    
    def get_account_balance(self) -> dict:
        """Get demo balance"""
        return {
            "accounts": {
                "flex": {
                    "balanceValue": self.demo_balance,
                    "availableMargin": self.demo_balance
                }
            }
        }
    
    def create_market_order(self, symbol: str, side: str, quantity: float, **kwargs) -> dict:
        """Simulate market order"""
        price = self.get_ticker_price(symbol)
        order = {
            "sendStatus": {
                "order_id": "demo_" + str(len(self.demo_orders) + 1),
                "status": "placed"
            },
            "order": {
                "symbol": symbol,
                "side": side,
                "orderType": "mkt",
                "size": quantity,
                "filled": quantity,
                "limitPrice": price
            }
        }
        self.demo_orders.append(order)
        return order
    
    def create_limit_order(self, symbol: str, side: str, quantity: float, price: float, **kwargs) -> dict:
        """Simulate limit order"""
        order = {
            "sendStatus": {
                "order_id": "demo_" + str(len(self.demo_orders) + 1),
                "status": "placed"
            },
            "order": {
                "symbol": symbol,
                "side": side,
                "orderType": "lmt",
                "size": quantity,
                "limitPrice": price
            }
        }
        self.demo_orders.append(order)
        return order
    
    def create_stop_loss(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        """Simulate stop loss"""
        return {
            "sendStatus": {
                "order_id": "demo_sl_" + str(len(self.demo_orders) + 1),
                "status": "placed"
            },
            "order": {
                "orderType": "stp",
                "stopPrice": stop_price
            }
        }
    
    def create_take_profit(self, symbol: str, side: str, quantity: float, stop_price: float) -> dict:
        """Simulate take profit"""
        return {
            "sendStatus": {
                "order_id": "demo_tp_" + str(len(self.demo_orders) + 1),
                "status": "placed"
            },
            "order": {
                "orderType": "take_profit",
                "limitPrice": stop_price
            }
        }
    
    def cancel_order(self, symbol: str, order_id: str) -> dict:
        """Simulate cancel order"""
        return {
            "cancelStatus": {
                "order_id": order_id,
                "status": "cancelled"
            }
        }
    
    def cancel_all_orders(self, symbol: str) -> dict:
        """Simulate cancel all orders"""
        return {
            "cancelStatus": {
                "status": "cancelled",
                "cancelledOrders": len(self.demo_orders)
            }
        }
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List:
        """Get simulated open orders"""
        orders = [o.get("order", {}) for o in self.demo_orders]
        if symbol:
            orders = [o for o in orders if o.get("symbol") == symbol]
        return orders
    
    def test_connection(self) -> bool:
        """Demo always connected"""
        return True
