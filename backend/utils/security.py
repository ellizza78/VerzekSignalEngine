"""
Security utilities: password hashing, encryption, JWT helpers
"""
import os
import bcrypt
from cryptography.fernet import Fernet


# Password hashing
def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode(), password_hash.encode())


# API key encryption (for exchange credentials)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    raise ValueError(
        "ENCRYPTION_KEY environment variable is required. "
        "Generate one with: python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
    )

fernet = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key"""
    return fernet.encrypt(api_key.encode()).decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key"""
    return fernet.decrypt(encrypted_key.encode()).decode()
