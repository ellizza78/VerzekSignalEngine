"""
Admin Dashboard Utilities - Helper functions for admin management
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List
from services.admin_notifications import admin_notifier


def get_pending_payouts_summary() -> Dict:
    """Get summary of all pending payout requests"""
    try:
        payments_file = "database/payments.json"
        if not os.path.exists(payments_file):
            return {
                'total_count': 0,
                'total_amount': 0,
                'payouts': []
            }
        
        with open(payments_file, 'r') as f:
            payments = json.load(f)
        
        pending_payouts = [
            p for p in payments 
            if p.get('payout_id') and p.get('status') == 'pending'
        ]
        
        total_amount = sum(p.get('amount_usdt', 0) for p in pending_payouts)
        
        return {
            'total_count': len(pending_payouts),
            'total_amount': total_amount,
            'payouts': pending_payouts
        }
    except Exception as e:
        print(f"Error getting payout summary: {e}")
        return {
            'total_count': 0,
            'total_amount': 0,
            'payouts': []
        }


def send_batch_payout_notification() -> bool:
    """
    Send batch notification for pending payouts
    Use this for scheduled summaries instead of spamming for each request
    """
    summary = get_pending_payouts_summary()
    
    if summary['total_count'] == 0:
        return False
    
    return admin_notifier.notify_large_payout_batch(summary['payouts'])


def send_daily_platform_summary() -> bool:
    """
    Send daily summary of platform metrics
    Call this once per day via scheduled task
    """
    try:
        # Get users
        users_file = "database/users_v2.json"
        users = []
        if os.path.exists(users_file):
            with open(users_file, 'r') as f:
                data = json.load(f)
                users = data.get('users', [])
        
        # Get payments
        payments_file = "database/payments.json"
        payments = []
        if os.path.exists(payments_file):
            with open(payments_file, 'r') as f:
                payments = json.load(f)
        
        # Get positions
        positions_file = "database/data.json"
        positions = []
        if os.path.exists(positions_file):
            with open(positions_file, 'r') as f:
                data = json.load(f)
                positions = data.get('positions', [])
        
        # Calculate daily stats
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        new_users = sum(
            1 for u in users 
            if u.get('created_at', '').startswith(str(today))
        )
        
        verified_payments = [
            p for p in payments 
            if p.get('status') == 'verified' 
            and p.get('verified_at', '').startswith(str(today))
            and not p.get('payout_id')  # Exclude payouts
        ]
        
        processed_payouts = [
            p for p in payments 
            if p.get('payout_id')
            and p.get('status') == 'completed'
            and p.get('completed_at', '').startswith(str(today))
        ]
        
        pending_payouts = [
            p for p in payments 
            if p.get('payout_id')
            and p.get('status') == 'pending'
        ]
        
        total_revenue = sum(p.get('amount_usdt', 0) for p in verified_payments)
        referral_commissions = sum(
            p.get('amount_usdt', 0) * 0.1 
            for p in verified_payments
            if p.get('referral_code')
        )
        
        active_positions = sum(1 for p in positions if p.get('status') == 'active')
        
        summary_data = {
            'new_users': new_users,
            'payments_verified': len(verified_payments),
            'total_revenue': total_revenue,
            'payouts_processed': len(processed_payouts),
            'pending_payouts': len(pending_payouts),
            'active_positions': active_positions,
            'referral_commissions': referral_commissions
        }
        
        return admin_notifier.notify_daily_summary(summary_data)
        
    except Exception as e:
        print(f"Error generating daily summary: {e}")
        return False


def process_payout(payout_id: str, tx_hash: str, admin_user_id: str) -> Dict:
    """
    Mark a payout as completed after admin sends USDT
    
    Args:
        payout_id: The payout request ID
        tx_hash: Transaction hash of the sent USDT
        admin_user_id: ID of admin who processed it
    """
    try:
        payments_file = "database/payments.json"
        
        if not os.path.exists(payments_file):
            return {'success': False, 'error': 'No payments found'}
        
        with open(payments_file, 'r') as f:
            payments = json.load(f)
        
        payout = next((p for p in payments if p.get('payout_id') == payout_id), None)
        
        if not payout:
            return {'success': False, 'error': 'Payout not found'}
        
        if payout['status'] != 'pending':
            return {'success': False, 'error': f"Payout status is {payout['status']}, not pending"}
        
        # Update payout status
        payout['status'] = 'completed'
        payout['completed_at'] = datetime.now().isoformat()
        payout['tx_hash'] = tx_hash
        payout['processed_by'] = admin_user_id
        
        # Save updated payments
        with open(payments_file, 'w') as f:
            json.dump(payments, f, indent=2)
        
        return {
            'success': True,
            'message': f'Payout {payout_id} marked as completed',
            'amount': payout.get('amount_usdt', 0),
            'user_id': payout.get('user_id')
        }
        
    except Exception as e:
        return {'success': False, 'error': str(e)}
