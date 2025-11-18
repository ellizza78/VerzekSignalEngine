"""
User Management Routes
Handles user settings, exchanges, preferences, risk management
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from datetime import datetime

from db import SessionLocal
from models import User, UserSettings, ExchangeAccount, DeviceToken
from utils.security import encrypt_api_key, decrypt_api_key
from utils.logger import api_logger

bp = Blueprint('users', __name__)


@bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get user details"""
    try:
        current_user = int(get_jwt_identity())  # Convert string to int
        if current_user != user_id:
            return jsonify({"ok": False, "error": "Unauthorized"}), 403
        
        db: Session = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            db.close()
            return jsonify({"ok": False, "error": "User not found"}), 404
        
        settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        
        user_data = {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "subscription_type": user.subscription_type,
            "is_verified": user.is_verified,
            "auto_trade_enabled": user.auto_trade_enabled,
            "settings": {
                "capital_usdt": settings.capital_usdt if settings else 0,
                "per_trade_usdt": settings.per_trade_usdt if settings else 5.0,
                "leverage": settings.leverage if settings else 1,
                "max_concurrent_trades": settings.max_concurrent_trades if settings else 5,
                "dca_enabled": settings.dca_enabled if settings else False,
                "auto_reversal_enabled": settings.auto_reversal_enabled if settings else True,
                "reversal_window_minutes": settings.reversal_window_minutes if settings else 15,
                "preferences": settings.preferences if settings else {}
            } if settings else {}
        }
        
        db.close()
        
        return jsonify({"ok": True, "user": user_data}), 200
        
    except Exception as e:
        api_logger.error(f"Get user error: {e}")
        return jsonify({"ok": False, "error": "Failed to get user"}), 500


@bp.route('/<int:user_id>/general', methods=['PUT'])
@jwt_required()
def update_general_settings(user_id):
    """Update general user settings"""
    try:
        current_user = int(get_jwt_identity())  # Convert string to int
        if current_user != user_id:
            return jsonify({"ok": False, "error": "Unauthorized"}), 403
        
        data = request.get_json()
        db: Session = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            db.close()
            return jsonify({"ok": False, "error": "User not found"}), 404
        
        # Update user fields
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'auto_trade_enabled' in data:
            user.auto_trade_enabled = bool(data['auto_trade_enabled'])
        
        db.commit()
        db.close()
        
        api_logger.info(f"User {user_id} updated general settings")
        
        return jsonify({"ok": True, "message": "Settings updated"}), 200
        
    except Exception as e:
        api_logger.error(f"Update general settings error: {e}")
        return jsonify({"ok": False, "error": "Failed to update settings"}), 500


@bp.route('/<int:user_id>/risk', methods=['PUT'])
@jwt_required()
def update_risk_settings(user_id):
    """Update risk management settings"""
    try:
        current_user = int(get_jwt_identity())  # Convert string to int
        if current_user != user_id:
            return jsonify({"ok": False, "error": "Unauthorized"}), 403
        
        data = request.get_json()
        db: Session = SessionLocal()
        settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        
        if not settings:
            db.close()
            return jsonify({"ok": False, "error": "Settings not found"}), 404
        
        # Update risk fields
        if 'capital_usdt' in data:
            settings.capital_usdt = float(data['capital_usdt'])
        if 'per_trade_usdt' in data:
            settings.per_trade_usdt = float(data['per_trade_usdt'])
        if 'leverage' in data:
            settings.leverage = min(max(int(data['leverage']), 1), 25)  # 1-25x
        if 'max_concurrent_trades' in data:
            settings.max_concurrent_trades = min(int(data['max_concurrent_trades']), 50)  # Max 50
        
        db.commit()
        db.close()
        
        api_logger.info(f"User {user_id} updated risk settings")
        
        return jsonify({"ok": True, "message": "Risk settings updated"}), 200
        
    except Exception as e:
        api_logger.error(f"Update risk settings error: {e}")
        return jsonify({"ok": False, "error": "Failed to update settings"}), 500


@bp.route('/<int:user_id>/strategy', methods=['PUT'])
@jwt_required()
def update_strategy_settings(user_id):
    """Update strategy settings"""
    try:
        current_user = int(get_jwt_identity())  # Convert string to int
        if current_user != user_id:
            return jsonify({"ok": False, "error": "Unauthorized"}), 403
        
        data = request.get_json()
        db: Session = SessionLocal()
        settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        
        if not settings:
            db.close()
            return jsonify({"ok": False, "error": "Settings not found"}), 404
        
        if 'strategy' in data:
            settings.strategy = data['strategy']
        
        db.commit()
        db.close()
        
        return jsonify({"ok": True, "message": "Strategy updated"}), 200
        
    except Exception as e:
        api_logger.error(f"Update strategy error: {e}")
        return jsonify({"ok": False, "error": "Failed to update strategy"}), 500


@bp.route('/<int:user_id>/dca', methods=['PUT'])
@jwt_required()
def update_dca_settings(user_id):
    """Update DCA settings"""
    try:
        current_user = int(get_jwt_identity())  # Convert string to int
        if current_user != user_id:
            return jsonify({"ok": False, "error": "Unauthorized"}), 403
        
        data = request.get_json()
        db: Session = SessionLocal()
        settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        
        if not settings:
            db.close()
            return jsonify({"ok": False, "error": "Settings not found"}), 404
        
        if 'dca_enabled' in data:
            settings.dca_enabled = bool(data['dca_enabled'])
        if 'dca_steps' in data:
            settings.dca_steps = int(data['dca_steps'])
        if 'dca_step_percent' in data:
            settings.dca_step_percent = float(data['dca_step_percent'])
        
        db.commit()
        db.close()
        
        return jsonify({"ok": True, "message": "DCA settings updated"}), 200
        
    except Exception as e:
        api_logger.error(f"Update DCA settings error: {e}")
        return jsonify({"ok": False, "error": "Failed to update DCA settings"}), 500


@bp.route('/<int:user_id>/reversal', methods=['PUT'])
@jwt_required()
def update_reversal_settings(user_id):
    """Update signal reversal settings"""
    try:
        current_user = int(get_jwt_identity())
        if current_user != user_id:
            return jsonify({"ok": False, "error": "Unauthorized"}), 403
        
        data = request.get_json()
        db: Session = SessionLocal()
        settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        
        if not settings:
            db.close()
            return jsonify({"ok": False, "error": "Settings not found"}), 404
        
        # Update reversal settings
        if 'auto_reversal_enabled' in data:
            settings.auto_reversal_enabled = bool(data['auto_reversal_enabled'])
        if 'reversal_window_minutes' in data:
            # Validate window (1-60 minutes)
            window = int(data['reversal_window_minutes'])
            settings.reversal_window_minutes = min(max(window, 1), 60)
        
        db.commit()
        db.close()
        
        api_logger.info(f"User {user_id} updated reversal settings: "
                       f"enabled={settings.auto_reversal_enabled}, "
                       f"window={settings.reversal_window_minutes}min")
        
        return jsonify({"ok": True, "message": "Reversal settings updated"}), 200
        
    except Exception as e:
        api_logger.error(f"Update reversal settings error: {e}")
        return jsonify({"ok": False, "error": "Failed to update reversal settings"}), 500


@bp.route('/<int:user_id>/preferences', methods=['PUT'])
@jwt_required()
def update_preferences(user_id):
    """Update user preferences"""
    try:
        current_user = int(get_jwt_identity())  # Convert string to int
        if current_user != user_id:
            return jsonify({"ok": False, "error": "Unauthorized"}), 403
        
        data = request.get_json()
        db: Session = SessionLocal()
        settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        
        if not settings:
            db.close()
            return jsonify({"ok": False, "error": "Settings not found"}), 404
        
        # Merge preferences
        current_prefs = settings.preferences or {}
        current_prefs.update(data.get('preferences', {}))
        settings.preferences = current_prefs
        
        db.commit()
        db.close()
        
        return jsonify({"ok": True, "message": "Preferences updated"}), 200
        
    except Exception as e:
        api_logger.error(f"Update preferences error: {e}")
        return jsonify({"ok": False, "error": "Failed to update preferences"}), 500


@bp.route('/<int:user_id>/exchanges', methods=['GET', 'POST', 'DELETE'])
@jwt_required()
def manage_exchanges(user_id):
    """Manage exchange accounts"""
    try:
        current_user = int(get_jwt_identity())  # Convert string to int
        if current_user != user_id:
            return jsonify({"ok": False, "error": "Unauthorized"}), 403
        
        db: Session = SessionLocal()
        
        if request.method == 'GET':
            # List exchanges
            exchanges = db.query(ExchangeAccount).filter(ExchangeAccount.user_id == user_id).all()
            exchange_list = [{
                "id": ex.id,
                "exchange": ex.exchange,
                "testnet": ex.testnet,
                "is_active": ex.is_active
            } for ex in exchanges]
            
            db.close()
            return jsonify({"ok": True, "exchanges": exchange_list}), 200
        
        elif request.method == 'POST':
            # Add exchange - check email verification first
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                db.close()
                return jsonify({"ok": False, "error": "User not found"}), 404
            
            if not user.is_verified:
                db.close()
                return jsonify({
                    "ok": False,
                    "error": "Email verification required",
                    "message": "Please verify your email address before connecting exchange accounts. Check your inbox for the verification link.",
                    "needs_verification": True
                }), 403
            
            data = request.get_json()
            exchange = ExchangeAccount(
                user_id=user_id,
                exchange=data.get('exchange'),
                api_key=encrypt_api_key(data.get('api_key', '')),
                api_secret=encrypt_api_key(data.get('api_secret', '')),
                testnet=data.get('testnet', True)
            )
            db.add(exchange)
            db.commit()
            db.close()
            
            api_logger.info(f"User {user_id} added exchange: {data.get('exchange')}")
            return jsonify({"ok": True, "message": "Exchange added"}), 201
        
        elif request.method == 'DELETE':
            # Delete exchange - check email verification first
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                db.close()
                return jsonify({"ok": False, "error": "User not found"}), 404
            
            if not user.is_verified:
                db.close()
                return jsonify({
                    "ok": False,
                    "error": "Email verification required",
                    "message": "Please verify your email address before managing exchange accounts.",
                    "needs_verification": True
                }), 403
            
            exchange_id = request.args.get('exchange_id')
            if exchange_id:
                db.query(ExchangeAccount).filter(
                    ExchangeAccount.id == exchange_id,
                    ExchangeAccount.user_id == user_id
                ).delete()
                db.commit()
            
            db.close()
            return jsonify({"ok": True, "message": "Exchange deleted"}), 200
        
    except Exception as e:
        api_logger.error(f"Manage exchanges error: {e}")
        return jsonify({"ok": False, "error": "Failed to manage exchanges"}), 500


@bp.route('/<int:user_id>/subscription', methods=['GET', 'PUT'])
@jwt_required()
def manage_subscription(user_id):
    """Get or update subscription"""
    try:
        current_user = int(get_jwt_identity())  # Convert string to int
        if current_user != user_id:
            return jsonify({"ok": False, "error": "Unauthorized"}), 403
        
        db: Session = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            db.close()
            return jsonify({"ok": False, "error": "User not found"}), 404
        
        if request.method == 'GET':
            subscription_data = {
                "plan": user.subscription_type,
                "auto_trade_enabled": user.auto_trade_enabled,
                "features": {
                    "signals": True,
                    "auto_trading": user.subscription_type in ["VIP", "PREMIUM"],
                    "advanced_analytics": user.subscription_type == "PREMIUM"
                }
            }
            db.close()
            return jsonify({"ok": True, "subscription": subscription_data}), 200
        
        elif request.method == 'PUT':
            # Update subscription (admin only or via payment verification)
            data = request.get_json()
            if 'subscription_type' in data:
                user.subscription_type = data['subscription_type']
                db.commit()
            
            db.close()
            return jsonify({"ok": True, "message": "Subscription updated"}), 200
        
    except Exception as e:
        api_logger.error(f"Manage subscription error: {e}")
        return jsonify({"ok": False, "error": "Failed to manage subscription"}), 500


@bp.route('/<int:user_id>/device-token', methods=['POST', 'DELETE'])
@jwt_required()
def manage_device_token(user_id):
    """Register or remove push notification device token"""
    try:
        current_user = int(get_jwt_identity())  # Convert string to int
        if current_user != user_id:
            return jsonify({"ok": False, "error": "Unauthorized"}), 403
        
        db: Session = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            db.close()
            return jsonify({"ok": False, "error": "User not found"}), 404
        
        if request.method == 'POST':
            data = request.get_json()
            push_token = data.get('push_token')
            device_name = data.get('device_name', 'Unknown Device')
            device_platform = data.get('device_platform', 'unknown')
            
            if not push_token:
                db.close()
                return jsonify({"ok": False, "error": "Push token required"}), 400
            
            if not push_token.startswith('ExponentPushToken['):
                db.close()
                return jsonify({"ok": False, "error": "Invalid Expo push token format"}), 400
            
            # Check if user has notifications enabled
            if not user.notifications_enabled:
                db.close()
                return jsonify({"ok": False, "error": "Notifications are disabled for this account"}), 403
            
            existing_token = db.query(DeviceToken).filter(
                DeviceToken.push_token == push_token
            ).first()
            
            if existing_token:
                if existing_token.user_id != user_id:
                    db.close()
                    return jsonify({"ok": False, "error": "Token belongs to another user"}), 409
                
                existing_token.last_active = datetime.utcnow()
                existing_token.is_active = True
                existing_token.device_name = device_name
                existing_token.device_platform = device_platform
                db.commit()
                
                api_logger.info(f"User {user_id} updated device token")
                db.close()
                return jsonify({"ok": True, "message": "Device token updated"}), 200
            
            new_device_token = DeviceToken(
                user_id=user_id,
                push_token=push_token,
                device_name=device_name,
                device_platform=device_platform
            )
            
            db.add(new_device_token)
            db.commit()
            db.close()
            
            api_logger.info(f"User {user_id} registered new device token")
            return jsonify({"ok": True, "message": "Device token registered"}), 201
        
        elif request.method == 'DELETE':
            data = request.get_json() or {}
            push_token = data.get('push_token')
            
            if not push_token:
                db.close()
                return jsonify({"ok": False, "error": "Push token required for deletion"}), 400
            
            device_token = db.query(DeviceToken).filter(
                DeviceToken.user_id == user_id,
                DeviceToken.push_token == push_token
            ).first()
            
            if device_token:
                device_token.is_active = False
                db.commit()
                api_logger.info(f"User {user_id} deactivated device token")
                db.close()
                return jsonify({"ok": True, "message": "Device token removed"}), 200
            else:
                db.close()
                return jsonify({"ok": False, "error": "Device token not found"}), 404
            
    except Exception as e:
        api_logger.error(f"Device token error: {e}")
        return jsonify({"ok": False, "error": "Failed to manage device token"}), 500


@bp.route('/<int:user_id>/notifications/settings', methods=['GET', 'PUT'])
@jwt_required()
def notification_settings(user_id):
    """Get or update notification settings"""
    try:
        current_user = int(get_jwt_identity())  # Convert string to int
        if current_user != user_id:
            return jsonify({"ok": False, "error": "Unauthorized"}), 403
        
        db: Session = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            db.close()
            return jsonify({"ok": False, "error": "User not found"}), 404
        
        if request.method == 'GET':
            settings_data = {
                "notifications_enabled": user.notifications_enabled,
                "subscription_type": user.subscription_type,
                "features": {
                    "signal_notifications": user.subscription_type in ["VIP", "PREMIUM"],
                    "trade_notifications": user.subscription_type == "PREMIUM"
                }
            }
            db.close()
            return jsonify({"ok": True, "settings": settings_data}), 200
        
        elif request.method == 'PUT':
            data = request.get_json()
            
            if 'notifications_enabled' in data:
                user.notifications_enabled = bool(data['notifications_enabled'])
                db.commit()
                api_logger.info(f"User {user_id} updated notification settings: enabled={user.notifications_enabled}")
            
            db.close()
            return jsonify({"ok": True, "message": "Notification settings updated"}), 200
            
    except Exception as e:
        api_logger.error(f"Notification settings error: {e}")
        return jsonify({"ok": False, "error": "Failed to manage notification settings"}), 500
