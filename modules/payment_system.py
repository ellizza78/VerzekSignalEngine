"""
Payment System - Handles USDT TRC20 verification and referral bonuses
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from utils.logger import log_event
from services.admin_notifications import admin_notifier
from services.financial_tracker import financial_tracker


class PaymentSystem:
    """
    Payment processing and verification for USDT TRC20 and referrals
    """
    
    def __init__(self):
        self.payments_file = "database/payments.json"
        self.referrals_file = "database/referrals.json"
        self.payments = self._load_payments()
        self.referrals = self._load_referrals()
        
        self.PLAN_PRICES = {
            'free': 0,
            'trial': 0,
            'vip': 50,      # $50 USDT monthly - Signals only
            'premium': 120  # $120 USDT monthly - Full auto-trading
        }
        
        self.REFERRAL_BONUS_PERCENT = 10  # 10% recurring commission
    
    def _load_payments(self) -> List[dict]:
        """Load payment records"""
        if os.path.exists(self.payments_file):
            with open(self.payments_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_payments(self):
        """Save payment records"""
        os.makedirs(os.path.dirname(self.payments_file), exist_ok=True)
        with open(self.payments_file, 'w') as f:
            json.dump(self.payments, f, indent=2)
    
    def _load_referrals(self) -> Dict:
        """Load referral data"""
        if os.path.exists(self.referrals_file):
            with open(self.referrals_file, 'r') as f:
                return json.load(f)
        return {
            'codes': {},  # referral_code -> user_id
            'referrals': {},  # referrer_user_id -> [referee_user_ids]
            'earnings': {},  # user_id -> total_earnings
            'wallets': {},  # user_id -> wallet_balance
            'recurring': {}  # user_id -> [recurring_subscriptions]
        }
    
    def _save_referrals(self):
        """Save referral data"""
        os.makedirs(os.path.dirname(self.referrals_file), exist_ok=True)
        with open(self.referrals_file, 'w') as f:
            json.dump(self.referrals, f, indent=2)
    
    def create_payment_request(
        self,
        user_id: str,
        plan: str,
        payment_method: str = 'usdt_trc20'
    ) -> dict:
        """
        Create payment request for subscription
        
        Returns payment details including wallet address and amount
        """
        amount_usdt = self.PLAN_PRICES.get(plan, 0)
        
        if amount_usdt == 0:
            return {
                'error': 'Free plan does not require payment',
                'success': False
            }
        
        payment_id = f"PAY_{user_id}_{int(datetime.now().timestamp())}"
        
        payment_request = {
            'payment_id': payment_id,
            'user_id': user_id,
            'plan': plan,
            'amount_usdt': amount_usdt,
            'payment_method': payment_method,
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=24)).isoformat(),
            'wallet_address': os.environ.get('USDT_TRC20_WALLET', 'TYourWalletAddressHere'),
            'network': 'TRC20 (TRON)',
            'instructions': [
                f"Send exactly {amount_usdt} USDT",
                "Network: TRC20 (TRON)",
                f"To wallet: {os.environ.get('USDT_TRC20_WALLET', 'TYourWalletAddressHere')}",
                "After payment, provide transaction hash for verification"
            ]
        }
        
        self.payments.append(payment_request)
        self._save_payments()
        
        log_event("PAYMENT", f"Payment request created: {payment_id} for user {user_id}")
        
        return {
            'success': True,
            'payment_request': payment_request
        }
    
    def verify_usdt_payment(
        self,
        payment_id: str,
        tx_hash: str,
        user_id: str,
        referral_code: Optional[str] = None
    ) -> dict:
        """
        Verify USDT TRC20 payment (admin manual verification for now)
        In production, integrate with TronScan API for automatic verification
        
        Returns verification result and activates subscription if valid
        """
        payment = next((p for p in self.payments if p['payment_id'] == payment_id), None)
        
        if not payment:
            return {'success': False, 'error': 'Payment request not found'}
        
        if payment['user_id'] != user_id:
            return {'success': False, 'error': 'Payment does not belong to this user'}
        
        if payment['status'] == 'verified':
            return {'success': False, 'error': 'Payment already verified'}
        
        payment['tx_hash'] = tx_hash
        payment['status'] = 'pending_verification'
        payment['submitted_at'] = datetime.now().isoformat()
        
        if referral_code:
            payment['referral_code'] = referral_code
        
        self._save_payments()
        
        log_event("PAYMENT", f"Payment {payment_id} submitted for verification. TX: {tx_hash}")
        
        return {
            'success': True,
            'message': 'Payment submitted for verification. Admin will confirm within 30 minutes.',
            'payment_id': payment_id,
            'status': 'pending_verification'
        }
    
    def admin_confirm_payment(self, payment_id: str, is_valid: bool) -> dict:
        """
        Admin confirms payment after manual verification
        Activates subscription and processes referral bonus if valid
        """
        payment = next((p for p in self.payments if p['payment_id'] == payment_id), None)
        
        if not payment:
            return {'success': False, 'error': 'Payment not found'}
        
        if is_valid:
            payment['status'] = 'verified'
            payment['verified_at'] = datetime.now().isoformat()
            
            user_id = payment['user_id']
            plan = payment['plan']
            amount = payment['amount_usdt']
            
            referrer_id = payment.get('referral_code')
            referral_bonus = 0
            if referrer_id and referrer_id in self.referrals['codes']:
                referral_bonus = amount * (self.REFERRAL_BONUS_PERCENT / 100)
                self._process_referral_bonus(
                    referrer_id=self.referrals['codes'][referrer_id],
                    referee_id=user_id,
                    payment_amount=amount
                )
            
            log_event("PAYMENT", f"Payment {payment_id} verified and subscription activated")
            
            self._save_payments()
            
            # Record in financial tracker
            financial_summary = financial_tracker.record_payment_received({
                'user_id': user_id,
                'plan': plan,
                'amount_usdt': amount,
                'tx_hash': payment.get('tx_hash', 'N/A'),
                'referral_bonus': referral_bonus
            })
            
            # Notify admin of successful payment with financial summary
            admin_notifier.notify_payment_received({
                'user_id': user_id,
                'plan': plan,
                'amount_usdt': amount,
                'tx_hash': payment.get('tx_hash', 'N/A'),
                'referral_bonus': referral_bonus
            }, financial_summary)
            
            return {
                'success': True,
                'message': f'Payment verified. {plan} subscription activated.',
                'user_id': user_id,
                'plan': plan
            }
        else:
            payment['status'] = 'rejected'
            payment['rejected_at'] = datetime.now().isoformat()
            
            self._save_payments()
            
            return {
                'success': False,
                'message': 'Payment rejected by admin',
                'payment_id': payment_id
            }
    
    def register_referral_code(self, user_id: str, referral_code: str):
        """Register user's referral code and initialize in-app wallet"""
        self.referrals['codes'][referral_code] = user_id
        self.referrals['referrals'][user_id] = []
        self.referrals['earnings'][user_id] = 0.0
        self.referrals['wallets'][user_id] = 0.0
        self.referrals['recurring'][user_id] = []
        self._save_referrals()
        
        log_event("REFERRAL", f"Referral code {referral_code} and wallet initialized for user {user_id}")
    
    def _process_referral_bonus(self, referrer_id: str, referee_id: str, payment_amount: float, is_recurring: bool = False):
        """
        Process referral bonus when referee makes payment
        10% commission credited to in-app wallet
        Continues every month for recurring subscriptions
        """
        bonus = payment_amount * (self.REFERRAL_BONUS_PERCENT / 100)
        
        if referrer_id not in self.referrals['referrals']:
            self.referrals['referrals'][referrer_id] = []
        
        if not is_recurring:
            self.referrals['referrals'][referrer_id].append({
                'referee_id': referee_id,
                'payment_amount': payment_amount,
                'bonus_earned': bonus,
                'date': datetime.now().isoformat()
            })
            
            if referrer_id not in self.referrals['recurring']:
                self.referrals['recurring'][referrer_id] = []
            
            self.referrals['recurring'][referrer_id].append({
                'referee_id': referee_id,
                'started_at': datetime.now().isoformat()
            })
        
        if referrer_id not in self.referrals['earnings']:
            self.referrals['earnings'][referrer_id] = 0.0
        
        if referrer_id not in self.referrals['wallets']:
            self.referrals['wallets'][referrer_id] = 0.0
        
        self.referrals['earnings'][referrer_id] += bonus
        self.referrals['wallets'][referrer_id] += bonus
        
        self._save_referrals()
        
        bonus_type = "Recurring" if is_recurring else "Initial"
        log_event("REFERRAL", f"{bonus_type} referral bonus ${bonus} credited to {referrer_id} wallet from {referee_id}")
    
    def get_referral_stats(self, user_id: str) -> dict:
        """Get referral statistics for user including in-app wallet balance"""
        return {
            'total_referrals': len(self.referrals['referrals'].get(user_id, [])),
            'total_earnings': self.referrals['earnings'].get(user_id, 0.0),
            'wallet_balance': self.referrals['wallets'].get(user_id, 0.0),
            'recurring_subscriptions': len(self.referrals['recurring'].get(user_id, [])),
            'referral_history': self.referrals['referrals'].get(user_id, []),
            'pending_payout': self.referrals['wallets'].get(user_id, 0.0)
        }
    
    def request_referral_payout(self, user_id: str, wallet_address: str) -> dict:
        """
        Request referral bonus payout from in-app wallet to user's external wallet
        Minimum payout: $10 USDT
        Withdrawal fee: $1 USDT (goes to system wallet)
        """
        wallet_balance = self.referrals['wallets'].get(user_id, 0.0)
        
        if wallet_balance < 10:
            return {
                'success': False,
                'error': 'Minimum payout is $10 USDT',
                'current_balance': wallet_balance
            }
        
        WITHDRAWAL_FEE = 1.0
        payout_amount = wallet_balance - WITHDRAWAL_FEE
        
        payout_id = f"PAYOUT_{user_id}_{int(datetime.now().timestamp())}"
        
        payout_request = {
            'payout_id': payout_id,
            'user_id': user_id,
            'amount_usdt': payout_amount,
            'withdrawal_fee': WITHDRAWAL_FEE,
            'total_deducted': wallet_balance,
            'wallet_address': wallet_address,
            'network': 'TRC20',
            'status': 'pending',
            'requested_at': datetime.now().isoformat()
        }
        
        self.referrals['wallets'][user_id] = 0.0
        
        self._save_referrals()
        
        self.payments.append(payout_request)
        self._save_payments()
        
        log_event("PAYOUT", f"Payout request {payout_id}: ${payout_amount} to {wallet_address} (${WITHDRAWAL_FEE} fee)")
        
        # Get current balance for notification
        current_balance = financial_tracker.get_balance()
        
        # Send instant notification to admin with balance info
        admin_notifier.notify_payout_request(payout_request, current_balance)
        
        return {
            'success': True,
            'message': f'Payout request submitted. ${payout_amount} USDT will be sent to {wallet_address} within 24 hours. (${WITHDRAWAL_FEE} withdrawal fee applied)',
            'payout_id': payout_id,
            'amount': payout_amount,
            'fee': WITHDRAWAL_FEE
        }
    
    def get_pending_payments(self) -> List[dict]:
        """Get all pending payment verifications for admin"""
        return [p for p in self.payments if p['status'] == 'pending_verification']
    
    def get_pending_payouts(self) -> List[dict]:
        """Get all pending referral payouts for admin"""
        return [p for p in self.payments if p.get('payout_id') and p['status'] == 'pending']


payment_system = PaymentSystem()
