"""
Telegram Notifications for Subscribers Group
Sends real-time updates about subscriptions, referrals, and payments
"""
import os
import requests
from datetime import datetime
from typing import Optional
from utils.logger import api_logger

# Telegram configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
SUBSCRIBERS_CHAT_ID = os.getenv('SUBSCRIBERS_CHAT_ID', '-1002721581400')
TELEGRAM_ENABLED = os.getenv('TELEGRAM_NOTIFICATIONS_ENABLED', 'true').lower() == 'true'


def send_telegram_message(text: str, parse_mode: str = "HTML") -> bool:
    """
    Send message to Verzek Subscribers Telegram group
    
    Args:
        text: Message content (supports HTML formatting)
        parse_mode: "HTML" or "Markdown" (default: HTML)
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    # Feature flag - can be disabled via environment variable
    if not TELEGRAM_ENABLED:
        api_logger.info("Telegram notifications disabled via TELEGRAM_NOTIFICATIONS_ENABLED=false")
        return False
    
    if not BOT_TOKEN:
        api_logger.warning("TELEGRAM_BOT_TOKEN not configured, skipping notification")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        
        payload = {
            "chat_id": SUBSCRIBERS_CHAT_ID,
            "text": text,
            "parse_mode": parse_mode
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        if result.get('ok'):
            api_logger.info(f"Telegram notification sent to subscribers group")
            return True
        else:
            api_logger.error(f"Telegram API error: {result.get('description')}")
            return False
            
    except requests.exceptions.Timeout:
        api_logger.error("Telegram notification timeout")
        return False
    except requests.exceptions.RequestException as e:
        api_logger.error(f"Telegram notification failed: {e}")
        return False
    except Exception as e:
        api_logger.error(f"Unexpected error sending Telegram notification: {e}")
        return False


def notify_new_subscription(user_name: str, plan_type: str, amount_usdt: float) -> bool:
    """
    Notify group about new subscription upgrade
    
    Args:
        user_name: User's full name (NOT email for privacy)
        plan_type: VIP or PREMIUM
        amount_usdt: Payment amount
    """
    emoji = "💎" if plan_type == "PREMIUM" else "⭐"
    
    message = f"""
{emoji} <b>NEW {plan_type} SUBSCRIBER!</b> {emoji}

👤 <b>Welcome:</b> {user_name}
💰 <b>Amount:</b> ${amount_usdt:.2f} USDT
📅 <b>Date:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

🎉 Welcome to the Verzek family! Happy trading!
    """.strip()
    
    return send_telegram_message(message)


def notify_referral_success(referrer_name: str, new_user_name: str, new_user_plan: str) -> bool:
    """
    Notify group about successful referral
    
    Args:
        referrer_name: Person who referred
        new_user_name: New user who joined
        new_user_plan: TRIAL, VIP, or PREMIUM
    """
    message = f"""
🤝 <b>NEW REFERRAL!</b>

👥 <b>Referred by:</b> {referrer_name}
🆕 <b>New member:</b> {new_user_name}
📊 <b>Plan:</b> {new_user_plan}
📅 <b>Date:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

💪 Keep spreading the word! Referral bonuses coming soon!
    """.strip()
    
    return send_telegram_message(message)


def notify_payment_received(amount_usdt: float, plan_type: str, tx_hash: Optional[str] = None) -> bool:
    """
    Notify group about payment received (pending verification)
    
    Args:
        amount_usdt: Payment amount
        plan_type: VIP or PREMIUM
        tx_hash: Transaction hash (optional, truncated for privacy)
    """
    tx_info = ""
    if tx_hash:
        # Show first 8 and last 6 chars only
        truncated = f"{tx_hash[:8]}...{tx_hash[-6:]}" if len(tx_hash) > 20 else tx_hash
        tx_info = f"\n🔗 <b>TX:</b> <code>{truncated}</code>"
    
    message = f"""
💸 <b>PAYMENT RECEIVED!</b>

💰 <b>Amount:</b> ${amount_usdt:.2f} USDT
📦 <b>Plan:</b> {plan_type}{tx_info}
📅 <b>Date:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

⏳ Pending admin verification...
    """.strip()
    
    return send_telegram_message(message)


def notify_milestone(milestone_type: str, count: int) -> bool:
    """
    Notify group about platform milestones
    
    Args:
        milestone_type: "users", "subscribers", "revenue"
        count: Milestone number
    """
    emojis = {
        "users": "👥",
        "subscribers": "⭐",
        "revenue": "💰"
    }
    
    emoji = emojis.get(milestone_type, "🎉")
    
    message = f"""
{emoji} <b>MILESTONE ACHIEVED!</b> {emoji}

We just reached <b>{count} {milestone_type.upper()}!</b>

Thank you to our amazing community! 🚀

📈 Verzek AutoTrader - Growing Together!
    """.strip()
    
    return send_telegram_message(message)


def notify_daily_stats(total_users: int, vip_count: int, premium_count: int, daily_revenue: float) -> bool:
    """
    Send daily platform statistics (optional, for admin use)
    
    Args:
        total_users: Total registered users
        vip_count: VIP subscribers
        premium_count: PREMIUM subscribers
        daily_revenue: Revenue for the day
    """
    message = f"""
📊 <b>DAILY STATS UPDATE</b>

👥 <b>Total Users:</b> {total_users}
⭐ <b>VIP Subscribers:</b> {vip_count}
💎 <b>PREMIUM Subscribers:</b> {premium_count}
💰 <b>Today's Revenue:</b> ${daily_revenue:.2f} USDT

📅 {datetime.utcnow().strftime('%Y-%m-%d')}
    """.strip()
    
    return send_telegram_message(message)


def test_notification() -> bool:
    """Test notification to verify bot configuration"""
    message = """
🤖 <b>VERZEK AUTOTRADER BOT ONLINE!</b>

✅ Notifications system activated
📢 You will receive updates about:
  • New subscriptions
  • Referral bonuses
  • Payment confirmations
  • Platform milestones

🚀 Let's trade smart together!
    """.strip()
    
    return send_telegram_message(message)
