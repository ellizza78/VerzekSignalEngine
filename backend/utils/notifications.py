"""
Push Notification Service for VerzekAutoTrader
Sends subscription-based notifications via Expo Push API
"""
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"
MAX_BATCH_SIZE = 100


def send_push_notification(
    push_tokens: List[str],
    title: str,
    body: str,
    data: Optional[Dict] = None,
    sound: str = "default",
    channel_id: str = "default",
    priority: str = "high"
) -> Dict:
    """
    Send push notification to Expo devices
    
    Args:
        push_tokens: List of Expo push tokens
        title: Notification title
        body: Notification body
        data: Custom data payload
        sound: Sound to play (default, signal, trade)
        channel_id: Android notification channel (default, signals, trades)
        priority: Notification priority (high, normal)
    
    Returns:
        Dictionary with success status and response data
    """
    if not push_tokens:
        logger.warning("No push tokens provided")
        return {"success": False, "error": "No push tokens provided"}
    
    valid_tokens = [t for t in push_tokens if t and t.startswith('ExponentPushToken[')]
    
    if not valid_tokens:
        logger.warning(f"No valid Expo push tokens found from {len(push_tokens)} tokens")
        return {"success": False, "error": "No valid push tokens"}
    
    messages = []
    for token in valid_tokens:
        message = {
            "to": token,
            "sound": sound,
            "title": title,
            "body": body,
            "data": data or {},
            "channelId": channel_id,
            "priority": priority,
            "badge": 1,
        }
        messages.append(message)
    
    results = []
    errors = []
    
    for i in range(0, len(messages), MAX_BATCH_SIZE):
        batch = messages[i:i + MAX_BATCH_SIZE]
        
        try:
            response = requests.post(
                EXPO_PUSH_URL,
                json=batch,
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                },
                timeout=10
            )
            
            if response.status_code == 200:
                response_data = response.json()
                results.extend(response_data.get('data', []))
                logger.info(f"Sent batch of {len(batch)} push notifications successfully")
            else:
                error_msg = f"Push notification failed: HTTP {response.status_code} - {response.text}"
                logger.error(error_msg)
                errors.append(error_msg)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Push notification request error: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error sending push notification: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
    
    if results:
        return {
            "success": True,
            "sent": len(results),
            "total_tokens": len(valid_tokens),
            "results": results,
            "errors": errors if errors else None
        }
    else:
        return {
            "success": False,
            "error": "All batches failed",
            "errors": errors
        }


def send_signal_notification(push_tokens: List[str], signal_data: Dict) -> Dict:
    """
    Send notification for new trading signal (VIP + PREMIUM users)
    
    Args:
        push_tokens: List of Expo push tokens
        signal_data: Dictionary containing signal information
    
    Returns:
        Notification send result
    """
    symbol = signal_data.get('symbol', 'Unknown')
    direction = signal_data.get('direction', 'BUY')
    entry = signal_data.get('entry_price') or signal_data.get('entry')
    
    entry_str = f"${float(entry):.4f}" if entry else "N/A"
    
    emoji = "🟢" if direction == "BUY" else "🔴"
    
    return send_push_notification(
        push_tokens=push_tokens,
        title=f"{emoji} New {direction} Signal",
        body=f"{symbol} - Entry: {entry_str}",
        data={
            "type": "signal",
            "signal_id": signal_data.get('id'),
            "symbol": symbol,
            "direction": direction,
            "entry_price": entry,
            "timestamp": datetime.utcnow().isoformat()
        },
        sound="default",
        channel_id="signals",
        priority="high"
    )


def send_trade_start_notification(push_tokens: List[str], position_data: Dict) -> Dict:
    """
    Send notification when trade starts (PREMIUM users only)
    
    Args:
        push_tokens: List of Expo push tokens
        position_data: Dictionary containing position information
    
    Returns:
        Notification send result
    """
    symbol = position_data.get('symbol', 'Unknown')
    direction = position_data.get('direction', 'LONG')
    entry = position_data.get('entry_price')
    
    entry_str = f"${float(entry):.4f}" if entry else "N/A"
    
    emoji = "✅"
    
    return send_push_notification(
        push_tokens=push_tokens,
        title=f"{emoji} Trade Started",
        body=f"{direction} {symbol} - Entry: {entry_str}",
        data={
            "type": "trade_start",
            "position_id": position_data.get('id'),
            "symbol": symbol,
            "direction": direction,
            "entry_price": entry,
            "timestamp": datetime.utcnow().isoformat()
        },
        sound="default",
        channel_id="trades",
        priority="high"
    )


def send_trade_end_notification(push_tokens: List[str], position_data: Dict) -> Dict:
    """
    Send notification when trade ends (PREMIUM users only)
    
    Args:
        push_tokens: List of Expo push tokens
        position_data: Dictionary containing position information
    
    Returns:
        Notification send result
    """
    symbol = position_data.get('symbol', 'Unknown')
    pnl = position_data.get('pnl', 0)
    pnl_pct = position_data.get('pnl_percentage', 0)
    
    pnl_emoji = "🟢" if pnl > 0 else "🔴" if pnl < 0 else "⚪"
    
    pnl_str = f"${float(pnl):.2f}" if pnl else "$0.00"
    pnl_pct_str = f"({float(pnl_pct):.2f}%)" if pnl_pct else ""
    
    return send_push_notification(
        push_tokens=push_tokens,
        title=f"{pnl_emoji} Trade Closed",
        body=f"{symbol} - PnL: {pnl_str} {pnl_pct_str}",
        data={
            "type": "trade_end",
            "position_id": position_data.get('id'),
            "symbol": symbol,
            "pnl": pnl,
            "pnl_percentage": pnl_pct,
            "timestamp": datetime.utcnow().isoformat()
        },
        sound="default",
        channel_id="trades",
        priority="high"
    )


def get_user_push_tokens(db_session, user_id: int) -> List[str]:
    """
    Get all active push tokens for a user
    
    Args:
        db_session: SQLAlchemy database session
        user_id: User ID
    
    Returns:
        List of active push tokens for the user
    """
    try:
        from models import DeviceToken
        
        device_tokens = db_session.query(DeviceToken).filter(
            DeviceToken.user_id == user_id,
            DeviceToken.is_active == True
        ).all()
        
        return [dt.push_token for dt in device_tokens if dt.push_token]
    except Exception as e:
        logger.error(f"Error fetching user push tokens: {e}")
        return []


def get_subscription_user_tokens(db_session, subscription_types: List[str]) -> Dict[int, List[str]]:
    """
    Get push tokens for all users with specific subscription types
    
    Args:
        db_session: SQLAlchemy database session
        subscription_types: List of subscription types (e.g., ['VIP', 'PREMIUM'])
    
    Returns:
        Dictionary mapping user_id to list of push tokens
    """
    try:
        from models import User, DeviceToken
        
        users = db_session.query(User).filter(
            User.subscription_type.in_(subscription_types),
            User.notifications_enabled == True,
            User.is_active == True
        ).all()
        
        user_tokens = {}
        
        for user in users:
            device_tokens = db_session.query(DeviceToken).filter(
                DeviceToken.user_id == user.id,
                DeviceToken.is_active == True
            ).all()
            
            tokens = [dt.push_token for dt in device_tokens if dt.push_token]
            if tokens:
                user_tokens[user.id] = tokens
        
        return user_tokens
    except Exception as e:
        logger.error(f"Error fetching subscription user tokens: {e}")
        return {}
