"""
Admin Routes
Handles: referral tracking, user management, system stats, payment/subscription management
Admin authentication via ADMIN_EMAIL in environment variables
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import os

from db import SessionLocal
from models import User, UserSettings, Position, Signal, TradeLog, Payment
from utils.logger import api_logger

bp = Blueprint('admin', __name__)

# Admin email from environment
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@verzekinnovative.com')

# Security check: Warn if using default admin email
if ADMIN_EMAIL == 'admin@verzekinnovative.com':
    import warnings
    warnings.warn(
        "⚠️  SECURITY WARNING: Using default ADMIN_EMAIL. "
        "Set ADMIN_EMAIL environment variable in production!",
        RuntimeWarning
    )
    api_logger.warning("ADMIN_EMAIL not configured - using default (INSECURE for production)")


def is_admin(user_id: int, db: Session) -> bool:
    """Check if user is admin"""
    user = db.query(User).filter(User.id == user_id).first()
    return user and user.email == ADMIN_EMAIL


@bp.route('/referrals', methods=['GET'])
@jwt_required()
def get_referrals():
    """
    Get referral tracking data for all users
    Returns: List of users with their referral codes and who they referred
    """
    try:
        user_id = get_jwt_identity()
        db: Session = SessionLocal()
        
        # Check admin access
        if not is_admin(user_id, db):
            db.close()
            return jsonify({"ok": False, "error": "Admin access required"}), 403
        
        # Get all users with referral data
        users = db.query(User).all()
        
        referral_data = []
        for user in users:
            # Count how many users this person referred
            referred_count = db.query(User).filter(User.referred_by == user.id).count()
            
            # Get list of referred users
            referred_users = db.query(User).filter(User.referred_by == user.id).all()
            
            referred_list = [{
                "id": ref.id,
                "email": ref.email,
                "full_name": ref.full_name,
                "subscription_type": ref.subscription_type,
                "joined_date": ref.created_at.isoformat() if ref.created_at else None,
                "is_verified": ref.is_verified
            } for ref in referred_users]
            
            referral_data.append({
                "user_id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "referral_code": user.referral_code,
                "subscription_type": user.subscription_type,
                "joined_date": user.created_at.isoformat() if user.created_at else None,
                "is_verified": user.is_verified,
                "referred_count": referred_count,
                "referred_users": referred_list,
                "referred_by_user_id": user.referred_by
            })
        
        db.close()
        
        return jsonify({
            "ok": True,
            "total_users": len(users),
            "referrals": referral_data
        }), 200
        
    except Exception as e:
        api_logger.error(f"Get referrals error: {e}")
        return jsonify({"ok": False, "error": "Failed to fetch referrals"}), 500


@bp.route('/referrals/payouts', methods=['GET'])
@jwt_required()
def calculate_referral_payouts():
    """
    Calculate referral bonuses owed to users
    Query params:
    - bonus_per_vip: Amount per VIP referral (default: 10 USDT)
    - bonus_per_premium: Amount per PREMIUM referral (default: 20 USDT)
    """
    try:
        user_id = get_jwt_identity()
        db: Session = SessionLocal()
        
        # Check admin access
        if not is_admin(user_id, db):
            db.close()
            return jsonify({"ok": False, "error": "Admin access required"}), 403
        
        # Get bonus amounts from query params
        bonus_vip = float(request.args.get('bonus_per_vip', 10))
        bonus_premium = float(request.args.get('bonus_per_premium', 20))
        
        # Get all users who have referred someone
        referrers = db.query(User).filter(User.id.in_(
            db.query(User.referred_by).filter(User.referred_by.isnot(None))
        )).all()
        
        payout_data = []
        total_owed = 0
        
        for referrer in referrers:
            # Count referrals by subscription type
            vip_count = db.query(User).filter(
                User.referred_by == referrer.id,
                User.subscription_type == 'VIP',
                User.is_verified == True
            ).count()
            
            premium_count = db.query(User).filter(
                User.referred_by == referrer.id,
                User.subscription_type == 'PREMIUM',
                User.is_verified == True
            ).count()
            
            # Calculate bonus
            bonus_amount = (vip_count * bonus_vip) + (premium_count * bonus_premium)
            total_owed += bonus_amount
            
            if bonus_amount > 0:
                payout_data.append({
                    "user_id": referrer.id,
                    "email": referrer.email,
                    "full_name": referrer.full_name,
                    "referral_code": referrer.referral_code,
                    "vip_referrals": vip_count,
                    "premium_referrals": premium_count,
                    "bonus_owed_usdt": bonus_amount
                })
        
        db.close()
        
        return jsonify({
            "ok": True,
            "total_payouts_owed_usdt": total_owed,
            "bonus_per_vip": bonus_vip,
            "bonus_per_premium": bonus_premium,
            "payouts": sorted(payout_data, key=lambda x: x['bonus_owed_usdt'], reverse=True)
        }), 200
        
    except Exception as e:
        api_logger.error(f"Calculate payouts error: {e}")
        return jsonify({"ok": False, "error": "Failed to calculate payouts"}), 500


@bp.route('/stats', methods=['GET'])
@jwt_required()
def get_system_stats():
    """
    Get overall system statistics
    """
    try:
        user_id = get_jwt_identity()
        db: Session = SessionLocal()
        
        # Check admin access
        if not is_admin(user_id, db):
            db.close()
            return jsonify({"ok": False, "error": "Admin access required"}), 403
        
        # User stats
        total_users = db.query(User).count()
        verified_users = db.query(User).filter(User.is_verified == True).count()
        trial_users = db.query(User).filter(User.subscription_type == 'TRIAL').count()
        vip_users = db.query(User).filter(User.subscription_type == 'VIP').count()
        premium_users = db.query(User).filter(User.subscription_type == 'PREMIUM').count()
        
        # Recent signups (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_signups = db.query(User).filter(User.created_at >= week_ago).count()
        
        # Trading stats
        total_positions = db.query(Position).count()
        open_positions = db.query(Position).filter(Position.status == 'OPEN').count()
        total_signals = db.query(Signal).count()
        
        # Revenue estimate (VIP: $50, PREMIUM: $120)
        monthly_revenue = (vip_users * 50) + (premium_users * 120)
        
        db.close()
        
        return jsonify({
            "ok": True,
            "users": {
                "total": total_users,
                "verified": verified_users,
                "trial": trial_users,
                "vip": vip_users,
                "premium": premium_users,
                "recent_signups_7d": recent_signups
            },
            "trading": {
                "total_positions": total_positions,
                "open_positions": open_positions,
                "total_signals": total_signals
            },
            "revenue": {
                "estimated_monthly_usd": monthly_revenue,
                "vip_subscribers": vip_users,
                "premium_subscribers": premium_users
            }
        }), 200
        
    except Exception as e:
        api_logger.error(f"Get stats error: {e}")
        return jsonify({"ok": False, "error": "Failed to fetch stats"}), 500


@bp.route('/payments/pending', methods=['GET'])
@jwt_required()
def get_pending_payments():
    """
    Get all pending payment verifications
    Sorted by creation date (newest first)
    """
    try:
        user_id = get_jwt_identity()
        db: Session = SessionLocal()
        
        # Check admin access
        if not is_admin(user_id, db):
            db.close()
            return jsonify({"ok": False, "error": "Admin access required"}), 403
        
        # Get pending payments
        pending_payments = db.query(Payment).filter(
            Payment.status.in_(['PENDING', 'PENDING_VERIFICATION'])
        ).order_by(Payment.created_at.desc()).all()
        
        payment_list = []
        for payment in pending_payments:
            # Get user info
            user = db.query(User).filter(User.id == payment.user_id).first()
            
            payment_list.append({
                "payment_id": payment.payment_id,
                "user_id": payment.user_id,
                "user_email": user.email if user else "Unknown",
                "user_name": user.full_name if user else "Unknown",
                "amount_usdt": payment.amount_usdt,
                "plan_type": payment.plan_type,
                "status": payment.status,
                "tx_hash": payment.tx_hash,
                "admin_wallet": payment.admin_wallet,
                "created_at": payment.created_at.isoformat() if payment.created_at else None,
                "waiting_hours": round((datetime.utcnow() - payment.created_at).total_seconds() / 3600, 1) if payment.created_at else None
            })
        
        db.close()
        
        return jsonify({
            "ok": True,
            "total_pending": len(payment_list),
            "payments": payment_list
        }), 200
        
    except Exception as e:
        api_logger.error(f"Get pending payments error: {e}")
        return jsonify({"ok": False, "error": "Failed to fetch pending payments"}), 500


@bp.route('/payments/all', methods=['GET'])
@jwt_required()
def get_all_payments():
    """
    Get all payments with optional filters
    Query params: status, plan_type, limit
    """
    try:
        user_id = get_jwt_identity()
        db: Session = SessionLocal()
        
        # Check admin access
        if not is_admin(user_id, db):
            db.close()
            return jsonify({"ok": False, "error": "Admin access required"}), 403
        
        # Build query
        query = db.query(Payment)
        
        # Apply filters
        status_filter = request.args.get('status')
        if status_filter:
            query = query.filter(Payment.status == status_filter.upper())
        
        plan_filter = request.args.get('plan_type')
        if plan_filter:
            query = query.filter(Payment.plan_type == plan_filter.upper())
        
        # Limit results
        limit = int(request.args.get('limit', 100))
        
        # Get payments
        payments = query.order_by(Payment.created_at.desc()).limit(limit).all()
        
        payment_list = []
        for payment in payments:
            # Get user info
            user = db.query(User).filter(User.id == payment.user_id).first()
            
            payment_list.append({
                "payment_id": payment.payment_id,
                "user_id": payment.user_id,
                "user_email": user.email if user else "Unknown",
                "user_name": user.full_name if user else "Unknown",
                "amount_usdt": payment.amount_usdt,
                "plan_type": payment.plan_type,
                "status": payment.status,
                "tx_hash": payment.tx_hash,
                "created_at": payment.created_at.isoformat() if payment.created_at else None,
                "verified_at": payment.verified_at.isoformat() if payment.verified_at else None
            })
        
        db.close()
        
        return jsonify({
            "ok": True,
            "total_results": len(payment_list),
            "filters_applied": {
                "status": status_filter,
                "plan_type": plan_filter,
                "limit": limit
            },
            "payments": payment_list
        }), 200
        
    except Exception as e:
        api_logger.error(f"Get all payments error: {e}")
        return jsonify({"ok": False, "error": "Failed to fetch payments"}), 500


@bp.route('/payments/approve/<payment_id>', methods=['POST'])
@jwt_required()
def approve_payment(payment_id):
    """
    Approve a payment and upgrade user subscription
    """
    try:
        user_id = get_jwt_identity()
        db: Session = SessionLocal()
        
        # Check admin access
        if not is_admin(user_id, db):
            db.close()
            return jsonify({"ok": False, "error": "Admin access required"}), 403
        
        # Get payment
        payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
        
        if not payment:
            db.close()
            return jsonify({"ok": False, "error": "Payment not found"}), 404
        
        if payment.status == "VERIFIED":
            db.close()
            return jsonify({"ok": False, "error": "Payment already verified"}), 400
        
        # Update payment
        payment.status = "VERIFIED"
        payment.verified_at = datetime.utcnow()
        
        # Upgrade user subscription
        user = db.query(User).filter(User.id == payment.user_id).first()
        if user:
            old_plan = user.subscription_type
            user.subscription_type = payment.plan_type
            
            api_logger.info(f"Admin {user_id} approved payment {payment_id}: User {user.id} upgraded from {old_plan} to {payment.plan_type}")
        
        db.commit()
        db.close()
        
        return jsonify({
            "ok": True,
            "message": "Payment approved and user upgraded",
            "payment_id": payment_id,
            "user_id": payment.user_id,
            "new_plan": payment.plan_type
        }), 200
        
    except Exception as e:
        api_logger.error(f"Approve payment error: {e}")
        return jsonify({"ok": False, "error": "Failed to approve payment"}), 500


@bp.route('/payments/reject/<payment_id>', methods=['POST'])
@jwt_required()
def reject_payment(payment_id):
    """
    Reject a payment (mark as FAILED)
    """
    try:
        user_id = get_jwt_identity()
        db: Session = SessionLocal()
        
        # Check admin access
        if not is_admin(user_id, db):
            db.close()
            return jsonify({"ok": False, "error": "Admin access required"}), 403
        
        data = request.get_json() or {}
        reason = data.get('reason', 'Payment verification failed')
        
        # Get payment
        payment = db.query(Payment).filter(Payment.payment_id == payment_id).first()
        
        if not payment:
            db.close()
            return jsonify({"ok": False, "error": "Payment not found"}), 404
        
        if payment.status == "VERIFIED":
            db.close()
            return jsonify({"ok": False, "error": "Cannot reject verified payment"}), 400
        
        # Update payment
        payment.status = "FAILED"
        
        api_logger.info(f"Admin {user_id} rejected payment {payment_id}: {reason}")
        
        db.commit()
        db.close()
        
        return jsonify({
            "ok": True,
            "message": "Payment rejected",
            "payment_id": payment_id,
            "reason": reason
        }), 200
        
    except Exception as e:
        api_logger.error(f"Reject payment error: {e}")
        return jsonify({"ok": False, "error": "Failed to reject payment"}), 500


@bp.route('/subscriptions/overview', methods=['GET'])
@jwt_required()
def get_subscriptions_overview():
    """
    Get subscription overview with breakdown by plan type
    """
    try:
        user_id = get_jwt_identity()
        db: Session = SessionLocal()
        
        # Check admin access
        if not is_admin(user_id, db):
            db.close()
            return jsonify({"ok": False, "error": "Admin access required"}), 403
        
        # Count by subscription type
        trial_count = db.query(User).filter(User.subscription_type == 'TRIAL').count()
        vip_count = db.query(User).filter(User.subscription_type == 'VIP').count()
        premium_count = db.query(User).filter(User.subscription_type == 'PREMIUM').count()
        
        # Payment stats
        total_payments = db.query(Payment).count()
        verified_payments = db.query(Payment).filter(Payment.status == 'VERIFIED').count()
        pending_payments = db.query(Payment).filter(Payment.status.in_(['PENDING', 'PENDING_VERIFICATION'])).count()
        
        # Revenue calculation
        verified_vip = db.query(func.count(Payment.id)).filter(
            Payment.plan_type == 'VIP',
            Payment.status == 'VERIFIED'
        ).scalar()
        
        verified_premium = db.query(func.count(Payment.id)).filter(
            Payment.plan_type == 'PREMIUM',
            Payment.status == 'VERIFIED'
        ).scalar()
        
        total_revenue = (verified_vip * 50) + (verified_premium * 100)
        
        db.close()
        
        return jsonify({
            "ok": True,
            "subscriptions": {
                "trial": trial_count,
                "vip": vip_count,
                "premium": premium_count,
                "total": trial_count + vip_count + premium_count
            },
            "payments": {
                "total": total_payments,
                "verified": verified_payments,
                "pending": pending_payments,
                "failed": total_payments - verified_payments - pending_payments
            },
            "revenue": {
                "total_usdt": total_revenue,
                "vip_payments": verified_vip,
                "premium_payments": verified_premium
            }
        }), 200
        
    except Exception as e:
        api_logger.error(f"Get subscriptions overview error: {e}")
        return jsonify({"ok": False, "error": "Failed to fetch overview"}), 500
