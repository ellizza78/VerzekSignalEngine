"""
Advanced Order Management for VerzekAutoTrader
Handles trailing stop loss, OCO orders, and advanced position management
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from modules import PositionTracker
from utils.logger import log_event
import json
import os


@dataclass
class TrailingStopConfig:
    """Configuration for trailing stop loss"""
    position_id: str
    user_id: str
    activation_price: float  # Price to activate trailing
    trail_percent: float  # Percentage to trail (e.g., 2.0 for 2%)
    trail_amount: float  # Fixed amount to trail (alternative to percent)
    highest_price: float  # Track highest price for LONG
    lowest_price: float  # Track lowest price for SHORT
    current_stop: float  # Current stop loss price
    active: bool  # Whether trailing is active
    created_at: str
    

@dataclass
class OCOOrder:
    """One-Cancels-Other order configuration"""
    oco_id: str
    user_id: str
    position_id: str
    order_type: str  # 'take_profit_stop_loss'
    take_profit_price: float
    stop_loss_price: float
    quantity: float  # Amount to close
    status: str  # 'active', 'executed', 'cancelled'
    executed_side: Optional[str]  # 'take_profit' or 'stop_loss'
    created_at: str


class AdvancedOrderManager:
    """Manages advanced order types and execution logic"""
    
    def __init__(self):
        self.trailing_stops_file = 'database/trailing_stops.json'
        self.oco_orders_file = 'database/oco_orders.json'
        self.position_tracker = PositionTracker()
        
        # Load existing orders
        self.trailing_stops = self._load_trailing_stops()
        self.oco_orders = self._load_oco_orders()
    
    def _load_trailing_stops(self) -> Dict[str, TrailingStopConfig]:
        """Load trailing stop configurations"""
        if not os.path.exists(self.trailing_stops_file):
            return {}
        
        try:
            with open(self.trailing_stops_file, 'r') as f:
                data = json.load(f)
                return {
                    k: TrailingStopConfig(**v) for k, v in data.items()
                }
        except:
            return {}
    
    def _save_trailing_stops(self):
        """Save trailing stop configurations"""
        os.makedirs(os.path.dirname(self.trailing_stops_file), exist_ok=True)
        data = {
            k: {
                'position_id': v.position_id,
                'user_id': v.user_id,
                'activation_price': v.activation_price,
                'trail_percent': v.trail_percent,
                'trail_amount': v.trail_amount,
                'highest_price': v.highest_price,
                'lowest_price': v.lowest_price,
                'current_stop': v.current_stop,
                'active': v.active,
                'created_at': v.created_at
            }
            for k, v in self.trailing_stops.items()
        }
        with open(self.trailing_stops_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_oco_orders(self) -> Dict[str, OCOOrder]:
        """Load OCO orders"""
        if not os.path.exists(self.oco_orders_file):
            return {}
        
        try:
            with open(self.oco_orders_file, 'r') as f:
                data = json.load(f)
                return {
                    k: OCOOrder(**v) for k, v in data.items()
                }
        except:
            return {}
    
    def _save_oco_orders(self):
        """Save OCO orders"""
        os.makedirs(os.path.dirname(self.oco_orders_file), exist_ok=True)
        data = {
            k: {
                'oco_id': v.oco_id,
                'user_id': v.user_id,
                'position_id': v.position_id,
                'order_type': v.order_type,
                'take_profit_price': v.take_profit_price,
                'stop_loss_price': v.stop_loss_price,
                'quantity': v.quantity,
                'status': v.status,
                'executed_side': v.executed_side,
                'created_at': v.created_at
            }
            for k, v in self.oco_orders.items()
        }
        with open(self.oco_orders_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def create_trailing_stop(self, user_id: str, position_id: str, 
                           trail_percent: float = 0, trail_amount: float = 0,
                           activation_price: Optional[float] = None) -> Dict[str, Any]:
        """
        Create a trailing stop loss for a position
        
        Args:
            user_id: User ID
            position_id: Position to protect
            trail_percent: Percentage to trail (e.g., 2.0 for 2%)
            trail_amount: Fixed amount to trail (alternative)
            activation_price: Price to activate trailing (optional)
        """
        # Get position (returns dict)
        position_dict = self.position_tracker.get_position(position_id)
        if not position_dict or position_dict.get('user_id') != user_id:
            return {'success': False, 'error': 'Position not found'}
        
        if position_dict.get('status') != 'active':
            return {'success': False, 'error': 'Position is not active'}
        
        # Validate trailing configuration
        if trail_percent <= 0 and trail_amount <= 0:
            return {'success': False, 'error': 'Must specify trail_percent or trail_amount'}
        
        # Initialize tracking prices
        current_price = position_dict.get('current_price') or position_dict.get('average_entry')
        
        if position_dict.get('side') == 'LONG':
            highest_price = current_price
            lowest_price = 0
            initial_stop = current_price * (1 - (trail_percent / 100)) if trail_percent else current_price - trail_amount
        else:  # SHORT
            highest_price = 0
            lowest_price = current_price
            initial_stop = current_price * (1 + (trail_percent / 100)) if trail_percent else current_price + trail_amount
        
        # Create trailing stop config
        trailing_stop = TrailingStopConfig(
            position_id=position_id,
            user_id=user_id,
            activation_price=activation_price or 0,
            trail_percent=trail_percent,
            trail_amount=trail_amount,
            highest_price=highest_price,
            lowest_price=lowest_price,
            current_stop=initial_stop,
            active=activation_price is None,  # Active immediately if no activation price
            created_at=datetime.utcnow().isoformat()
        )
        
        self.trailing_stops[position_id] = trailing_stop
        self._save_trailing_stops()
        
        log_event("ADVANCED_ORDERS", f"Created trailing stop for position {position_id}: {trail_percent}% / ${trail_amount}")
        
        return {
            'success': True,
            'trailing_stop': {
                'position_id': position_id,
                'trail_percent': trail_percent,
                'trail_amount': trail_amount,
                'current_stop': initial_stop,
                'active': trailing_stop.active
            }
        }
    
    def update_trailing_stops(self, current_prices: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Update all trailing stops based on current prices
        Returns list of positions that hit their trailing stop
        
        Args:
            current_prices: Dict of {symbol: current_price}
        """
        triggered_stops = []
        
        for position_id, trailing in list(self.trailing_stops.items()):
            position_dict = self.position_tracker.get_position(position_id)
            position = type('Position', (), position_dict)() if position_dict else None
            
            if not position or position.status != 'active':
                # Remove trailing stop for closed/missing positions
                del self.trailing_stops[position_id]
                continue
            
            current_price = current_prices.get(position.symbol)
            if not current_price:
                continue
            
            # Check if trailing should be activated
            if not trailing.active and trailing.activation_price > 0:
                if (position.side == 'LONG' and current_price >= trailing.activation_price) or \
                   (position.side == 'SHORT' and current_price <= trailing.activation_price):
                    trailing.active = True
                    log_event("ADVANCED_ORDERS", f"Trailing stop activated for {position_id} at ${current_price}")
            
            # Update trailing stop if active
            if trailing.active:
                should_update = False
                
                if position.side == 'LONG':
                    # Update highest price
                    if current_price > trailing.highest_price:
                        trailing.highest_price = current_price
                        should_update = True
                    
                    # Calculate new stop based on highest price
                    if trailing.trail_percent > 0:
                        new_stop = trailing.highest_price * (1 - (trailing.trail_percent / 100))
                    else:
                        new_stop = trailing.highest_price - trailing.trail_amount
                    
                    # Only move stop up, never down
                    if new_stop > trailing.current_stop:
                        trailing.current_stop = new_stop
                        should_update = True
                    
                    # Check if stop hit
                    if current_price <= trailing.current_stop:
                        triggered_stops.append({
                            'position_id': position_id,
                            'symbol': position.symbol,
                            'stop_price': trailing.current_stop,
                            'current_price': current_price,
                            'reason': 'trailing_stop_hit'
                        })
                        del self.trailing_stops[position_id]
                
                else:  # SHORT position
                    # Update lowest price
                    if current_price < trailing.lowest_price or trailing.lowest_price == 0:
                        trailing.lowest_price = current_price
                        should_update = True
                    
                    # Calculate new stop based on lowest price
                    if trailing.trail_percent > 0:
                        new_stop = trailing.lowest_price * (1 + (trailing.trail_percent / 100))
                    else:
                        new_stop = trailing.lowest_price + trailing.trail_amount
                    
                    # Only move stop down, never up
                    if new_stop < trailing.current_stop or trailing.current_stop == 0:
                        trailing.current_stop = new_stop
                        should_update = True
                    
                    # Check if stop hit
                    if current_price >= trailing.current_stop:
                        triggered_stops.append({
                            'position_id': position_id,
                            'symbol': position.symbol,
                            'stop_price': trailing.current_stop,
                            'current_price': current_price,
                            'reason': 'trailing_stop_hit'
                        })
                        del self.trailing_stops[position_id]
                
                if should_update:
                    log_event("ADVANCED_ORDERS", f"Updated trailing stop for {position_id}: ${trailing.current_stop}")
        
        if triggered_stops or len(self.trailing_stops) != len(self._load_trailing_stops()):
            self._save_trailing_stops()
        
        return triggered_stops
    
    def create_oco_order(self, user_id: str, position_id: str,
                        take_profit_price: float, stop_loss_price: float,
                        quantity: Optional[float] = None) -> Dict[str, Any]:
        """
        Create a One-Cancels-Other order
        
        Args:
            user_id: User ID
            position_id: Position ID
            take_profit_price: Take profit price level
            stop_loss_price: Stop loss price level
            quantity: Amount to close (None = full position)
        """
        # Get position (returns dict)
        position_dict = self.position_tracker.get_position(position_id)
        if not position_dict or position_dict.get('user_id') != user_id:
            return {'success': False, 'error': 'Position not found'}
        
        if position_dict.get('status') != 'active':
            return {'success': False, 'error': 'Position is not active'}
        
        # Validate prices
        if position_dict.get('side') == 'LONG':
            if take_profit_price <= position_dict.get('average_entry'):
                return {'success': False, 'error': 'Take profit must be above entry for LONG'}
            if stop_loss_price >= position_dict.get('average_entry'):
                return {'success': False, 'error': 'Stop loss must be below entry for LONG'}
        else:  # SHORT
            if take_profit_price >= position_dict.get('average_entry'):
                return {'success': False, 'error': 'Take profit must be below entry for SHORT'}
            if stop_loss_price <= position_dict.get('average_entry'):
                return {'success': False, 'error': 'Stop loss must be above entry for SHORT'}
        
        # Generate OCO ID
        import uuid
        oco_id = f"oco_{uuid.uuid4().hex[:8]}"
        
        # Create OCO order
        oco_order = OCOOrder(
            oco_id=oco_id,
            user_id=user_id,
            position_id=position_id,
            order_type='take_profit_stop_loss',
            take_profit_price=take_profit_price,
            stop_loss_price=stop_loss_price,
            quantity=quantity or position_dict.get('quantity'),
            status='active',
            executed_side=None,
            created_at=datetime.utcnow().isoformat()
        )
        
        self.oco_orders[oco_id] = oco_order
        self._save_oco_orders()
        
        log_event("ADVANCED_ORDERS", f"Created OCO order {oco_id} for position {position_id}")
        
        return {
            'success': True,
            'oco_order': {
                'oco_id': oco_id,
                'position_id': position_id,
                'take_profit_price': take_profit_price,
                'stop_loss_price': stop_loss_price,
                'quantity': oco_order.quantity,
                'status': 'active'
            }
        }
    
    def check_oco_orders(self, current_prices: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Check OCO orders and return triggered orders
        
        Args:
            current_prices: Dict of {symbol: current_price}
        """
        triggered_orders = []
        
        for oco_id, oco in list(self.oco_orders.items()):
            if oco.status != 'active':
                continue
            
            position_dict = self.position_tracker.get_position(oco.position_id)
            position = type('Position', (), position_dict)() if position_dict else None
            if not position or position.status != 'active':
                # Cancel OCO if position closed
                oco.status = 'cancelled'
                continue
            
            current_price = current_prices.get(position.symbol)
            if not current_price:
                continue
            
            # Check if either side triggered
            tp_hit = False
            sl_hit = False
            
            if position.side == 'LONG':
                tp_hit = current_price >= oco.take_profit_price
                sl_hit = current_price <= oco.stop_loss_price
            else:  # SHORT
                tp_hit = current_price <= oco.take_profit_price
                sl_hit = current_price >= oco.stop_loss_price
            
            if tp_hit or sl_hit:
                executed_side = 'take_profit' if tp_hit else 'stop_loss'
                execution_price = oco.take_profit_price if tp_hit else oco.stop_loss_price
                
                triggered_orders.append({
                    'oco_id': oco_id,
                    'position_id': oco.position_id,
                    'symbol': position.symbol,
                    'executed_side': executed_side,
                    'execution_price': execution_price,
                    'quantity': oco.quantity,
                    'current_price': current_price
                })
                
                # Mark as executed
                oco.status = 'executed'
                oco.executed_side = executed_side
                
                log_event("ADVANCED_ORDERS", f"OCO {oco_id} triggered: {executed_side} at ${execution_price}")
        
        if triggered_orders:
            self._save_oco_orders()
        
        return triggered_orders
    
    def cancel_oco_order(self, user_id: str, oco_id: str) -> Dict[str, Any]:
        """Cancel an OCO order"""
        if oco_id not in self.oco_orders:
            return {'success': False, 'error': 'OCO order not found'}
        
        oco = self.oco_orders[oco_id]
        
        if oco.user_id != user_id:
            return {'success': False, 'error': 'Unauthorized'}
        
        if oco.status != 'active':
            return {'success': False, 'error': f'OCO order is {oco.status}'}
        
        oco.status = 'cancelled'
        self._save_oco_orders()
        
        log_event("ADVANCED_ORDERS", f"Cancelled OCO order {oco_id}")
        
        return {'success': True, 'message': 'OCO order cancelled'}
    
    def get_user_advanced_orders(self, user_id: str) -> Dict[str, Any]:
        """Get all advanced orders for a user"""
        trailing = [
            {
                'position_id': ts.position_id,
                'trail_percent': ts.trail_percent,
                'trail_amount': ts.trail_amount,
                'current_stop': ts.current_stop,
                'active': ts.active,
                'created_at': ts.created_at
            }
            for ts in self.trailing_stops.values()
            if ts.user_id == user_id
        ]
        
        oco = [
            {
                'oco_id': o.oco_id,
                'position_id': o.position_id,
                'take_profit_price': o.take_profit_price,
                'stop_loss_price': o.stop_loss_price,
                'quantity': o.quantity,
                'status': o.status,
                'created_at': o.created_at
            }
            for o in self.oco_orders.values()
            if o.user_id == user_id
        ]
        
        return {
            'trailing_stops': trailing,
            'oco_orders': oco
        }


# Global instance
advanced_order_manager = AdvancedOrderManager()
