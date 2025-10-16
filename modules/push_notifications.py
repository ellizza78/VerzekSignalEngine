"""
Push Notification Module for VerzekAutoTrader
Handles real-time notifications via Firebase Cloud Messaging (FCM)
"""

import requests
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from utils.logger import log_event


class PushNotificationService:
    def __init__(self):
        self.fcm_server_key = os.environ.get('FCM_SERVER_KEY', '')
        self.fcm_api_url = 'https://fcm.googleapis.com/fcm/send'
        self.device_tokens_file = 'database/device_tokens.json'
        
        # Load device tokens
        self._load_device_tokens()
    
    def _load_device_tokens(self) -> Dict[str, List[str]]:
        """Load user device tokens from file"""
        if not os.path.exists(self.device_tokens_file):
            return {}
        
        try:
            with open(self.device_tokens_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_device_tokens(self, tokens: Dict[str, List[str]]):
        """Save device tokens to file"""
        with open(self.device_tokens_file, 'w') as f:
            json.dump(tokens, f, indent=2)
    
    def register_device(self, user_id: str, device_token: str) -> bool:
        """Register a device token for a user"""
        tokens = self._load_device_tokens()
        
        if user_id not in tokens:
            tokens[user_id] = []
        
        # Add token if not already registered
        if device_token not in tokens[user_id]:
            tokens[user_id].append(device_token)
            self._save_device_tokens(tokens)
            log_event("PUSH", f"Registered device token for user {user_id}")
            return True
        
        return False
    
    def unregister_device(self, user_id: str, device_token: str) -> bool:
        """Unregister a device token"""
        tokens = self._load_device_tokens()
        
        if user_id in tokens and device_token in tokens[user_id]:
            tokens[user_id].remove(device_token)
            if not tokens[user_id]:
                del tokens[user_id]
            self._save_device_tokens(tokens)
            log_event("PUSH", f"Unregistered device token for user {user_id}")
            return True
        
        return False
    
    def get_user_tokens(self, user_id: str) -> List[str]:
        """Get all device tokens for a user"""
        tokens = self._load_device_tokens()
        return tokens.get(user_id, [])
    
    def send_notification(self, user_id: str, title: str, body: str, 
                         data: Optional[Dict] = None, priority: str = "high") -> Dict[str, Any]:
        """
        Send push notification to user's devices
        
        Args:
            user_id: User to notify
            title: Notification title
            body: Notification body
            data: Custom data payload
            priority: "high" or "normal"
        """
        if not self.fcm_server_key:
            log_event("PUSH", "⚠️ FCM_SERVER_KEY not configured, skipping notification")
            return {'success': False, 'error': 'FCM not configured'}
        
        tokens = self.get_user_tokens(user_id)
        
        if not tokens:
            log_event("PUSH", f"No device tokens for user {user_id}")
            return {'success': False, 'error': 'No device tokens'}
        
        results = []
        
        for token in tokens:
            payload = {
                'to': token,
                'priority': priority,
                'notification': {
                    'title': title,
                    'body': body,
                    'sound': 'default',
                    'badge': '1'
                }
            }
            
            if data:
                payload['data'] = data
            
            try:
                response = requests.post(
                    self.fcm_api_url,
                    headers={
                        'Authorization': f'Key={self.fcm_server_key}',
                        'Content-Type': 'application/json'
                    },
                    json=payload,
                    timeout=10
                )
                
                results.append({
                    'token': token[:20] + '...',
                    'status': response.status_code,
                    'success': response.status_code == 200
                })
                
                if response.status_code == 200:
                    log_event("PUSH", f"Sent notification to user {user_id}: {title}")
                else:
                    log_event("PUSH", f"Failed to send to {user_id}: {response.text}")
                
            except Exception as e:
                log_event("PUSH", f"Error sending notification: {str(e)}")
                results.append({
                    'token': token[:20] + '...',
                    'error': str(e),
                    'success': False
                })
        
        return {
            'success': any(r['success'] for r in results),
            'results': results
        }
    
    def send_bulk_notification(self, user_ids: List[str], title: str, body: str, 
                              data: Optional[Dict] = None) -> Dict[str, Any]:
        """Send notification to multiple users"""
        results = []
        
        for user_id in user_ids:
            result = self.send_notification(user_id, title, body, data)
            results.append({
                'user_id': user_id,
                'result': result
            })
        
        successful = sum(1 for r in results if r['result']['success'])
        
        return {
            'total_users': len(user_ids),
            'successful': successful,
            'failed': len(user_ids) - successful,
            'results': results
        }
    
    # Predefined notification types
    
    def notify_new_signal(self, user_id: str, signal_data: Dict):
        """Notify user of new trading signal"""
        title = f"🎯 New {signal_data.get('side', 'LONG')} Signal"
        body = f"{signal_data.get('symbol')} - Entry: {signal_data.get('entry_price')}"
        
        data = {
            'type': 'new_signal',
            'signal_id': signal_data.get('signal_id'),
            'symbol': signal_data.get('symbol'),
            'side': signal_data.get('side')
        }
        
        return self.send_notification(user_id, title, body, data, priority="high")
    
    def notify_trade_executed(self, user_id: str, trade_data: Dict):
        """Notify user of executed trade"""
        title = f"✅ Trade Executed"
        body = f"{trade_data.get('symbol')} {trade_data.get('side')} - {trade_data.get('quantity')} @ {trade_data.get('price')}"
        
        data = {
            'type': 'trade_executed',
            'position_id': trade_data.get('position_id'),
            'symbol': trade_data.get('symbol')
        }
        
        return self.send_notification(user_id, title, body, data)
    
    def notify_position_closed(self, user_id: str, position_data: Dict):
        """Notify user of closed position"""
        pnl = position_data.get('pnl', 0)
        emoji = "🟢" if pnl > 0 else "🔴"
        
        title = f"{emoji} Position Closed"
        body = f"{position_data.get('symbol')} - PnL: ${pnl:.2f}"
        
        data = {
            'type': 'position_closed',
            'position_id': position_data.get('position_id'),
            'pnl': pnl
        }
        
        return self.send_notification(user_id, title, body, data)
    
    def notify_target_hit(self, user_id: str, target_data: Dict):
        """Notify user when target is hit"""
        title = f"🎯 Target {target_data.get('target_number')} Hit!"
        body = f"{target_data.get('symbol')} reached ${target_data.get('price')}"
        
        data = {
            'type': 'target_hit',
            'position_id': target_data.get('position_id'),
            'target_number': target_data.get('target_number')
        }
        
        return self.send_notification(user_id, title, body, data, priority="high")
    
    def notify_stop_loss(self, user_id: str, position_data: Dict):
        """Notify user of stop loss trigger"""
        title = f"⚠️ Stop Loss Triggered"
        body = f"{position_data.get('symbol')} - Loss: ${position_data.get('pnl', 0):.2f}"
        
        data = {
            'type': 'stop_loss',
            'position_id': position_data.get('position_id')
        }
        
        return self.send_notification(user_id, title, body, data, priority="high")
    
    def notify_payment_approved(self, user_id: str, payment_data: Dict):
        """Notify user of approved payment"""
        title = f"💰 Payment Approved"
        body = f"{payment_data.get('plan')} subscription activated - ${payment_data.get('amount')}"
        
        data = {
            'type': 'payment_approved',
            'plan': payment_data.get('plan'),
            'amount': payment_data.get('amount')
        }
        
        return self.send_notification(user_id, title, body, data)
    
    def notify_subscription_expiring(self, user_id: str, days_remaining: int):
        """Notify user of expiring subscription"""
        title = f"⏰ Subscription Expiring Soon"
        body = f"Your subscription expires in {days_remaining} days. Renew to continue trading."
        
        data = {
            'type': 'subscription_expiring',
            'days_remaining': days_remaining
        }
        
        return self.send_notification(user_id, title, body, data)
    
    def notify_security_alert(self, user_id: str, alert_message: str):
        """Notify user of security alert"""
        title = f"🔒 Security Alert"
        body = alert_message
        
        data = {
            'type': 'security_alert',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return self.send_notification(user_id, title, body, data, priority="high")
    
    def notify_referral_bonus(self, user_id: str, bonus_amount: float):
        """Notify user of referral bonus"""
        title = f"🎁 Referral Bonus Earned!"
        body = f"You earned ${bonus_amount:.2f} in referral commission"
        
        data = {
            'type': 'referral_bonus',
            'amount': bonus_amount
        }
        
        return self.send_notification(user_id, title, body, data)
    
    def notify_withdrawal_completed(self, user_id: str, withdrawal_data: Dict):
        """Notify user of completed withdrawal"""
        title = f"✅ Withdrawal Complete"
        body = f"${withdrawal_data.get('amount')} sent to your wallet"
        
        data = {
            'type': 'withdrawal_completed',
            'amount': withdrawal_data.get('amount'),
            'tx_hash': withdrawal_data.get('tx_hash')
        }
        
        return self.send_notification(user_id, title, body, data)


# Global instance
push_service = PushNotificationService()
