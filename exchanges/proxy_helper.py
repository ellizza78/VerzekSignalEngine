"""
Proxy Helper for Exchange API Routing
Provides static IP support via Cloudflare Workers proxy
"""

import os
import hmac
import hashlib
import requests
from typing import Optional, Dict
from urllib.parse import urlparse, urlencode


class ProxyHelper:
    """Helper class for routing exchange API calls through proxy"""
    
    def __init__(self):
        self.proxy_enabled = os.getenv("PROXY_ENABLED", "false").lower() == "true"
        self.proxy_url = os.getenv("PROXY_URL", "")
        self.proxy_secret = os.getenv("PROXY_SECRET_KEY", "")
        
        if self.proxy_enabled and not self.proxy_url:
            print("[PROXY WARNING] PROXY_ENABLED=true but PROXY_URL not set. Using direct connection.")
            self.proxy_enabled = False
        
        if self.proxy_enabled and not self.proxy_secret:
            print("[PROXY WARNING] PROXY_ENABLED=true but PROXY_SECRET_KEY not set. Using direct connection.")
            self.proxy_enabled = False
    
    def _generate_proxy_signature(self, body: str = "") -> str:
        """Generate HMAC-SHA256 signature for proxy authentication"""
        signature = hmac.new(
            self.proxy_secret.encode('utf-8'),
            body.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        timeout: int = 10
    ) -> requests.Response:
        """
        Make HTTP request through proxy (if enabled) or directly
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            url: Full URL to exchange API endpoint
            params: Query parameters
            headers: HTTP headers
            json_data: JSON body (for POST requests)
            timeout: Request timeout in seconds
        
        Returns:
            Response object from requests library
        """
        if not self.proxy_enabled:
            # Direct connection (no proxy)
            return requests.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                json=json_data,
                timeout=timeout
            )
        
        # Route through proxy
        parsed_url = urlparse(url)
        exchange_host = parsed_url.netloc
        path = parsed_url.path
        
        # Build query string
        query_string = ""
        if params:
            query_string = urlencode(params)
        if parsed_url.query:
            query_string = f"{parsed_url.query}&{query_string}" if query_string else parsed_url.query
        
        # Prepare body for signature
        body = ""
        if json_data:
            import json
            body = json.dumps(json_data, separators=(',', ':'))
        
        # Generate proxy signature
        proxy_signature = self._generate_proxy_signature(body)
        
        # Build proxy headers
        proxy_headers = {
            "X-Proxy-Signature": proxy_signature,
            "X-Exchange-Host": exchange_host,
            "Content-Type": "application/json" if json_data else "application/x-www-form-urlencoded"
        }
        
        # Add original exchange headers (API keys, etc.)
        if headers:
            for key, value in headers.items():
                if key.lower() not in ['host', 'content-length']:
                    proxy_headers[key] = value
        
        # Build proxy URL
        proxy_endpoint = f"{self.proxy_url}?path={path}"
        if query_string:
            proxy_endpoint = f"{proxy_endpoint}&{query_string}"
        
        # Make request through proxy
        try:
            if method == "GET":
                response = requests.get(
                    proxy_endpoint,
                    headers=proxy_headers,
                    timeout=timeout
                )
            elif method == "POST":
                response = requests.post(
                    proxy_endpoint,
                    headers=proxy_headers,
                    data=body if body else None,
                    timeout=timeout
                )
            elif method == "DELETE":
                response = requests.delete(
                    proxy_endpoint,
                    headers=proxy_headers,
                    timeout=timeout
                )
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
            
        except requests.exceptions.RequestException as e:
            print(f"[PROXY ERROR] Request failed through proxy: {e}")
            print(f"[PROXY ERROR] Falling back to direct connection...")
            
            # Fallback to direct connection on proxy failure
            return requests.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                json=json_data,
                timeout=timeout
            )


# Global singleton instance
_proxy_helper = None

def get_proxy_helper() -> ProxyHelper:
    """Get or create global ProxyHelper instance"""
    global _proxy_helper
    if _proxy_helper is None:
        _proxy_helper = ProxyHelper()
    return _proxy_helper
