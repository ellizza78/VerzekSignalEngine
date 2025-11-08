"""
Positions Routes
Handles viewing and managing user positions
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from datetime import datetime

from db import SessionLocal
from models import Position, PositionTarget, User
from utils.logger import api_logger

bp = Blueprint('positions', __name__)


@bp.route('', methods=['GET'])
@jwt_required()
def get_my_positions():
    """Get positions for current user"""
    try:
        user_id = get_jwt_identity()
        status = request.args.get('status')  # OPEN, CLOSED, etc.
        limit = int(request.args.get('limit', 100))
        
        db: Session = SessionLocal()
        query = db.query(Position).filter(Position.user_id == user_id).order_by(Position.created_at.desc())
        
        if status:
            query = query.filter(Position.status == status.upper())
        
        positions = query.limit(limit).all()
        
        position_list = []
        for pos in positions:
            targets = db.query(PositionTarget).filter(PositionTarget.position_id == pos.id).all()
            
            position_list.append({
                "id": pos.id,
                "signal_id": pos.signal_id,
                "symbol": pos.symbol,
                "side": pos.side,
                "leverage": pos.leverage,
                "qty": pos.qty,
                "entry_price": pos.entry_price,
                "remaining_qty": pos.remaining_qty,
                "status": pos.status,
                "pnl_usdt": pos.pnl_usdt,
                "pnl_pct": pos.pnl_pct,
                "created_at": pos.created_at.isoformat() if pos.created_at else None,
                "targets": [{
                    "index": t.target_index,
                    "price": t.price,
                    "qty": t.qty,
                    "hit": t.hit,
                    "hit_at": t.hit_at.isoformat() if t.hit_at else None
                } for t in targets]
            })
        
        db.close()
        
        return jsonify({"ok": True, "positions": position_list}), 200
        
    except Exception as e:
        api_logger.error(f"Get positions error: {e}")
        return jsonify({"ok": False, "error": "Failed to get positions"}), 500


@bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_positions(user_id):
    """Get positions for a specific user (admin or self)"""
    try:
        current_user = get_jwt_identity()
        
        # Allow if admin or same user
        if current_user != user_id:
            # TODO: Add admin check
            return jsonify({"ok": False, "error": "Unauthorized"}), 403
        
        db: Session = SessionLocal()
        positions = db.query(Position).filter(Position.user_id == user_id).order_by(Position.created_at.desc()).all()
        
        position_list = []
        for pos in positions:
            targets = db.query(PositionTarget).filter(PositionTarget.position_id == pos.id).all()
            
            position_list.append({
                "id": pos.id,
                "signal_id": pos.signal_id,
                "symbol": pos.symbol,
                "side": pos.side,
                "leverage": pos.leverage,
                "qty": pos.qty,
                "entry_price": pos.entry_price,
                "remaining_qty": pos.remaining_qty,
                "status": pos.status,
                "pnl_usdt": pos.pnl_usdt,
                "pnl_pct": pos.pnl_pct,
                "created_at": pos.created_at.isoformat() if pos.created_at else None,
                "targets": [{
                    "index": t.target_index,
                    "price": t.price,
                    "qty": t.qty,
                    "hit": t.hit
                } for t in targets]
            })
        
        db.close()
        
        return jsonify({"ok": True, "positions": position_list}), 200
        
    except Exception as e:
        api_logger.error(f"Get user positions error: {e}")
        return jsonify({"ok": False, "error": "Failed to get positions"}), 500


@bp.route('/close', methods=['POST'])
@jwt_required()
def close_position():
    """Manually close a position"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        position_id = data.get('position_id')
        
        if not position_id:
            return jsonify({"ok": False, "error": "position_id required"}), 400
        
        db: Session = SessionLocal()
        position = db.query(Position).filter(
            Position.id == position_id,
            Position.user_id == user_id
        ).first()
        
        if not position:
            db.close()
            return jsonify({"ok": False, "error": "Position not found"}), 404
        
        if position.status not in ["OPEN", "PARTIAL"]:
            db.close()
            return jsonify({"ok": False, "error": "Position already closed"}), 400
        
        # Close position
        position.status = "CLOSED"
        position.closed_at = datetime.utcnow()
        position.remaining_qty = 0
        
        # Log event
        from models import TradeLog
        trade_log = TradeLog(
            user_id=user_id,
            position_id=position_id,
            signal_id=position.signal_id,
            type="CLOSE",
            message="Position manually closed",
            meta={"manual": True}
        )
        db.add(trade_log)
        
        db.commit()
        db.close()
        
        api_logger.info(f"Position #{position_id} manually closed by user {user_id}")
        
        return jsonify({"ok": True, "message": "Position closed"}), 200
        
    except Exception as e:
        api_logger.error(f"Close position error: {e}")
        return jsonify({"ok": False, "error": "Failed to close position"}), 500
