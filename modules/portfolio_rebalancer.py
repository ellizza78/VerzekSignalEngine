import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from modules.audit_logger import log_event

class PortfolioRebalancer:
    """Manages portfolio rebalancing and allocation"""
    
    def __init__(self, position_tracker):
        self.position_tracker = position_tracker
        self.allocations_file = "database/portfolio_allocations.json"
        self.rebalance_history_file = "database/rebalance_history.json"
        self.allocations = self._load_allocations()
        
    def _load_allocations(self) -> Dict:
        """Load portfolio allocations"""
        if os.path.exists(self.allocations_file):
            try:
                with open(self.allocations_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading allocations: {e}")
        return {}
    
    def _save_allocations(self):
        """Save portfolio allocations"""
        os.makedirs(os.path.dirname(self.allocations_file), exist_ok=True)
        with open(self.allocations_file, 'w') as f:
            json.dump(self.allocations, f, indent=2)
    
    def _log_rebalance(self, user_id: str, changes: List[Dict]):
        """Log rebalance action"""
        history_entry = {
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'changes': changes
        }
        
        history = []
        if os.path.exists(self.rebalance_history_file):
            try:
                with open(self.rebalance_history_file, 'r') as f:
                    history = json.load(f)
            except:
                pass
        
        history.append(history_entry)
        history = history[-1000:]
        
        os.makedirs(os.path.dirname(self.rebalance_history_file), exist_ok=True)
        with open(self.rebalance_history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def set_allocation(self, user_id: str, allocations: Dict[str, float]) -> Dict:
        """
        Set target portfolio allocation percentages
        
        Args:
            user_id: User ID
            allocations: Dict of {symbol: percentage} e.g., {'BTCUSDT': 40, 'ETHUSDT': 30, 'SOLUSDT': 30}
        """
        total = sum(allocations.values())
        if abs(total - 100) > 0.01:
            return {'success': False, 'error': f'Allocations must total 100%, got {total}%'}
        
        if user_id not in self.allocations:
            self.allocations[user_id] = {}
        
        self.allocations[user_id] = {
            'allocations': allocations,
            'auto_rebalance': False,
            'rebalance_threshold': 5.0,
            'updated_at': datetime.utcnow().isoformat()
        }
        
        self._save_allocations()
        
        log_event("PORTFOLIO", f"User {user_id} set allocations: {allocations}", severity="info")
        
        return {
            'success': True,
            'allocations': allocations,
            'message': 'Portfolio allocation updated'
        }
    
    def get_current_allocation(self, user_id: str) -> Dict[str, float]:
        """Get current portfolio allocation percentages"""
        positions = self.position_tracker.get_user_positions(user_id, status='active')
        
        total_value = sum([
            pos.get('quantity', 0) * pos.get('current_price', pos.get('average_entry', 0))
            for pos in positions
        ])
        
        if total_value == 0:
            return {}
        
        allocation = {}
        for pos in positions:
            symbol = pos.get('symbol')
            value = pos.get('quantity', 0) * pos.get('current_price', pos.get('average_entry', 0))
            allocation[symbol] = (value / total_value) * 100
        
        return allocation
    
    def calculate_rebalance_actions(self, user_id: str) -> Dict:
        """Calculate what trades needed to rebalance portfolio"""
        if user_id not in self.allocations:
            return {'success': False, 'error': 'No target allocation set'}
        
        target = self.allocations[user_id]['allocations']
        current = self.get_current_allocation(user_id)
        threshold = self.allocations[user_id].get('rebalance_threshold', 5.0)
        
        positions = self.position_tracker.get_user_positions(user_id, status='active')
        total_value = sum([
            pos.get('quantity', 0) * pos.get('current_price', pos.get('average_entry', 0))
            for pos in positions
        ])
        
        actions = []
        
        for symbol, target_pct in target.items():
            current_pct = current.get(symbol, 0)
            diff = target_pct - current_pct
            
            if abs(diff) > threshold:
                target_value = (target_pct / 100) * total_value
                current_value = (current_pct / 100) * total_value
                trade_value = target_value - current_value
                
                actions.append({
                    'symbol': symbol,
                    'current_pct': round(current_pct, 2),
                    'target_pct': target_pct,
                    'diff_pct': round(diff, 2),
                    'trade_value': round(trade_value, 2),
                    'action': 'BUY' if trade_value > 0 else 'SELL'
                })
        
        return {
            'success': True,
            'needs_rebalance': len(actions) > 0,
            'total_value': total_value,
            'actions': actions,
            'threshold': threshold
        }
    
    def execute_rebalance(self, user_id: str, dry_run: bool = True) -> Dict:
        """Execute portfolio rebalancing"""
        rebalance_plan = self.calculate_rebalance_actions(user_id)
        
        if not rebalance_plan['success']:
            return rebalance_plan
        
        if not rebalance_plan['needs_rebalance']:
            return {
                'success': True,
                'message': 'Portfolio is already balanced',
                'actions': []
            }
        
        if dry_run:
            return {
                'success': True,
                'dry_run': True,
                'message': 'Rebalance plan calculated (not executed)',
                'actions': rebalance_plan['actions']
            }
        
        executed_actions = []
        for action in rebalance_plan['actions']:
            executed_actions.append({
                'symbol': action['symbol'],
                'action': action['action'],
                'value': action['trade_value'],
                'status': 'simulated'
            })
        
        self._log_rebalance(user_id, executed_actions)
        
        log_event("PORTFOLIO", f"User {user_id} rebalanced portfolio: {len(executed_actions)} actions", severity="info")
        
        return {
            'success': True,
            'message': f'Portfolio rebalanced with {len(executed_actions)} actions',
            'actions': executed_actions
        }
    
    def enable_auto_rebalance(self, user_id: str, threshold: float = 5.0) -> Dict:
        """Enable automatic rebalancing when allocation drifts beyond threshold"""
        if user_id not in self.allocations:
            return {'success': False, 'error': 'Set target allocation first'}
        
        self.allocations[user_id]['auto_rebalance'] = True
        self.allocations[user_id]['rebalance_threshold'] = threshold
        self._save_allocations()
        
        return {
            'success': True,
            'message': f'Auto-rebalance enabled with {threshold}% threshold'
        }
    
    def get_allocation_drift(self, user_id: str) -> Dict:
        """Get how far current allocation has drifted from target"""
        if user_id not in self.allocations:
            return {'success': False, 'error': 'No target allocation set'}
        
        target = self.allocations[user_id]['allocations']
        current = self.get_current_allocation(user_id)
        
        drift = {}
        max_drift = 0
        
        for symbol in target.keys():
            target_pct = target.get(symbol, 0)
            current_pct = current.get(symbol, 0)
            diff = abs(target_pct - current_pct)
            drift[symbol] = {
                'target': target_pct,
                'current': round(current_pct, 2),
                'drift': round(diff, 2)
            }
            max_drift = max(max_drift, diff)
        
        return {
            'success': True,
            'drift': drift,
            'max_drift': round(max_drift, 2),
            'needs_rebalance': max_drift > self.allocations[user_id].get('rebalance_threshold', 5.0)
        }
