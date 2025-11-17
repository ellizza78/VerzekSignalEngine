"""
House Signals Routes
Handles signals from VerzekSignalEngine (internal API with token auth)
"""
import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from functools import wraps

from db import SessionLocal
from models import HouseSignal, HouseSignalPosition, User
from utils.logger import api_logger
from utils.notifications import send_signal_notification, get_subscription_user_tokens
from broadcast import broadcast_signal

bp = Blueprint('house_signals', __name__)

HOUSE_ENGINE_TOKEN = os.getenv("HOUSE_ENGINE_TOKEN")


def require_internal_token(f):
    """Decorator to validate internal API token from VerzekSignalEngine"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('X-INTERNAL-TOKEN')
        
        if not token:
            api_logger.warning("House signal rejected: Missing X-INTERNAL-TOKEN header")
            return jsonify({"ok": False, "error": "Unauthorized"}), 401
        
        if not HOUSE_ENGINE_TOKEN:
            api_logger.error("HOUSE_ENGINE_TOKEN not configured in environment")
            return jsonify({"ok": False, "error": "Server configuration error"}), 500
        
        if token != HOUSE_ENGINE_TOKEN:
            api_logger.warning(f"House signal rejected: Invalid token")
            return jsonify({"ok": False, "error": "Forbidden"}), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


@bp.route('/ingest', methods=['POST'])
@require_internal_token
def ingest_signal():
    """
    Receive signal from VerzekSignalEngine
    
    Payload example:
    {
      "source": "SCALPER",
      "symbol": "BTCUSDT",
      "side": "LONG",
      "entry": 50000.0,
      "stop_loss": 49750.0,
      "take_profits": [50200, 50500],
      "timeframe": "M5",
      "confidence": 78,
      "timestamp": "2025-11-15T15:22:00Z",
      "metadata": {}
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['source', 'symbol', 'side', 'entry', 'stop_loss', 'take_profits', 'timeframe', 'confidence']
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({"ok": False, "error": f"Missing fields: {missing}"}), 400
        
        # Validate data types
        if not isinstance(data['take_profits'], list) or len(data['take_profits']) == 0:
            return jsonify({"ok": False, "error": "take_profits must be a non-empty list"}), 400
        
        db: Session = SessionLocal()
        
        # Create house signal
        signal = HouseSignal(
            source=data['source'].upper(),
            symbol=data['symbol'].upper(),
            side=data['side'].upper(),
            entry=float(data['entry']),
            stop_loss=float(data['stop_loss']),
            take_profits=data['take_profits'],
            timeframe=data['timeframe'].upper(),
            confidence=int(data['confidence']),
            version=data.get('version', 'SE.v1.0'),
            meta_data=data.get('metadata', {}),
            status='ACTIVE'
        )
        
        db.add(signal)
        db.commit()
        db.refresh(signal)
        
        signal_id = signal.id
        
        api_logger.info(
            f"House signal ingested: {signal.source} | {signal.symbol} | {signal.side} | "
            f"Entry: {signal.entry} | SL: {signal.stop_loss} | TPs: {signal.take_profits} | "
            f"Confidence: {signal.confidence}% | ID: {signal_id}"
        )
        
        # Create paper trading position (auto-opens)
        position = HouseSignalPosition(
            signal_id=signal_id,
            status='OPEN',
            entry_price=signal.entry,
            opened_at=datetime.utcnow()
        )
        
        db.add(position)
        db.commit()
        
        api_logger.info(f"House position opened for signal {signal_id}")
        
        # Broadcast to Telegram VIP/TRIAL groups
        try:
            telegram_signal_data = {
                "symbol": signal.symbol,
                "side": signal.side,
                "entry": signal.entry,
                "tp": signal.take_profits,
                "sl": signal.stop_loss,
                "leverage": data.get('leverage', 1),
                "trade_type": "FUTURES",
                "duration": signal.timeframe,
                "confidence": signal.confidence
            }
            broadcast_signal(telegram_signal_data, target="both")
            api_logger.info(f"Telegram broadcast sent for house signal {signal_id}")
        except Exception as e:
            api_logger.error(f"Failed to broadcast to Telegram for signal {signal_id}: {e}")
        
        # Broadcast to mobile app subscribers (VIP + PREMIUM only)
        try:
            user_tokens = get_subscription_user_tokens(db, ['VIP', 'PREMIUM'])
            
            if user_tokens:
                all_tokens = [token for tokens in user_tokens.values() for token in tokens]
                
                notification_data = {
                    "id": signal_id,
                    "symbol": signal.symbol,
                    "side": signal.side,
                    "entry": signal.entry,
                    "source": signal.source,
                    "confidence": signal.confidence
                }
                
                send_signal_notification(all_tokens, notification_data)
                api_logger.info(f"Push notifications sent for house signal {signal_id}")
        except Exception as e:
            api_logger.error(f"Failed to send push notifications for house signal {signal_id}: {e}")
        
        db.close()
        
        return jsonify({
            "ok": True,
            "signal_id": signal_id,
            "message": "Signal ingested and position opened"
        }), 200
        
    except Exception as e:
        api_logger.error(f"House signal ingestion error: {e}")
        return jsonify({"ok": False, "error": "Failed to process signal"}), 500


@bp.route('/live', methods=['GET'])
@jwt_required()
def get_live_signals():
    """
    Get recent active house signals for mobile app
    VIP and PREMIUM users only
    """
    try:
        user_id = get_jwt_identity()
        
        db: Session = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            db.close()
            return jsonify({"ok": False, "error": "User not found"}), 404
        
        # Check subscription tier
        if user.subscription_type not in ['VIP', 'PREMIUM']:
            db.close()
            return jsonify({
                "ok": False,
                "error": "Upgrade to VIP or PREMIUM to access house signals"
            }), 403
        
        # Get active signals from last 24 hours
        cutoff = datetime.utcnow() - timedelta(hours=24)
        signals = db.query(HouseSignal).filter(
            HouseSignal.status == 'ACTIVE',
            HouseSignal.created_at >= cutoff
        ).order_by(desc(HouseSignal.created_at)).limit(50).all()
        
        signal_list = [{
            "id": sig.id,
            "source": sig.source,
            "symbol": sig.symbol,
            "side": sig.side,
            "entry": sig.entry,
            "stop_loss": sig.stop_loss,
            "take_profits": sig.take_profits,
            "timeframe": sig.timeframe,
            "confidence": sig.confidence,
            "version": sig.version,
            "metadata": sig.meta_data,
            "created_at": sig.created_at.isoformat() if sig.created_at else None
        } for sig in signals]
        
        db.close()
        
        return jsonify({"ok": True, "signals": signal_list, "count": len(signal_list)}), 200
        
    except Exception as e:
        api_logger.error(f"Get live house signals error: {e}")
        return jsonify({"ok": False, "error": "Failed to get signals"}), 500


@bp.route('/admin/signals', methods=['GET'])
@jwt_required()
def admin_get_signals():
    """
    Get house signals (admin endpoint)
    Query params: status, source, limit, offset
    """
    try:
        user_id = get_jwt_identity()
        
        db: Session = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.subscription_type != 'PREMIUM':
            db.close()
            return jsonify({"ok": False, "error": "Admin access required"}), 403
        
        # Query params
        status = request.args.get('status', 'ACTIVE').upper()
        source = request.args.get('source', '').upper()
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        query = db.query(HouseSignal)
        
        if status:
            query = query.filter(HouseSignal.status == status)
        if source:
            query = query.filter(HouseSignal.source == source)
        
        total = query.count()
        signals = query.order_by(desc(HouseSignal.created_at)).limit(limit).offset(offset).all()
        
        signal_list = [{
            "id": sig.id,
            "source": sig.source,
            "symbol": sig.symbol,
            "side": sig.side,
            "entry": sig.entry,
            "stop_loss": sig.stop_loss,
            "take_profits": sig.take_profits,
            "timeframe": sig.timeframe,
            "confidence": sig.confidence,
            "metadata": sig.meta_data,
            "status": sig.status,
            "created_at": sig.created_at.isoformat() if sig.created_at else None,
            "closed_at": sig.closed_at.isoformat() if sig.closed_at else None
        } for sig in signals]
        
        db.close()
        
        return jsonify({
            "ok": True,
            "signals": signal_list,
            "total": total,
            "limit": limit,
            "offset": offset
        }), 200
        
    except Exception as e:
        api_logger.error(f"Admin get house signals error: {e}")
        return jsonify({"ok": False, "error": "Failed to get signals"}), 500


@bp.route('/admin/positions', methods=['GET'])
@jwt_required()
def admin_get_positions():
    """Get house signal positions with performance stats"""
    try:
        user_id = get_jwt_identity()
        
        db: Session = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.subscription_type != 'PREMIUM':
            db.close()
            return jsonify({"ok": False, "error": "Admin access required"}), 403
        
        status = request.args.get('status', 'OPEN').upper()
        limit = int(request.args.get('limit', 100))
        
        query = db.query(HouseSignalPosition).join(HouseSignal)
        
        if status:
            query = query.filter(HouseSignalPosition.status == status)
        
        positions = query.order_by(desc(HouseSignalPosition.updated_at)).limit(limit).all()
        
        position_list = [{
            "id": pos.id,
            "signal_id": pos.signal_id,
            "symbol": pos.signal.symbol,
            "side": pos.signal.side,
            "source": pos.signal.source,
            "status": pos.status,
            "entry_price": pos.entry_price,
            "exit_price": pos.exit_price,
            "tps_hit": pos.tps_hit,
            "mfe": pos.mfe,
            "mae": pos.mae,
            "pnl_pct": pos.pnl_pct,
            "opened_at": pos.opened_at.isoformat() if pos.opened_at else None,
            "closed_at": pos.closed_at.isoformat() if pos.closed_at else None
        } for pos in positions]
        
        db.close()
        
        return jsonify({"ok": True, "positions": position_list, "count": len(position_list)}), 200
        
    except Exception as e:
        api_logger.error(f"Admin get house positions error: {e}")
        return jsonify({"ok": False, "error": "Failed to get positions"}), 500


@bp.route('/admin/performance', methods=['GET'])
@jwt_required()
def admin_get_performance():
    """Get daily performance statistics for house signals"""
    try:
        user_id = get_jwt_identity()
        
        db: Session = SessionLocal()
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user or user.subscription_type != 'PREMIUM':
            db.close()
            return jsonify({"ok": False, "error": "Admin access required"}), 403
        
        # Get stats for each bot source
        sources = ['SCALPER', 'TREND', 'QFL', 'AI_ML']
        performance = {}
        
        for source in sources:
            # Total signals
            total_signals = db.query(HouseSignal).filter(HouseSignal.source == source).count()
            
            # Closed positions
            closed_positions = db.query(HouseSignalPosition).join(HouseSignal).filter(
                HouseSignal.source == source,
                HouseSignalPosition.status.in_(['TP_HIT', 'SL_HIT', 'CLOSED'])
            ).all()
            
            if closed_positions:
                wins = len([p for p in closed_positions if p.pnl_pct > 0])
                losses = len([p for p in closed_positions if p.pnl_pct <= 0])
                win_rate = (wins / len(closed_positions)) * 100 if len(closed_positions) > 0 else 0
                avg_pnl = sum(p.pnl_pct for p in closed_positions) / len(closed_positions)
            else:
                wins = 0
                losses = 0
                win_rate = 0
                avg_pnl = 0
            
            performance[source] = {
                "total_signals": total_signals,
                "total_closed": len(closed_positions),
                "wins": wins,
                "losses": losses,
                "win_rate": round(win_rate, 2),
                "avg_pnl_pct": round(avg_pnl, 2)
            }
        
        # Overall stats
        overall_closed = db.query(HouseSignalPosition).filter(
            HouseSignalPosition.status.in_(['TP_HIT', 'SL_HIT', 'CLOSED'])
        ).all()
        
        if overall_closed:
            overall_wins = len([p for p in overall_closed if p.pnl_pct > 0])
            overall_win_rate = (overall_wins / len(overall_closed)) * 100
            overall_avg_pnl = sum(p.pnl_pct for p in overall_closed) / len(overall_closed)
        else:
            overall_win_rate = 0
            overall_avg_pnl = 0
        
        db.close()
        
        return jsonify({
            "ok": True,
            "performance_by_source": performance,
            "overall": {
                "total_closed": len(overall_closed),
                "win_rate": round(overall_win_rate, 2),
                "avg_pnl_pct": round(overall_avg_pnl, 2)
            }
        }), 200
        
    except Exception as e:
        api_logger.error(f"Admin get house performance error: {e}")
        return jsonify({"ok": False, "error": "Failed to get performance"}), 500
