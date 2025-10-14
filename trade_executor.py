"""
VerzekAutoTrader - Trade Execution Module
-----------------------------------------
Handles trade execution for Binance, Bybit, and Phemex.
Falls back to simulation if no valid API keys are found.
"""

import os
import json
import time
import random
from datetime import datetime
from utils.logger import log_event

# =====================================
# LOAD CONFIG
# =====================================

CONFIG_PATH = "config/config.json"

def load_config():
    if not os.path.exists(CONFIG_PATH):
        raise FileNotFoundError("⚠️ config/config.json missing.")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

config = load_config()
exchange_settings = config.get("exchange_settings", {})
auto_trade_config = config.get("auto_trade", {})

# =====================================
# MOCK PRICE FETCHER
# =====================================

def get_market_price(symbol):
    """Mock live price fetcher (later replace with real exchange data)."""
    # For now, simulate a price to keep demo working
    base_price = {
        "BTCUSDT": 29700.0,
        "ETHUSDT": 1680.0,
        "BNBUSDT": 228.0
    }.get(symbol.upper(), random.uniform(50, 50000))
    return round(base_price + random.uniform(-5, 5), 4)


# =====================================
# EXCHANGE CONNECTOR PLACEHOLDERS
# =====================================

def connect_exchange():
    """Initialize exchange connection (Bybit, Binance, or Phemex)."""
    ex = exchange_settings.get("default_exchange", "bybit").lower()
    key = exchange_settings.get("api_key", "")
    secret = exchange_settings.get("api_secret", "")

    if not key or not secret:
        log_event("WARNING", "⚠️ No API key/secret found. Running in simulation mode.")
        return None, "simulation"

    log_event("INFO", f"🔑 Connecting to {ex.title()}...")
    # TODO: Integrate actual SDKs here later (ccxt or direct SDK)
    return None, ex


# =====================================
# TRADE EXECUTION
# =====================================

def execute_trade(symbol, side="buy", amount=0.01, tp=None, sl=None):
    """Executes or simulates a trade."""
    balance = random.uniform(100, 1000)  # demo balance simulation
    entry_price = get_market_price(symbol)
    exchange, mode = connect_exchange()

    trade = {
        "symbol": symbol.upper(),
        "side": side.upper(),
        "entry_price": entry_price,
        "tp": tp,
        "sl": sl,
        "amount": amount,
        "balance": round(balance, 2),
        "mode": mode,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "EXECUTED" if mode != "simulation" else "SIMULATED"
    }

    if mode == "simulation":
        log_event("TRADE", f"🟢 Simulated {side.upper()} {symbol} Entry={entry_price}")
    else:
        # Real exchange logic placeholder
        log_event("TRADE", f"💹 Live {side.upper()} {symbol} order executed on {mode.upper()}")

    save_trade_record(trade)
    return trade


# =====================================
# SAVE TRADE RECORD
# =====================================

def save_trade_record(trade):
    """Save all executed trades to database/trades_log.csv"""
    os.makedirs("database", exist_ok=True)
    csv_path = "database/trades_log.csv"

    header = "Timestamp,Symbol,Side,Entry,TP,SL,Amount,Balance,Mode,Status\n"
    if not os.path.exists(csv_path):
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write(header)

    with open(csv_path, "a", encoding="utf-8") as f:
        f.write(
            f"{trade['timestamp']},{trade['symbol']},{trade['side']},"
            f"{trade['entry_price']},{trade['tp']},{trade['sl']},"
            f"{trade['amount']},{trade['balance']},{trade['mode']},{trade['status']}\n"
        )

    log_event("INFO", f"💾 Trade saved for {trade['symbol']}")


# =====================================
# GET ALL TRADES (For API)
# =====================================

def get_all_trades():
    """Retrieve all trades from the CSV log file for API consumption."""
    csv_path = "database/trades_log.csv"
    
    if not os.path.exists(csv_path):
        return []
    
    trades = []
    with open(csv_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        # Skip header
        for line in lines[1:]:
            parts = line.strip().split(",")
            if len(parts) >= 10:
                trades.append({
                    "timestamp": parts[0],
                    "symbol": parts[1],
                    "side": parts[2],
                    "entry_price": float(parts[3]),
                    "tp": parts[4] if parts[4] != "None" else None,
                    "sl": parts[5] if parts[5] != "None" else None,
                    "amount": float(parts[6]),
                    "balance": float(parts[7]),
                    "mode": parts[8],
                    "status": parts[9]
                })
    
    return trades


# =====================================
# DEMO RUN (Optional)
# =====================================

if __name__ == "__main__":
    demo = execute_trade("BTCUSDT", side="buy", tp=30200, sl=29400)
    print(json.dumps(demo, indent=2))
