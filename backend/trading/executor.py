"""
Trade Executor - Auto-Trading Worker Logic
Processes signals, opens positions, manages TP/SL for users with auto_trade_enabled=True
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from models import User, UserSettings, Signal, Position, PositionTarget, TradeLog
from trading.paper_client import paper_client
from utils.logger import worker_logger
from utils.notifications import (
    send_trade_start_notification,
    send_trade_end_notification,
    get_user_push_tokens
)


def run_once(db: Session):
    """
    Single execution cycle of the worker
    1. Process new signals for auto-trade users
    2. Monitor existing positions for TP/SL hits
    """
    try:
        # Step 1: Open positions for new signals
        process_new_signals(db)
        
        # Step 2: Monitor positions for target hits
        monitor_positions(db)
        
    except Exception as e:
        worker_logger.error(f"Worker execution error: {e}")


def process_new_signals(db: Session):
    """
    Find signals with status='NEW' and create positions for eligible users
    """
    try:
        # Get all NEW signals
        new_signals = db.query(Signal).filter(Signal.status == 'NEW').all()
        
        if not new_signals:
            return
        
        # Get all users with auto_trade enabled
        auto_trade_users = db.query(User).filter(User.auto_trade_enabled == True).all()
        
        for signal in new_signals:
            for user in auto_trade_users:
                # Check if user can take this trade
                if not can_user_trade(db, user.id):
                    continue
                
                # Open position
                open_position_for_signal(db, user.id, signal)
            
            # Mark signal as OPENED after processing
            signal.status = 'OPENED'
        
        db.commit()
        
    except Exception as e:
        worker_logger.error(f"Process new signals error: {e}")
        db.rollback()


def can_user_trade(db: Session, user_id: int) -> bool:
    """
    Check if user can take a new trade
    - Must have auto_trade_enabled
    - Must not exceed max_concurrent_trades (50 max)
    """
    try:
        settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        if not settings:
            return False
        
        # Count active positions
        active_count = db.query(Position).filter(
            Position.user_id == user_id,
            Position.status.in_(['OPEN', 'PARTIAL'])
        ).count()
        
        max_concurrent = min(settings.max_concurrent_trades, 50)  # Cap at 50
        
        return active_count < max_concurrent
        
    except Exception as e:
        worker_logger.error(f"Can user trade check error: {e}")
        return False


def open_position_for_signal(db: Session, user_id: int, signal: Signal):
    """
    Open a position for a user based on a signal
    """
    try:
        settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        if not settings:
            return
        
        # Calculate quantity based on per_trade_usdt and leverage
        leverage = settings.leverage
        per_trade = settings.per_trade_usdt
        qty = (per_trade * leverage) / signal.entry
        
        # Open position via paper client
        order = paper_client.open_position(
            user_id=user_id,
            symbol=signal.symbol,
            side=signal.side,
            qty=qty,
            entry_price=signal.entry,
            leverage=leverage
        )
        
        if not order.get('success'):
            worker_logger.warning(f"Failed to open position for user {user_id}: {order.get('error')}")
            return
        
        # Create position record
        position = Position(
            user_id=user_id,
            signal_id=signal.id,
            symbol=signal.symbol,
            side=signal.side,
            leverage=leverage,
            qty=qty,
            entry_price=order['entry_price'],
            remaining_qty=qty,
            status='OPEN'
        )
        db.add(position)
        db.flush()
        
        # Create TP targets (split qty across targets)
        tp_prices = signal.tp if isinstance(signal.tp, list) else [signal.tp]
        qty_per_target = qty / len(tp_prices)
        
        for i, tp_price in enumerate(tp_prices, 1):
            target = PositionTarget(
                position_id=position.id,
                target_index=i,
                price=tp_price,
                qty=qty_per_target,
                hit=False
            )
            db.add(target)
        
        # Log event
        trade_log = TradeLog(
            user_id=user_id,
            position_id=position.id,
            signal_id=signal.id,
            type='OPEN',
            message=f"Opened {signal.side} position: {qty:.4f} {signal.symbol} @ {order['entry_price']}",
            meta=order
        )
        db.add(trade_log)
        
        db.commit()
        
        worker_logger.info(f"Position opened for user {user_id}, signal #{signal.id}")
        
        # Send trade start notification (PREMIUM users only)
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if user and user.subscription_type == 'PREMIUM' and user.notifications_enabled:
                tokens = get_user_push_tokens(db, user_id)
                
                if tokens:
                    position_data = {
                        "id": position.id,
                        "symbol": position.symbol,
                        "direction": position.side,
                        "entry_price": position.entry_price,
                    }
                    send_trade_start_notification(tokens, position_data)
                    worker_logger.info(f"📱 Sent trade start notification to user {user_id}")
        except Exception as notif_error:
            worker_logger.error(f"Trade start notification failed: {notif_error}")
        
    except Exception as e:
        worker_logger.error(f"Open position error: {e}")
        db.rollback()


def monitor_positions(db: Session):
    """
    Monitor all open positions and check for TP/SL hits
    """
    try:
        # Get all open/partial positions
        open_positions = db.query(Position).filter(
            Position.status.in_(['OPEN', 'PARTIAL'])
        ).all()
        
        for position in open_positions:
            check_position_targets(db, position)
        
        db.commit()
        
    except Exception as e:
        worker_logger.error(f"Monitor positions error: {e}")
        db.rollback()


def check_position_targets(db: Session, position: Position):
    """
    Check if position has hit any targets or stop loss
    """
    try:
        signal = db.query(Signal).filter(Signal.id == position.signal_id).first()
        if not signal:
            return
        
        # Get TP targets and SL
        tp_prices = signal.tp if isinstance(signal.tp, list) else [signal.tp]
        sl_price = signal.sl
        
        # Check current price
        result = paper_client.check_price_targets(
            symbol=position.symbol,
            targets=tp_prices,
            sl=sl_price,
            entry=position.entry_price,
            side=position.side
        )
        
        current_price = result.get('current_price')
        if not current_price:
            return
        
        # Handle stop loss hit
        if result.get('hit_sl'):
            close_position_sl(db, position, sl_price)
            return
        
        # Handle target hit
        target_index = result.get('hit_target_index')
        if target_index:
            close_position_target(db, position, target_index, current_price)
        
    except Exception as e:
        worker_logger.error(f"Check position targets error: {e}")


def close_position_target(db: Session, position: Position, target_index: int, price: float):
    """
    Close partial position when target is hit
    """
    try:
        # Find the target
        target = db.query(PositionTarget).filter(
            PositionTarget.position_id == position.id,
            PositionTarget.target_index == target_index,
            PositionTarget.hit == False
        ).first()
        
        if not target:
            return
        
        # Close partial qty
        close_result = paper_client.close_position(
            user_id=position.user_id,
            symbol=position.symbol,
            side=position.side,
            qty=target.qty,
            entry_price=position.entry_price,
            exit_price=price,
            leverage=position.leverage
        )
        
        if close_result.get('success'):
            # Mark target as hit
            target.hit = True
            target.hit_at = datetime.utcnow()
            
            # Update position
            position.remaining_qty -= target.qty
            position.pnl_usdt += close_result.get('pnl_usdt', 0)
            position.pnl_pct = close_result.get('pnl_pct', 0)
            
            if position.remaining_qty <= 0:
                position.status = 'CLOSED'
                position.closed_at = datetime.utcnow()
            else:
                position.status = 'PARTIAL'
            
            # Log event
            trade_log = TradeLog(
                user_id=position.user_id,
                position_id=position.id,
                signal_id=position.signal_id,
                type='TP_HIT',
                message=f"Target {target_index} hit at {price}",
                meta=close_result
            )
            db.add(trade_log)
            
            worker_logger.info(f"Target {target_index} hit for position #{position.id}, PnL: {close_result.get('pnl_usdt')}")
            
            # Send trade end notification when position fully closes (PREMIUM users only)
            if position.status == 'CLOSED':
                try:
                    user = db.query(User).filter(User.id == position.user_id).first()
                    
                    if user and user.subscription_type == 'PREMIUM' and user.notifications_enabled:
                        tokens = get_user_push_tokens(db, position.user_id)
                        
                        if tokens:
                            position_data = {
                                "id": position.id,
                                "symbol": position.symbol,
                                "pnl": position.pnl_usdt,
                                "pnl_percentage": position.pnl_pct,
                            }
                            send_trade_end_notification(tokens, position_data)
                            worker_logger.info(f"📱 Sent trade end notification to user {position.user_id}")
                except Exception as notif_error:
                    worker_logger.error(f"Trade end notification failed: {notif_error}")
        
    except Exception as e:
        worker_logger.error(f"Close position target error: {e}")


def close_position_sl(db: Session, position: Position, sl_price: float):
    """
    Close entire position when stop loss is hit
    """
    try:
        close_result = paper_client.close_position(
            user_id=position.user_id,
            symbol=position.symbol,
            side=position.side,
            qty=position.remaining_qty,
            entry_price=position.entry_price,
            exit_price=sl_price,
            leverage=position.leverage
        )
        
        if close_result.get('success'):
            position.status = 'STOPPED'
            position.closed_at = datetime.utcnow()
            position.remaining_qty = 0
            position.pnl_usdt = close_result.get('pnl_usdt', 0)
            position.pnl_pct = close_result.get('pnl_pct', 0)
            
            # Log event
            trade_log = TradeLog(
                user_id=position.user_id,
                position_id=position.id,
                signal_id=position.signal_id,
                type='SL_HIT',
                message=f"Stop loss hit at {sl_price}",
                meta=close_result
            )
            db.add(trade_log)
            
            worker_logger.info(f"Stop loss hit for position #{position.id}, PnL: {close_result.get('pnl_usdt')}")
            
            # Send trade end notification (PREMIUM users only)
            try:
                user = db.query(User).filter(User.id == position.user_id).first()
                
                if user and user.subscription_type == 'PREMIUM' and user.notifications_enabled:
                    tokens = get_user_push_tokens(db, position.user_id)
                    
                    if tokens:
                        position_data = {
                            "id": position.id,
                            "symbol": position.symbol,
                            "pnl": position.pnl_usdt,
                            "pnl_percentage": position.pnl_pct,
                        }
                        send_trade_end_notification(tokens, position_data)
                        worker_logger.info(f"📱 Sent trade end notification to user {position.user_id}")
            except Exception as notif_error:
                worker_logger.error(f"Trade end notification failed: {notif_error}")
        
    except Exception as e:
        worker_logger.error(f"Close position SL error: {e}")
