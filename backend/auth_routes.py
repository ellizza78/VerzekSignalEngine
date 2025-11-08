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

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        full_name = data.get('full_name', data.get('username', ''))
        
        if not email or not password:
            return jsonify({"ok": False, "error": "Email and password required"}), 400
        
        db: Session = SessionLocal()
        
        # Check if user exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            db.close()
            return jsonify({"ok": False, "error": "Email already registered"}), 400
        
        # Create user
        user = User(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            is_verified=False,
            subscription_type="TRIAL"
        )
        db.add(user)
        db.flush()
        
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
        
        # Generate tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        api_logger.info(f"New user registered: {email}")
        
        db.close()
        
        return jsonify({
            "ok": True,
            "message": "Registration successful",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "subscription_type": user.subscription_type,
                "is_verified": user.is_verified
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
                "auto_trade_enabled": user.auto_trade_enabled
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
    """Password reset request (stub for now)"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        # TODO: Implement password reset email
        api_logger.info(f"Password reset requested for {email}")
        
        return jsonify({
            "ok": True,
            "message": "Password reset email sent"
        }), 200
        
    except Exception as e:
        api_logger.error(f"Forgot password error: {e}")
        return jsonify({"ok": False, "error": "Failed to process request"}), 500
