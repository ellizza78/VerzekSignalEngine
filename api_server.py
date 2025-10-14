"""
api_server.py
-------------
Flask REST API layer for VerzekAutoTrader.
Allows mobile app or external dashboard to fetch real-time data.
"""

from flask import Flask, jsonify
from utils.logger import log_event
from trade_executor import get_all_trades
import time
import os

app = Flask(__name__)

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
            "/api/latest": "Get latest trade"
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


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    log_event("API", f"🌐 Starting Flask API on port {port}")
    app.run(host="0.0.0.0", port=port)
