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
import time
import os

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
            "/api/users/<user_id>/risk": "Risk settings (GET/PUT)",
            "/api/users/<user_id>/dca": "DCA settings (GET/PUT)",
            "/api/users/<user_id>/exchanges": "Exchange accounts (GET/POST)",
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
# RISK SETTINGS
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
# DCA SETTINGS
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
