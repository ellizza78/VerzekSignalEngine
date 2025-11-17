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
from utils.telegram_notifications import notify_referral_success

bp = Blueprint('auth', __name__)


@bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"ok": False, "error": "Invalid request payload"}), 400
        
        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''
        full_name = (data.get('full_name') or data.get('username') or '').strip()
        referral_code_input = (data.get('referral_code') or '').strip().upper()
        
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
        referrer_user = None
        if referral_code_input:
            referrer = db.query(User).filter(User.referral_code == referral_code_input).first()
            if referrer:
                referrer_id = referrer.id
                referrer_user = referrer
                api_logger.info(f"New user referred by user {referrer_id} with code {referral_code_input}")
        
        # Create user (unverified)
        user = User(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            is_verified=False,  # Require email verification
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
        
        # Generate verification token and send email
        try:
            verification_token = generate_verification_token(user.id, db)
            send_verification_email(email, verification_token, user.id)
            api_logger.info(f"Verification email sent to {email}")
        except Exception as e:
            api_logger.error(f"Verification email failed for {email}: {e}")
        
        # Notify Telegram group if user was referred
        if referrer_user:
            try:
                notify_referral_success(
                    referrer_name=referrer_user.full_name or "User",
                    new_user_name=user.full_name or "New User",
                    new_user_plan=user.subscription_type
                )
            except Exception as e:
                api_logger.warning(f"Telegram referral notification failed: {e}")
        
        # Generate tokens (identity must be string for Flask-JWT-Extended)
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
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
                "referral_code": user.referral_code,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
        }), 201
        
    except Exception as e:
        api_logger.error(f"Registration error: {e}")
        return jsonify({"ok": False, "error": "Registration failed"}), 500


@bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"ok": False, "error": "Invalid request payload"}), 400
        
        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''
        
        if not email or not password:
            return jsonify({"ok": False, "error": "Email and password required"}), 400
        
        db: Session = SessionLocal()
        user = db.query(User).filter(User.email == email).first()
        
        if not user or not verify_password(password, user.password_hash):
            db.close()
            return jsonify({"ok": False, "error": "Invalid credentials"}), 401
        
        # Check if email is verified
        if not user.is_verified:
            db.close()
            return jsonify({
                "ok": False,
                "error": "Email not verified. Please check your inbox for the verification link.",
                "needs_verification": True
            }), 403
        
        # Generate tokens (identity must be string for Flask-JWT-Extended)
        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        
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
                "referral_code": user.referral_code,
                "created_at": user.created_at.isoformat() if user.created_at else None
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
        # user_id is already a string from JWT, but ensure it stays string
        access_token = create_access_token(identity=str(user_id))
        
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
        user_id = get_jwt_identity()  # Returns string
        db: Session = SessionLocal()
        user = db.query(User).filter(User.id == int(user_id)).first()
        
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


@bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    """Verify email address with token (GET for email links, POST for API calls)"""
    try:
        # GET request from email link
        if request.method == 'GET':
            token = request.args.get('token', '').strip()
            user_id_param = request.args.get('user_id', '').strip()
        # POST request from API
        else:
            data = request.get_json(silent=True)
            if not isinstance(data, dict):
                return jsonify({"ok": False, "error": "Invalid request payload"}), 400
            token = (data.get('token') or '').strip()
            user_id_param = None
        
        if not token:
            return jsonify({"ok": False, "error": "Verification token required"}), 400
        
        db: Session = SessionLocal()
        
        # Verify token
        user_id = verify_token(token, "email_verification", db)
        if not user_id:
            db.close()
            return jsonify({"ok": False, "error": "Invalid or expired verification token"}), 400
        
        # Mark user as verified
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            db.close()
            return jsonify({"ok": False, "error": "User not found"}), 404
        
        user.is_verified = True
        db.commit()
        
        # Invalidate token
        invalidate_token(token, db)
        db.close()
        
        api_logger.info(f"Email verified for user {user_id}")
        
        # If GET request from email, redirect to app
        if request.method == 'GET':
            from flask import redirect
            return redirect(f"verzek-app://verify-email-success?user_id={user_id}&email={user.email}"), 302
        
        # If POST request from API, return JSON
        return jsonify({
            "ok": True,
            "message": "Email verified successfully! You can now log in."
        }), 200
        
    except Exception as e:
        api_logger.error(f"Email verification error: {e}")
        return jsonify({"ok": False, "error": "Verification failed"}), 500


@bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Resend verification email (public endpoint - works with or without auth)"""
    try:
        db: Session = SessionLocal()
        user = None
        
        # Try to get user from JWT token (if authenticated)
        try:
            user_id = get_jwt_identity()
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
        except:
            pass
        
        # If not authenticated, get email from request body
        if not user:
            data = request.get_json(silent=True)
            if not isinstance(data, dict):
                db.close()
                return jsonify({"ok": False, "error": "Invalid request payload"}), 400
            
            email = (data.get('email') or '').strip().lower()
            
            if not email:
                db.close()
                return jsonify({"ok": False, "error": "Email required"}), 400
            
            user = db.query(User).filter(User.email == email).first()
        
        # Always return success (don't reveal if email exists for security)
        if user:
            if user.is_verified:
                api_logger.info(f"Verification resend attempted for already verified email: {user.email}")
                db.close()
                return jsonify({
                    "ok": True,
                    "message": "If this email is unverified, a verification link has been sent"
                }), 200
            
            # Generate new verification token and send email
            try:
                verification_token = generate_verification_token(user.id, db)
                send_verification_email(user.email, verification_token, user.id)
                api_logger.info(f"Verification email resent to {user.email}")
            except Exception as e:
                api_logger.error(f"Failed to resend verification email: {e}")
                db.close()
                return jsonify({"ok": False, "error": "Failed to send email"}), 500
        else:
            api_logger.info(f"Verification resend attempted for non-existent email")
        
        db.close()
        
        return jsonify({
            "ok": True,
            "message": "If this email is unverified, a verification link has been sent"
        }), 200
        
    except Exception as e:
        api_logger.error(f"Resend verification error: {e}")
        return jsonify({"ok": False, "error": "Failed to send verification"}), 500


@bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Password reset request - sends email with reset token"""
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"ok": False, "error": "Invalid request payload"}), 400
        
        email = (data.get('email') or '').strip().lower()
        
        if not email:
            return jsonify({"ok": False, "error": "Email required"}), 400
        
        db: Session = SessionLocal()
        user = db.query(User).filter(User.email == email).first()
        
        # Always return success (don't reveal if email exists for security)
        if user:
            # Generate reset token (now with db session)
            reset_token = generate_reset_token(user.id, db)
            
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


@bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    """Reset password with token (GET redirects to app, POST processes reset)"""
    try:
        # GET request from email link - redirect to app
        if request.method == 'GET':
            token = request.args.get('token', '').strip()
            user_id_param = request.args.get('user_id', '').strip()
            
            if not token:
                return jsonify({"ok": False, "error": "Token required"}), 400
            
            # Redirect to app with token
            from flask import redirect
            return redirect(f"verzek-app://reset-password?token={token}&user_id={user_id_param}"), 302
        
        # POST request from API - process password reset
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"ok": False, "error": "Invalid request payload"}), 400
        
        token = (data.get('token') or '').strip()
        new_password = data.get('new_password') or data.get('password') or ''
        
        if not token or not new_password:
            return jsonify({"ok": False, "error": "Token and new password required"}), 400
        
        # Verify token (now with db session)
        db: Session = SessionLocal()
        user_id = verify_token(token, "password_reset", db)
        if not user_id:
            db.close()
            return jsonify({"ok": False, "error": "Invalid or expired reset token"}), 400
        
        # Update password
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            db.close()
            return jsonify({"ok": False, "error": "User not found"}), 404
        
        user.password_hash = hash_password(new_password)
        db.commit()
        
        # Invalidate token
        invalidate_token(token, db)
        db.close()
        
        api_logger.info(f"Password reset successful for user {user_id}")
        
        return jsonify({
            "ok": True,
            "message": "Password reset successful"
        }), 200
        
    except Exception as e:
        api_logger.error(f"Reset password error: {e}")
        return jsonify({"ok": False, "error": "Failed to reset password"}), 500
