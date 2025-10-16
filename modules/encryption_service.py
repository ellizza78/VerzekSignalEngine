"""
Encryption Service - Secure storage for API keys and sensitive data
Uses Fernet symmetric encryption (AES-128 CBC mode)
"""

import os
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from typing import Optional
from utils.logger import log_event


class EncryptionService:
    """
    Handles encryption/decryption of sensitive data (API keys, secrets)
    Uses environment-based master key for encryption
    """
    
    def __init__(self):
        self.master_key = self._get_or_create_master_key()
        self.cipher = Fernet(self.master_key)
    
    def _get_or_create_master_key(self) -> bytes:
        """
        Get master encryption key from environment
        CRITICAL: Key MUST be set in environment - will raise error if missing
        """
        # MUST have master key in environment for security
        master_key_env = os.environ.get('ENCRYPTION_MASTER_KEY')
        
        if master_key_env:
            # Use existing key from environment
            return master_key_env.encode()
        
        # SECURITY: Generate secure random key if missing (first run only)
        # Admin must save this to Replit Secrets immediately!
        import secrets
        key = base64.urlsafe_b64encode(secrets.token_bytes(32))
        
        log_event("ENCRYPTION", "🔴 CRITICAL: No ENCRYPTION_MASTER_KEY found!")
        log_event("ENCRYPTION", "🔴 Generated one-time key - MUST be saved to Replit Secrets!")
        log_event("ENCRYPTION", "🔴 Add this to Secrets tab: ENCRYPTION_MASTER_KEY")
        log_event("ENCRYPTION", "🔴 Value (COPY NOW, shown once): " + "*" * 20 + " [Hidden for security]")
        
        # Do NOT log the actual key - this was the security vulnerability
        # Admin must regenerate and set in secrets manually
        raise RuntimeError(
            "ENCRYPTION_MASTER_KEY not set in environment! "
            "Generate a secure key and add to Replit Secrets. "
            "Run: python -c 'import secrets,base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())'"
        )
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt sensitive data
        Returns base64-encoded encrypted string
        """
        if not plaintext:
            return ""
        
        try:
            encrypted = self.cipher.encrypt(plaintext.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            log_event("ERROR", f"Encryption failed: {str(e)}")
            raise
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        Decrypt sensitive data
        Returns original plaintext
        """
        if not encrypted_text:
            return ""
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_text.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            log_event("ERROR", f"Decryption failed: {str(e)}")
            raise
    
    def encrypt_dict(self, data: dict, fields_to_encrypt: list) -> dict:
        """
        Encrypt specific fields in a dictionary
        """
        encrypted_data = data.copy()
        
        for field in fields_to_encrypt:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt(str(encrypted_data[field]))
        
        return encrypted_data
    
    def decrypt_dict(self, data: dict, fields_to_decrypt: list) -> dict:
        """
        Decrypt specific fields in a dictionary
        """
        decrypted_data = data.copy()
        
        for field in fields_to_decrypt:
            if field in decrypted_data and decrypted_data[field]:
                decrypted_data[field] = self.decrypt(decrypted_data[field])
        
        return decrypted_data
    
    def encrypt_api_credentials(self, api_key: str, api_secret: str) -> dict:
        """
        Encrypt exchange API credentials
        """
        return {
            'api_key_encrypted': self.encrypt(api_key),
            'api_secret_encrypted': self.encrypt(api_secret),
            'encrypted': True
        }
    
    def decrypt_api_credentials(self, encrypted_creds: dict) -> dict:
        """
        Decrypt exchange API credentials
        """
        if not encrypted_creds.get('encrypted'):
            # Legacy unencrypted data
            log_event("WARNING", "Attempting to decrypt unencrypted credentials")
            return {
                'api_key': encrypted_creds.get('api_key', ''),
                'api_secret': encrypted_creds.get('api_secret', '')
            }
        
        return {
            'api_key': self.decrypt(encrypted_creds['api_key_encrypted']),
            'api_secret': self.decrypt(encrypted_creds['api_secret_encrypted'])
        }


# Global encryption service instance
encryption_service = EncryptionService()
