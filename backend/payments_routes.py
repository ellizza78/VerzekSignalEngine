"""
Payments Routes
Handles USDT TRC-20 payment processing for subscription upgrades
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from db import SessionLocal
from models import Payment, User
from utils.logger import api_logger
from utils.telegram_notifications import notify_payment_received

bp = Blueprint('payments', __name__)

# Admin USDT TRC-20 wallet (configure in env)
ADMIN_WALLET = "TYourAdminWalletAddressHere"


@bp.route('/create', methods=['POST'])
@jwt_required()
def create_payment():
    """Create a payment request for subscription upgrade"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        plan_type = data.get('plan_type', '').upper()
        if plan_type not in ['VIP', 'PREMIUM']:
            return jsonify({"ok": False, "error": "Invalid plan type"}), 400
        
        # Pricing
        pricing = {
            'VIP': 50.0,  # $50 USDT
            'PREMIUM': 100.0  # $100 USDT
        }
        amount = pricing.get(plan_type)
        
        db: Session = SessionLocal()
        
        # Create payment record
        payment_id = f"VZK-{uuid.uuid4().hex[:12].upper()}"
        payment = Payment(
            user_id=user_id,
            payment_id=payment_id,
            amount_usdt=amount,
            plan_type=plan_type,
            status="PENDING",
            admin_wallet=ADMIN_WALLET
        )
        
        db.add(payment)
        db.commit()
        
        db.close()
        
        api_logger.info(f"Payment created: {payment_id} for user {user_id}")
        
        return jsonify({
            "ok": True,
            "payment_id": payment_id,
            "amount_usdt": amount,
            "admin_wallet": ADMIN_WALLET,
            "plan_type": plan_type,
            "instructions": "Send exact amount to admin wallet and submit transaction hash"
        }), 201
        
    except Exception as e:
        api_logger.error(f"Create payment error: {e}")
        return jsonify({"ok": False, "error": "Failed to create payment"}), 500


@bp.route('/verify', methods=['POST'])
@jwt_required()
def verify_payment():
    """Verify payment and upgrade subscription"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        payment_id = data.get('payment_id')
        tx_hash = data.get('tx_hash')
        
        if not payment_id or not tx_hash:
            return jsonify({"ok": False, "error": "payment_id and tx_hash required"}), 400
        
        db: Session = SessionLocal()
        
        payment = db.query(Payment).filter(
            Payment.payment_id == payment_id,
            Payment.user_id == user_id
        ).first()
        
        if not payment:
            db.close()
            return jsonify({"ok": False, "error": "Payment not found"}), 404
        
        if payment.status == "VERIFIED":
            db.close()
            return jsonify({"ok": False, "error": "Payment already verified"}), 400
        
        # TODO: Verify transaction on blockchain (TronScan API)
        # For now, mark as pending verification
        payment.tx_hash = tx_hash
        payment.status = "PENDING_VERIFICATION"
        
        db.commit()
        
        # Notify Telegram subscribers group about payment received
        try:
            notify_payment_received(
                amount_usdt=payment.amount_usdt,
                plan_type=payment.plan_type,
                tx_hash=tx_hash
            )
        except Exception as e:
            api_logger.warning(f"Telegram notification failed: {e}")
        
        db.close()
        
        api_logger.info(f"Payment {payment_id} submitted for verification by user {user_id}")
        
        return jsonify({
            "ok": True,
            "message": "Payment submitted for verification. Admin will verify within 24 hours."
        }), 200
        
    except Exception as e:
        api_logger.error(f"Verify payment error: {e}")
        return jsonify({"ok": False, "error": "Failed to verify payment"}), 500


@bp.route('/<payment_id>', methods=['GET'])
@jwt_required()
def get_payment_status(payment_id):
    """Get payment status"""
    try:
        user_id = get_jwt_identity()
        
        db: Session = SessionLocal()
        payment = db.query(Payment).filter(
            Payment.payment_id == payment_id,
            Payment.user_id == user_id
        ).first()
        
        if not payment:
            db.close()
            return jsonify({"ok": False, "error": "Payment not found"}), 404
        
        payment_data = {
            "payment_id": payment.payment_id,
            "amount_usdt": payment.amount_usdt,
            "plan_type": payment.plan_type,
            "status": payment.status,
            "tx_hash": payment.tx_hash,
            "created_at": payment.created_at.isoformat() if payment.created_at else None,
            "verified_at": payment.verified_at.isoformat() if payment.verified_at else None
        }
        
        db.close()
        
        return jsonify({"ok": True, "payment": payment_data}), 200
        
    except Exception as e:
        api_logger.error(f"Get payment status error: {e}")
        return jsonify({"ok": False, "error": "Failed to get payment"}), 500


@bp.route('/my-payments', methods=['GET'])
@jwt_required()
def get_my_payments():
    """Get all payments for current user"""
    try:
        user_id = get_jwt_identity()
        
        db: Session = SessionLocal()
        payments = db.query(Payment).filter(Payment.user_id == user_id).order_by(Payment.created_at.desc()).all()
        
        payment_list = [{
            "payment_id": p.payment_id,
            "amount_usdt": p.amount_usdt,
            "plan_type": p.plan_type,
            "status": p.status,
            "created_at": p.created_at.isoformat() if p.created_at else None
        } for p in payments]
        
        db.close()
        
        return jsonify({"ok": True, "payments": payment_list}), 200
        
    except Exception as e:
        api_logger.error(f"Get my payments error: {e}")
        return jsonify({"ok": False, "error": "Failed to get payments"}), 500


@bp.route('/admin/verify/<payment_id>', methods=['POST'])
@jwt_required()
def admin_verify_payment(payment_id):
    """
    DEPRECATED: Use /api/admin/payments/approve/<payment_id> instead
    This endpoint is kept for backward compatibility but requires admin access
    """
    try:
        import os
        user_id = get_jwt_identity()
        
        # CRITICAL: Admin authentication check
        db: Session = SessionLocal()
        admin_user = db.query(User).filter(User.id == user_id).first()
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@verzekinnovative.com')
        
        if not admin_user or admin_user.email != admin_email:
            db.close()
            api_logger.warning(f"Unauthorized admin verify attempt by user {user_id}")
            return jsonify({"ok": False, "error": "Admin access required"}), 403
        
        payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
        
        if not payment:
            db.close()
            return jsonify({"ok": False, "error": "Payment not found"}), 404
        
        # Update payment status
        payment.status = "VERIFIED"
        payment.verified_at = datetime.utcnow()
        
        # Upgrade user subscription
        user = db.query(User).filter(User.id == payment.user_id).first()
        if user:
            user.subscription_type = payment.plan_type
        
        db.commit()
        db.close()
        
        api_logger.info(f"Payment {payment_id} verified by admin, user upgraded to {payment.plan_type}")
        
        return jsonify({"ok": True, "message": "Payment verified and user upgraded"}), 200
        
    except Exception as e:
        api_logger.error(f"Admin verify payment error: {e}")
        return jsonify({"ok": False, "error": "Failed to verify payment"}), 500
