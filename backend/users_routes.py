"""
User Management Routes
Handles user settings, exchanges, preferences, risk management
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session

from db import SessionLocal
from models import User, UserSettings, ExchangeAccount
from utils.security import encrypt_api_key, decrypt_api_key
from utils.logger import api_logger

bp = Blueprint('users', __name__)


@bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Get user details"""
    try:
        current_user = get_jwt_identity()
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
        current_user = get_jwt_identity()
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
        current_user = get_jwt_identity()
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
        current_user = get_jwt_identity()
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
        current_user = get_jwt_identity()
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


@bp.route('/<int:user_id>/preferences', methods=['PUT'])
@jwt_required()
def update_preferences(user_id):
    """Update user preferences"""
    try:
        current_user = get_jwt_identity()
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
        current_user = get_jwt_identity()
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
        current_user = get_jwt_identity()
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
