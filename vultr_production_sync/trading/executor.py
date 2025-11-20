"""
Trade Executor - Auto-Trading Worker Logic
Processes signals, opens positions, manages TP/SL for users with auto_trade_enabled=True
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import requests
import os

from models import User, UserSettings, Signal, Position, PositionTarget, TradeLog
from trading.paper_client import paper_client
from utils.logger import worker_logger
from utils.notifications import (
    send_trade_start_notification,
    send_trade_end_notification,
    get_user_push_tokens
)
from broadcast import broadcast_signal_cancelled


def notify_signal_engine_tp_hit(signal_id: str, hit_price: float, tp_number: int):
    """
    Send webhook to Signal Engine to record TP hit with retry logic
    
    Args:
        signal_id: Signal ID from signal engine
        hit_price: Price at which TP was hit
        tp_number: TP number (1-5)
    """
    webhook_url = os.getenv('SIGNAL_ENGINE_WEBHOOK_URL', 'http://localhost:8050')
    
    payload = {
        'signal_id': signal_id,
        'hit_price': hit_price,
        'tp_number': tp_number
    }
    
    # Get webhook secret for authentication
    webhook_secret = os.getenv('SIGNAL_ENGINE_WEBHOOK_SECRET', 'dev-secret-change-in-prod')
    
    headers = {
        'Content-Type': 'application/json',
        'X-Webhook-Secret': webhook_secret
    }
    
    # Retry up to 3 times with exponential backoff
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{webhook_url}/api/signals/tp-hit",
                json=payload,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                outcome = result.get('outcome', {})
                is_final = outcome.get('is_final', False)
                
                worker_logger.info(
                    f"✅ Signal Engine notified: TP{tp_number} hit for {signal_id[:8]} "
                    f"(Final: {is_final})"
                )
                return True
            else:
                worker_logger.warning(
                    f"⚠️ Signal Engine TP webhook failed (attempt {attempt + 1}/{max_retries}): "
                    f"Status {response.status_code}, Response: {response.text}"
                )
                
        except requests.exceptions.Timeout:
            worker_logger.error(
                f"⏱️  Signal Engine TP webhook timeout (attempt {attempt + 1}/{max_retries}) "
                f"for {signal_id[:8]}"
            )
        except requests.exceptions.ConnectionError:
            worker_logger.error(
                f"🔌 Signal Engine TP webhook connection error (attempt {attempt + 1}/{max_retries}) "
                f"for {signal_id[:8]} - Is webhook server running?"
            )
        except Exception as e:
            worker_logger.error(
                f"❌ Signal Engine TP webhook error (attempt {attempt + 1}/{max_retries}): {e}"
            )
        
        # Wait before retry (exponential backoff: 1s, 2s, 4s)
        if attempt < max_retries - 1:
            import time
            wait_time = 2 ** attempt
            worker_logger.info(f"Retrying in {wait_time}s...")
            time.sleep(wait_time)
    
    # All retries failed - log error but don't block execution
    worker_logger.error(
        f"🚨 Signal Engine TP webhook failed after {max_retries} attempts for {signal_id[:8]}! "
        f"TP{tp_number} hit may not be tracked."
    )
    return False


def notify_signal_engine_closure(signal_id: str, exit_price: float, close_reason: str):
    """
    Send webhook to Signal Engine to close tracked signal with retry logic
    
    Args:
        signal_id: Signal ID from signal engine
        exit_price: Actual exit price
        close_reason: TP, SL, CANCEL, or REVERSAL
    """
    webhook_url = os.getenv('SIGNAL_ENGINE_WEBHOOK_URL', 'http://localhost:8050')
    
    payload = {
        'signal_id': signal_id,
        'exit_price': exit_price,
        'close_reason': close_reason
    }
    
    # Get webhook secret for authentication
    webhook_secret = os.getenv('SIGNAL_ENGINE_WEBHOOK_SECRET', 'dev-secret-change-in-prod')
    
    headers = {
        'Content-Type': 'application/json',
        'X-Webhook-Secret': webhook_secret
    }
    
    # Retry up to 3 times with exponential backoff
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{webhook_url}/api/signals/close",
                json=payload,
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                worker_logger.info(f"✅ Signal Engine notified: {signal_id[:8]} closed ({close_reason})")
                return True
            else:
                worker_logger.warning(
                    f"⚠️ Signal Engine webhook failed (attempt {attempt + 1}/{max_retries}): "
                    f"Status {response.status_code}, Response: {response.text}"
                )
                
        except requests.exceptions.Timeout:
            worker_logger.error(
                f"⏱️  Signal Engine webhook timeout (attempt {attempt + 1}/{max_retries}) "
                f"for {signal_id[:8]}"
            )
        except requests.exceptions.ConnectionError:
            worker_logger.error(
                f"🔌 Signal Engine webhook connection error (attempt {attempt + 1}/{max_retries}) "
                f"for {signal_id[:8]} - Is webhook server running?"
            )
        except Exception as e:
            worker_logger.error(
                f"❌ Signal Engine webhook error (attempt {attempt + 1}/{max_retries}): {e}"
            )
        
        # Wait before retry (exponential backoff: 1s, 2s, 4s)
        if attempt < max_retries - 1:
            import time
            wait_time = 2 ** attempt
            worker_logger.info(f"Retrying in {wait_time}s...")
            time.sleep(wait_time)
    
    # All retries failed - log critical error
    worker_logger.error(
        f"🚨 CRITICAL: Signal Engine webhook failed after {max_retries} attempts! "
        f"Signal {signal_id[:8]} may be stuck ACTIVE. Manual intervention required."
    )
    return False


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
                
                # Check for signal reversal (opposite direction on same symbol)
                handle_signal_reversal(db, user.id, signal)
                
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


def handle_signal_reversal(db: Session, user_id: int, new_signal: Signal):
    """
    Detect and handle signal reversals (opposite direction on same symbol)
    If user has auto_reversal enabled and an opposite position exists within the reversal window,
    close the existing position before opening the new one.
    
    Example: BTCUSDT LONG at 2:39 PM → BTCUSDT SHORT at 2:42 PM
    Result: Close LONG position, then open SHORT position
    """
    try:
        # Get user settings
        settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
        if not settings or not settings.auto_reversal_enabled:
            return  # Auto-reversal disabled
        
        # Find active positions for this symbol
        active_positions = db.query(Position).filter(
            Position.user_id == user_id,
            Position.symbol == new_signal.symbol,
            Position.status.in_(['OPEN', 'PARTIAL'])
        ).all()
        
        if not active_positions:
            return  # No active positions on this symbol
        
        # Check if any position is in opposite direction (instant reversal, no time window)
        for position in active_positions:
            # Normalize sides to handle both BUY/SELL and LONG/SHORT formats
            position_side = position.side.upper()
            signal_side = new_signal.side.upper()
            
            # Map BUY/SELL to LONG/SHORT for consistency
            if position_side == 'BUY':
                position_side = 'LONG'
            elif position_side == 'SELL':
                position_side = 'SHORT'
            
            if signal_side == 'BUY':
                signal_side = 'LONG'
            elif signal_side == 'SELL':
                signal_side = 'SHORT'
            
            # Check if direction is opposite
            is_opposite = (
                (position_side == 'LONG' and signal_side == 'SHORT') or
                (position_side == 'SHORT' and signal_side == 'LONG')
            )
            
            if not is_opposite:
                continue  # Same direction, allow multiple positions (position stacking)
            
            # REVERSAL DETECTED - Close the opposite position immediately
            time_diff = (datetime.utcnow() - position.created_at).total_seconds()
            worker_logger.warning(
                f"🔄 INSTANT SIGNAL REVERSAL DETECTED for user {user_id}: "
                f"{position.symbol} {position_side} → {signal_side} "
                f"(position age: {time_diff:.0f}s, no time restriction)"
            )
            
            # Get current market price for exit
            current_price = paper_client.get_current_price(position.symbol)
            if not current_price:
                worker_logger.error(f"Failed to get current price for {position.symbol}, skipping reversal")
                continue
            
            # Close the opposite position at market price
            close_result = paper_client.close_position(
                user_id=user_id,
                symbol=position.symbol,
                side=position.side,
                qty=position.remaining_qty,
                entry_price=position.entry_price,
                exit_price=current_price,
                leverage=position.leverage
            )
            
            if close_result.get('success'):
                position.status = 'CANCELLED'
                position.closed_at = datetime.utcnow()
                position.remaining_qty = 0
                position.pnl_usdt = close_result.get('pnl_usdt', 0)
                position.pnl_pct = close_result.get('pnl_pct', 0)
                
                # Log reversal event
                trade_log = TradeLog(
                    user_id=user_id,
                    position_id=position.id,
                    signal_id=position.signal_id,
                    type='REVERSAL',
                    message=f"Position closed due to instant market reversal: {position_side} → {signal_side}",
                    meta={
                        'reversal_reason': 'market_direction_change',
                        'new_signal_id': new_signal.id,
                        'position_age_seconds': time_diff,
                        'close_price': current_price,
                        'instant_reversal': True,
                        **close_result
                    }
                )
                db.add(trade_log)
                
                worker_logger.info(
                    f"✅ Reversed position #{position.id}: {position.side} @ {position.entry_price} → "
                    f"Closed @ {current_price}, PnL: {close_result.get('pnl_usdt', 0):.2f} USDT"
                )
                
                # Mark all targets as cancelled
                for target in position.targets:
                    if not target.hit:
                        target.hit = True
                        target.hit_at = datetime.utcnow()
                
                # Send Telegram cancellation notification
                try:
                    signal = db.query(Signal).filter(Signal.id == position.signal_id).first()
                    if signal:
                        broadcast_signal_cancelled(
                            signal_id=signal.id,
                            symbol=position.symbol,
                            reason=f"Signal Reversal: {position_side} → {signal_side}"
                        )
                        worker_logger.info(f"📢 Sent reversal notification to Telegram for {position.symbol}")
                except Exception as broadcast_error:
                    worker_logger.error(f"Telegram reversal notification failed: {broadcast_error}")
                
                # Notify Signal Engine that position closed (reversal)
                if position.signal_id:
                    notify_signal_engine_closure(position.signal_id, current_price, 'REVERSAL')
                
                db.flush()  # Commit the reversal before opening new position
            else:
                worker_logger.error(
                    f"Failed to close position #{position.id} for reversal: {close_result.get('error')}"
                )
        
    except Exception as e:
        worker_logger.error(f"Signal reversal handling error: {e}", exc_info=True)


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
            
            # Broadcast TP hit to Telegram
            try:
                from broadcast import broadcast_target_hit
                signal = db.query(Signal).filter(Signal.id == position.signal_id).first()
                if signal:
                    broadcast_target_hit(
                        signal_id=signal.id,
                        symbol=position.symbol,
                        target_index=target_index,
                        price=price,
                        target="both"
                    )
                    worker_logger.info(f"📢 Telegram: TP{target_index} hit notification sent")
            except Exception as tg_error:
                worker_logger.error(f"Telegram TP notification failed: {tg_error}")
            
            # Notify Signal Engine of TP hit for multi-TP tracking
            if position.signal_id:
                try:
                    notify_signal_engine_tp_hit(
                        signal_id=position.signal_id,
                        hit_price=price,
                        tp_number=target_index
                    )
                except Exception as se_error:
                    worker_logger.error(f"Signal Engine TP notification failed: {se_error}")
            
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
                
                # Notify Signal Engine that position fully closed
                if position.signal_id:
                    notify_signal_engine_closure(position.signal_id, price, 'TP')
        
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
            
            # Broadcast SL hit to Telegram
            try:
                from broadcast import broadcast_stop_loss
                signal = db.query(Signal).filter(Signal.id == position.signal_id).first()
                if signal:
                    broadcast_stop_loss(
                        signal_id=signal.id,
                        symbol=position.symbol,
                        price=sl_price,
                        target="both"
                    )
                    worker_logger.info(f"📢 Telegram: Stop loss hit notification sent")
            except Exception as tg_error:
                worker_logger.error(f"Telegram SL notification failed: {tg_error}")
            
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
            
            # Notify Signal Engine that position closed (stop loss)
            if position.signal_id:
                notify_signal_engine_closure(position.signal_id, sl_price, 'SL')
        
    except Exception as e:
        worker_logger.error(f"Close position SL error: {e}")
