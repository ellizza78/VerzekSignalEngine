"""
Financial Tracker - Tracks all money in/out and running balance
Provides real-time financial tracking for admin
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class FinancialTracker:
    """
    Tracks financial transactions and maintains running balance
    
    All amounts in USDT
    - Payments IN: Subscription payments to your wallet
    - Payments OUT: Referral payouts you send to users
    - Running Balance: Net profit (IN - OUT)
    """
    
    def __init__(self):
        self.data_file = "database/financial_tracking.json"
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load financial tracking data"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Default structure
        return {
            'total_received': 0.0,
            'total_paid_out': 0.0,
            'balance': 0.0,
            'transactions': [],
            'last_updated': datetime.now().isoformat()
        }
    
    def _save_data(self):
        """Save financial tracking data"""
        self.data['last_updated'] = datetime.now().isoformat()
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def record_payment_received(self, payment_data: Dict) -> Dict:
        """
        Record a subscription payment received
        
        Args:
            payment_data: {
                'user_id': str,
                'amount_usdt': float,
                'plan': str,
                'tx_hash': str,
                'referral_bonus': float (optional)
            }
        
        Returns:
            Financial summary with new balance
        """
        amount = payment_data.get('amount_usdt', 0)
        referral_bonus = payment_data.get('referral_bonus', 0)
        net_revenue = amount - referral_bonus  # Your actual revenue
        
        # Update totals
        self.data['total_received'] += net_revenue
        self.data['balance'] += net_revenue
        
        # Record transaction
        transaction = {
            'type': 'payment_in',
            'timestamp': datetime.now().isoformat(),
            'user_id': payment_data.get('user_id'),
            'plan': payment_data.get('plan'),
            'gross_amount': amount,
            'referral_bonus': referral_bonus,
            'net_revenue': net_revenue,
            'tx_hash': payment_data.get('tx_hash', 'N/A'),
            'balance_after': self.data['balance']
        }
        
        self.data['transactions'].append(transaction)
        self._save_data()
        
        return {
            'gross_amount': amount,
            'referral_bonus': referral_bonus,
            'net_revenue': net_revenue,
            'total_received': self.data['total_received'],
            'total_paid_out': self.data['total_paid_out'],
            'balance': self.data['balance']
        }
    
    def record_payout_sent(self, payout_data: Dict) -> Dict:
        """
        Record a referral payout sent to user
        
        Args:
            payout_data: {
                'payout_id': str,
                'user_id': str,
                'amount_usdt': float,
                'tx_hash': str
            }
        
        Returns:
            Financial summary with new balance
        """
        amount = payout_data.get('amount_usdt', 0)
        
        # Update totals
        self.data['total_paid_out'] += amount
        self.data['balance'] -= amount
        
        # Record transaction
        transaction = {
            'type': 'payout_out',
            'timestamp': datetime.now().isoformat(),
            'payout_id': payout_data.get('payout_id'),
            'user_id': payout_data.get('user_id'),
            'amount': amount,
            'tx_hash': payout_data.get('tx_hash', 'N/A'),
            'balance_after': self.data['balance']
        }
        
        self.data['transactions'].append(transaction)
        self._save_data()
        
        return {
            'amount_paid': amount,
            'total_received': self.data['total_received'],
            'total_paid_out': self.data['total_paid_out'],
            'balance': self.data['balance']
        }
    
    def get_balance(self) -> float:
        """Get current balance"""
        return self.data['balance']
    
    def get_summary(self) -> Dict:
        """Get financial summary"""
        return {
            'total_received': self.data['total_received'],
            'total_paid_out': self.data['total_paid_out'],
            'balance': self.data['balance'],
            'transaction_count': len(self.data['transactions']),
            'last_updated': self.data['last_updated']
        }
    
    def get_period_summary(self, days: int = 7) -> Dict:
        """
        Get financial summary for a time period
        
        Args:
            days: Number of days to look back (default: 7)
        """
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        recent_transactions = [
            t for t in self.data['transactions']
            if datetime.fromisoformat(t['timestamp']) >= cutoff
        ]
        
        payments_in = sum(
            t.get('net_revenue', 0) 
            for t in recent_transactions 
            if t['type'] == 'payment_in'
        )
        
        payouts_out = sum(
            t.get('amount', 0) 
            for t in recent_transactions 
            if t['type'] == 'payout_out'
        )
        
        return {
            'period_days': days,
            'payments_received': payments_in,
            'payouts_sent': payouts_out,
            'net_change': payments_in - payouts_out,
            'transaction_count': len(recent_transactions),
            'current_balance': self.data['balance']
        }
    
    def reset_balance(self, reason: str = "Manual reset"):
        """
        Reset balance (use with caution!)
        Keeps transaction history but resets running totals
        """
        transaction = {
            'type': 'balance_reset',
            'timestamp': datetime.now().isoformat(),
            'reason': reason,
            'old_balance': self.data['balance']
        }
        
        self.data['balance'] = 0.0
        self.data['total_received'] = 0.0
        self.data['total_paid_out'] = 0.0
        self.data['transactions'].append(transaction)
        self._save_data()


# Global instance
financial_tracker = FinancialTracker()
