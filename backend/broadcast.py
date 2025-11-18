"""
Telegram and App Broadcasting Module
Sends trading signals and events to VIP/Trial Telegram groups
"""
import os
import requests
from typing import Dict, Optional
from utils.logger import api_logger


BOT_TOKEN = os.getenv("BROADCAST_BOT_TOKEN", os.getenv("TELEGRAM_BOT_TOKEN", ""))
VIP_CHAT_ID = os.getenv("TELEGRAM_VIP_CHAT_ID", "")
TRIAL_CHAT_ID = os.getenv("TELEGRAM_TRIAL_CHAT_ID", "")


def _send_telegram(chat_id: str, text: str, parse_mode: str = "HTML"):
    """Send message to Telegram chat"""
    if not BOT_TOKEN or not chat_id:
        api_logger.warning("Telegram credentials missing, skipping broadcast")
        return
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(
            url,
            json={"chat_id": chat_id, "text": text, "parse_mode": parse_mode},
            timeout=10
        )
        if response.status_code != 200:
            api_logger.error(f"Telegram send failed: {response.text}")
    except Exception as e:
        api_logger.error(f"Telegram broadcast error: {e}")


def broadcast_signal(signal: Dict, target: str = "both"):
    """
    Broadcast trading signal to Telegram groups
    
    Args:
        signal: Signal dictionary with keys: symbol, side, entry, tp, sl, etc.
        target: "vip", "trial", or "both"
    """
    tp_str = ", ".join([str(t) for t in signal.get("tp", [])])
    
    message = f"""
🔥 <b>VERZEK TRADING SIGNAL</b> 🔥

<b>{signal.get('symbol', '?')}</b> - {signal.get('side', '?')}

📍 Entry: <b>{signal.get('entry')}</b>
🎯 Targets: <b>{tp_str}</b>
🛑 Stop Loss: <b>{signal.get('sl')}</b>

⚙️ Leverage: {signal.get('leverage', 1)}x
📊 Type: {signal.get('trade_type', 'FUTURES')}
⏱️ Duration: {signal.get('duration', 'SHORT')}
💯 Confidence: {signal.get('confidence', '-')}%

🚀 <i>Auto-trading enabled for Premium users</i>
    """.strip()
    
    if target in ("vip", "both"):
        _send_telegram(VIP_CHAT_ID, message)
    
    if target in ("trial", "both"):
        _send_telegram(TRIAL_CHAT_ID, message)
    
    api_logger.info(f"Broadcasted signal {signal.get('symbol')} to {target}")


def broadcast_target_hit(signal_id: int, symbol: str, target_index: int, price: float, target: str = "both"):
    """Broadcast when a take-profit target is hit"""
    message = f"""
✅ <b>TARGET {target_index} HIT!</b>

📊 {symbol}
🎯 Price: <b>{price}</b>

<i>Signal #{signal_id}</i>
    """.strip()
    
    if target in ("vip", "both"):
        _send_telegram(VIP_CHAT_ID, message)
    
    if target in ("trial", "both"):
        _send_telegram(TRIAL_CHAT_ID, message)


def broadcast_stop_loss(signal_id: int, symbol: str, price: float, target: str = "both"):
    """Broadcast when stop loss is triggered"""
    message = f"""
🛑 <b>STOP LOSS TRIGGERED</b>

📊 {symbol}
💥 Price: <b>{price}</b>

<i>Signal #{signal_id} - Position closed</i>
    """.strip()
    
    if target in ("vip", "both"):
        _send_telegram(VIP_CHAT_ID, message)
    
    if target in ("trial", "both"):
        _send_telegram(TRIAL_CHAT_ID, message)


def broadcast_signal_cancelled(signal_id: int, symbol: str, reason: str = "Manual", target: str = "both"):
    """Broadcast when a signal is cancelled"""
    message = f"""
❌ <b>SIGNAL CANCELLED</b>

📊 {symbol}
📝 Reason: {reason}

<i>Signal #{signal_id}</i>
    """.strip()
    
    if target in ("vip", "both"):
        _send_telegram(VIP_CHAT_ID, message)
    
    if target in ("trial", "both"):
        _send_telegram(TRIAL_CHAT_ID, message)


def broadcast_event(text: str, target: str = "both"):
    """Generic event broadcaster"""
    if target in ("vip", "both"):
        _send_telegram(VIP_CHAT_ID, text)
    
    if target in ("trial", "both"):
        _send_telegram(TRIAL_CHAT_ID, text)
