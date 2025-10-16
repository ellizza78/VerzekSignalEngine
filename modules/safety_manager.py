"""
Safety Manager
Provides kill switch, order idempotency, and safety checks for the trading system
"""

import json
import os
import time
from typing import Optional, Set
from datetime import datetime, timedelta
from utils.logger import log_event


class SafetyManager:
    """Manages safety rails for the trading system"""
    
    def __init__(self, storage_path: str = "database/safety_state.json"):
        self.storage_path = storage_path
        
        # Kill switch state
        self.kill_switch_active = False
        self.kill_switch_reason = ""
        self.kill_switch_activated_at: Optional[str] = None
        
        # Order idempotency tracking
        self.order_ids: Set[str] = set()
        self.order_timestamps = {}
        
        # Circuit breaker state
        self.circuit_breaker_active = False
        self.circuit_breaker_reason = ""
        
        # Circuit breaker configuration
        self.circuit_breaker_config = {
            "max_loss_percent": 10.0,  # 10% max loss before trigger
            "max_consecutive_losses": 5,  # 5 losses in a row triggers
            "lookback_minutes": 60,  # Check losses in last 60 minutes
            "enabled": True
        }
        
        # Loss tracking for circuit breaker
        self.recent_trades = []  # List of {timestamp, pnl, user_id}
        self.consecutive_losses = 0
        
        # Trading pause state
        self.trading_paused = False
        self.pause_until: Optional[str] = None
        
        self._load_state()
    
    def _load_state(self):
        """Load safety state from disk"""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.kill_switch_active = data.get("kill_switch_active", False)
                    self.kill_switch_reason = data.get("kill_switch_reason", "")
                    self.kill_switch_activated_at = data.get("kill_switch_activated_at")
                    self.circuit_breaker_active = data.get("circuit_breaker_active", False)
                    self.circuit_breaker_reason = data.get("circuit_breaker_reason", "")
                    self.circuit_breaker_config = data.get("circuit_breaker_config", self.circuit_breaker_config)
                    self.recent_trades = data.get("recent_trades", [])
                    self.consecutive_losses = data.get("consecutive_losses", 0)
                    self.trading_paused = data.get("trading_paused", False)
                    self.pause_until = data.get("pause_until")
                    self.order_ids = set(data.get("order_ids", []))
            except Exception as e:
                log_event("SAFETY", f"Error loading safety state: {e}")
        else:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
    
    def _save_state(self):
        """Save safety state to disk"""
        try:
            data = {
                "kill_switch_active": self.kill_switch_active,
                "kill_switch_reason": self.kill_switch_reason,
                "kill_switch_activated_at": self.kill_switch_activated_at,
                "circuit_breaker_active": self.circuit_breaker_active,
                "circuit_breaker_reason": self.circuit_breaker_reason,
                "circuit_breaker_config": self.circuit_breaker_config,
                "recent_trades": self.recent_trades,
                "consecutive_losses": self.consecutive_losses,
                "trading_paused": self.trading_paused,
                "pause_until": self.pause_until,
                "order_ids": list(self.order_ids)
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            log_event("SAFETY", f"Error saving safety state: {e}")
    
    def activate_kill_switch(self, reason: str = "Manual activation"):
        """Activate emergency kill switch - stops ALL trading"""
        self.kill_switch_active = True
        self.kill_switch_reason = reason
        self.kill_switch_activated_at = datetime.now().isoformat()
        self._save_state()
        log_event("SAFETY", f"🚨 KILL SWITCH ACTIVATED: {reason}")
        return {
            "status": "activated",
            "reason": reason,
            "timestamp": self.kill_switch_activated_at
        }
    
    def deactivate_kill_switch(self):
        """Deactivate kill switch - resume trading"""
        if not self.kill_switch_active:
            return {"status": "already_inactive"}
        
        self.kill_switch_active = False
        self.kill_switch_reason = ""
        self.kill_switch_activated_at = None
        self._save_state()
        log_event("SAFETY", "✅ Kill switch deactivated - trading resumed")
        return {"status": "deactivated"}
    
    def is_trading_allowed(self) -> tuple[bool, str]:
        """Check if trading is currently allowed"""
        # Check kill switch
        if self.kill_switch_active:
            return False, f"Kill switch active: {self.kill_switch_reason}"
        
        # Check circuit breaker
        if self.circuit_breaker_active:
            return False, f"Circuit breaker active: {self.circuit_breaker_reason}"
        
        # Check trading pause
        if self.trading_paused:
            if self.pause_until:
                pause_time = datetime.fromisoformat(self.pause_until)
                if datetime.now() < pause_time:
                    return False, f"Trading paused until {self.pause_until}"
                else:
                    # Auto-resume after pause expires
                    self.trading_paused = False
                    self.pause_until = None
                    self._save_state()
        
        return True, "Trading allowed"
    
    def activate_circuit_breaker(self, reason: str):
        """Activate circuit breaker (e.g., after rapid losses)"""
        self.circuit_breaker_active = True
        self.circuit_breaker_reason = reason
        self._save_state()
        log_event("SAFETY", f"⚠️ CIRCUIT BREAKER ACTIVATED: {reason}")
        return {"status": "activated", "reason": reason}
    
    def deactivate_circuit_breaker(self):
        """Deactivate circuit breaker"""
        self.circuit_breaker_active = False
        self.circuit_breaker_reason = ""
        self._save_state()
        log_event("SAFETY", "✅ Circuit breaker deactivated")
        return {"status": "deactivated"}
    
    def pause_trading(self, duration_minutes: int = 60, reason: str = "Manual pause"):
        """Pause trading for a specific duration"""
        pause_until = datetime.now() + timedelta(minutes=duration_minutes)
        self.trading_paused = True
        self.pause_until = pause_until.isoformat()
        self._save_state()
        log_event("SAFETY", f"⏸️ Trading paused for {duration_minutes} minutes: {reason}")
        return {
            "status": "paused",
            "pause_until": self.pause_until,
            "reason": reason
        }
    
    def resume_trading(self):
        """Resume trading immediately"""
        self.trading_paused = False
        self.pause_until = None
        self._save_state()
        log_event("SAFETY", "▶️ Trading resumed")
        return {"status": "resumed"}
    
    def check_order_idempotency(self, order_id: str) -> bool:
        """Check if order has already been placed (prevents duplicates)
        
        Returns:
            True if order is new (safe to place)
            False if order is duplicate (should skip)
        """
        # Clean old orders (older than 24 hours)
        current_time = time.time()
        cutoff_time = current_time - 86400  # 24 hours
        
        old_orders = [
            oid for oid, timestamp in self.order_timestamps.items()
            if timestamp < cutoff_time
        ]
        
        for oid in old_orders:
            self.order_ids.discard(oid)
            del self.order_timestamps[oid]
        
        # Check if order exists
        if order_id in self.order_ids:
            log_event("SAFETY", f"⚠️ Duplicate order detected: {order_id}")
            return False
        
        # Add new order
        self.order_ids.add(order_id)
        self.order_timestamps[order_id] = current_time
        self._save_state()
        return True
    
    def mark_order_placed(self, order_id: str):
        """Mark an order as placed"""
        self.order_ids.add(order_id)
        self.order_timestamps[order_id] = time.time()
        self._save_state()
    
    def get_safety_status(self) -> dict:
        """Get current safety system status"""
        allowed, reason = self.is_trading_allowed()
        return {
            "trading_allowed": allowed,
            "reason": reason if not allowed else "All systems operational",
            "kill_switch": {
                "active": self.kill_switch_active,
                "reason": self.kill_switch_reason,
                "activated_at": self.kill_switch_activated_at
            },
            "circuit_breaker": {
                "active": self.circuit_breaker_active,
                "reason": self.circuit_breaker_reason
            },
            "trading_pause": {
                "active": self.trading_paused,
                "until": self.pause_until
            },
            "tracked_orders": len(self.order_ids)
        }
    
    def validate_symbol(self, symbol: str, allowed_symbols: list = None, blocked_symbols: list = None) -> tuple[bool, str]:
        """Validate if symbol is allowed for trading
        
        Args:
            symbol: Trading symbol (e.g., BTCUSDT)
            allowed_symbols: Whitelist of allowed symbols (if None, all allowed)
            blocked_symbols: Blacklist of blocked symbols
        
        Returns:
            (is_valid, reason)
        """
        # Check blocked list first
        if blocked_symbols and symbol in blocked_symbols:
            return False, f"Symbol {symbol} is blacklisted"
        
        # Check allowed list (if specified)
        if allowed_symbols and symbol not in allowed_symbols:
            return False, f"Symbol {symbol} not in whitelist"
        
        return True, "Symbol allowed"
    
    def validate_leverage(self, leverage: int, max_leverage: int = 20) -> tuple[bool, str]:
        """Validate leverage is within safe limits"""
        if leverage < 1:
            return False, "Leverage must be at least 1x"
        
        if leverage > max_leverage:
            return False, f"Leverage {leverage}x exceeds maximum {max_leverage}x"
        
        return True, "Leverage within limits"
    
    def validate_order_size(self, order_size: float, min_size: float = 5.0, max_size: float = 10000.0) -> tuple[bool, str]:
        """Validate order size is within safe limits"""
        if order_size < min_size:
            return False, f"Order size ${order_size} below minimum ${min_size}"
        
        if order_size > max_size:
            return False, f"Order size ${order_size} exceeds maximum ${max_size}"
        
        return True, "Order size within limits"
    
    def record_trade_result(self, pnl: float, user_id: str = "system", account_balance: float = 1000.0):
        """Record trade result and check circuit breaker conditions
        
        Args:
            pnl: Profit/loss from the trade
            user_id: User ID who made the trade
            account_balance: Current account balance for percentage calculation
        """
        if not self.circuit_breaker_config.get("enabled", True):
            return
        
        # Record trade
        trade_record = {
            "timestamp": datetime.now().isoformat(),
            "pnl": pnl,
            "user_id": user_id
        }
        self.recent_trades.append(trade_record)
        
        # Clean old trades (outside lookback window)
        lookback_minutes = self.circuit_breaker_config.get("lookback_minutes", 60)
        cutoff_time = datetime.now() - timedelta(minutes=lookback_minutes)
        
        self.recent_trades = [
            t for t in self.recent_trades
            if datetime.fromisoformat(t["timestamp"]) > cutoff_time
        ]
        
        # Track consecutive losses
        if pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        # Check circuit breaker conditions
        self._check_circuit_breaker_triggers(account_balance)
        
        self._save_state()
    
    def _check_circuit_breaker_triggers(self, account_balance: float):
        """Check if circuit breaker should be triggered"""
        if self.circuit_breaker_active:
            return  # Already active
        
        # Condition 1: Total loss percentage exceeded
        max_loss_pct = self.circuit_breaker_config.get("max_loss_percent", 10.0)
        total_pnl = sum(t["pnl"] for t in self.recent_trades)
        
        if total_pnl < 0 and account_balance > 0:
            loss_pct = abs(total_pnl) / account_balance * 100
            if loss_pct >= max_loss_pct:
                reason = f"Loss {loss_pct:.2f}% exceeds {max_loss_pct}% threshold"
                self.activate_circuit_breaker(reason)
                return
        
        # Condition 2: Consecutive losses exceeded
        max_consecutive = self.circuit_breaker_config.get("max_consecutive_losses", 5)
        if self.consecutive_losses >= max_consecutive:
            reason = f"{self.consecutive_losses} consecutive losses (max: {max_consecutive})"
            self.activate_circuit_breaker(reason)
            return
    
    def update_circuit_breaker_config(self, config: dict):
        """Update circuit breaker configuration"""
        self.circuit_breaker_config.update(config)
        self._save_state()
        log_event("SAFETY", f"Circuit breaker config updated: {config}")
    
    def get_loss_metrics(self) -> dict:
        """Get current loss metrics for monitoring"""
        total_pnl = sum(t["pnl"] for t in self.recent_trades)
        losing_trades = [t for t in self.recent_trades if t["pnl"] < 0]
        winning_trades = [t for t in self.recent_trades if t["pnl"] > 0]
        
        return {
            "total_trades": len(self.recent_trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "consecutive_losses": self.consecutive_losses,
            "total_pnl": total_pnl,
            "lookback_window_minutes": self.circuit_breaker_config.get("lookback_minutes", 60)
        }
