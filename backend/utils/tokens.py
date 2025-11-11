"""
Token utilities for password reset and email verification
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional

# In-memory token storage (for simple implementation)
# In production, use Redis or database
_active_tokens = {}


def generate_reset_token(user_id: int) -> str:
    """Generate password reset token (15-minute expiration)"""
    token = secrets.token_urlsafe(32)
    expiry = datetime.utcnow() + timedelta(minutes=15)
    
    _active_tokens[token] = {
        "user_id": user_id,
        "type": "password_reset",
        "expiry": expiry
    }
    
    return token


def generate_verification_token(user_id: int) -> str:
    """Generate email verification token (24-hour expiration)"""
    token = secrets.token_urlsafe(32)
    expiry = datetime.utcnow() + timedelta(hours=24)
    
    _active_tokens[token] = {
        "user_id": user_id,
        "type": "email_verification",
        "expiry": expiry
    }
    
    return token


def verify_token(token: str, token_type: str) -> Optional[int]:
    """Verify token and return user_id if valid"""
    if token not in _active_tokens:
        return None
    
    token_data = _active_tokens[token]
    
    # Check token type
    if token_data["type"] != token_type:
        return None
    
    # Check expiration
    if datetime.utcnow() > token_data["expiry"]:
        del _active_tokens[token]  # Clean up expired token
        return None
    
    return token_data["user_id"]


def invalidate_token(token: str):
    """Invalidate a token (use after successful password reset/verification)"""
    if token in _active_tokens:
        del _active_tokens[token]


def generate_referral_code(user_id: int) -> str:
    """Generate unique referral code for user"""
    # Create a hash based on user_id and random salt
    raw_code = hashlib.sha256(f"{user_id}{secrets.token_hex(8)}".encode()).hexdigest()[:6].upper()
    return f"VZK{raw_code}"
