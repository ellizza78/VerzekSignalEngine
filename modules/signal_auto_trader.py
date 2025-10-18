"""
Signal Auto-Trader
Automatically executes trades for signals received from broadcast bot
Processes priority signals first, then regular signals
"""

import re
import time
from typing import Optional, Dict, List
from modules.dca_orchestrator import DCAOrchestrator
from modules.user_manager_v2 import UserManager
from utils.logger import log_event

class SignalAutoTrader:
    """Auto-trades signals for users with auto-trading enabled"""
    
    def __init__(self):
        self.orchestrator = DCAOrchestrator()
        self.user_manager = UserManager()
        log_event("AUTO_TRADER", "Signal Auto-Trader initialized")
    
    def is_priority_signal(self, text: str) -> bool:
        """Check if signal text contains priority indicators"""
        text_upper = text.upper()
        
        priority_keywords = [
            "SETUP AUTO-TRADE",
            "SETUP AUTOTRADE",
            "AUTO-TRADE SETUP",
            "AUTOTRADE SETUP",
            "PRIORITY SIGNAL",
            "HIGH PRIORITY"
        ]
        
        return any(keyword in text_upper for keyword in priority_keywords)
    
    def parse_signal(self, text: str) -> Optional[Dict]:
        """
        Parse signal from text message
        
        Returns:
            Dict with symbol, side, entry, stop_loss, targets or None if invalid
        """
        text_upper = text.upper()
        
        # Extract symbol (e.g., BTCUSDT, BTC/USDT, #BTCUSDT)
        symbol_match = re.search(r'([A-Z]{2,10})[/]?USDT', text_upper)
        if not symbol_match:
            return None
        
        symbol = symbol_match.group(1) + "USDT"
        
        # Extract side (LONG or SHORT)
        if "LONG" in text_upper:
            side = "LONG"
        elif "SHORT" in text_upper:
            side = "SHORT"
        else:
            return None  # No side specified
        
        # Extract entry price
        entry_price = None
        entry_match = re.search(r'ENTRY[:\s]*([0-9.]+)', text_upper)
        if entry_match:
            try:
                entry_price = float(entry_match.group(1))
            except:
                pass
        
        # Extract stop loss
        stop_loss = None
        sl_match = re.search(r'(?:STOP[\s-]*LOSS|SL)[:\s]*([0-9.]+)', text_upper)
        if sl_match:
            try:
                stop_loss = float(sl_match.group(1))
            except:
                pass
        
        # Extract leverage
        leverage = 10  # Default
        lev_match = re.search(r'LEV(?:ERAGE)?[:\s]*X?([0-9]+)', text_upper)
        if lev_match:
            try:
                leverage = int(lev_match.group(1))
            except:
                pass
        
        # Extract targets
        targets = []
        # Match patterns like: "Targets: 0.1311 - 0.1318 - 0.1325"
        targets_match = re.search(r'TARGETS?[:\s]*([0-9.\s-]+)', text_upper)
        if targets_match:
            target_str = targets_match.group(1)
            # Split by dash or comma
            target_parts = re.split(r'[-,\s]+', target_str)
            for i, part in enumerate(target_parts, 1):
                try:
                    price = float(part.strip())
                    if price > 0:
                        targets.append({"target_num": i, "price": price})
                except:
                    pass
        
        return {
            "symbol": symbol,
            "side": side,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "leverage": leverage,
            "targets": targets if targets else None
        }
    
    def process_signal_for_auto_trading(self, signal_text: str, provider: str = "telegram") -> Dict:
        """
        Process signal and auto-execute for all eligible users
        
        Args:
            signal_text: Raw signal text
            provider: Signal provider name
        
        Returns:
            Summary of execution results
        """
        # Parse signal
        signal_data = self.parse_signal(signal_text)
        if not signal_data:
            log_event("AUTO_TRADER", "Failed to parse signal - invalid format")
            return {
                "success": False,
                "error": "Invalid signal format",
                "users_traded": 0
            }
        
        # Check if priority signal
        is_priority = self.is_priority_signal(signal_text)
        
        if is_priority:
            log_event("AUTO_TRADER", f"⚡ Processing PRIORITY auto-trade signal: {signal_data['symbol']}")
        else:
            log_event("AUTO_TRADER", f"Processing auto-trade signal: {signal_data['symbol']}")
        
        # Get all users with auto-trading enabled
        all_users = self.user_manager.get_all_users()
        eligible_users = [
            user for user in all_users
            if user.dca_settings.get("enabled", False)
        ]
        
        if not eligible_users:
            log_event("AUTO_TRADER", "No users with auto-trading enabled")
            return {
                "success": True,
                "users_traded": 0,
                "message": "No auto-trading users"
            }
        
        # Execute signal for each eligible user
        results = {
            "success": True,
            "signal": signal_data,
            "is_priority": is_priority,
            "users_attempted": len(eligible_users),
            "users_traded": 0,
            "users_failed": 0,
            "errors": []
        }
        
        for user in eligible_users:
            try:
                result = self.orchestrator.execute_signal(
                    user_id=user.user_id,
                    symbol=signal_data["symbol"],
                    side=signal_data["side"],
                    entry_price=signal_data.get("entry_price"),
                    leverage=signal_data.get("leverage", 10),
                    targets=signal_data.get("targets"),
                    stop_loss=signal_data.get("stop_loss"),
                    provider=provider,
                    is_priority=is_priority  # PASS PRIORITY FLAG HERE ✅
                )
                
                if result.get("success"):
                    results["users_traded"] += 1
                    log_event("AUTO_TRADER", f"✅ Auto-traded {signal_data['symbol']} for user {user.user_id}")
                else:
                    results["users_failed"] += 1
                    error_msg = result.get("error", "Unknown error")
                    results["errors"].append({
                        "user_id": user.user_id,
                        "error": error_msg
                    })
                    log_event("AUTO_TRADER", f"❌ Failed for user {user.user_id}: {error_msg}")
            
            except Exception as e:
                results["users_failed"] += 1
                results["errors"].append({
                    "user_id": user.user_id,
                    "error": str(e)
                })
                log_event("AUTO_TRADER", f"❌ Exception for user {user.user_id}: {e}")
        
        # Log summary
        priority_marker = "⚡ PRIORITY " if is_priority else ""
        log_event("AUTO_TRADER", 
                 f"✅ {priority_marker}Auto-trade complete: {results['users_traded']}/{results['users_attempted']} users traded")
        
        return results

# Global instance
signal_auto_trader = SignalAutoTrader()
