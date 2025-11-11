"""
Token utilities for password reset and email verification
Uses database storage for production reliability
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session


def generate_reset_token(user_id: int, db: Session) -> str:
    """Generate password reset token (15-minute expiration)"""
    from models import VerificationToken
    
    token = secrets.token_urlsafe(32)
    expiry = datetime.utcnow() + timedelta(minutes=15)
    
    db_token = VerificationToken(
        token=token,
        user_id=user_id,
        token_type="password_reset",
        expires_at=expiry
    )
    db.add(db_token)
    db.commit()
    
    return token


def generate_verification_token(user_id: int, db: Session) -> str:
    """Generate email verification token (24-hour expiration)"""
    from models import VerificationToken
    
    token = secrets.token_urlsafe(32)
    expiry = datetime.utcnow() + timedelta(hours=24)
    
    db_token = VerificationToken(
        token=token,
        user_id=user_id,
        token_type="email_verification",
        expires_at=expiry
    )
    db.add(db_token)
    db.commit()
    
    return token


def verify_token(token: str, token_type: str, db: Session) -> Optional[int]:
    """Verify token and return user_id if valid"""
    from models import VerificationToken
    
    db_token = db.query(VerificationToken).filter(
        VerificationToken.token == token,
        VerificationToken.token_type == token_type
    ).first()
    
    if not db_token:
        return None
    
    # Check expiration
    if datetime.utcnow() > db_token.expires_at:
        db.delete(db_token)  # Clean up expired token
        db.commit()
        return None
    
    return db_token.user_id


def invalidate_token(token: str, db: Session):
    """Invalidate a token (use after successful password reset/verification)"""
    from models import VerificationToken
    
    db_token = db.query(VerificationToken).filter(
        VerificationToken.token == token
    ).first()
    
    if db_token:
        db.delete(db_token)
        db.commit()


def cleanup_expired_tokens(db: Session):
    """Clean up all expired tokens (call periodically via cron)"""
    from models import VerificationToken
    
    now = datetime.utcnow()
    db.query(VerificationToken).filter(
        VerificationToken.expires_at < now
    ).delete()
    db.commit()


def generate_referral_code(user_id: int) -> str:
    """Generate unique referral code for user"""
    raw_code = hashlib.sha256(f"{user_id}{secrets.token_hex(8)}".encode()).hexdigest()[:6].upper()
    return f"VZK{raw_code}"
