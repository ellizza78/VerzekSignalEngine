"""
Royal Q DCA (Dollar Cost Averaging) Engine
Implements margin call strategy with layered buying/selling and take-profit logic.

Strategy Overview:
1. Place base order (initial entry)
2. If price moves against position, place margin calls (DCA) at intervals
3. Each call uses multiplier to increase position size
4. Calculate average entry after each fill
5. Take profit when price rebounds above average + TP%
6. Support partial TP, trailing stops, and breakeven SL
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum


class PositionSide(Enum):
    LONG = "LONG"
    SHORT = "SHORT"


class DCALevel:
    """Represents a single DCA (margin call) level"""
    
    def __init__(self, level: int, trigger_price: float, size: float, multiplier: float):
        self.level = level
        self.trigger_price = trigger_price
        self.size = size
        self.multiplier = multiplier
        self.filled_price: Optional[float] = None
        self.filled_qty: Optional[float] = None
        self.filled_at: Optional[str] = None
        self.status = "pending"  # pending, triggered, filled, cancelled
        
    def to_dict(self) -> dict:
        return {
            "level": self.level,
            "trigger_price": self.trigger_price,
            "size": self.size,
            "multiplier": self.multiplier,
            "filled_price": self.filled_price,
            "filled_qty": self.filled_qty,
            "filled_at": self.filled_at,
            "status": self.status
        }


class RoyalQPosition:
    """Manages a single position with Royal Q DCA strategy"""
    
    def __init__(
        self,
        position_id: str,
        user_id: str,
        symbol: str,
        side: PositionSide,
        base_order_size: float,
        entry_price: float,
        config: dict
    ):
        self.position_id = position_id
        self.user_id = user_id
        self.symbol = symbol
        self.side = side
        self.base_order_size = base_order_size
        self.entry_price = entry_price
        self.config = config
        
        # DCA levels
        self.dca_levels: List[DCALevel] = []
        self.max_levels = len(config.get("levels", []))
        
        # Position tracking
        self.total_filled_qty = 0.0
        self.total_cost = 0.0
        self.avg_entry = entry_price
        
        # TP/SL settings
        self.tp_percent = config.get("tp_pct", 1.2)
        self.tp_mode = config.get("tp_mode", "whole")  # whole, partial
        self.partial_tp_schema = config.get("partial_tp_schema", [30, 30, 40])
        self.sl_percent = config.get("sl_pct", 3.0)
        
        # Trailing settings
        self.trailing_enabled = config.get("trailing", {}).get("enabled", False)
        self.trailing_callback = config.get("trailing", {}).get("callback_pct", 0.5)
        
        # Investment limits
        self.max_investment = config.get("max_investment", 1000)
        self.total_invested = base_order_size
        
        # Status
        self.status = "active"  # active, tp_hit, sl_hit, closed
        self.opened_at = datetime.now().isoformat()
        self.closed_at: Optional[str] = None
        self.pnl = 0.0
        
        # TP tracking for partial TP mode
        self.tp_levels_hit = []
        self.breakeven_sl_set = False
        
        # Record base order as first fill
        self._record_base_order_fill()
        
        # Initialize DCA levels
        self._initialize_dca_levels()
    
    def _record_base_order_fill(self):
        """Record the base order as the first fill"""
        self.total_filled_qty = self.base_order_size / self.entry_price  # Convert $ to coin qty
        self.total_cost = self.base_order_size
        self.total_invested = self.base_order_size
        self.avg_entry = self.entry_price
    
    def _initialize_dca_levels(self):
        """Create DCA levels based on config"""
        levels_config = self.config.get("levels", [])
        current_price = self.entry_price
        
        for i, level_cfg in enumerate(levels_config):
            drop_pct = level_cfg.get("drop_pct", 0)
            multiplier = level_cfg.get("multiplier", 1.0)
            
            # Calculate trigger price based on side
            if self.side == PositionSide.LONG:
                # For LONG: trigger below entry (price drops)
                trigger_price = current_price * (1 - drop_pct / 100)
            else:
                # For SHORT: trigger above entry (price rises)
                trigger_price = current_price * (1 + drop_pct / 100)
            
            # Calculate order size with multiplier
            size = self.base_order_size * multiplier
            
            # Check investment limit
            if self.total_invested + size > self.max_investment:
                break
            
            level = DCALevel(
                level=i + 1,
                trigger_price=trigger_price,
                size=size,
                multiplier=multiplier
            )
            self.dca_levels.append(level)
            current_price = trigger_price
    
    def check_dca_triggers(self, current_price: float) -> List[DCALevel]:
        """Check if any DCA levels should be triggered"""
        triggered = []
        
        for level in self.dca_levels:
            if level.status != "pending":
                continue
            
            should_trigger = False
            
            if self.side == PositionSide.LONG:
                # LONG: trigger when price drops below trigger price
                should_trigger = current_price <= level.trigger_price
            else:
                # SHORT: trigger when price rises above trigger price
                should_trigger = current_price >= level.trigger_price
            
            if should_trigger:
                level.status = "triggered"
                triggered.append(level)
        
        return triggered
    
    def fill_dca_level(self, level: DCALevel, filled_price: float, filled_qty: float):
        """Mark a DCA level as filled and update average entry"""
        level.filled_price = filled_price
        level.filled_qty = filled_qty
        level.filled_at = datetime.now().isoformat()
        level.status = "filled"
        
        # Update totals
        self.total_filled_qty += filled_qty
        self.total_cost += filled_price * filled_qty
        self.total_invested += level.size
        
        # Recalculate average entry
        if self.total_filled_qty > 0:
            self.avg_entry = self.total_cost / self.total_filled_qty
    
    def check_take_profit(self, current_price: float) -> Tuple[bool, Optional[str]]:
        """Check if take profit conditions are met
        
        Returns:
            (should_take_profit, tp_type) where tp_type is 'whole', 'partial_1', 'partial_2', 'partial_3', or None
        """
        if self.status != "active":
            return False, None
        
        # Calculate TP price
        if self.side == PositionSide.LONG:
            tp_price = self.avg_entry * (1 + self.tp_percent / 100)
            tp_hit = current_price >= tp_price
        else:
            tp_price = self.avg_entry * (1 - self.tp_percent / 100)
            tp_hit = current_price <= tp_price
        
        if not tp_hit:
            return False, None
        
        # Determine TP type based on mode
        if self.tp_mode == "whole":
            return True, "whole"
        elif self.tp_mode == "partial":
            # Check which partial TP level to hit
            if len(self.tp_levels_hit) == 0:
                return True, "partial_1"
            elif len(self.tp_levels_hit) == 1:
                return True, "partial_2"
            elif len(self.tp_levels_hit) == 2:
                return True, "partial_3"
        
        return False, None
    
    def execute_take_profit(self, tp_type: str, current_price: float) -> dict:
        """Execute take profit and return action details"""
        result = {
            "action": "take_profit",
            "tp_type": tp_type,
            "price": current_price,
            "avg_entry": self.avg_entry
        }
        
        if tp_type == "whole":
            # Close entire position
            result["close_percent"] = 100
            result["close_qty"] = self.total_filled_qty
            self.status = "tp_hit"
            self.closed_at = datetime.now().isoformat()
            
        elif tp_type.startswith("partial"):
            # Partial TP
            tp_index = int(tp_type.split("_")[1]) - 1
            close_percent = self.partial_tp_schema[tp_index]
            close_qty = self.total_filled_qty * (close_percent / 100)
            
            result["close_percent"] = close_percent
            result["close_qty"] = close_qty
            
            self.tp_levels_hit.append(tp_type)
            
            # Update position
            self.total_filled_qty -= close_qty
            self.total_cost -= self.avg_entry * close_qty
            
            # Set breakeven SL after first TP
            if tp_index == 0 and not self.breakeven_sl_set:
                result["set_breakeven_sl"] = True
                self.breakeven_sl_set = True
            
            # Close position if this was the last partial TP
            if len(self.tp_levels_hit) == 3:
                self.status = "tp_hit"
                self.closed_at = datetime.now().isoformat()
        
        # Calculate PnL
        qty_closed = result["close_qty"]
        if self.side == PositionSide.LONG:
            pnl = (current_price - self.avg_entry) * qty_closed
        else:
            pnl = (self.avg_entry - current_price) * qty_closed
        
        result["pnl"] = pnl
        self.pnl += pnl
        
        return result
    
    def check_stop_loss(self, current_price: float) -> bool:
        """Check if stop loss is hit"""
        if self.status != "active":
            return False
        
        # Use breakeven SL if set, otherwise regular SL
        if self.breakeven_sl_set:
            sl_price = self.avg_entry
        else:
            if self.side == PositionSide.LONG:
                sl_price = self.avg_entry * (1 - self.sl_percent / 100)
                return current_price <= sl_price
            else:
                sl_price = self.avg_entry * (1 + self.sl_percent / 100)
                return current_price >= sl_price
        
        # Check breakeven SL
        if self.side == PositionSide.LONG:
            return current_price <= sl_price
        else:
            return current_price >= sl_price
    
    def execute_stop_loss(self, current_price: float) -> dict:
        """Execute stop loss and close position"""
        # Calculate PnL
        if self.side == PositionSide.LONG:
            pnl = (current_price - self.avg_entry) * self.total_filled_qty
        else:
            pnl = (self.avg_entry - current_price) * self.total_filled_qty
        
        self.pnl = pnl
        self.status = "sl_hit"
        self.closed_at = datetime.now().isoformat()
        
        return {
            "action": "stop_loss",
            "price": current_price,
            "avg_entry": self.avg_entry,
            "close_qty": self.total_filled_qty,
            "pnl": pnl,
            "breakeven": self.breakeven_sl_set
        }
    
    def to_dict(self) -> dict:
        """Convert position to dictionary"""
        return {
            "position_id": self.position_id,
            "user_id": self.user_id,
            "symbol": self.symbol,
            "side": self.side.value,
            "base_order_size": self.base_order_size,
            "entry_price": self.entry_price,
            "avg_entry": self.avg_entry,
            "total_filled_qty": self.total_filled_qty,
            "total_cost": self.total_cost,
            "total_invested": self.total_invested,
            "max_investment": self.max_investment,
            "dca_levels": [level.to_dict() for level in self.dca_levels],
            "tp_percent": self.tp_percent,
            "tp_mode": self.tp_mode,
            "partial_tp_schema": self.partial_tp_schema,
            "tp_levels_hit": self.tp_levels_hit,
            "sl_percent": self.sl_percent,
            "breakeven_sl_set": self.breakeven_sl_set,
            "trailing_enabled": self.trailing_enabled,
            "trailing_callback": self.trailing_callback,
            "status": self.status,
            "pnl": self.pnl,
            "opened_at": self.opened_at,
            "closed_at": self.closed_at
        }


class RoyalQEngine:
    """Main Royal Q DCA Engine - manages multiple positions"""
    
    def __init__(self):
        self.positions: Dict[str, RoyalQPosition] = {}
    
    def create_position(
        self,
        position_id: str,
        user_id: str,
        symbol: str,
        side: str,
        base_order_size: float,
        entry_price: float,
        royalq_config: dict
    ) -> RoyalQPosition:
        """Create a new Royal Q position"""
        position_side = PositionSide.LONG if side.upper() in ["LONG", "BUY"] else PositionSide.SHORT
        
        position = RoyalQPosition(
            position_id=position_id,
            user_id=user_id,
            symbol=symbol,
            side=position_side,
            base_order_size=base_order_size,
            entry_price=entry_price,
            config=royalq_config
        )
        
        self.positions[position_id] = position
        return position
    
    def get_position(self, position_id: str) -> Optional[RoyalQPosition]:
        """Get position by ID"""
        return self.positions.get(position_id)
    
    def update_position(self, position_id: str, current_price: float) -> dict:
        """Update position with current price and check for triggers
        
        Returns action dict with triggered events
        """
        position = self.positions.get(position_id)
        if not position or position.status != "active":
            return {"action": "none"}
        
        result = {"action": "none", "events": []}
        
        # Check DCA triggers
        triggered_levels = position.check_dca_triggers(current_price)
        if triggered_levels:
            result["events"].append({
                "type": "dca_triggered",
                "levels": [level.to_dict() for level in triggered_levels]
            })
        
        # Check take profit
        tp_hit, tp_type = position.check_take_profit(current_price)
        if tp_hit and tp_type:
            tp_result = position.execute_take_profit(tp_type, current_price)
            result["action"] = "take_profit"
            result["tp_result"] = tp_result
            return result
        
        # Check stop loss
        sl_hit = position.check_stop_loss(current_price)
        if sl_hit:
            sl_result = position.execute_stop_loss(current_price)
            result["action"] = "stop_loss"
            result["sl_result"] = sl_result
            return result
        
        return result
    
    def get_active_positions(self, user_id: Optional[str] = None) -> List[RoyalQPosition]:
        """Get all active positions, optionally filtered by user"""
        positions = [p for p in self.positions.values() if p.status == "active"]
        if user_id:
            positions = [p for p in positions if p.user_id == user_id]
        return positions
    
    def get_user_positions(self, user_id: str) -> List[RoyalQPosition]:
        """Get all positions for a user"""
        return [p for p in self.positions.values() if p.user_id == user_id]
    
    def close_position(self, position_id: str, current_price: float, reason: str = "manual") -> dict:
        """Manually close a position"""
        position = self.positions.get(position_id)
        if not position:
            return {"error": "Position not found"}
        
        if position.status != "active":
            return {"error": "Position already closed"}
        
        # Calculate final PnL
        if position.side == PositionSide.LONG:
            pnl = (current_price - position.avg_entry) * position.total_filled_qty
        else:
            pnl = (position.avg_entry - current_price) * position.total_filled_qty
        
        position.pnl = pnl
        position.status = "closed"
        position.closed_at = datetime.now().isoformat()
        
        return {
            "action": "manual_close",
            "reason": reason,
            "position_id": position_id,
            "close_price": current_price,
            "avg_entry": position.avg_entry,
            "qty": position.total_filled_qty,
            "pnl": pnl
        }
