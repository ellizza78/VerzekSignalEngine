"""
Paper Trading Client
Simulates trading without real exchange connections
Supports up to 50 concurrent positions per user
"""
import os
from typing import Dict, Optional, List
from datetime import datetime

from utils.price_feed import price_feed
from utils.logger import worker_logger


class PaperTradingClient:
    """
    Paper trading engine that simulates order execution
    Tracks virtual balances and supports leverage trading
    """
    
    def __init__(self):
        self.mode = os.getenv("EXCHANGE_MODE", "paper")
        self.user_balances = {}  # user_id -> balance
        worker_logger.info(f"Paper trading client initialized (mode: {self.mode})")
    
    def get_balance(self, user_id: int) -> float:
        """Get user's virtual USDT balance"""
        return self.user_balances.get(user_id, 0.0)
    
    def set_balance(self, user_id: int, balance: float):
        """Set user's virtual balance"""
        self.user_balances[user_id] = balance
    
    def open_position(self, user_id: int, symbol: str, side: str, qty: float, 
                     entry_price: float, leverage: int = 1) -> Dict:
        """
        Open a new position (simulated)
        
        Args:
            user_id: User ID
            symbol: Trading pair (BTCUSDT, etc.)
            side: LONG or SHORT
            qty: Quantity in base currency
            entry_price: Entry price
            leverage: Leverage multiplier
        
        Returns:
            Dict with order details
        """
        try:
            # Get current price (use entry_price or fetch live)
            current_price = price_feed.get_price(symbol) or entry_price
            
            # Calculate cost
            cost_usdt = (qty * current_price) / leverage
            
            # Check if user has enough balance
            balance = self.get_balance(user_id)
            if cost_usdt > balance:
                worker_logger.warning(f"Insufficient balance for user {user_id}: need {cost_usdt}, have {balance}")
                return {
                    "success": False,
                    "error": "Insufficient balance",
                    "cost": cost_usdt,
                    "balance": balance
                }
            
            # Deduct from balance
            self.user_balances[user_id] = balance - cost_usdt
            
            order = {
                "success": True,
                "symbol": symbol,
                "side": side,
                "qty": qty,
                "entry_price": current_price,
                "leverage": leverage,
                "cost_usdt": cost_usdt,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            worker_logger.info(f"Opened {side} position for user {user_id}: {qty} {symbol} @ {current_price}")
            
            return order
            
        except Exception as e:
            worker_logger.error(f"Open position error: {e}")
            return {"success": False, "error": str(e)}
    
    def close_position(self, user_id: int, symbol: str, side: str, qty: float,
                      entry_price: float, exit_price: Optional[float] = None,
                      leverage: int = 1) -> Dict:
        """
        Close a position (simulated)
        
        Returns:
            Dict with PnL calculation
        """
        try:
            # Get current price
            current_price = exit_price or price_feed.get_price(symbol) or entry_price
            
            # Calculate PnL
            if side == "LONG":
                pnl_pct = ((current_price - entry_price) / entry_price) * 100 * leverage
                pnl_usdt = ((current_price - entry_price) / entry_price) * (qty * entry_price)
            else:  # SHORT
                pnl_pct = ((entry_price - current_price) / entry_price) * 100 * leverage
                pnl_usdt = ((entry_price - current_price) / entry_price) * (qty * entry_price)
            
            # Return cost to user balance
            cost_usdt = (qty * entry_price) / leverage
            balance = self.get_balance(user_id)
            self.user_balances[user_id] = balance + cost_usdt + pnl_usdt
            
            result = {
                "success": True,
                "symbol": symbol,
                "side": side,
                "qty": qty,
                "entry_price": entry_price,
                "exit_price": current_price,
                "pnl_usdt": round(pnl_usdt, 2),
                "pnl_pct": round(pnl_pct, 2),
                "new_balance": round(self.user_balances[user_id], 2),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            worker_logger.info(f"Closed {side} position for user {user_id}: PnL {pnl_usdt:.2f} USDT ({pnl_pct:.2f}%)")
            
            return result
            
        except Exception as e:
            worker_logger.error(f"Close position error: {e}")
            return {"success": False, "error": str(e)}
    
    def check_price_targets(self, symbol: str, targets: List[float], sl: float, 
                           entry: float, side: str) -> Dict:
        """
        Check if current price has hit any targets or stop loss
        
        Returns:
            Dict with hit_target_index, hit_sl, current_price
        """
        current_price = price_feed.get_price(symbol)
        
        if not current_price:
            return {"current_price": None}
        
        result = {
            "current_price": current_price,
            "hit_target_index": None,
            "hit_sl": False
        }
        
        if side == "LONG":
            # Check stop loss
            if current_price <= sl:
                result["hit_sl"] = True
                return result
            
            # Check targets (ascending prices for LONG)
            for i, target_price in enumerate(targets, 1):
                if current_price >= target_price:
                    result["hit_target_index"] = i
                    break
        
        else:  # SHORT
            # Check stop loss
            if current_price >= sl:
                result["hit_sl"] = True
                return result
            
            # Check targets (descending prices for SHORT)
            for i, target_price in enumerate(targets, 1):
                if current_price <= target_price:
                    result["hit_target_index"] = i
                    break
        
        return result


# Global paper trading client instance
paper_client = PaperTradingClient()
