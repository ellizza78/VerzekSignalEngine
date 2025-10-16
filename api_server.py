"""
api_server.py
-------------
Flask REST API layer for VerzekAutoTrader.
Allows mobile app or external dashboard to fetch real-time data.
"""

from flask import Flask, jsonify, request
from utils.logger import log_event
from trade_executor import get_all_trades
from modules import UserManager, PositionTracker, SafetyManager
from modules.auth import (
    hash_password, verify_password, 
    create_access_token, create_refresh_token,
    token_required, refresh_token_required
)
from modules.subscription_security import subscription_security
from modules.payment_system import payment_system
from flask_simple_captcha import CAPTCHA
import time
import os
import re
from datetime import datetime, timedelta

# Phase 1 Security Features
from modules.rate_limiter import init_rate_limiter
from modules.two_factor_auth import two_factor_auth
from modules.backup_system import backup_system
from modules.tronscan_client import tronscan_client
from modules.audit_logger import audit_logger, AuditEventType

app = Flask(__name__)

# Configure CAPTCHA
CAPTCHA_CONFIG = {
    'SECRET_CAPTCHA_KEY': os.environ.get('CAPTCHA_SECRET_KEY', 'VerzekAutoTrader2025SecureKey!@#'),
    'CAPTCHA_LENGTH': 6,
    'CAPTCHA_DIGITS': True,
    'EXPIRE_SECONDS': 600,
    'CAPTCHA_IMG_FORMAT': 'JPEG'
}

SIMPLE_CAPTCHA = CAPTCHA(config=CAPTCHA_CONFIG)
app = SIMPLE_CAPTCHA.init_app(app)

# Initialize rate limiter
limiter = init_rate_limiter(app)

# Initialize managers
user_manager = UserManager()
position_tracker = PositionTracker()
safety_manager = SafetyManager()

# ============================
# APP STATUS
# ============================

start_time = time.time()

# ============================
# HOME PAGE
# ============================

@app.route("/")
def home():
    uptime = round(time.time() - start_time, 2)
    return jsonify({
        "name": "VerzekAutoTrader API",
        "version": "1.0",
        "status": "online",
        "uptime_seconds": uptime,
        "description": "Automated cryptocurrency trading bot API",
        "endpoints": {
            "/": "API documentation (this page)",
            "/api/status": "Get bot status and uptime",
            "/api/test": "Test API connection",
            "/api/trades": "Get all executed trades",
            "/api/latest": "Get latest trade",
            "/api/users": "User management (GET/POST)",
            "/api/users/<user_id>": "Single user (GET/PUT/DELETE)",
            "/api/users/<user_id>/general": "General mode settings (GET/PUT)",
            "/api/users/<user_id>/risk": "Capital & risk settings (GET/PUT)",
            "/api/users/<user_id>/strategy": "Strategy parameters (GET/PUT)",
            "/api/users/<user_id>/dca": "DCA margin call settings (GET/PUT)",
            "/api/users/<user_id>/exchanges": "Exchange accounts (GET/POST)",
            "/api/users/<user_id>/subscription": "Subscription management (GET/POST)",
            "/api/positions": "All positions (GET)",
            "/api/positions/<user_id>": "User positions (GET)",
            "/api/safety/status": "Safety system status (GET)",
            "/api/safety/killswitch": "Kill switch control (POST)",
            "/api/safety/pause": "Pause trading (POST)",
            "/api/safety/resume": "Resume trading (POST)"
        },
        "message": "VerzekAutoTrader is running smoothly! 🚀"
    })


@app.route("/api/status")
def get_status():
    uptime = round(time.time() - start_time, 2)
    return jsonify({
        "bot": "VerzekAutoTrader",
        "status": "online",
        "uptime_seconds": uptime,
        "message": "Bot is running smoothly 🚀"
    })


# ============================
# FETCH TRADES
# ============================

@app.route("/api/trades")
def fetch_trades():
    trades = get_all_trades()
    return jsonify({
        "count": len(trades),
        "trades": trades
    })


# ============================
# FETCH LATEST TRADE
# ============================

@app.route("/api/latest")
def latest_trade():
    trades = get_all_trades()
    if not trades:
        return jsonify({"message": "No trades found yet."})
    return jsonify(trades[-1])


# ============================
# TEST CONNECTION
# ============================

@app.route("/api/test")
def test():
    return jsonify({
        "status": "success",
        "message": "📡 Flask API connection successful!"
    })


@app.route("/api/system/ip")
def get_server_ip():
    """Get server IP for exchange API whitelisting"""
    import requests as req
    try:
        response = req.get('https://api.ipify.org?format=json', timeout=5)
        server_ip = response.json().get('ip', '34.11.228.15')
    except:
        server_ip = '34.11.228.15'
    
    return jsonify({
        "server_ip": server_ip,
        "instructions": {
            "step_1": "Copy the IP address above",
            "step_2": "Go to your exchange (Binance, Bybit, etc.)",
            "step_3": "When creating API keys, select 'Restrict access to trusted IPs only'",
            "step_4": "Add this IP address to the whitelist",
            "step_5": "Enable 'Enable Futures' permission",
            "step_6": "Enable 'Enable Reading' permission",
            "important": "⚠️ ALWAYS use ISOLATED MARGIN on your exchange, NOT Cross Margin"
        },
        "supported_exchanges": [
            {
                "name": "Binance",
                "api_url": "https://www.binance.com/en/my/settings/api-management"
            },
            {
                "name": "Bybit",
                "api_url": "https://www.bybit.com/app/user/api-management"
            },
            {
                "name": "Phemex",
                "api_url": "https://phemex.com/account/api-management"
            },
            {
                "name": "Coinexx",
                "api_url": "https://www.coinexx.com/api"
            }
        ]
    })


# ============================
# CAPTCHA ENDPOINTS
# ============================

@app.route("/api/captcha/generate", methods=["GET"])
def generate_captcha():
    """Generate a new CAPTCHA challenge"""
    captcha_dict = SIMPLE_CAPTCHA.create()
    return jsonify({
        "captcha_hash": captcha_dict['captcha_hash'],
        "captcha_image": captcha_dict['captcha_base64']
    })


@app.route("/api/captcha/verify", methods=["POST"])
def verify_captcha():
    """Verify CAPTCHA (standalone endpoint for testing)"""
    data = request.json
    c_hash = data.get('captcha_hash')
    c_text = data.get('captcha_text')
    
    if SIMPLE_CAPTCHA.verify(c_text, c_hash):
        return jsonify({'status': 'success', 'message': 'CAPTCHA verified'}), 200
    else:
        return jsonify({'status': 'failed', 'error': 'Invalid CAPTCHA'}), 400


# ============================
# AUTHENTICATION
# ============================

@app.route("/api/auth/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():
    """Register a new user with rate limiting"""
    data = request.json
    
    email = data.get("email", "").strip().lower()
    password = data.get("password")
    full_name = data.get("full_name", "")
    captcha_hash = data.get("captcha_hash")
    captcha_text = data.get("captcha_text")
    
    # CAPTCHA validation
    if not captcha_hash or not captcha_text:
        return jsonify({"error": "CAPTCHA is required"}), 400
    
    if not SIMPLE_CAPTCHA.verify(captcha_text, captcha_hash):
        return jsonify({"error": "Invalid CAPTCHA. Please try again."}), 400
    
    # Validation
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    # Email format validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        return jsonify({"error": "Invalid email format"}), 400
    
    # Password strength
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    
    # Check if user already exists
    users = user_manager.get_all_users()
    for user in users:
        if user.email == email:
            return jsonify({"error": "User with this email already exists"}), 409
    
    # Create user with email as user_id
    user_id = email.replace("@", "_").replace(".", "_")
    user = user_manager.create_user(user_id)
    
    # Set user credentials
    user.email = email
    user.full_name = full_name
    user.password_hash = hash_password(password)
    user_manager._save_users()
    
    # Generate tokens
    access_token = create_access_token(user_id, email)
    refresh_token = create_refresh_token(user_id)
    
    log_event("AUTH", f"New user registered: {email}")
    
    return jsonify({
        "message": "Registration successful",
        "user": {
            "user_id": user_id,
            "email": email,
            "full_name": full_name,
            "plan": user.plan
        },
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    }), 201


@app.route("/api/auth/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    """Login user with 2FA support and rate limiting"""
    data = request.json
    
    email = data.get("email", "").strip().lower()
    password = data.get("password")
    mfa_token = data.get("mfa_token")  # Optional 2FA token
    captcha_hash = data.get("captcha_hash")
    captcha_text = data.get("captcha_text")
    
    # CAPTCHA validation
    if not captcha_hash or not captcha_text:
        return jsonify({"error": "CAPTCHA is required"}), 400
    
    if not SIMPLE_CAPTCHA.verify(captcha_text, captcha_hash):
        audit_logger.log_event(
            AuditEventType.LOGIN_FAILED,
            ip_address=request.remote_addr,
            details={'reason': 'invalid_captcha', 'email': email}
        )
        return jsonify({"error": "Invalid CAPTCHA. Please try again."}), 400
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    # Find user by email
    users = user_manager.get_all_users()
    user = None
    for u in users:
        if u.email == email:
            user = u
            break
    
    if not user:
        audit_logger.log_event(
            AuditEventType.LOGIN_FAILED,
            ip_address=request.remote_addr,
            details={'reason': 'user_not_found', 'email': email}
        )
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Verify password
    if not user.password_hash or not verify_password(password, user.password_hash):
        audit_logger.log_event(
            AuditEventType.LOGIN_FAILED,
            user_id=user.user_id,
            ip_address=request.remote_addr,
            details={'reason': 'invalid_password'}
        )
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Check if 2FA is enabled
    if two_factor_auth.is_enabled(user.user_id):
        if not mfa_token:
            # Password correct, but 2FA required
            return jsonify({
                "requires_2fa": True,
                "message": "2FA verification required",
                "user_id": user.user_id
            }), 200
        
        # Verify 2FA token
        is_valid, message = two_factor_auth.verify_token(user.user_id, mfa_token)
        
        if not is_valid:
            audit_logger.log_event(
                AuditEventType.MFA_FAILED,
                user_id=user.user_id,
                ip_address=request.remote_addr
            )
            return jsonify({"error": f"Invalid 2FA code: {message}"}), 401
        
        audit_logger.log_event(
            AuditEventType.MFA_VERIFIED,
            user_id=user.user_id,
            ip_address=request.remote_addr
        )
    
    # Generate tokens
    access_token = create_access_token(user.user_id, email)
    refresh_token = create_refresh_token(user.user_id)
    
    audit_logger.log_event(
        AuditEventType.LOGIN_SUCCESS,
        user_id=user.user_id,
        ip_address=request.remote_addr
    )
    
    log_event("AUTH", f"User logged in: {email}")
    
    return jsonify({
        "message": "Login successful",
        "user": {
            "user_id": user.user_id,
            "email": email,
            "full_name": user.full_name,
            "plan": user.plan,
            "plan_expires_at": user.plan_expires_at,
            "mfa_enabled": two_factor_auth.is_enabled(user.user_id)
        },
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer"
    })


@app.route("/api/auth/refresh", methods=["POST"])
@refresh_token_required
def refresh():
    """Refresh access token using refresh token"""
    user_id = request.user_id
    user = user_manager.get_user(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Generate new access token
    access_token = create_access_token(user_id, user.email)
    
    return jsonify({
        "access_token": access_token,
        "token_type": "Bearer"
    })


@app.route("/api/auth/me", methods=["GET"])
@token_required
def get_current_user():
    """Get current authenticated user info"""
    user_id = request.user_id
    user = user_manager.get_user(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "user": user.to_dict()
    })


# ============================
# USER MANAGEMENT
# ============================

@app.route("/api/users", methods=["GET", "POST"])
def handle_users():
    """Get all users or create a new user"""
    if request.method == "GET":
        users = user_manager.get_all_users()
        return jsonify({
            "count": len(users),
            "users": [user.to_dict() for user in users]
        })
    
    elif request.method == "POST":
        data = request.json
        user_id = data.get("user_id")
        telegram_id = data.get("telegram_id")
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        user = user_manager.create_user(user_id, telegram_id)
        return jsonify({
            "message": "User created successfully",
            "user": user.to_dict()
        }), 201


@app.route("/api/users/<user_id>", methods=["GET", "PUT", "DELETE"])
def handle_single_user(user_id):
    """Get, update, or delete a specific user"""
    if request.method == "GET":
        user = user_manager.get_user(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        return jsonify(user.to_dict())
    
    elif request.method == "PUT":
        user = user_manager.get_user(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        updates = request.json
        user_manager.update_user(user_id, updates)
        return jsonify({
            "message": "User updated successfully",
            "user": user_manager.get_user(user_id).to_dict()
        })
    
    elif request.method == "DELETE":
        user = user_manager.get_user(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        user_manager.delete_user(user_id)
        return jsonify({"message": "User deleted successfully"})


# ============================
# GENERAL MODE SETTINGS
# ============================

@app.route("/api/users/<user_id>/general", methods=["GET", "PUT"])
def handle_general_settings(user_id):
    """Get or update user's general mode settings"""
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if request.method == "GET":
        return jsonify(user.general_settings)
    
    elif request.method == "PUT":
        updates = request.json
        user.update_general_settings(updates)
        user_manager._save_users()
        return jsonify({
            "message": "General settings updated",
            "general_settings": user.general_settings
        })


# ============================
# CAPITAL & RISK SETTINGS
# ============================

@app.route("/api/users/<user_id>/risk", methods=["GET", "PUT"])
def handle_risk_settings(user_id):
    """Get or update user's risk settings"""
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if request.method == "GET":
        return jsonify(user.risk_settings)
    
    elif request.method == "PUT":
        updates = request.json
        user.update_risk_settings(updates)
        user_manager._save_users()
        return jsonify({
            "message": "Risk settings updated",
            "risk_settings": user.risk_settings
        })


# ============================
# STRATEGY PARAMETERS
# ============================

@app.route("/api/users/<user_id>/strategy", methods=["GET", "PUT"])
def handle_strategy_settings(user_id):
    """Get or update user's strategy parameters"""
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if request.method == "GET":
        return jsonify(user.strategy_settings)
    
    elif request.method == "PUT":
        updates = request.json
        user.update_strategy_settings(updates)
        user_manager._save_users()
        return jsonify({
            "message": "Strategy settings updated",
            "strategy_settings": user.strategy_settings
        })


# ============================
# DCA MARGIN CALL SETTINGS (VIP ONLY)
# ============================

@app.route("/api/users/<user_id>/dca", methods=["GET", "PUT"])
def handle_dca_settings(user_id):
    """Get or update user's DCA settings"""
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if request.method == "GET":
        return jsonify(user.dca_settings)
    
    elif request.method == "PUT":
        updates = request.json
        user.update_dca_settings(updates)
        user_manager._save_users()
        return jsonify({
            "message": "DCA settings updated",
            "dca_settings": user.dca_settings
        })


# ============================
# EXCHANGE ACCOUNTS
# ============================

@app.route("/api/users/<user_id>/exchanges", methods=["GET", "POST", "DELETE"])
def handle_exchanges(user_id):
    """Get, add, or remove exchange accounts"""
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if request.method == "GET":
        return jsonify({
            "count": len(user.exchange_accounts),
            "exchanges": user.exchange_accounts
        })
    
    elif request.method == "POST":
        data = request.json
        exchange = data.get("exchange")
        api_key_id = data.get("api_key_id")
        testnet = data.get("testnet", False)
        
        if not exchange or not api_key_id:
            return jsonify({"error": "exchange and api_key_id required"}), 400
        
        user_manager.add_exchange_to_user(user_id, exchange, api_key_id, testnet)
        return jsonify({
            "message": "Exchange account added",
            "exchanges": user_manager.get_user(user_id).exchange_accounts
        }), 201
    
    elif request.method == "DELETE":
        account_id = request.json.get("account_id")
        if not account_id:
            return jsonify({"error": "account_id required"}), 400
        
        user_manager.remove_exchange_account(user_id, account_id)
        return jsonify({"message": "Exchange account removed"})


# ============================
# SUBSCRIPTION MANAGEMENT
# ============================

@app.route("/api/users/<user_id>/subscription", methods=["GET", "POST"])
def handle_subscription(user_id):
    """Get subscription info or activate a plan"""
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if request.method == "GET":
        # Check if subscription expired and lock if needed
        user.check_and_lock_expired_users()
        user_manager._save_users()
        
        return jsonify({
            "plan": user.plan,
            "plan_started_at": user.plan_started_at,
            "plan_expires_at": user.plan_expires_at,
            "is_expired": user.is_subscription_expired(),
            "group_access": user.telegram_group_access,
            "features": user.get_plan_features()
        })
    
    elif request.method == "POST":
        data = request.json
        plan = data.get("plan")  # free, pro, vip
        
        if plan not in ["free", "pro", "vip"]:
            return jsonify({"error": "Invalid plan. Must be: free, pro, or vip"}), 400
        
        # Set duration based on plan
        duration_map = {"free": 3, "pro": 30, "vip": 30}
        duration = duration_map[plan]
        
        user.activate_subscription(plan, duration)
        user_manager._save_users()
        
        return jsonify({
            "message": f"{plan.upper()} plan activated successfully",
            "plan": user.plan,
            "plan_expires_at": user.plan_expires_at,
            "group_access": user.telegram_group_access,
            "features": user.get_plan_features()
        }), 201
# ============================
# TRADING PREFERENCES
# ============================

@app.route("/api/users/<user_id>/preferences", methods=["GET", "PUT"])
def handle_trading_preferences(user_id):
    """Get or update user's trading preferences (notifications, symbols, etc)"""
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    if request.method == "GET":
        return jsonify(user.trading_preferences)
    
    elif request.method == "PUT":
        updates = request.json
        user.trading_preferences.update(updates)
        user.updated_at = time.time()
        user_manager._save_users()
        return jsonify({
            "message": "Trading preferences updated",
            "trading_preferences": user.trading_preferences
        })


# ============================
# SIGNALS FEED
# ============================

@app.route("/api/signals", methods=["GET"])
def get_signals():
    """Get recent trading signals from broadcast log"""
    try:
        log_file = "database/broadcast_log.txt"
        if not os.path.exists(log_file):
            return jsonify({"count": 0, "signals": []})
        
        # Read last 50 lines from log file
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()[-50:]
        
        signals = []
        for line in lines:
            # Parse timestamp and text
            match = re.match(r'\[(.*?)\] (.*)', line.strip())
            if match:
                timestamp, text = match.groups()
                
                # Only include lines that look like signals (contain trading keywords)
                if any(kw in text.upper() for kw in ["LONG", "SHORT", "ENTRY", "TARGET", "USDT"]):
                    signals.append({
                        "timestamp": timestamp,
                        "text": text,
                        "id": f"{timestamp}_{len(signals)}"
                    })
        
        # Reverse to show newest first
        signals.reverse()
        
        return jsonify({
            "count": len(signals),
            "signals": signals
        })
    except Exception as e:
        log_event("ERROR", f"Error reading signals: {e}")
        return jsonify({"error": "Failed to read signals", "count": 0, "signals": []}), 500


# ============================
# POSITIONS
# ============================

@app.route("/api/positions", methods=["GET"])
def get_all_positions():
    """Get all positions across all users"""
    all_positions = position_tracker.get_all_positions()
    return jsonify({
        "count": len(all_positions),
        "positions": all_positions
    })


@app.route("/api/positions/<user_id>", methods=["GET"])
def get_user_positions(user_id):
    """Get positions for a specific user"""
    # Filter positions by user_id
    all_positions = position_tracker.get_all_positions()
    user_positions = [p for p in all_positions if p.get("user_id") == user_id]
    
    return jsonify({
        "user_id": user_id,
        "count": len(user_positions),
        "positions": user_positions
    })


# ============================
# STATISTICS
# ============================

@app.route("/api/users/<user_id>/stats", methods=["GET"])
def get_user_stats(user_id):
    """Get user trading statistics"""
    user = user_manager.get_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "stats": user.stats,
        "daily_stats": user.daily_stats
    })


# ============================
# SAFETY CONTROLS
# ============================

@app.route("/api/safety/status", methods=["GET"])
def get_safety_status():
    """Get safety system status"""
    return jsonify(safety_manager.get_safety_status())


@app.route("/api/safety/killswitch", methods=["POST"])
def control_killswitch():
    """Activate or deactivate kill switch"""
    data = request.json or {}
    action = data.get("action")  # "activate" or "deactivate"
    reason = data.get("reason", "Manual activation")
    
    if action == "activate":
        result = safety_manager.activate_kill_switch(reason)
        return jsonify(result)
    elif action == "deactivate":
        result = safety_manager.deactivate_kill_switch()
        return jsonify(result)
    else:
        return jsonify({"error": "Invalid action. Use 'activate' or 'deactivate'"}), 400


@app.route("/api/safety/pause", methods=["POST"])
def pause_trading():
    """Pause trading for a specific duration"""
    data = request.json or {}
    duration = data.get("duration_minutes", 60)
    reason = data.get("reason", "Manual pause")
    
    result = safety_manager.pause_trading(duration, reason)
    return jsonify(result)


@app.route("/api/safety/resume", methods=["POST"])
def resume_trading():
    """Resume trading immediately"""
    result = safety_manager.resume_trading()
    return jsonify(result)


@app.route("/api/safety/circuit-breaker", methods=["POST"])
def control_circuit_breaker():
    """Activate or deactivate circuit breaker"""
    data = request.json or {}
    action = data.get("action")
    reason = data.get("reason", "Manual activation")
    
    if action == "activate":
        result = safety_manager.activate_circuit_breaker(reason)
        return jsonify(result)
    elif action == "deactivate":
        result = safety_manager.deactivate_circuit_breaker()
        return jsonify(result)
    else:
        return jsonify({"error": "Invalid action. Use 'activate' or 'deactivate'"}), 400


# ============================
# PAYMENT & SUBSCRIPTION SYSTEM
# ============================

@app.route("/api/payments/create", methods=["POST"])
@token_required
def create_payment_request(current_user_id):
    """Create payment request for subscription upgrade"""
    data = request.json
    plan = data.get('plan')
    
    if not plan or plan not in ['pro', 'vip']:
        return jsonify({'error': 'Invalid plan. Choose pro or vip'}), 400
    
    result = payment_system.create_payment_request(current_user_id, plan)
    return jsonify(result)


@app.route("/api/payments/verify", methods=["POST"])
@token_required
def submit_payment_verification(current_user_id):
    """Submit payment for verification with TX hash and MANDATORY HMAC signature"""
    data = request.json
    
    payment_id = data.get('payment_id')
    tx_hash = data.get('tx_hash')
    referral_code = data.get('referral_code')
    signature = request.headers.get('X-Payment-Signature')
    
    if not payment_id or not tx_hash:
        return jsonify({'error': 'payment_id and tx_hash required'}), 400
    
    if not signature:
        return jsonify({'error': 'X-Payment-Signature header required for security'}), 401
    
    payment_data = {
        'payment_id': payment_id,
        'tx_hash': tx_hash,
        'user_id': current_user_id
    }
    
    if not subscription_security.verify_payment_signature(payment_data, signature):
        return jsonify({'error': 'Invalid payment signature'}), 403
    
    result = payment_system.verify_usdt_payment(
        payment_id, tx_hash, current_user_id, referral_code
    )
    return jsonify(result)


@app.route("/api/payments/pending", methods=["GET"])
@token_required
def get_pending_payments_admin(current_user_id):
    """Admin: Get pending payment verifications"""
    user = user_manager.get_user(current_user_id)
    
    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    pending = payment_system.get_pending_payments()
    return jsonify({'count': len(pending), 'payments': pending})


@app.route("/api/payments/confirm/<payment_id>", methods=["POST"])
@token_required
def confirm_payment_admin(current_user_id, payment_id):
    """Admin: Confirm payment and activate subscription with MANDATORY HMAC signature"""
    from datetime import datetime, timedelta
    
    user = user_manager.get_user(current_user_id)
    
    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.json
    is_valid = data.get('is_valid', False)
    signature = request.headers.get('X-Admin-Signature')
    
    if not signature:
        return jsonify({'error': 'X-Admin-Signature header required for security'}), 401
    
    admin_action = {
        'payment_id': payment_id,
        'admin_id': current_user_id,
        'is_valid': is_valid,
        'timestamp': int(datetime.now().timestamp())
    }
    
    if not subscription_security.verify_payment_signature(admin_action, signature):
        return jsonify({'error': 'Invalid admin signature'}), 403
    
    result = payment_system.admin_confirm_payment(payment_id, is_valid)
    
    if result['success'] and is_valid:
        target_user = user_manager.get_user(result['user_id'])
        target_user.plan = result['plan']
        target_user.plan_started_at = datetime.now().isoformat()
        target_user.plan_expires_at = (datetime.now() + timedelta(days=30)).isoformat()
        
        license_key = subscription_security.generate_license_key(
            result['user_id'], result['plan'], 30
        )
        target_user.license_key = license_key
        
        user_manager._save_users()
        
        result['license_key'] = license_key
    
    return jsonify(result)


# ============================
# REFERRAL SYSTEM
# ============================

@app.route("/api/referral/code", methods=["GET"])
@token_required
def get_referral_code(current_user_id):
    """Get user's referral code"""
    user = user_manager.get_user(current_user_id)
    
    if not hasattr(user, 'referral_code') or not user.referral_code:
        user.referral_code = subscription_security.generate_referral_code(current_user_id)
        payment_system.register_referral_code(current_user_id, user.referral_code)
        user_manager._save_users()
    
    return jsonify({
        'referral_code': user.referral_code,
        'referral_link': f"https://verzek.app/register?ref={user.referral_code}"
    })


@app.route("/api/referral/stats", methods=["GET"])
@token_required
def get_referral_stats_endpoint(current_user_id):
    """Get referral statistics, earnings, and in-app wallet balance"""
    stats = payment_system.get_referral_stats(current_user_id)
    return jsonify(stats)


@app.route("/api/wallet/balance", methods=["GET"])
@token_required
def get_wallet_balance(current_user_id):
    """Get user's in-app wallet balance"""
    wallet_balance = payment_system.referrals.get('wallets', {}).get(current_user_id, 0.0)
    return jsonify({
        'balance': wallet_balance,
        'currency': 'USDT',
        'minimum_withdrawal': 10.0,
        'withdrawal_fee': 1.0
    })


@app.route("/api/referral/payout", methods=["POST"])
@token_required
def request_referral_payout_endpoint(current_user_id):
    """Request payout of referral earnings"""
    data = request.json
    wallet_address = data.get('wallet_address')
    
    if not wallet_address:
        return jsonify({'error': 'wallet_address required'}), 400
    
    result = payment_system.request_referral_payout(current_user_id, wallet_address)
    return jsonify(result)


@app.route("/api/referral/payouts/pending", methods=["GET"])
@token_required
def get_pending_payouts_admin(current_user_id):
    """Admin: Get pending referral payouts"""
    user = user_manager.get_user(current_user_id)
    
    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    pending = payment_system.get_pending_payouts()
    return jsonify({'count': len(pending), 'payouts': pending})


# ============================
# SUBSCRIPTION SECURITY
# ============================

@app.route("/api/subscription/validate", methods=["POST"])
@token_required
def validate_subscription(current_user_id):
    """Validate user's subscription and license key"""
    user = user_manager.get_user(current_user_id)
    
    if not hasattr(user, 'license_key') or not user.license_key:
        return jsonify({
            'valid': False,
            'plan': user.plan,
            'message': 'No license key found'
        })
    
    is_valid, message = subscription_security.validate_license_key(
        user.license_key, current_user_id
    )
    
    if not is_valid and user.plan in ['pro', 'vip']:
        user.plan = 'free'
        user_manager._save_users()
    
    return jsonify({
        'valid': is_valid,
        'plan': user.plan,
        'message': message
    })


# ============================
# 2FA / MFA ENDPOINTS
# ============================

@app.route("/api/2fa/enroll", methods=["POST"])
@token_required
def enroll_2fa(current_user_id):
    """Enroll user in 2FA"""
    user = user_manager.get_user(current_user_id)
    
    enrollment_data = two_factor_auth.enroll_user(current_user_id, user.email)
    
    audit_logger.log_event(
        AuditEventType.MFA_ENROLLED,
        user_id=current_user_id,
        ip_address=request.remote_addr
    )
    
    return jsonify({
        'success': True,
        'qr_code': enrollment_data['qr_code'],
        'secret': enrollment_data['secret'],
        'backup_codes': enrollment_data['backup_codes'],
        'message': 'Scan QR code with Google Authenticator or Authy'
    })


@app.route("/api/2fa/verify", methods=["POST"])
@token_required
def verify_2fa_enable(current_user_id):
    """Verify and enable 2FA for user"""
    data = request.json
    token = data.get('token')
    
    if not token:
        return jsonify({'error': 'Verification token required'}), 400
    
    is_valid, message = two_factor_auth.verify_and_enable(current_user_id, token)
    
    if is_valid:
        audit_logger.log_event(
            AuditEventType.MFA_ENABLED,
            user_id=current_user_id,
            ip_address=request.remote_addr
        )
    
    return jsonify({
        'success': is_valid,
        'message': message
    })


@app.route("/api/2fa/disable", methods=["POST"])
@token_required
def disable_2fa(current_user_id):
    """Disable 2FA for user (requires password)"""
    data = request.json
    password = data.get('password')
    
    if not password:
        return jsonify({'error': 'Password required to disable 2FA'}), 400
    
    user = user_manager.get_user(current_user_id)
    
    if not verify_password(password, user.password_hash):
        return jsonify({'error': 'Invalid password'}), 403
    
    is_success, message = two_factor_auth.disable_2fa(current_user_id, password)
    
    if is_success:
        audit_logger.log_event(
            AuditEventType.MFA_DISABLED,
            user_id=current_user_id,
            ip_address=request.remote_addr
        )
    
    return jsonify({
        'success': is_success,
        'message': message
    })


@app.route("/api/2fa/backup-codes", methods=["POST"])
@token_required
def regenerate_backup_codes(current_user_id):
    """Regenerate 2FA backup codes"""
    try:
        backup_codes = two_factor_auth.regenerate_backup_codes(current_user_id)
        
        audit_logger.log_event(
            AuditEventType.ADMIN_ACTION,
            user_id=current_user_id,
            ip_address=request.remote_addr,
            details={'action': 'regenerate_backup_codes'}
        )
        
        return jsonify({
            'success': True,
            'backup_codes': backup_codes
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@app.route("/api/2fa/status", methods=["GET"])
@token_required
def get_2fa_status(current_user_id):
    """Get 2FA status for user"""
    status = two_factor_auth.get_mfa_status(current_user_id)
    return jsonify(status)


# ============================
# BACKUP & DISASTER RECOVERY
# ============================

@app.route("/api/backup/create", methods=["POST"])
@token_required
def create_backup(current_user_id):
    """Create system backup (admin only)"""
    user = user_manager.get_user(current_user_id)
    
    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        backup_path = backup_system.create_backup()
        
        audit_logger.log_event(
            AuditEventType.BACKUP_CREATED,
            user_id=current_user_id,
            ip_address=request.remote_addr,
            details={'backup_path': backup_path}
        )
        
        return jsonify({
            'success': True,
            'backup_path': backup_path,
            'message': 'Backup created successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/backup/list", methods=["GET"])
@token_required
def list_backups(current_user_id):
    """List all available backups (admin only)"""
    user = user_manager.get_user(current_user_id)
    
    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    backups = backup_system.list_backups()
    stats = backup_system.get_backup_stats()
    
    return jsonify({
        'backups': backups,
        'stats': stats
    })


@app.route("/api/backup/restore/<backup_name>", methods=["POST"])
@token_required
def restore_backup(current_user_id, backup_name):
    """Restore from backup (admin only, DANGEROUS)"""
    user = user_manager.get_user(current_user_id)
    
    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    # Require password confirmation
    data = request.json
    password = data.get('password')
    
    if not password or not verify_password(password, user.password_hash):
        return jsonify({'error': 'Password confirmation required'}), 403
    
    success = backup_system.restore_backup(backup_name)
    
    if success:
        audit_logger.log_event(
            AuditEventType.BACKUP_RESTORED,
            user_id=current_user_id,
            ip_address=request.remote_addr,
            details={'backup_name': backup_name},
            severity='critical'
        )
    
    return jsonify({
        'success': success,
        'message': 'Backup restored successfully' if success else 'Restore failed'
    })


# ============================
# TRONSCAN AUTO-VERIFICATION
# ============================

@app.route("/api/payments/auto-verify/<payment_id>", methods=["POST"])
@token_required
def auto_verify_payment(current_user_id, payment_id):
    """Auto-verify payment using TronScan API (admin only)"""
    user = user_manager.get_user(current_user_id)
    
    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    # Get payment details
    payment = next((p for p in payment_system.payments if p['payment_id'] == payment_id), None)
    
    if not payment:
        return jsonify({'error': 'Payment not found'}), 404
    
    if 'tx_hash' not in payment:
        return jsonify({'error': 'Transaction hash not submitted yet'}), 400
    
    # Verify with TronScan
    verification = tronscan_client.verify_transaction(
        payment['tx_hash'],
        payment['amount_usdt']
    )
    
    if verification.get('verified'):
        # Auto-confirm payment
        result = payment_system.admin_confirm_payment(payment_id, True)
        
        if result['success']:
            target_user = user_manager.get_user(result['user_id'])
            target_user.plan = result['plan']
            target_user.plan_started_at = datetime.now().isoformat()
            target_user.plan_expires_at = (datetime.now() + timedelta(days=30)).isoformat()
            
            license_key = subscription_security.generate_license_key(
                result['user_id'], result['plan'], 30
            )
            target_user.license_key = license_key
            
            user_manager._save_users()
            
            audit_logger.log_event(
                AuditEventType.PAYMENT_CONFIRMED,
                user_id=current_user_id,
                ip_address=request.remote_addr,
                details={
                    'payment_id': payment_id,
                    'auto_verified': True,
                    'amount': verification['amount']
                }
            )
            
            return jsonify({
                'success': True,
                'verified': True,
                'message': 'Payment auto-verified and confirmed',
                'license_key': license_key,
                'verification_details': verification
            })
    
    return jsonify({
        'success': False,
        'verified': False,
        'error': verification.get('error', 'Verification failed'),
        'verification_details': verification
    })


# ============================
# AUDIT LOGS
# ============================

@app.route("/api/audit/user/<user_id>", methods=["GET"])
@token_required
def get_user_audit_logs(current_user_id, user_id):
    """Get audit logs for a user (admin or self)"""
    user = user_manager.get_user(current_user_id)
    
    # Can only view own logs unless admin
    if user.plan != 'admin' and current_user_id != user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    limit = request.args.get('limit', 50, type=int)
    events = audit_logger.get_user_activity(user_id, limit)
    
    return jsonify({
        'user_id': user_id,
        'event_count': len(events),
        'events': events
    })


@app.route("/api/audit/suspicious", methods=["GET"])
@token_required
def get_suspicious_activity(current_user_id):
    """Get suspicious activity (admin only)"""
    user = user_manager.get_user(current_user_id)
    
    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    limit = request.args.get('limit', 20, type=int)
    events = audit_logger.get_suspicious_activity(limit)
    
    return jsonify({
        'event_count': len(events),
        'events': events
    })


@app.route("/api/audit/alerts", methods=["GET"])
@token_required
def get_security_alerts(current_user_id):
    """Get security alerts (admin only)"""
    user = user_manager.get_user(current_user_id)
    
    if user.plan != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    resolved = request.args.get('resolved')
    if resolved is not None:
        resolved = resolved.lower() == 'true'
    
    alerts = audit_logger.get_alerts(resolved)
    
    return jsonify({
        'alert_count': len(alerts),
        'alerts': alerts
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    log_event("API", f"🌐 Starting Flask API on port {port}")
    app.run(host="0.0.0.0", port=port)
