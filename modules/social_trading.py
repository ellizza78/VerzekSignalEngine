import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import uuid
from modules.audit_logger import log_event

class SocialTradingManager:
    """Manages copy trading and social features"""
    
    def __init__(self, position_tracker):
        self.position_tracker = position_tracker
        self.masters_file = "database/trading_masters.json"
        self.followers_file = "database/trading_followers.json"
        self.copy_trades_file = "database/copy_trades.json"
        self.masters = self._load_masters()
        self.followers = self._load_followers()
        
    def _load_masters(self) -> Dict:
        """Load trading masters (users being copied)"""
        if os.path.exists(self.masters_file):
            try:
                with open(self.masters_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_masters(self):
        """Save trading masters"""
        os.makedirs(os.path.dirname(self.masters_file), exist_ok=True)
        with open(self.masters_file, 'w') as f:
            json.dump(self.masters, f, indent=2)
    
    def _load_followers(self) -> Dict:
        """Load followers (users copying others)"""
        if os.path.exists(self.followers_file):
            try:
                with open(self.followers_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_followers(self):
        """Save followers"""
        os.makedirs(os.path.dirname(self.followers_file), exist_ok=True)
        with open(self.followers_file, 'w') as f:
            json.dump(self.followers, f, indent=2)
    
    def become_master_trader(self, user_id: str, profile: Dict) -> Dict:
        """Register user as a master trader that others can copy"""
        positions = self.position_tracker.get_user_positions(user_id, status='closed')
        
        if len(positions) < 10:
            return {'success': False, 'error': 'Need at least 10 closed trades to become master'}
        
        total_pnl = sum([p.get('pnl', 0) for p in positions])
        
        if total_pnl <= 0:
            return {'success': False, 'error': 'Must have positive total PnL to become master'}
        
        master_id = f"master_{uuid.uuid4().hex[:8]}"
        
        self.masters[master_id] = {
            'master_id': master_id,
            'user_id': user_id,
            'display_name': profile.get('display_name', f'Trader {user_id[:8]}'),
            'bio': profile.get('bio', ''),
            'strategy_description': profile.get('strategy', ''),
            'min_copy_amount': profile.get('min_copy_amount', 100),
            'copy_fee_percentage': profile.get('copy_fee', 10),
            'follower_count': 0,
            'total_pnl': round(total_pnl, 2),
            'win_rate': 0,
            'verified': False,
            'created_at': datetime.utcnow().isoformat()
        }
        
        self._calculate_master_stats(master_id)
        self._save_masters()
        
        log_event("SOCIAL_TRADING", f"User {user_id} became master trader {master_id}", severity="info")
        
        return {
            'success': True,
            'master_id': master_id,
            'message': 'Successfully registered as master trader'
        }
    
    def _calculate_master_stats(self, master_id: str):
        """Calculate and update master trader statistics"""
        if master_id not in self.masters:
            return
        
        user_id = self.masters[master_id]['user_id']
        positions = self.position_tracker.get_user_positions(user_id, status='closed')
        
        if not positions:
            return
        
        wins = len([p for p in positions if p.get('pnl', 0) > 0])
        total = len(positions)
        win_rate = (wins / total * 100) if total > 0 else 0
        
        total_pnl = sum([p.get('pnl', 0) for p in positions])
        avg_pnl = total_pnl / total if total > 0 else 0
        
        losing_trades = [p for p in positions if p.get('pnl', 0) < 0]
        avg_loss = abs(sum([p.get('pnl', 0) for p in losing_trades]) / len(losing_trades)) if losing_trades else 0
        
        winning_trades = [p for p in positions if p.get('pnl', 0) > 0]
        avg_win = sum([p.get('pnl', 0) for p in winning_trades]) / len(winning_trades) if winning_trades else 0
        
        risk_reward = avg_win / avg_loss if avg_loss > 0 else 0
        
        self.masters[master_id].update({
            'total_trades': total,
            'win_rate': round(win_rate, 1),
            'total_pnl': round(total_pnl, 2),
            'avg_pnl_per_trade': round(avg_pnl, 2),
            'risk_reward_ratio': round(risk_reward, 2),
            'last_updated': datetime.utcnow().isoformat()
        })
        
        self._save_masters()
    
    def copy_trader(self, follower_user_id: str, master_id: str, settings: Dict) -> Dict:
        """Start copying a master trader"""
        if master_id not in self.masters:
            return {'success': False, 'error': 'Master trader not found'}
        
        master = self.masters[master_id]
        
        if settings.get('copy_amount', 0) < master['min_copy_amount']:
            return {
                'success': False,
                'error': f"Minimum copy amount is ${master['min_copy_amount']}"
            }
        
        copy_id = f"copy_{uuid.uuid4().hex[:8]}"
        
        if follower_user_id not in self.followers:
            self.followers[follower_user_id] = {}
        
        self.followers[follower_user_id][copy_id] = {
            'copy_id': copy_id,
            'master_id': master_id,
            'master_user_id': master['user_id'],
            'copy_amount': settings.get('copy_amount'),
            'copy_ratio': settings.get('copy_ratio', 1.0),
            'max_positions': settings.get('max_positions', 5),
            'stop_loss_pct': settings.get('stop_loss_pct'),
            'take_profit_pct': settings.get('take_profit_pct'),
            'active': True,
            'total_copied': 0,
            'started_at': datetime.utcnow().isoformat()
        }
        
        self.masters[master_id]['follower_count'] = self.masters[master_id].get('follower_count', 0) + 1
        
        self._save_followers()
        self._save_masters()
        
        log_event("SOCIAL_TRADING", f"User {follower_user_id} started copying {master_id}", severity="info")
        
        return {
            'success': True,
            'copy_id': copy_id,
            'master': {
                'display_name': master['display_name'],
                'win_rate': master.get('win_rate', 0),
                'total_pnl': master.get('total_pnl', 0)
            },
            'message': f"Now copying {master['display_name']}"
        }
    
    def stop_copying(self, follower_user_id: str, copy_id: str) -> Dict:
        """Stop copying a master trader"""
        if follower_user_id not in self.followers or copy_id not in self.followers[follower_user_id]:
            return {'success': False, 'error': 'Copy relationship not found'}
        
        copy_data = self.followers[follower_user_id][copy_id]
        master_id = copy_data['master_id']
        
        copy_data['active'] = False
        copy_data['stopped_at'] = datetime.utcnow().isoformat()
        
        if master_id in self.masters:
            self.masters[master_id]['follower_count'] = max(0, self.masters[master_id].get('follower_count', 1) - 1)
        
        self._save_followers()
        self._save_masters()
        
        log_event("SOCIAL_TRADING", f"User {follower_user_id} stopped copying {master_id}", severity="info")
        
        return {
            'success': True,
            'message': 'Stopped copying trader',
            'total_copied_trades': copy_data.get('total_copied', 0)
        }
    
    def get_top_masters(self, limit: int = 10, sort_by: str = 'pnl') -> List[Dict]:
        """Get top performing master traders"""
        masters_list = list(self.masters.values())
        
        for master in masters_list:
            self._calculate_master_stats(master['master_id'])
        
        if sort_by == 'pnl':
            masters_list.sort(key=lambda x: x.get('total_pnl', 0), reverse=True)
        elif sort_by == 'win_rate':
            masters_list.sort(key=lambda x: x.get('win_rate', 0), reverse=True)
        elif sort_by == 'followers':
            masters_list.sort(key=lambda x: x.get('follower_count', 0), reverse=True)
        
        return masters_list[:limit]
    
    def copy_master_trade(self, master_user_id: str, position_data: Dict):
        """Automatically copy a master's trade to followers"""
        master_id = None
        for mid, mdata in self.masters.items():
            if mdata['user_id'] == master_user_id:
                master_id = mid
                break
        
        if not master_id:
            return
        
        for follower_user_id, copies in self.followers.items():
            for copy_id, copy_data in copies.items():
                if copy_data['master_id'] == master_id and copy_data.get('active'):
                    follower_positions = self.position_tracker.get_active_positions(follower_user_id)
                    
                    if len(follower_positions) >= copy_data.get('max_positions', 5):
                        continue
                    
                    copied_position = position_data.copy()
                    copied_position['user_id'] = follower_user_id
                    copied_position['quantity'] = position_data['quantity'] * copy_data.get('copy_ratio', 1.0)
                    copied_position['is_copy_trade'] = True
                    copied_position['copied_from'] = master_user_id
                    copied_position['copy_id'] = copy_id
                    
                    self.position_tracker.add_position(copied_position)
                    
                    copy_data['total_copied'] = copy_data.get('total_copied', 0) + 1
                    self._save_followers()
                    
                    log_event("SOCIAL_TRADING", f"Copied trade from {master_user_id} to {follower_user_id}", severity="info")
