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
import time
import os
import re

app = Flask(__name__)

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


# ============================
# AUTHENTICATION
# ============================

@app.route("/api/auth/register", methods=["POST"])
def register():
    """Register a new user"""
    data = request.json
    
    email = data.get("email", "").strip().lower()
    password = data.get("password")
    full_name = data.get("full_name", "")
    
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
def login():
    """Login user and return JWT tokens"""
    data = request.json
    
    email = data.get("email", "").strip().lower()
    password = data.get("password")
    
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
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Verify password
    if not user.password_hash or not verify_password(password, user.password_hash):
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Generate tokens
    access_token = create_access_token(user.user_id, email)
    refresh_token = create_refresh_token(user.user_id)
    
    log_event("AUTH", f"User logged in: {email}")
    
    return jsonify({
        "message": "Login successful",
        "user": {
            "user_id": user.user_id,
            "email": email,
            "full_name": user.full_name,
            "plan": user.plan,
            "plan_expires_at": user.plan_expires_at
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


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    log_event("API", f"🌐 Starting Flask API on port {port}")
    app.run(host="0.0.0.0", port=port)
