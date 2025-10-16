"""
Advanced Analytics Engine for VerzekAutoTrader
Provides comprehensive performance metrics and trading analytics
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict
from modules import PositionTracker, UserManager
import json
import os


class AnalyticsEngine:
    def __init__(self):
        self.position_tracker = PositionTracker()
        self.user_manager = UserManager()
    
    def get_user_performance(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get comprehensive performance metrics for a user"""
        positions = [p for p in self.position_tracker.load_positions() if p.user_id == user_id]
        
        # Filter by date range
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_positions = []
        
        for pos in positions:
            try:
                if hasattr(pos, 'created_at'):
                    pos_date = datetime.fromisoformat(pos.created_at)
                    if pos_date >= cutoff_date:
                        recent_positions.append(pos)
                else:
                    recent_positions.append(pos)
            except:
                recent_positions.append(pos)
        
        if not recent_positions:
            return self._empty_performance_metrics()
        
        # Calculate metrics
        active = [p for p in recent_positions if p.status == 'active']
        closed = [p for p in recent_positions if p.status == 'closed']
        
        # Win/Loss metrics
        profitable = [p for p in closed if p.realized_pnl > 0]
        losing = [p for p in closed if p.realized_pnl < 0]
        
        win_rate = (len(profitable) / len(closed) * 100) if closed else 0
        
        # PnL metrics
        total_realized_pnl = sum([p.realized_pnl for p in closed])
        total_unrealized_pnl = sum([p.unrealized_pnl for p in active])
        total_pnl = total_realized_pnl + total_unrealized_pnl
        
        # Average metrics
        avg_win = (sum([p.realized_pnl for p in profitable]) / len(profitable)) if profitable else 0
        avg_loss = (sum([p.realized_pnl for p in losing]) / len(losing)) if losing else 0
        
        # Risk metrics
        largest_win = max([p.realized_pnl for p in profitable]) if profitable else 0
        largest_loss = min([p.realized_pnl for p in losing]) if losing else 0
        
        # Profit factor (total wins / total losses)
        total_wins = sum([p.realized_pnl for p in profitable]) if profitable else 0
        total_losses = abs(sum([p.realized_pnl for p in losing])) if losing else 0
        profit_factor = (total_wins / total_losses) if total_losses > 0 else 0
        
        # Symbol performance
        symbol_stats = self._calculate_symbol_performance(recent_positions)
        
        # Daily PnL breakdown
        daily_pnl = self._calculate_daily_pnl(closed)
        
        return {
            'period_days': days,
            'summary': {
                'total_positions': len(recent_positions),
                'active_positions': len(active),
                'closed_positions': len(closed),
                'profitable_trades': len(profitable),
                'losing_trades': len(losing)
            },
            'pnl': {
                'total_pnl': round(total_pnl, 2),
                'realized_pnl': round(total_realized_pnl, 2),
                'unrealized_pnl': round(total_unrealized_pnl, 2)
            },
            'win_metrics': {
                'win_rate': round(win_rate, 1),
                'profit_factor': round(profit_factor, 2),
                'avg_win': round(avg_win, 2),
                'avg_loss': round(avg_loss, 2),
                'largest_win': round(largest_win, 2),
                'largest_loss': round(largest_loss, 2)
            },
            'symbol_performance': symbol_stats,
            'daily_pnl': daily_pnl
        }
    
    def _calculate_symbol_performance(self, positions: List) -> List[Dict]:
        """Calculate performance by symbol"""
        symbol_data = defaultdict(lambda: {
            'trades': 0,
            'wins': 0,
            'losses': 0,
            'total_pnl': 0.0,
            'win_rate': 0.0
        })
        
        for pos in positions:
            if pos.status == 'closed':
                symbol_data[pos.symbol]['trades'] += 1
                symbol_data[pos.symbol]['total_pnl'] += pos.realized_pnl
                
                if pos.realized_pnl > 0:
                    symbol_data[pos.symbol]['wins'] += 1
                else:
                    symbol_data[pos.symbol]['losses'] += 1
        
        # Calculate win rates and format
        result = []
        for symbol, data in symbol_data.items():
            if data['trades'] > 0:
                data['win_rate'] = round((data['wins'] / data['trades'] * 100), 1)
                data['total_pnl'] = round(data['total_pnl'], 2)
                result.append({
                    'symbol': symbol,
                    **data
                })
        
        # Sort by total PnL descending
        result.sort(key=lambda x: x['total_pnl'], reverse=True)
        return result[:10]  # Top 10 symbols
    
    def _calculate_daily_pnl(self, closed_positions: List) -> List[Dict]:
        """Calculate daily PnL breakdown"""
        daily_data = defaultdict(float)
        
        for pos in closed_positions:
            try:
                if hasattr(pos, 'closed_at') and pos.closed_at:
                    close_date = datetime.fromisoformat(pos.closed_at).date()
                    daily_data[close_date.isoformat()] += pos.realized_pnl
            except:
                continue
        
        # Format and sort
        result = [
            {
                'date': date,
                'pnl': round(pnl, 2)
            }
            for date, pnl in daily_data.items()
        ]
        
        result.sort(key=lambda x: x['date'], reverse=True)
        return result[:30]  # Last 30 days
    
    def _empty_performance_metrics(self) -> Dict:
        """Return empty metrics structure"""
        return {
            'period_days': 0,
            'summary': {
                'total_positions': 0,
                'active_positions': 0,
                'closed_positions': 0,
                'profitable_trades': 0,
                'losing_trades': 0
            },
            'pnl': {
                'total_pnl': 0,
                'realized_pnl': 0,
                'unrealized_pnl': 0
            },
            'win_metrics': {
                'win_rate': 0,
                'profit_factor': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'largest_win': 0,
                'largest_loss': 0
            },
            'symbol_performance': [],
            'daily_pnl': []
        }
    
    def get_platform_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get platform-wide analytics"""
        all_positions = self.position_tracker.load_positions()
        all_users = self.user_manager.get_all_users()
        
        # Filter positions by date
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_positions = []
        
        for pos in all_positions:
            try:
                if hasattr(pos, 'created_at'):
                    pos_date = datetime.fromisoformat(pos.created_at)
                    if pos_date >= cutoff_date:
                        recent_positions.append(pos)
                else:
                    recent_positions.append(pos)
            except:
                recent_positions.append(pos)
        
        # Calculate platform metrics
        active_traders = len(set([p.user_id for p in recent_positions if p.status == 'active']))
        total_volume = sum([p.quantity * p.average_entry for p in recent_positions])
        
        closed = [p for p in recent_positions if p.status == 'closed']
        profitable = [p for p in closed if p.realized_pnl > 0]
        
        platform_pnl = sum([p.realized_pnl for p in closed])
        platform_win_rate = (len(profitable) / len(closed) * 100) if closed else 0
        
        # User distribution
        user_distribution = {
            'free': len([u for u in all_users if u.plan == 'FREE']),
            'pro': len([u for u in all_users if u.plan == 'PRO']),
            'vip': len([u for u in all_users if u.plan == 'VIP'])
        }
        
        # Most active traders
        trader_activity = defaultdict(int)
        for pos in recent_positions:
            trader_activity[pos.user_id] += 1
        
        top_traders = sorted(
            [{'user_id': uid, 'trades': count} for uid, count in trader_activity.items()],
            key=lambda x: x['trades'],
            reverse=True
        )[:5]
        
        return {
            'period_days': days,
            'platform_metrics': {
                'total_positions': len(recent_positions),
                'active_traders': active_traders,
                'total_volume': round(total_volume, 2),
                'platform_pnl': round(platform_pnl, 2),
                'platform_win_rate': round(platform_win_rate, 1)
            },
            'user_distribution': user_distribution,
            'top_traders': top_traders
        }
    
    def get_risk_metrics(self, user_id: str) -> Dict[str, Any]:
        """Calculate risk metrics for a user"""
        positions = [p for p in self.position_tracker.load_positions() 
                    if p.user_id == user_id and p.status == 'active']
        
        if not positions:
            return {
                'total_exposure': 0,
                'positions_at_risk': 0,
                'max_drawdown': 0,
                'risk_score': 0
            }
        
        # Calculate exposure
        total_exposure = sum([p.quantity * p.average_entry for p in positions])
        
        # Positions at risk (negative unrealized PnL)
        at_risk = [p for p in positions if p.unrealized_pnl < 0]
        positions_at_risk = len(at_risk)
        
        # Max drawdown
        max_drawdown = min([p.unrealized_pnl for p in at_risk]) if at_risk else 0
        
        # Risk score (0-100, higher is riskier)
        risk_score = min(100, (positions_at_risk / max(len(positions), 1) * 100))
        
        return {
            'total_exposure': round(total_exposure, 2),
            'positions_at_risk': positions_at_risk,
            'max_drawdown': round(max_drawdown, 2),
            'risk_score': round(risk_score, 1),
            'active_positions': len(positions)
        }


# Global instance
analytics_engine = AnalyticsEngine()
