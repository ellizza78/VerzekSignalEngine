"""
Two-Factor Authentication (2FA) System
Implements TOTP-based 2FA with backup codes
"""

import pyotp
import qrcode
import io
import base64
import json
import os
from datetime import datetime
from typing import Optional, List, Tuple
import secrets
from modules.encryption_service import encryption_service
from utils.logger import log_event


class TwoFactorAuth:
    """
    Handles 2FA enrollment, verification, and backup codes
    """
    
    def __init__(self):
        self.mfa_file = "database/mfa_secrets.json"
        self.mfa_data = self._load_mfa_data()
    
    def _load_mfa_data(self) -> dict:
        """Load MFA secrets from encrypted storage"""
        if os.path.exists(self.mfa_file):
            with open(self.mfa_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_mfa_data(self):
        """Save MFA secrets to encrypted storage"""
        os.makedirs(os.path.dirname(self.mfa_file), exist_ok=True)
        with open(self.mfa_file, 'w') as f:
            json.dump(self.mfa_data, f, indent=2)
    
    def enroll_user(self, user_id: str, email: str) -> dict:
        """
        Enroll user in 2FA
        Returns QR code and secret for app enrollment
        """
        # Generate secret key
        secret = pyotp.random_base32()
        
        # Create TOTP instance
        totp = pyotp.TOTP(secret)
        
        # Generate provisioning URI for QR code
        provisioning_uri = totp.provisioning_uri(
            name=email,
            issuer_name="VerzekAutoTrader"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Generate backup codes
        backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
        
        # Encrypt and store
        encrypted_secret = encryption_service.encrypt(secret)
        encrypted_backup_codes = [encryption_service.encrypt(code) for code in backup_codes]
        
        self.mfa_data[user_id] = {
            'secret_encrypted': encrypted_secret,
            'backup_codes_encrypted': encrypted_backup_codes,
            'enabled': False,  # Not enabled until first verification
            'enrolled_at': datetime.now().isoformat()
        }
        
        self._save_mfa_data()
        
        log_event("2FA", f"User {user_id} enrolled in 2FA")
        
        return {
            'qr_code': f"data:image/png;base64,{qr_base64}",
            'secret': secret,  # Show once for manual entry
            'backup_codes': backup_codes,
            'provisioning_uri': provisioning_uri
        }
    
    def verify_and_enable(self, user_id: str, token: str) -> Tuple[bool, str]:
        """
        Verify token and enable 2FA for user
        """
        if user_id not in self.mfa_data:
            return (False, "2FA not enrolled for this user")
        
        user_mfa = self.mfa_data[user_id]
        
        # Decrypt secret
        secret = encryption_service.decrypt(user_mfa['secret_encrypted'])
        
        # Verify token
        totp = pyotp.TOTP(secret)
        
        if totp.verify(token, valid_window=1):
            # Enable 2FA
            self.mfa_data[user_id]['enabled'] = True
            self.mfa_data[user_id]['enabled_at'] = datetime.now().isoformat()
            self._save_mfa_data()
            
            log_event("2FA", f"User {user_id} enabled 2FA successfully")
            return (True, "2FA enabled successfully")
        else:
            log_event("2FA", f"User {user_id} failed 2FA verification")
            return (False, "Invalid verification code")
    
    def verify_token(self, user_id: str, token: str, allow_backup: bool = True) -> Tuple[bool, str]:
        """
        Verify 2FA token or backup code
        """
        if user_id not in self.mfa_data:
            return (False, "2FA not enabled for this user")
        
        user_mfa = self.mfa_data[user_id]
        
        if not user_mfa.get('enabled'):
            return (False, "2FA not enabled for this user")
        
        # Try TOTP token first
        secret = encryption_service.decrypt(user_mfa['secret_encrypted'])
        totp = pyotp.TOTP(secret)
        
        if totp.verify(token, valid_window=1):
            log_event("2FA", f"User {user_id} verified with TOTP")
            return (True, "Verified successfully")
        
        # Try backup codes if allowed
        if allow_backup:
            backup_codes = [
                encryption_service.decrypt(code) 
                for code in user_mfa.get('backup_codes_encrypted', [])
            ]
            
            if token.upper() in backup_codes:
                # Remove used backup code
                idx = backup_codes.index(token.upper())
                user_mfa['backup_codes_encrypted'].pop(idx)
                self._save_mfa_data()
                
                log_event("2FA", f"User {user_id} verified with backup code")
                return (True, "Verified with backup code (this code has been consumed)")
        
        log_event("2FA", f"User {user_id} failed 2FA verification")
        return (False, "Invalid verification code")
    
    def is_enabled(self, user_id: str) -> bool:
        """Check if 2FA is enabled for user"""
        return self.mfa_data.get(user_id, {}).get('enabled', False)
    
    def disable_2fa(self, user_id: str, password: str) -> Tuple[bool, str]:
        """
        Disable 2FA for user (requires password confirmation)
        """
        if user_id in self.mfa_data:
            del self.mfa_data[user_id]
            self._save_mfa_data()
            
            log_event("2FA", f"User {user_id} disabled 2FA")
            return (True, "2FA disabled successfully")
        
        return (False, "2FA not enabled for this user")
    
    def regenerate_backup_codes(self, user_id: str) -> List[str]:
        """
        Regenerate backup codes for user
        """
        if user_id not in self.mfa_data:
            raise ValueError("2FA not enabled for this user")
        
        # Generate new backup codes
        backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
        encrypted_backup_codes = [encryption_service.encrypt(code) for code in backup_codes]
        
        self.mfa_data[user_id]['backup_codes_encrypted'] = encrypted_backup_codes
        self._save_mfa_data()
        
        log_event("2FA", f"User {user_id} regenerated backup codes")
        
        return backup_codes
    
    def get_mfa_status(self, user_id: str) -> dict:
        """Get 2FA status for user"""
        if user_id not in self.mfa_data:
            return {
                'enabled': False,
                'enrolled': False
            }
        
        user_mfa = self.mfa_data[user_id]
        backup_count = len(user_mfa.get('backup_codes_encrypted', []))
        
        return {
            'enabled': user_mfa.get('enabled', False),
            'enrolled': True,
            'enrolled_at': user_mfa.get('enrolled_at'),
            'backup_codes_remaining': backup_count
        }


# Global 2FA instance
two_factor_auth = TwoFactorAuth()
