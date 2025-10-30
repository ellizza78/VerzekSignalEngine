"""
Recurring Payments Handler - Processes monthly subscription renewals and referral bonuses
"""

import json
import os
from datetime import datetime, timedelta
from typing import List
from utils.logger import log_event
from modules.payment_system import payment_system


class RecurringPaymentHandler:
    """
    Handles automatic processing of recurring subscriptions
    and monthly referral commission payments
    """
    
    def __init__(self):
        self.users_file = "database/users.json"
        self.last_check_file = "database/last_recurring_check.json"
        self.last_check = self._load_last_check()
    
    def _load_last_check(self) -> dict:
        """Load last check timestamp"""
        if os.path.exists(self.last_check_file):
            with open(self.last_check_file, 'r') as f:
                return json.load(f)
        return {'last_processed': datetime.now().isoformat()}
    
    def _save_last_check(self):
        """Save last check timestamp"""
        os.makedirs(os.path.dirname(self.last_check_file), exist_ok=True)
        with open(self.last_check_file, 'w') as f:
            json.dump(self.last_check, f, indent=2)
    
    def process_monthly_renewals(self):
        """
        Check for subscription renewals and process recurring referral bonuses
        Runs daily to check if 30 days have passed since last payment
        """
        now = datetime.now()
        last_processed = datetime.fromisoformat(self.last_check['last_processed'])
        
        # Only process once per day
        if (now - last_processed).days < 1:
            return
        
        log_event("RECURRING", "Checking for subscription renewals and recurring commissions...")
        
        # Process all active recurring subscriptions
        for referrer_id, recurring_subs in payment_system.referrals.get('recurring', {}).items():
            for sub in recurring_subs:
                referee_id = sub['referee_id']
                started_at = datetime.fromisoformat(sub['started_at'])
                
                # Check if 30 days have passed
                days_since_start = (now - started_at).days
                
                if days_since_start > 0 and days_since_start % 30 == 0:
                    # Find referee's active subscription plan and amount
                    referee_payment = self._get_active_subscription(referee_id)
                    
                    if referee_payment:
                        payment_amount = referee_payment['amount_usdt']
                        
                        # Process recurring referral bonus (10%)
                        payment_system._process_referral_bonus(
                            referrer_id=referrer_id,
                            referee_id=referee_id,
                            payment_amount=payment_amount,
                            is_recurring=True
                        )
                        
                        log_event("RECURRING", f"Processed recurring commission for {referrer_id} from {referee_id} subscription")
        
        self.last_check['last_processed'] = now.isoformat()
        self._save_last_check()
    
    def _get_active_subscription(self, user_id: str) -> dict:
        """Get active subscription payment for user"""
        if not os.path.exists(self.users_file):
            return None
        
        with open(self.users_file, 'r') as f:
            users = json.load(f)
        
        user = users.get(user_id)
        if not user:
            return None
        
        plan = user.get('plan', 'free')
        if plan == 'free':
            return None
        
        # Check if subscription is still active
        expires_at = user.get('plan_expires_at')
        if expires_at:
            expiry_date = datetime.fromisoformat(expires_at)
            if datetime.now() > expiry_date:
                return None
        
        # Return subscription details
        amount = 50 if plan == 'vip' else 120 if plan == 'premium' else 0
        
        return {
            'user_id': user_id,
            'plan': plan,
            'amount_usdt': amount
        }


recurring_handler = RecurringPaymentHandler()
