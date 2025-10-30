"""
Admin Notification Service - Sends alerts for critical events
Supports Telegram, Email, and batched summaries for scale
"""

import os
import requests
from datetime import datetime
from typing import Optional, Dict, List
from utils.logger import log_event


class AdminNotificationService:
    """
    Sends notifications to admin for critical events:
    - Referral payout requests
    - Large payment amounts
    - System alerts
    - Daily/hourly summaries for scale
    """
    
    def __init__(self):
        self.telegram_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.admin_chat_id = os.environ.get('ADMIN_CHAT_ID')
        self.telegram_enabled = bool(self.telegram_token and self.admin_chat_id)
        
        # Thresholds for different notification types
        self.HIGH_AMOUNT_THRESHOLD = 100  # $100+ gets instant alert
        self.BATCH_INTERVAL = 3600  # 1 hour for batch summaries
        
        # Track pending notifications for batching
        self.pending_notifications = []
        
        if self.telegram_enabled:
            log_event("NOTIFICATIONS", "✅ Admin notifications enabled (Telegram)")
        else:
            log_event("NOTIFICATIONS", "⚠️ Admin notifications disabled (missing credentials)")
    
    def send_telegram(self, message: str, parse_mode: str = "HTML") -> bool:
        """Send message via Telegram"""
        if not self.telegram_enabled:
            log_event("NOTIFICATIONS", f"[SKIPPED] {message[:100]}")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                'chat_id': self.admin_chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                log_event("NOTIFICATIONS", f"✅ Telegram sent: {message[:50]}...")
                return True
            else:
                log_event("NOTIFICATIONS", f"❌ Telegram failed: {response.status_code}")
                return False
                
        except Exception as e:
            log_event("NOTIFICATIONS", f"❌ Telegram error: {str(e)}")
            return False
    
    def notify_payout_request(self, payout_data: Dict, current_balance: Optional[float] = None) -> bool:
        """
        Notify admin of new referral payout request
        
        Args:
            payout_data: {
                'payout_id': str,
                'user_id': str,
                'amount_usdt': float,
                'wallet_address': str,
                'requested_at': str
            }
            current_balance: Current financial balance (optional)
        """
        user_id = payout_data.get('user_id', 'Unknown')
        amount = payout_data.get('amount_usdt', 0)
        wallet = payout_data.get('wallet_address', 'N/A')
        payout_id = payout_data.get('payout_id', 'N/A')
        
        # Format message with emojis and formatting
        priority = "🔴 HIGH PRIORITY" if amount >= self.HIGH_AMOUNT_THRESHOLD else "🟢"
        
        message = f"""
{priority} <b>💰 PAYOUT REQUEST</b>

<b>User:</b> {user_id}
<b>Amount:</b> ${amount:.2f} USDT
<b>Fee:</b> $1.00 USDT
<b>Net Payout:</b> ${amount:.2f} USDT

<b>Destination:</b>
<code>{wallet}</code>

<b>Payout ID:</b> <code>{payout_id}</code>

⏰ <i>Requested: {payout_data.get('requested_at', 'N/A')}</i>

"""
        
        # Add balance info if provided
        if current_balance is not None:
            balance_after = current_balance - amount
            message += f"""
━━━━━━━━━━━━━━━━━━━
💰 <b>BALANCE CHECK</b>
Current: ${current_balance:.2f}
After Payout: ${balance_after:.2f}
━━━━━━━━━━━━━━━━━━━

"""
        
        message += f"""<b>Action Required:</b>
1. Verify wallet address is valid
2. Send ${amount:.2f} USDT to address above
3. Mark payout as completed in system

Network: TRC20 (TRON)
Processing Time: Within 24 hours
"""
        
        return self.send_telegram(message)
    
    def notify_payout_completed(self, payout_data: Dict, financial_summary: Optional[Dict] = None) -> bool:
        """
        Notify admin when payout is marked as completed (for their records)
        
        Args:
            payout_data: Payout details
            financial_summary: Financial tracker data (optional)
        """
        user_id = payout_data.get('user_id', 'Unknown')
        amount = payout_data.get('amount_usdt', 0)
        tx_hash = payout_data.get('tx_hash', 'N/A')
        
        message = f"""
✅ <b>PAYOUT SENT</b>

<b>User:</b> {user_id}
<b>Amount:</b> -${amount:.2f} USDT

<b>TX Hash:</b>
<code>{tx_hash[:32]}...</code>

"""
        
        # Add financial summary if provided
        if financial_summary:
            balance = financial_summary.get('balance', 0)
            total_in = financial_summary.get('total_received', 0)
            total_out = financial_summary.get('total_paid_out', 0)
            
            balance_emoji = "📈" if balance >= 0 else "📉"
            
            message += f"""
━━━━━━━━━━━━━━━━━━━
💰 <b>FINANCIAL SUMMARY</b>

Total Received: ${total_in:.2f}
Total Paid Out: ${total_out:.2f}
{balance_emoji} <b>Balance: ${balance:.2f} USDT</b>
━━━━━━━━━━━━━━━━━━━
"""
        
        return self.send_telegram(message)
    
    def notify_payment_received(self, payment_data: Dict, financial_summary: Optional[Dict] = None) -> bool:
        """
        Notify admin of successful subscription payment with financial tracking
        
        Args:
            payment_data: {
                'user_id': str,
                'username': str (optional),
                'full_name': str (optional),
                'plan': str,
                'amount_usdt': float,
                'tx_hash': str,
                'referral_bonus': float (optional)
            }
            financial_summary: Financial tracker data (optional)
        """
        user_id = payment_data.get('user_id', 'Unknown')
        username = payment_data.get('username', user_id)
        full_name = payment_data.get('full_name', '')
        plan = payment_data.get('plan', 'N/A').upper()
        amount = payment_data.get('amount_usdt', 0)
        tx_hash = payment_data.get('tx_hash', 'N/A')
        bonus = payment_data.get('referral_bonus', 0)
        net_revenue = amount - bonus
        
        # Build user display with username and full name
        user_display = f"@{username}"
        if full_name:
            user_display += f" ({full_name})"
        
        message = f"""
✅ <b>PAYMENT RECEIVED</b>

<b>User:</b> {user_display}
<b>User ID:</b> {user_id}
<b>Plan:</b> {plan}
<b>Amount:</b> ${amount:.2f} USDT
"""
        
        if bonus > 0:
            message += f"<b>Referral Bonus:</b> -${bonus:.2f} (paid to referrer)\n"
        
        message += f"<b>Your Revenue:</b> +${net_revenue:.2f} USDT\n"
        
        message += f"""
<b>TX Hash:</b>
<code>{tx_hash[:32]}...</code>

"""
        
        # Add financial summary if provided
        if financial_summary:
            balance = financial_summary.get('balance', 0)
            total_in = financial_summary.get('total_received', 0)
            total_out = financial_summary.get('total_paid_out', 0)
            
            balance_emoji = "📈" if balance >= 0 else "📉"
            
            message += f"""
━━━━━━━━━━━━━━━━━━━
💰 <b>FINANCIAL SUMMARY</b>

Total Received: ${total_in:.2f}
Total Paid Out: ${total_out:.2f}
{balance_emoji} <b>Balance: ${balance:.2f} USDT</b>
━━━━━━━━━━━━━━━━━━━
"""
        
        return self.send_telegram(message)
    
    def notify_large_payout_batch(self, payouts: List[Dict]) -> bool:
        """
        Send summary notification for multiple pending payouts
        Used when there are many requests to avoid spam
        """
        if not payouts:
            return False
        
        total_amount = sum(p.get('amount_usdt', 0) for p in payouts)
        total_fee = len(payouts) * 1.0  # $1 per payout
        
        message = f"""
📊 <b>PENDING PAYOUTS SUMMARY</b>

<b>Total Requests:</b> {len(payouts)}
<b>Total Amount:</b> ${total_amount:.2f} USDT
<b>Total Fees:</b> ${total_fee:.2f} USDT

<b>Breakdown:</b>
"""
        
        # Show top 5 largest payouts
        sorted_payouts = sorted(payouts, key=lambda x: x.get('amount_usdt', 0), reverse=True)
        for i, payout in enumerate(sorted_payouts[:5], 1):
            user = payout.get('user_id', 'Unknown')
            amount = payout.get('amount_usdt', 0)
            message += f"{i}. {user}: ${amount:.2f}\n"
        
        if len(payouts) > 5:
            message += f"\n...and {len(payouts) - 5} more\n"
        
        message += f"""
⚠️ <b>Action Required:</b>
Process {len(payouts)} payout request(s)

Check admin panel for full details.
"""
        
        return self.send_telegram(message)
    
    def notify_daily_summary(self, summary_data: Dict) -> bool:
        """
        Send daily summary of platform activity
        
        Args:
            summary_data: {
                'new_users': int,
                'payments_verified': int,
                'total_revenue': float,
                'payouts_processed': int,
                'pending_payouts': int,
                'active_positions': int
            }
        """
        message = f"""
📈 <b>DAILY SUMMARY - {datetime.now().strftime('%Y-%m-%d')}</b>

<b>💰 Revenue</b>
• Payments Verified: {summary_data.get('payments_verified', 0)}
• Total Revenue: ${summary_data.get('total_revenue', 0):.2f} USDT

<b>👥 Users</b>
• New Registrations: {summary_data.get('new_users', 0)}
• Active Positions: {summary_data.get('active_positions', 0)}

<b>💸 Payouts</b>
• Processed: {summary_data.get('payouts_processed', 0)}
• Pending: {summary_data.get('pending_payouts', 0)}

<b>📊 Referrals</b>
• Commissions Paid: ${summary_data.get('referral_commissions', 0):.2f}

─────────────────────────
VerzekAutoTrader Platform
"""
        
        return self.send_telegram(message)
    
    def notify_system_alert(self, alert_type: str, message: str) -> bool:
        """
        Send critical system alerts
        
        Args:
            alert_type: 'error', 'warning', 'info'
            message: Alert message
        """
        emoji = {
            'error': '🚨',
            'warning': '⚠️',
            'info': 'ℹ️'
        }.get(alert_type.lower(), '📢')
        
        alert_message = f"""
{emoji} <b>SYSTEM ALERT - {alert_type.upper()}</b>

{message}

<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>
"""
        
        return self.send_telegram(alert_message)
    
    def get_pending_payouts_count(self) -> int:
        """Get count of pending payout requests from database"""
        try:
            import json
            payments_file = "database/payments.json"
            if os.path.exists(payments_file):
                with open(payments_file, 'r') as f:
                    payments = json.load(f)
                    return sum(1 for p in payments if p.get('status') == 'pending' and 'payout_id' in p)
        except Exception as e:
            log_event("NOTIFICATIONS", f"Error counting payouts: {e}")
        return 0


# Global instance
admin_notifier = AdminNotificationService()
