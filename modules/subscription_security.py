"""
Subscription Security Module
Protects against hacking and fake subscriptions with license key validation
"""

import hashlib
import secrets
import hmac
from datetime import datetime, timedelta
from typing import Optional, Tuple
import json
import os


class SubscriptionSecurity:
    """
    Multi-layer security for subscription validation
    """
    
    def __init__(self):
        self.secret_key = os.environ.get('SUBSCRIPTION_SECRET_KEY', 'VerzekAutoTrader2025SecureSubscriptions!@#')
        self.licenses_file = "database/licenses.json"
        self.licenses = self._load_licenses()
    
    def _load_licenses(self) -> dict:
        """Load issued license keys from persistent storage"""
        if os.path.exists(self.licenses_file):
            with open(self.licenses_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_licenses(self):
        """Save license keys to persistent storage"""
        os.makedirs(os.path.dirname(self.licenses_file), exist_ok=True)
        with open(self.licenses_file, 'w') as f:
            json.dump(self.licenses, f, indent=2)
    
    def generate_license_key(self, user_id: str, plan: str, duration_days: int) -> str:
        """
        Generate cryptographically secure license key with embedded expiry
        Format: VZK-{USER_HASH}-{PLAN}-{BASE64_EXPIRY}-{CHECKSUM}
        """
        from base64 import urlsafe_b64encode
        
        user_hash = hashlib.sha256(user_id.encode()).hexdigest()[:8].upper()
        
        expiry_date = datetime.now() + timedelta(days=duration_days)
        expiry_timestamp = int(expiry_date.timestamp())
        
        expiry_b64 = urlsafe_b64encode(str(expiry_timestamp).encode()).decode().rstrip('=')
        
        plan_code = plan.upper()[:3]
        
        payload = f"{user_id}|{plan}|{expiry_timestamp}"
        checksum = hmac.new(
            self.secret_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()[:8].upper()
        
        license_key = f"VZK-{user_hash}-{plan_code}-{expiry_b64}-{checksum}"
        
        self.licenses[license_key] = {
            'user_id': user_id,
            'plan': plan,
            'expiry': expiry_timestamp,
            'created_at': datetime.now().isoformat()
        }
        
        self._save_licenses()
        
        return license_key
    
    def validate_license_key(self, license_key: str, user_id: str) -> Tuple[bool, str]:
        """
        Validate license key against user_id and expiry
        Can validate even after restart by decoding from license key itself
        
        Returns:
            (is_valid: bool, error_message: str)
        """
        from base64 import urlsafe_b64decode
        
        try:
            parts = license_key.split('-')
            if len(parts) != 5 or parts[0] != 'VZK':
                return (False, "Invalid license key format")
            
            user_hash, plan_code, expiry_b64, checksum = parts[1:]
            
            expected_user_hash = hashlib.sha256(user_id.encode()).hexdigest()[:8].upper()
            if user_hash != expected_user_hash:
                return (False, "License key does not match user")
            
            try:
                padding = 4 - (len(expiry_b64) % 4)
                if padding != 4:
                    expiry_b64 += '=' * padding
                expiry_timestamp = int(urlsafe_b64decode(expiry_b64).decode())
            except Exception as e:
                return (False, f"Invalid expiry encoding in license key: {e}")
            
            if license_key in self.licenses:
                stored_license = self.licenses[license_key]
                plan = stored_license['plan']
            else:
                plan_map = {'PRO': 'pro', 'VIP': 'vip', 'FRE': 'free'}
                plan = plan_map.get(plan_code, plan_code.lower())
            
            payload = f"{user_id}|{plan}|{expiry_timestamp}"
            expected_checksum = hmac.new(
                self.secret_key.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()[:8].upper()
            
            if checksum != expected_checksum:
                return (False, "License key checksum failed - possible tampering detected")
            
            if datetime.now().timestamp() > expiry_timestamp:
                return (False, "License key has expired")
            
            return (True, "License key valid")
            
        except Exception as e:
            return (False, f"License validation error: {str(e)}")
    
    def verify_payment_signature(self, payment_data: dict, signature: str) -> bool:
        """
        Verify payment webhook signature to prevent fake payment notifications
        Used for both Stripe webhooks and crypto payment confirmations
        """
        payload = json.dumps(payment_data, sort_keys=True)
        expected_signature = hmac.new(
            self.secret_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    def create_payment_signature(self, payment_data: dict) -> str:
        """Create signature for payment verification"""
        payload = json.dumps(payment_data, sort_keys=True)
        return hmac.new(
            self.secret_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def generate_referral_code(self, user_id: str) -> str:
        """
        Generate unique referral code for user
        Format: VZK{6-char-unique-code}
        """
        raw_code = hashlib.sha256(f"{user_id}{secrets.token_hex(8)}".encode()).hexdigest()[:6].upper()
        return f"VZK{raw_code}"
    
    def validate_referral_code(self, referral_code: str) -> bool:
        """Validate referral code format"""
        return (
            len(referral_code) == 9 and
            referral_code.startswith('VZK') and
            referral_code[3:].isalnum()
        )
    
    def detect_subscription_fraud(self, user_id: str, payment_amount: float, user_history: dict) -> Tuple[bool, str]:
        """
        Fraud detection for subscription payments
        
        Checks:
        - Multiple failed payments from same IP
        - Unusual payment patterns
        - Rapid subscription changes
        - Amount manipulation
        """
        flags = []
        
        if payment_amount <= 0:
            flags.append("Invalid payment amount")
        
        if user_history.get('failed_payments', 0) > 3:
            flags.append("Multiple failed payment attempts")
        
        last_subscription = user_history.get('last_subscription_date')
        if last_subscription:
            last_date = datetime.fromisoformat(last_subscription)
            hours_since = (datetime.now() - last_date).total_seconds() / 3600
            if hours_since < 1:
                flags.append("Rapid subscription changes detected")
        
        if user_history.get('subscription_count', 0) > 10:
            flags.append("Unusual subscription activity")
        
        is_fraud = len(flags) > 0
        reason = "; ".join(flags) if flags else "No fraud detected"
        
        return (is_fraud, reason)


subscription_security = SubscriptionSecurity()
