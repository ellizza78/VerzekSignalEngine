# Exchange Client Proxy Integration

This document shows how to integrate proxy support into exchange clients.

## Integration Pattern

### Step 1: Import Proxy Helper

```python
from exchanges.proxy_helper import get_proxy_helper
```

### Step 2: Update `_request` Method

Replace direct `requests` calls with proxy helper:

**Before (Direct Connection):**
```python
def _request(self, method: str, endpoint: str, params: Optional[dict] = None, signed: bool = False) -> dict:
    url = f"{self.base_url}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, params=params, headers=self.headers, timeout=10)
        # ... etc
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
```

**After (With Proxy Support):**
```python
def _request(self, method: str, endpoint: str, params: Optional[dict] = None, signed: bool = False) -> dict:
    url = f"{self.base_url}{endpoint}"
    proxy = get_proxy_helper()
    
    try:
        # Route through proxy (automatically uses direct connection if proxy disabled)
        response = proxy.request(
            method=method,
            url=url,
            params=params,
            headers=self.headers,
            timeout=10
        )
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
```

### Step 3: Handle JSON POST Requests (Bybit, Phemex)

For exchanges that use JSON body instead of query params:

```python
def _request(self, method: str, endpoint: str, params: Optional[dict] = None, signed: bool = False) -> dict:
    url = f"{self.base_url}{endpoint}"
    proxy = get_proxy_helper()
    
    try:
        if method == "POST":
            # Use json_data parameter for POST with JSON body
            response = proxy.request(
                method=method,
                url=url,
                headers=self.headers,
                json_data=params,  # <- Use json_data instead of params
                timeout=10
            )
        else:
            response = proxy.request(
                method=method,
                url=url,
                params=params,
                headers=self.headers,
                timeout=10
            )
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
```

## Complete Example: Binance Client

```python
from exchanges.proxy_helper import get_proxy_helper

class BinanceClient:
    def __init__(self, testnet: bool = False):
        self.testnet = testnet
        self.api_key = os.getenv("BINANCE_API_KEY", "")
        self.api_secret = os.getenv("BINANCE_API_SECRET", "")
        
        if testnet:
            self.base_url = "https://testnet.binancefuture.com"
        else:
            self.base_url = "https://fapi.binance.com"
        
        self.headers = {"X-MBX-APIKEY": self.api_key}
    
    def _request(self, method: str, endpoint: str, params: Optional[dict] = None, signed: bool = False) -> dict:
        if params is None:
            params = {}
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            params['signature'] = self._generate_signature(params)
        
        url = f"{self.base_url}{endpoint}"
        proxy = get_proxy_helper()  # <- Get proxy helper
        
        try:
            # Route through proxy (falls back to direct if disabled/failed)
            response = proxy.request(
                method=method,
                url=url,
                params=params,
                headers=self.headers,
                timeout=10
            )
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
```

## Files to Update

1. ✅ `exchanges/proxy_helper.py` - Created
2. ⚠️ `exchanges/binance_client.py` - Needs update
3. ⚠️ `exchanges/bybit_client.py` - Needs update
4. ⚠️ `exchanges/phemex_client.py` - Needs update
5. ⚠️ `exchanges/coinexx_client.py` - Needs update

## Testing Proxy Integration

### Test 1: Direct Connection (Proxy Disabled)

```bash
# Replit Secrets
PROXY_ENABLED=false

# Result: All requests go directly to exchanges
```

### Test 2: Proxy Connection (Proxy Enabled)

```bash
# Replit Secrets
PROXY_ENABLED=true
PROXY_URL=https://verzek-exchange-proxy.your-subdomain.workers.dev/proxy
PROXY_SECRET_KEY=a1b2c3d4e5f6...

# Result: All requests routed through Cloudflare Workers proxy
```

### Test 3: Proxy Fallback (Proxy Fails)

```bash
# Replit Secrets (with wrong proxy URL)
PROXY_ENABLED=true
PROXY_URL=https://invalid-proxy.com/proxy
PROXY_SECRET_KEY=...

# Result: Proxy fails, automatically falls back to direct connection
```

## Benefits

1. ✅ **Backward Compatible**: Works without any configuration (direct connection)
2. ✅ **Automatic Fallback**: If proxy fails, falls back to direct connection
3. ✅ **Zero Code Changes**: Just set environment variables to enable proxy
4. ✅ **Static IP**: When proxy enabled, all requests use Cloudflare's static IP
5. ✅ **Secure**: HMAC signature authentication prevents unauthorized proxy use

## Configuration Summary

| Environment Variable | Required | Example | Description |
|---------------------|----------|---------|-------------|
| PROXY_ENABLED | No | `true` | Enable proxy routing (default: `false`) |
| PROXY_URL | If enabled | `https://...workers.dev/proxy` | Cloudflare Workers proxy endpoint |
| PROXY_SECRET_KEY | If enabled | `a1b2c3d4...` | HMAC secret for proxy authentication |

## Next Steps

1. Deploy Cloudflare Workers proxy (see `cloudflare_proxy/README.md`)
2. Get dedicated egress IP from Cloudflare
3. Set Replit Secrets (PROXY_ENABLED, PROXY_URL, PROXY_SECRET_KEY)
4. Whitelist Cloudflare IP on exchanges
5. Test trading with small amounts
6. Monitor for 24 hours before full production
