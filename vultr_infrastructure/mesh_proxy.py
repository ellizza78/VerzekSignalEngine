#!/usr/bin/env python3
"""
Verzek Proxy Mesh - FastAPI Service
Handles exchange API requests with HMAC authentication and static IP routing
Deploy this on all Vultr nodes (hub + workers)
"""

from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import JSONResponse
import httpx
import hmac
import hashlib
import os
import logging
from datetime import datetime

# ============================================
# CONFIGURATION
# ============================================

ALLOWED_EXCHANGES = [
    "fapi.binance.com",
    "testnet.binancefuture.com",
    "api.binance.com",
    "api.bybit.com",
    "api-testnet.bybit.com",
    "api.phemex.com",
    "testnet-api.phemex.com",
    "futures.kraken.com",
    "api.kraken.com"
]

# Load proxy secret from environment
PROXY_SECRET = os.getenv("PROXY_SECRET_KEY", "")

if not PROXY_SECRET:
    raise ValueError("PROXY_SECRET_KEY environment variable must be set!")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================
# FASTAPI APP
# ============================================

app = FastAPI(
    title="Verzek Proxy Mesh",
    description="Static IP proxy for exchange API routing",
    version="1.0.0"
)

# ============================================
# HELPER FUNCTIONS
# ============================================

def verify_signature(body: bytes, signature: str) -> bool:
    """Verify HMAC-SHA256 signature"""
    if not signature:
        return False
    
    expected = hmac.new(
        PROXY_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected)

# ============================================
# ENDPOINTS
# ============================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "VerzekProxyMesh",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/ip")
async def get_ip_info(request: Request):
    """Get IP address information"""
    client_ip = request.client.host
    
    # Try to get real IP from proxy headers
    forwarded_for = request.headers.get("x-forwarded-for")
    real_ip = request.headers.get("x-real-ip")
    
    return {
        "client_ip": client_ip,
        "x_forwarded_for": forwarded_for,
        "x_real_ip": real_ip,
        "service": "VerzekProxyMesh",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_request(
    request: Request,
    full_path: str,
    x_exchange_host: str = Header(None),
    x_proxy_signature: str = Header(None)
):
    """
    Proxy requests to exchange APIs
    
    Required Headers:
        X-Exchange-Host: Target exchange hostname (e.g., fapi.binance.com)
        X-Proxy-Signature: HMAC-SHA256 signature of request body
    """
    
    # Validate exchange host
    if not x_exchange_host:
        logger.warning(f"Missing X-Exchange-Host header from {request.client.host}")
        raise HTTPException(
            status_code=400,
            detail="Missing X-Exchange-Host header"
        )
    
    if x_exchange_host not in ALLOWED_EXCHANGES:
        logger.warning(f"Unauthorized exchange host: {x_exchange_host} from {request.client.host}")
        raise HTTPException(
            status_code=403,
            detail=f"Unauthorized exchange host: {x_exchange_host}"
        )
    
    # Get request body
    body = await request.body()
    
    # Verify signature
    if not verify_signature(body, x_proxy_signature):
        logger.warning(f"Invalid signature from {request.client.host} for {x_exchange_host}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing X-Proxy-Signature header"
        )
    
    # Build target URL
    query_string = str(request.query_params)
    target_url = f"https://{x_exchange_host}/{full_path}"
    if query_string:
        target_url += f"?{query_string}"
    
    logger.info(f"Proxying {request.method} {target_url} from {request.client.host}")
    
    # Forward request to exchange
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Copy headers (exclude proxy-specific ones)
            headers = dict(request.headers)
            headers.pop("x-proxy-signature", None)
            headers.pop("x-exchange-host", None)
            headers["host"] = x_exchange_host
            
            # Remove internal headers
            headers.pop("x-forwarded-for", None)
            headers.pop("x-real-ip", None)
            
            # Make request to exchange
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body if body else None
            )
            
            # Log response
            logger.info(f"Response from {x_exchange_host}: {response.status_code}")
            
            # Return response with CORS headers
            return JSONResponse(
                content=response.json() if _is_json(response) else {"data": response.text},
                status_code=response.status_code,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "*"
                }
            )
        
        except httpx.TimeoutException:
            logger.error(f"Timeout connecting to {x_exchange_host}")
            raise HTTPException(
                status_code=504,
                detail=f"Timeout connecting to {x_exchange_host}"
            )
        
        except Exception as e:
            logger.error(f"Error proxying to {x_exchange_host}: {str(e)}")
            raise HTTPException(
                status_code=502,
                detail=f"Proxy request failed: {str(e)}"
            )

def _is_json(response):
    """Check if response is JSON"""
    content_type = response.headers.get("content-type", "")
    return "application/json" in content_type.lower()

# ============================================
# CORS MIDDLEWARE
# ============================================

@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """Handle CORS preflight requests"""
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }
    )

# ============================================
# STARTUP EVENT
# ============================================

@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info("=" * 60)
    logger.info("Verzek Proxy Mesh - FastAPI Service")
    logger.info("=" * 60)
    logger.info(f"Proxy Secret Key: {'*' * 20} (loaded)")
    logger.info(f"Allowed Exchanges: {', '.join(ALLOWED_EXCHANGES)}")
    logger.info("Service ready to proxy exchange API requests")
    logger.info("=" * 60)

if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        log_level="info"
    )
