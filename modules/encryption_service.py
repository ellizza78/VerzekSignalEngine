"""
Encryption Service - Secure storage for API keys and sensitive data
Uses Fernet symmetric encryption (AES-128 CBC mode)
"""

import os
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
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
        Get master encryption key from environment or generate new one
        CRITICAL: This key must be backed up securely!
        """
        # Check if master key exists in environment
        master_key_env = os.environ.get('ENCRYPTION_MASTER_KEY')
        
        if master_key_env:
            # Use existing key from environment
            return master_key_env.encode()
        
        # Generate new master key using server-specific salt
        password = os.environ.get('ENCRYPTION_PASSWORD', 'VerzekAutoTrader2025SecureEncryption!@#')
        salt = os.environ.get('ENCRYPTION_SALT', 'VerzekSalt2025').encode()
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        
        log_event("ENCRYPTION", "⚠️ Generated new encryption key. BACKUP THIS KEY!")
        log_event("ENCRYPTION", f"Set ENCRYPTION_MASTER_KEY environment variable to: {key.decode()}")
        
        return key
    
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
