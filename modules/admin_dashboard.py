"""
Admin Dashboard Module for VerzekAutoTrader
Provides backend logic for admin dashboard functionality
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from modules import UserManager, PositionTracker
from modules.payment_system import payment_system
from modules.subscription_security import subscription_security
import json
import os
from utils.logger import log_event


class AdminDashboard:
    def __init__(self):
        self.user_manager = UserManager()
        self.position_tracker = PositionTracker()
        
    def get_system_overview(self) -> Dict[str, Any]:
        """Get high-level system statistics"""
        users = self.user_manager.get_all_users()
        positions = self.position_tracker.load_positions()
        
        # User statistics (with backward compatibility for legacy 'PRO' plan)
        total_users = len(users)
        active_users = len([u for u in users if u.plan not in ['FREE', 'free']])
        free_users = len([u for u in users if u.plan in ['FREE', 'free', 'trial']])
        vip_users = len([u for u in users if u.plan in ['VIP', 'vip']])
        premium_users = len([u for u in users if u.plan in ['PREMIUM', 'premium', 'PRO', 'pro']])
        
        # Position statistics
        active_positions = len([p for p in positions if p.status == 'active'])
        total_positions = len(positions)
        
        # Calculate total PnL across all positions
        total_pnl = sum([p.unrealized_pnl for p in positions if p.status == 'active'])
        realized_pnl = sum([p.realized_pnl for p in positions if p.status == 'closed'])
        
        # Payment statistics
        payments = payment_system._load_payments()
        total_revenue = sum([p['amount'] for p in payments if p['status'] == 'approved'])
        pending_payments = len([p for p in payments if p['status'] == 'pending'])
        
        return {
            'users': {
                'total': total_users,
                'active': active_users,
                'free': free_users,
                'vip': vip_users,
                'premium': premium_users
            },
            'positions': {
                'active': active_positions,
                'total': total_positions,
                'unrealized_pnl': round(total_pnl, 2),
                'realized_pnl': round(realized_pnl, 2)
            },
            'revenue': {
                'total': round(total_revenue, 2),
                'pending_payments': pending_payments
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_user_list(self, plan_filter: Optional[str] = None, 
                      search: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of users with optional filtering"""
        users = self.user_manager.get_all_users()
        
        # Apply filters
        if plan_filter:
            users = [u for u in users if u.plan == plan_filter.upper()]
        
        if search:
            search_lower = search.lower()
            users = [u for u in users if 
                    search_lower in u.email.lower() or 
                    search_lower in u.full_name.lower() or
                    search_lower in u.user_id.lower()]
        
        # Load all positions ONCE for performance (not in loop)
        all_positions = self.position_tracker.load_positions()
        
        # Group positions by user_id for fast lookup
        positions_by_user = {}
        for pos in all_positions:
            if pos.user_id not in positions_by_user:
                positions_by_user[pos.user_id] = []
            positions_by_user[pos.user_id].append(pos)
        
        # Format user data
        user_list = []
        for user in users:
            # Get user's positions from pre-loaded dict
            user_positions = positions_by_user.get(user.user_id, [])
            
            # Get user's active license
            license_key = None
            if hasattr(user, 'license_key'):
                license_key = user.license_key
            
            user_list.append({
                'user_id': user.user_id,
                'email': user.email,
                'full_name': user.full_name,
                'plan': user.plan,
                'plan_expires_at': user.plan_expires_at,
                'license_key': license_key,
                'active_positions': len([p for p in user_positions if p.status == 'active']),
                'total_trades': len(user_positions),
                'created_at': getattr(user, 'created_at', 'N/A'),
                'mfa_enabled': hasattr(user, 'mfa_enabled') and user.mfa_enabled
            })
        
        return sorted(user_list, key=lambda x: x['email'])
    
    def get_pending_payments(self) -> List[Dict[str, Any]]:
        """Get all pending payment verifications"""
        payments = payment_system._load_payments()
        pending = [p for p in payments if p['status'] == 'pending']
        
        # Enrich with user data
        for payment in pending:
            user = self.user_manager.get_user(payment['user_id'])
            if user:
                payment['user_email'] = user.email
                payment['user_name'] = user.full_name
        
        return sorted(pending, key=lambda x: x['created_at'], reverse=True)
    
    def get_recent_activity(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent system activity from audit logs"""
        audit_log_file = 'database/audit_logs.jsonl'
        
        if not os.path.exists(audit_log_file):
            return []
        
        activities = []
        with open(audit_log_file, 'r') as f:
            for line in f:
                try:
                    activities.append(json.loads(line))
                except:
                    continue
        
        # Sort by timestamp descending and limit
        activities.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return activities[:limit]
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        # Check critical files exist
        critical_files = [
            'database/users.json',
            'database/positions.json',
            'database/user_exchange_accounts.json',
            'database/payments.json',
            'database/licenses.json'
        ]
        
        files_ok = all([os.path.exists(f) for f in critical_files])
        
        # Check environment variables
        required_env_vars = [
            'ENCRYPTION_MASTER_KEY',
            'TELEGRAM_BOT_TOKEN',
            'BROADCAST_BOT_TOKEN',
            'ADMIN_CHAT_ID'
        ]
        
        env_vars_ok = all([os.environ.get(var) for var in required_env_vars])
        
        # Check backup status
        backup_dir = 'backups'
        latest_backup = None
        if os.path.exists(backup_dir):
            backups = [f for f in os.listdir(backup_dir) if f.endswith('.tar.gz')]
            if backups:
                backups.sort(reverse=True)
                latest_backup = backups[0]
        
        # Get disk usage (approximate)
        db_size = 0
        if os.path.exists('database'):
            for file in os.listdir('database'):
                file_path = os.path.join('database', file)
                if os.path.isfile(file_path):
                    db_size += os.path.getsize(file_path)
        
        return {
            'status': 'healthy' if (files_ok and env_vars_ok) else 'degraded',
            'critical_files': files_ok,
            'environment_vars': env_vars_ok,
            'latest_backup': latest_backup,
            'database_size_mb': round(db_size / (1024 * 1024), 2),
            'uptime_check': datetime.utcnow().isoformat()
        }
    
    def get_revenue_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get revenue analytics for specified period"""
        payments = payment_system._load_payments()
        
        # Filter by date range
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_payments = []
        
        for payment in payments:
            try:
                payment_date = datetime.fromisoformat(payment['created_at'])
                if payment_date >= cutoff_date:
                    recent_payments.append(payment)
            except:
                continue
        
        # Calculate metrics
        approved = [p for p in recent_payments if p['status'] == 'approved']
        rejected = [p for p in recent_payments if p['status'] == 'rejected']
        pending = [p for p in recent_payments if p['status'] == 'pending']
        
        total_revenue = sum([p['amount'] for p in approved])
        
        # Revenue by plan (case-insensitive, with legacy 'pro' support)
        vip_revenue = sum([p['amount'] for p in approved if p['plan'].lower() == 'vip'])
        premium_revenue = sum([p['amount'] for p in approved if p['plan'].lower() in ['premium', 'pro']])
        
        return {
            'period_days': days,
            'total_revenue': round(total_revenue, 2),
            'vip_revenue': round(vip_revenue, 2),
            'premium_revenue': round(premium_revenue, 2),
            'payments': {
                'approved': len(approved),
                'rejected': len(rejected),
                'pending': len(pending)
            },
            'conversion_rate': round((len(approved) / len(recent_payments) * 100) if recent_payments else 0, 1)
        }
    
    def get_trading_performance(self) -> Dict[str, Any]:
        """Get overall trading performance metrics"""
        positions = self.position_tracker.load_positions()
        
        if not positions:
            return {
                'total_positions': 0,
                'active_positions': 0,
                'closed_positions': 0,
                'win_rate': 0,
                'total_pnl': 0
            }
        
        active = [p for p in positions if p.status == 'active']
        closed = [p for p in positions if p.status == 'closed']
        
        # Calculate win rate from closed positions
        profitable = [p for p in closed if p.realized_pnl > 0]
        win_rate = (len(profitable) / len(closed) * 100) if closed else 0
        
        # Calculate PnL
        total_realized_pnl = sum([p.realized_pnl for p in closed])
        total_unrealized_pnl = sum([p.unrealized_pnl for p in active])
        
        return {
            'total_positions': len(positions),
            'active_positions': len(active),
            'closed_positions': len(closed),
            'win_rate': round(win_rate, 1),
            'profitable_trades': len(profitable),
            'losing_trades': len(closed) - len(profitable),
            'total_realized_pnl': round(total_realized_pnl, 2),
            'total_unrealized_pnl': round(total_unrealized_pnl, 2),
            'total_pnl': round(total_realized_pnl + total_unrealized_pnl, 2)
        }


# Global instance
admin_dashboard = AdminDashboard()
