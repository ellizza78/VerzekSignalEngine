"""
signal_parser.py
----------------
Smart parser for Telegram crypto trading signals.
Supports both Verzek custom format and Cornix-style signal formats.
"""

import re
from utils.logger import log_event


def parse_signal(message_text: str):
    """
    Detect and parse different signal formats.
    Returns a normalized dictionary of trade details.
    """

    text = message_text.upper().strip()
    if not text:
        return None

    # -----------------------------
    # 1️⃣ Detect signal type
    # -----------------------------
    if "ENTRY" in text and "STOP" in text:
        signal_type = "CORNIX"
    elif "RSI" in text or "MACD" in text or "STOCH" in text:
        signal_type = "VERZEK"
    else:
        signal_type = "UNKNOWN"

    # -----------------------------
    # 2️⃣ Common elements (symbol + direction)
    # -----------------------------
    direction = "LONG" if "LONG" in text else "SHORT" if "SHORT" in text else None
    symbol_match = re.search(r"([A-Z]{3,5})[\/\-]?USDT", text)
    symbol = f"{symbol_match.group(1)}USDT" if symbol_match else None

    # -----------------------------
    # 3️⃣ Cornix-style parsing
    # -----------------------------
    entry = take_profits = stop_loss = timeframe = None

    if signal_type == "CORNIX":
        # Timeframe
        tf_match = re.search(r"TIMEFRAME[:\s]*([0-9]+[MH])", text)
        timeframe = tf_match.group(1) if tf_match else "1H"

        # Entry
        entry_match = re.search(r"ENTRY[:\s]*([0-9]+(?:\.[0-9]+)?)", text)
        entry = float(entry_match.group(1)) if entry_match else None

        # Take Profits (can be multiple, extract numbered targets)
        # First try: TARGET 1: price, TARGET 2: price, etc.
        target_match = re.findall(r"TARGET\s*(\d+)[:\s]*([0-9]+(?:\.[0-9]+)?)", text)
        if target_match:
            take_profits = [{"target_num": int(t[0]), "price": float(t[1])} for t in target_match]
        else:
            # Fallback: TAKE PROFIT / TP with numbers
            tp_match = re.findall(r"(?:TAKE\s*PROFIT|TP)\s*(\d+)?[:\s]*([0-9]+(?:\.[0-9]+)?)", text)
            if tp_match:
                take_profits = [
                    {"target_num": int(t[0]) if t[0] else i+1, "price": float(t[1])} 
                    for i, t in enumerate(tp_match)
                ]
            else:
                # Simple TP extraction (no numbers)
                simple_tp = re.findall(r"(?:TAKE\s*PROFIT|TP)[:\s]*([0-9]+(?:\.[0-9]+)?)", text)
                take_profits = [{"target_num": i+1, "price": float(tp)} for i, tp in enumerate(simple_tp)]

        # Stop Loss
        sl_match = re.search(r"STOP(?:\s*LOSS)?[:\s]*([0-9]+(?:\.[0-9]+)?)", text)
        stop_loss = float(sl_match.group(1)) if sl_match else None

    # -----------------------------
    # 4️⃣ Verzek-style parsing
    # -----------------------------
    elif signal_type == "VERZEK":
        timeframe_match = re.search(r"(\d+[mMhH])", text)
        timeframe = timeframe_match.group(1).upper() if timeframe_match else "1H"

        rsi_match = re.search(r"RSI[:\s]*([0-9]+(?:\.[0-9]+)?)", text)
        macd_match = re.search(r"MACD[:\s]*([-+]?[0-9]*\.?[0-9]+)", text)
        stoch_match = re.search(r"STOCH[:\s]*([0-9]+(?:\.[0-9]+)?)", text)

        rsi = float(rsi_match.group(1)) if rsi_match else None
        macd = float(macd_match.group(1)) if macd_match else None
        stochastic = float(stoch_match.group(1)) if stoch_match else None

        entry = None
        stop_loss = None
        take_profits = []

    # -----------------------------
    # 5️⃣ Pattern detection
    # -----------------------------
    pattern = None
    if "ENGULF" in text:
        pattern = "Engulfing"
    elif "PIN BAR" in text or "PINBAR" in text:
        pattern = "Pin Bar"

    # -----------------------------
    # 6️⃣ Final assembly
    # -----------------------------
    if not symbol or not direction:
        log_event("WARN", f"❌ Could not parse signal: {text}")
        return None

    signal_data = {
        "source_type": signal_type,
        "symbol": symbol,
        "direction": direction,
        "timeframe": timeframe,
        "entry": entry,
        "tp": take_profits,
        "sl": stop_loss,
        "pattern": pattern,
        "type": "FUTURES",
        "source_text": message_text
    }

    log_event("INFO", f"📩 Parsed {signal_type} signal: {signal_data}")
    return signal_data


def parse_close_signal(message_text: str):
    """
    Detect close/cancel signal messages.
    Returns dict with close action details or None if not a close signal.
    
    Detects patterns like:
    - "Signal Cancelled"
    - "BTCUSDT Closed"
    - "Stop Loss Hit"
    - "SL Hit"
    - "Position Closed"
    - "Trade Closed"
    """
    
    text = message_text.upper().strip()
    if not text:
        return None
    
    # Extract symbol
    symbol_match = re.search(r"([A-Z]{3,5})[\/\-]?USDT", text)
    symbol = f"{symbol_match.group(1)}USDT" if symbol_match else None
    
    # Detect close/cancel keywords
    close_keywords = [
        "SIGNAL CANCELLED", "SIGNAL CANCELED",
        "CANCELLED", "CANCELED",
        "CLOSED", "CLOSE",
        "STOP LOSS HIT", "SL HIT",
        "STOP LOSS", "STOPLOSS",
        "POSITION CLOSED", "TRADE CLOSED"
    ]
    
    is_close_signal = any(keyword in text for keyword in close_keywords)
    
    if not is_close_signal:
        return None
    
    # Determine close reason
    close_reason = "manual_close"
    if "CANCEL" in text:
        close_reason = "signal_cancelled"
    elif "STOP LOSS" in text or "SL HIT" in text or "STOPLOSS" in text:
        close_reason = "stop_loss_hit"
    elif "CLOSED" in text or "CLOSE" in text:
        close_reason = "closed"
    
    close_data = {
        "action": "close",
        "symbol": symbol,
        "reason": close_reason,
        "source_text": message_text
    }
    
    log_event("INFO", f"🛑 Detected close signal: {close_data}")
    return close_data
