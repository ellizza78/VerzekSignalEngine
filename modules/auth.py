"""
Authentication Module
--------------------
JWT-based authentication for mobile app users
"""

import jwt
import bcrypt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "verzek-super-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour
REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30 days


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(user_id: str, email: str) -> str:
    """Create JWT access token"""
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.utcnow(),
        "type": "access"
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """Create JWT refresh token"""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "iat": datetime.utcnow(),
        "type": "refresh"
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_token(token: str):
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # "Bearer TOKEN"
            except IndexError:
                return jsonify({"error": "Invalid authorization header format"}), 401
        
        if not token:
            return jsonify({"error": "Authentication token is missing"}), 401
        
        # Decode and verify token
        payload = decode_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Check token type
        if payload.get("type") != "access":
            return jsonify({"error": "Invalid token type"}), 401
        
        # Add user_id to request context
        request.user_id = payload.get("user_id")
        request.user_email = payload.get("email")
        
        return f(*args, **kwargs)
    
    return decorated


def refresh_token_required(f):
    """Decorator to require valid refresh token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"error": "Invalid authorization header format"}), 401
        
        if not token:
            return jsonify({"error": "Refresh token is missing"}), 401
        
        payload = decode_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired refresh token"}), 401
        
        if payload.get("type") != "refresh":
            return jsonify({"error": "Invalid token type"}), 401
        
        request.user_id = payload.get("user_id")
        
        return f(*args, **kwargs)
    
    return decorated
