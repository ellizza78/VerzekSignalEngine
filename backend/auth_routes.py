"""
Authentication Routes
Handles: register, login, refresh, me, email verification, password reset
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from datetime import datetime

from db import SessionLocal
from models import User, UserSettings
from utils.security import hash_password, verify_password
from utils.logger import api_logger
from utils.tokens import generate_reset_token, generate_verification_token, verify_token, invalidate_token, generate_referral_code
from utils.email import send_password_reset_email, send_verification_email, send_welcome_email

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        full_name = data.get('full_name', data.get('username', ''))
        referral_code_input = data.get('referral_code', '').strip().upper()
        
        if not email or not password:
            return jsonify({"ok": False, "error": "Email and password required"}), 400
        
        db: Session = SessionLocal()
        
        # Check if user exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            db.close()
            return jsonify({"ok": False, "error": "Email already registered"}), 400
        
        # Validate referral code if provided
        referrer_id = None
        if referral_code_input:
            referrer = db.query(User).filter(User.referral_code == referral_code_input).first()
            if referrer:
                referrer_id = referrer.id
                api_logger.info(f"New user referred by user {referrer_id} with code {referral_code_input}")
        
        # Create user
        user = User(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            is_verified=True,  # Set to True for now (user requested no email verification currently)
            subscription_type="TRIAL",
            referred_by=referrer_id
        )
        db.add(user)
        db.flush()
        
        # Generate unique referral code for new user
        user.referral_code = generate_referral_code(user.id)
        
        # Create default settings
        settings = UserSettings(
            user_id=user.id,
            capital_usdt=0,
            per_trade_usdt=5.0,
            leverage=1,
            max_concurrent_trades=5
        )
        db.add(settings)
        db.commit()
        
        # Send welcome email (async, don't block registration)
        try:
            send_welcome_email(email, full_name or "User")
        except Exception as e:
            api_logger.error(f"Welcome email failed for {email}: {e}")
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        api_logger.info(f"New user registered: {email} with referral code {user.referral_code}")
        
        db.close()
        
        return jsonify({
            "ok": True,
            "message": "Registration successful",
            "token": access_token,  # Mobile app expects "token"
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "subscription_type": user.subscription_type,
                "is_verified": user.is_verified,
                "referral_code": user.referral_code
            }
        }), 201
        
    except Exception as e:
        api_logger.error(f"Registration error: {e}")
        return jsonify({"ok": False, "error": "Registration failed"}), 500


@bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({"ok": False, "error": "Email and password required"}), 400
        
        db: Session = SessionLocal()
        user = db.query(User).filter(User.email == email).first()
        
        if not user or not verify_password(password, user.password_hash):
            db.close()
            return jsonify({"ok": False, "error": "Invalid credentials"}), 401
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        api_logger.info(f"User logged in: {email}")
        
        db.close()
        
        return jsonify({
            "ok": True,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "subscription_type": user.subscription_type,
                "is_verified": user.is_verified,
                "auto_trade_enabled": user.auto_trade_enabled,
                "referral_code": user.referral_code
            }
        }), 200
        
    except Exception as e:
        api_logger.error(f"Login error: {e}")
        return jsonify({"ok": False, "error": "Login failed"}), 500


@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        user_id = get_jwt_identity()
        access_token = create_access_token(identity=user_id)
        
        return jsonify({
            "ok": True,
            "access_token": access_token
        }), 200
        
    except Exception as e:
        api_logger.error(f"Token refresh error: {e}")
        return jsonify({"ok": False, "error": "Refresh failed"}), 500


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    try:
        user_id = get_jwt_identity()
        db: Session = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            db.close()
            return jsonify({"ok": False, "error": "User not found"}), 404
        
        user_data = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "subscription_type": user.subscription_type,
            "is_verified": user.is_verified,
            "auto_trade_enabled": user.auto_trade_enabled,
            "referral_code": user.referral_code,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
        
        db.close()
        
        return jsonify({
            "ok": True,
            "user": user_data
        }), 200
        
    except Exception as e:
        api_logger.error(f"Get user error: {e}")
        return jsonify({"ok": False, "error": "Failed to get user"}), 500


@bp.route('/resend-verification', methods=['POST'])
@jwt_required()
def resend_verification():
    """Resend verification email (stub for now)"""
    try:
        user_id = get_jwt_identity()
        # TODO: Implement email sending
        api_logger.info(f"Verification email requested for user {user_id}")
        
        return jsonify({
            "ok": True,
            "message": "Verification email sent"
        }), 200
        
    except Exception as e:
        api_logger.error(f"Resend verification error: {e}")
        return jsonify({"ok": False, "error": "Failed to send verification"}), 500


@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Password reset request - sends email with reset token"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({"ok": False, "error": "Email required"}), 400
        
        db: Session = SessionLocal()
        user = db.query(User).filter(User.email == email).first()
        
        # Always return success (don't reveal if email exists for security)
        if user:
            # Generate reset token
            reset_token = generate_reset_token(user.id)
            
            # Send reset email
            send_password_reset_email(email, reset_token, user.id)
            api_logger.info(f"Password reset email sent to {email}")
        else:
            api_logger.info(f"Password reset requested for non-existent email: {email}")
        
        db.close()
        
        return jsonify({
            "ok": True,
            "message": "If this email exists, a password reset link has been sent"
        }), 200
        
    except Exception as e:
        api_logger.error(f"Forgot password error: {e}")
        return jsonify({"ok": False, "error": "Failed to process request"}), 500


@bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    try:
        data = request.get_json()
        token = data.get('token', '').strip()
        new_password = data.get('password', '')
        
        if not token or not new_password:
            return jsonify({"ok": False, "error": "Token and new password required"}), 400
        
        # Verify token
        user_id = verify_token(token, "password_reset")
        if not user_id:
            return jsonify({"ok": False, "error": "Invalid or expired reset token"}), 400
        
        # Update password
        db: Session = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            db.close()
            return jsonify({"ok": False, "error": "User not found"}), 404
        
        user.password_hash = hash_password(new_password)
        db.commit()
        db.close()
        
        # Invalidate token
        invalidate_token(token)
        
        api_logger.info(f"Password reset successful for user {user_id}")
        
        return jsonify({
            "ok": True,
            "message": "Password reset successful"
        }), 200
        
    except Exception as e:
        api_logger.error(f"Reset password error: {e}")
        return jsonify({"ok": False, "error": "Failed to reset password"}), 500
