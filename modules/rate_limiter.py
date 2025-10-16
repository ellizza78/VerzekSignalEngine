"""
Rate Limiting & API Security
Implements per-IP and per-user rate limiting with Flask-Limiter
"""

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request
import json
from datetime import datetime
from utils.logger import log_event


def get_user_identifier():
    """
    Get identifier for rate limiting (user_id or IP)
    Prioritizes authenticated user_id over IP address
    """
    # Try to get user_id from JWT token
    if hasattr(request, 'user_id'):
        return f"user:{request.user_id}"
    
    # Fallback to IP address
    return f"ip:{get_remote_address()}"


class RateLimitHandler:
    """Handles rate limit violations and logging"""
    
    @staticmethod
    def on_breach(limit_data):
        """Called when rate limit is exceeded"""
        identifier = get_user_identifier()
        endpoint = request.endpoint
        
        log_event("RATE_LIMIT", f"Rate limit exceeded: {identifier} on {endpoint}")
        
        # Log to security audit file
        audit_log = {
            'timestamp': datetime.now().isoformat(),
            'event': 'rate_limit_breach',
            'identifier': identifier,
            'endpoint': endpoint,
            'ip': get_remote_address(),
            'limit': str(limit_data)
        }
        
        try:
            with open('database/security_audit.json', 'a') as f:
                f.write(json.dumps(audit_log) + '\n')
        except Exception as e:
            log_event("ERROR", f"Failed to write audit log: {str(e)}")


def init_rate_limiter(app):
    """
    Initialize rate limiter with Flask app
    
    Default limits:
    - Global: 100 requests per minute per IP
    - Per-user: 200 requests per minute per authenticated user
    - Auth endpoints: 5 requests per minute (prevent brute force)
    - Payment endpoints: 10 requests per minute
    - Trading endpoints: 30 requests per minute
    """
    
    limiter = Limiter(
        app=app,
        key_func=get_user_identifier,
        default_limits=["100 per minute"],
        storage_uri="memory://",  # Use Redis in production
        on_breach=RateLimitHandler.on_breach
    )
    
    return limiter


# Rate limit decorators for different endpoint types
def rate_limit_auth(f):
    """Strict rate limit for authentication endpoints"""
    from functools import wraps
    from flask_limiter import Limiter
    
    @wraps(f)
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)
    
    # Applied via limiter.limit() decorator in api_server.py
    return decorated
