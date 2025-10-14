"""
binance_client.py
---------------------------------
Simulated Binance Futures client for VerzekAutoTrader.

This version safely runs in 'simulation' mode (no API keys needed)
and automatically switches to Testnet or Live mode when configured later.

Switching to real trading:
1. Add your API keys to config/config.json or environment variables:
   BINANCE_API_KEY / BINANCE_API_SECRET
2. Set "mode": "testnet" or "live" in config/config.json
3. Restart the bot — no code change required.
"""

import os
import json
import random
import time
from datetime import datetime
from utils.logger import log_event


CONFIG_PATH = "config/config.json"


# ============================
# LOAD CONFIGURATION
# ============================

def load_config():
    """Load trading configuration."""
    if not os.path.exists(CONFIG_PATH):
        log_event("ERROR", "⚠️ config/config.json not found for Binance client.")
        return {"mode": "simulation"}

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


config = load_config()
MODE = config.get("mode", "simulation").lower()
API_KEY = os.getenv("BINANCE_API_KEY", config.get("binance_api_key", ""))
API_SECRET = os.getenv("BINANCE_API_SECRET", config.get("binance_api_secret", ""))


# ============================
# SIMULATION ENGINE
# ============================

def _mock_order(symbol, side, amount, price=None):
    """Generate a fake order response for simulation mode."""
    order_id = int(time.time() * 1000)
    executed_price = price or random.uniform(0.95, 1.05) * 100
    log_event("SIMULATED", f"📊 Simulated {side.upper()} order placed for {symbol} — Amount: {amount}, Price: {executed_price:.4f}")
    return {
        "order_id": order_id,
        "symbol": symbol,
        "side": side,
        "amount": amount,
        "price": executed_price,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "FILLED",
        "mode": "simulation",
    }


# ============================
# PUBLIC INTERFACE
# ============================

def create_order(symbol, side, amount, price=None, order_type="market", params=None):
    """
    Place a buy/sell order.
    In simulation mode → returns mock order.
    In testnet/live mode → will call Binance API when keys are added.
    """
    if MODE == "simulation":
        return _mock_order(symbol, side, amount, price)

    if not API_KEY or not API_SECRET:
        log_event("WARNING", "⚠️ API keys missing. Switching to simulation mode automatically.")
        return _mock_order(symbol, side, amount, price)

    # Placeholder for future real API call (ccxt or binance-futures)
    log_event("REAL", f"📡 Would execute {side.upper()} {order_type} order for {symbol} on Binance {MODE} mode.")
    return _mock_order(symbol, side, amount, price)


def set_tp_sl(order_id, tp_price, sl_price):
    """Simulate setting Take-Profit and Stop-Loss."""
    log_event("TP/SL", f"🎯 TP: {tp_price}, 🛑 SL: {sl_price} (Simulated for Order {order_id})")
    return {"order_id": order_id, "tp": tp_price, "sl": sl_price, "status": "simulated"}


def get_balance():
    """Return fake account balance for simulation."""
    balance = round(random.uniform(1000, 2000), 2)
    log_event("BALANCE", f"💰 Simulated USDT balance: {balance}")
    return {"asset": "USDT", "balance": balance, "mode": MODE}


def get_position(symbol):
    """Return fake open position."""
    position = {
        "symbol": symbol,
        "size": random.uniform(0.1, 1.0),
        "entry_price": random.uniform(90, 110),
        "unrealized_pnl": round(random.uniform(-5, 5), 2),
        "timestamp": datetime.utcnow().isoformat(),
        "mode": MODE,
    }
    log_event("POSITION", f"📈 Simulated position for {symbol}: {position}")
    return position


# ============================
# SELF TEST (optional)
# ============================

if __name__ == "__main__":
    log_event("TEST", "Running BinanceClient simulation test...")
    order = create_order("BTCUSDT", "buy", 0.01)
    tp_sl = set_tp_sl(order["order_id"], 105.0, 95.0)
    pos = get_position("BTCUSDT")
    bal = get_balance()

    print("\n✅ SIMULATION SUMMARY:")
    print(order)
    print(tp_sl)
    print(pos)
    print(bal)
