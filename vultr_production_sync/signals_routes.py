"""
Signals Routes
Handles signal creation, listing, and lifecycle callbacks (TP, SL, Cancel)
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from datetime import datetime

from db import SessionLocal
from models import Signal, Position, TradeLog
from broadcast import broadcast_signal, broadcast_target_hit, broadcast_stop_loss, broadcast_signal_cancelled
from utils.logger import api_logger
from utils.rate_limiter import rate_limiter
from utils.notifications import send_signal_notification, get_subscription_user_tokens

bp = Blueprint('signals', __name__)


@bp.route('', methods=['GET'])
@jwt_required()
def get_signals():
    """List all signals (with optional filtering)"""
    try:
        status = request.args.get('status')  # NEW, OPENED, CLOSED, etc.
        limit = int(request.args.get('limit', 50))
        
        db: Session = SessionLocal()
        query = db.query(Signal).order_by(Signal.created_at.desc())
        
        if status:
            query = query.filter(Signal.status == status.upper())
        
        signals = query.limit(limit).all()
        
        signal_list = [{
            "id": sig.id,
            "symbol": sig.symbol,
            "side": sig.side,
            "entry": sig.entry,
            "tp": sig.tp,
            "sl": sig.sl,
            "leverage": sig.leverage,
            "confidence": sig.confidence,
            "trade_type": sig.trade_type,
            "duration": sig.duration,
            "status": sig.status,
            "created_at": sig.created_at.isoformat() if sig.created_at else None
        } for sig in signals]
        
        db.close()
        
        return jsonify({"ok": True, "signals": signal_list}), 200
        
    except Exception as e:
        api_logger.error(f"Get signals error: {e}")
        return jsonify({"ok": False, "error": "Failed to get signals"}), 500


@bp.route('', methods=['POST'])
@jwt_required()
def create_signal():
    """Create a new signal and broadcast it"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['symbol', 'side', 'entry', 'tp', 'sl']
        for field in required:
            if field not in data:
                return jsonify({"ok": False, "error": f"Missing field: {field}"}), 400
        
        # Rate limiting check
        symbol = data['symbol'].upper()
        allowed, reason = rate_limiter.check_signal_rate(symbol, limit_per_minute=1)
        if not allowed:
            api_logger.warning(f"Rate limit exceeded for {symbol}: {reason}")
            return jsonify({"ok": False, "error": reason}), 429
        
        db: Session = SessionLocal()
        
        # Create signal
        signal = Signal(
            symbol=data['symbol'].upper(),
            side=data['side'].upper(),
            entry=float(data['entry']),
            tp=data['tp'],  # List of target prices
            sl=float(data['sl']),
            leverage=int(data.get('leverage', 1)),
            confidence=int(data.get('confidence', 0)),
            trade_type=data.get('trade_type', 'FUTURES'),
            duration=data.get('duration', 'SHORT'),
            status='NEW',
            meta=data.get('meta', {})
        )
        
        db.add(signal)
        db.commit()
        db.refresh(signal)
        
        signal_id = signal.id
        
        # Broadcast to Telegram
        signal_dict = {
            "symbol": signal.symbol,
            "side": signal.side,
            "entry": signal.entry,
            "tp": signal.tp,
            "sl": signal.sl,
            "leverage": signal.leverage,
            "confidence": signal.confidence,
            "trade_type": signal.trade_type,
            "duration": signal.duration
        }
        broadcast_signal(signal_dict, target="both")
        
        # Send push notifications to VIP + PREMIUM users
        try:
            user_tokens = get_subscription_user_tokens(db, ['VIP', 'PREMIUM'])
            
            if user_tokens:
                all_tokens = [token for tokens in user_tokens.values() for token in tokens]
                
                signal_notification_data = {
                    "id": signal.id,
                    "symbol": signal.symbol,
                    "direction": signal.side,
                    "entry_price": signal.entry,
                }
                
                result = send_signal_notification(all_tokens, signal_notification_data)
                api_logger.info(f"📱 Sent signal notifications to {len(all_tokens)} devices")
        except Exception as e:
            api_logger.error(f"Signal notification failed: {e}")
        
        db.close()
        
        api_logger.info(f"Signal created and broadcasted: {signal.symbol} #{signal_id}")
        
        return jsonify({
            "ok": True,
            "message": "Signal created and broadcasted",
            "signal_id": signal_id
        }), 201
        
    except Exception as e:
        api_logger.error(f"Create signal error: {e}")
        return jsonify({"ok": False, "error": "Failed to create signal"}), 500


@bp.route('/target-reached', methods=['POST'])
@jwt_required()
def target_reached():
    """Callback when a target is hit"""
    try:
        data = request.get_json()
        signal_id = data.get('signal_id')
        target_index = data.get('target_index')
        
        if not signal_id or target_index is None:
            return jsonify({"ok": False, "error": "signal_id and target_index required"}), 400
        
        db: Session = SessionLocal()
        signal = db.query(Signal).filter(Signal.id == signal_id).first()
        
        if not signal:
            db.close()
            return jsonify({"ok": False, "error": "Signal not found"}), 404
        
        # Update positions: close partial qty at this target
        positions = db.query(Position).filter(
            Position.signal_id == signal_id,
            Position.status == "OPEN"
        ).all()
        
        for position in positions:
            # Mark target as hit in PositionTarget
            from models import PositionTarget
            target = db.query(PositionTarget).filter(
                PositionTarget.position_id == position.id,
                PositionTarget.target_index == target_index,
                PositionTarget.hit == False
            ).first()
            
            if target:
                target.hit = True
                target.hit_at = datetime.utcnow()
                position.remaining_qty -= target.qty
                
                if position.remaining_qty <= 0:
                    position.status = "CLOSED"
                    position.closed_at = datetime.utcnow()
                else:
                    position.status = "PARTIAL"
                
                # Log trade event
                trade_log = TradeLog(
                    user_id=position.user_id,
                    position_id=position.id,
                    signal_id=signal_id,
                    type="TP_HIT",
                    message=f"Target {target_index} hit at {target.price}",
                    meta={"target_index": target_index, "price": target.price, "qty": target.qty}
                )
                db.add(trade_log)
        
        # Update signal status
        if signal.status == "NEW":
            signal.status = "PARTIAL"
        
        # Check if all targets hit
        all_targets_hit = all(t.hit for p in positions for t in p.targets)
        if all_targets_hit:
            signal.status = "CLOSED"
        
        db.commit()
        
        # Broadcast event
        tp_price = signal.tp[target_index - 1] if target_index <= len(signal.tp) else 0
        broadcast_target_hit(signal_id, signal.symbol, target_index, tp_price, target="both")
        
        db.close()
        
        api_logger.info(f"Target {target_index} hit for signal #{signal_id}")
        
        return jsonify({"ok": True, "message": f"Target {target_index} processed"}), 200
        
    except Exception as e:
        api_logger.error(f"Target reached error: {e}")
        return jsonify({"ok": False, "error": "Failed to process target"}), 500


@bp.route('/stop-loss', methods=['POST'])
@jwt_required()
def stop_loss_hit():
    """Callback when stop loss is triggered"""
    try:
        data = request.get_json()
        signal_id = data.get('signal_id')
        
        if not signal_id:
            return jsonify({"ok": False, "error": "signal_id required"}), 400
        
        db: Session = SessionLocal()
        signal = db.query(Signal).filter(Signal.id == signal_id).first()
        
        if not signal:
            db.close()
            return jsonify({"ok": False, "error": "Signal not found"}), 404
        
        # Close all positions for this signal
        positions = db.query(Position).filter(
            Position.signal_id == signal_id,
            Position.status.in_(["OPEN", "PARTIAL"])
        ).all()
        
        for position in positions:
            position.status = "STOPPED"
            position.closed_at = datetime.utcnow()
            position.remaining_qty = 0
            
            # Log trade event
            trade_log = TradeLog(
                user_id=position.user_id,
                position_id=position.id,
                signal_id=signal_id,
                type="SL_HIT",
                message=f"Stop loss triggered at {signal.sl}",
                meta={"sl_price": signal.sl}
            )
            db.add(trade_log)
        
        signal.status = "STOPPED"
        db.commit()
        
        # Broadcast event
        broadcast_stop_loss(signal_id, signal.symbol, signal.sl, target="both")
        
        db.close()
        
        api_logger.info(f"Stop loss triggered for signal #{signal_id}")
        
        return jsonify({"ok": True, "message": "Stop loss processed"}), 200
        
    except Exception as e:
        api_logger.error(f"Stop loss error: {e}")
        return jsonify({"ok": False, "error": "Failed to process stop loss"}), 500


@bp.route('/cancel', methods=['POST'])
@jwt_required()
def cancel_signal():
    """Cancel a signal"""
    try:
        data = request.get_json()
        signal_id = data.get('signal_id')
        reason = data.get('reason', 'Manual cancellation')
        
        if not signal_id:
            return jsonify({"ok": False, "error": "signal_id required"}), 400
        
        db: Session = SessionLocal()
        signal = db.query(Signal).filter(Signal.id == signal_id).first()
        
        if not signal:
            db.close()
            return jsonify({"ok": False, "error": "Signal not found"}), 404
        
        # Close all positions
        positions = db.query(Position).filter(
            Position.signal_id == signal_id,
            Position.status.in_(["OPEN", "PARTIAL"])
        ).all()
        
        for position in positions:
            position.status = "CANCELLED"
            position.closed_at = datetime.utcnow()
            position.remaining_qty = 0
            
            # Log trade event
            trade_log = TradeLog(
                user_id=position.user_id,
                position_id=position.id,
                signal_id=signal_id,
                type="CANCELLED",
                message=f"Signal cancelled: {reason}",
                meta={"reason": reason}
            )
            db.add(trade_log)
        
        signal.status = "CANCELLED"
        db.commit()
        
        # Broadcast event
        broadcast_signal_cancelled(signal_id, signal.symbol, reason, target="both")
        
        db.close()
        
        api_logger.info(f"Signal #{signal_id} cancelled: {reason}")
        
        return jsonify({"ok": True, "message": "Signal cancelled"}), 200
        
    except Exception as e:
        api_logger.error(f"Cancel signal error: {e}")
        return jsonify({"ok": False, "error": "Failed to cancel signal"}), 500
