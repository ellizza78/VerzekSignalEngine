"""
Webhook Handler for VerzekAutoTrader
Receives and processes signals from external sources (TradingView, custom APIs)
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os
import hmac
import hashlib
from utils.logger import log_event


class WebhookHandler:
    """Handle webhook signals from external sources"""
    
    def __init__(self):
        self.webhooks_file = 'database/webhooks.json'
        self.webhook_secrets_file = 'database/webhook_secrets.json'
        self.webhook_configs = self._load_webhook_configs()
        self.webhook_secrets = self._load_webhook_secrets()
    
    def _load_webhook_configs(self) -> Dict:
        """Load webhook configurations"""
        if not os.path.exists(self.webhooks_file):
            return {}
        
        try:
            with open(self.webhooks_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_webhook_configs(self):
        """Save webhook configurations"""
        os.makedirs(os.path.dirname(self.webhooks_file), exist_ok=True)
        with open(self.webhooks_file, 'w') as f:
            json.dump(self.webhook_configs, f, indent=2)
    
    def _load_webhook_secrets(self) -> Dict:
        """Load webhook secrets"""
        if not os.path.exists(self.webhook_secrets_file):
            return {}
        
        try:
            with open(self.webhook_secrets_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_webhook_secrets(self):
        """Save webhook secrets"""
        os.makedirs(os.path.dirname(self.webhook_secrets_file), exist_ok=True)
        with open(self.webhook_secrets_file, 'w') as f:
            json.dump(self.webhook_secrets, f, indent=2)
    
    def create_webhook(self, user_id: str, name: str, source: str = 'custom') -> Dict[str, Any]:
        """
        Create a new webhook endpoint for a user
        
        Args:
            user_id: User ID
            name: Webhook name
            source: Source type ('tradingview', 'custom', etc.)
        """
        import uuid
        webhook_id = f"wh_{uuid.uuid4().hex[:12]}"
        secret = uuid.uuid4().hex
        
        webhook_config = {
            'webhook_id': webhook_id,
            'user_id': user_id,
            'name': name,
            'source': source,
            'enabled': True,
            'created_at': datetime.utcnow().isoformat(),
            'signals_received': 0
        }
        
        self.webhook_configs[webhook_id] = webhook_config
        self.webhook_secrets[webhook_id] = secret
        
        self._save_webhook_configs()
        self._save_webhook_secrets()
        
        log_event("WEBHOOK", f"Created webhook {webhook_id} for user {user_id}")
        
        return {
            'success': True,
            'webhook': {
                'webhook_id': webhook_id,
                'name': name,
                'url': f'/api/webhook/{webhook_id}',
                'secret': secret,
                'source': source
            }
        }
    
    def verify_signature(self, webhook_id: str, payload: str, signature: str) -> bool:
        """Verify webhook signature"""
        if webhook_id not in self.webhook_secrets:
            return False
        
        secret = self.webhook_secrets[webhook_id].encode()
        expected_signature = hmac.new(secret, payload.encode(), hashlib.sha256).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    def process_webhook_signal(self, webhook_id: str, payload: Dict, signature: Optional[str] = None) -> Dict[str, Any]:
        """
        Process incoming webhook signal
        
        Args:
            webhook_id: Webhook ID
            payload: Signal data
            signature: Optional HMAC signature for verification
        """
        # Validate webhook exists
        if webhook_id not in self.webhook_configs:
            return {'success': False, 'error': 'Webhook not found'}
        
        webhook = self.webhook_configs[webhook_id]
        
        # Check if enabled
        if not webhook['enabled']:
            return {'success': False, 'error': 'Webhook is disabled'}
        
        # Verify signature if provided
        if signature:
            payload_str = json.dumps(payload, sort_keys=True)
            if not self.verify_signature(webhook_id, payload_str, signature):
                log_event("WEBHOOK", f"❌ Invalid signature for webhook {webhook_id}")
                return {'success': False, 'error': 'Invalid signature'}
        
        # Parse signal based on source
        if webhook['source'] == 'tradingview':
            signal = self._parse_tradingview_signal(payload)
        else:
            signal = self._parse_custom_signal(payload)
        
        if not signal:
            return {'success': False, 'error': 'Invalid signal format'}
        
        # Add metadata
        signal['webhook_id'] = webhook_id
        signal['user_id'] = webhook['user_id']
        signal['source'] = webhook['source']
        signal['received_at'] = datetime.utcnow().isoformat()
        
        # Update webhook stats
        webhook['signals_received'] += 1
        self._save_webhook_configs()
        
        # Save signal for processing
        self._save_signal(signal)
        
        log_event("WEBHOOK", f"✅ Processed signal from webhook {webhook_id}: {signal['symbol']} {signal['side']}")
        
        return {
            'success': True,
            'signal': {
                'symbol': signal['symbol'],
                'side': signal['side'],
                'entry_price': signal.get('entry_price'),
                'signal_id': signal.get('signal_id')
            }
        }
    
    def _parse_tradingview_signal(self, payload: Dict) -> Optional[Dict]:
        """Parse TradingView alert format"""
        try:
            # TradingView sends: {"ticker": "BTCUSDT", "action": "buy", "price": 50000}
            return {
                'signal_id': f"tv_{datetime.utcnow().timestamp()}",
                'symbol': payload.get('ticker', '').upper(),
                'side': 'LONG' if payload.get('action', '').lower() == 'buy' else 'SHORT',
                'entry_price': float(payload.get('price', 0)),
                'stop_loss': float(payload.get('stop', 0)) if payload.get('stop') else None,
                'targets': [float(t) for t in payload.get('targets', [])] if payload.get('targets') else []
            }
        except:
            return None
    
    def _parse_custom_signal(self, payload: Dict) -> Optional[Dict]:
        """Parse custom signal format"""
        try:
            # Expected format: {"symbol": "BTCUSDT", "side": "LONG", "entry": 50000, ...}
            return {
                'signal_id': payload.get('signal_id', f"custom_{datetime.utcnow().timestamp()}"),
                'symbol': payload.get('symbol', '').upper(),
                'side': payload.get('side', '').upper(),
                'entry_price': float(payload.get('entry', 0)) if payload.get('entry') else None,
                'stop_loss': float(payload.get('stop_loss', 0)) if payload.get('stop_loss') else None,
                'targets': payload.get('targets', [])
            }
        except:
            return None
    
    def _save_signal(self, signal: Dict):
        """Save signal for processing"""
        signals_file = 'database/webhook_signals.json'
        
        signals = []
        if os.path.exists(signals_file):
            try:
                with open(signals_file, 'r') as f:
                    signals = json.load(f)
            except:
                signals = []
        
        signals.append(signal)
        
        # Keep last 1000 signals
        signals = signals[-1000:]
        
        os.makedirs(os.path.dirname(signals_file), exist_ok=True)
        with open(signals_file, 'w') as f:
            json.dump(signals, f, indent=2)
    
    def get_user_webhooks(self, user_id: str) -> List[Dict]:
        """Get all webhooks for a user"""
        return [
            {
                'webhook_id': wh['webhook_id'],
                'name': wh['name'],
                'source': wh['source'],
                'enabled': wh['enabled'],
                'signals_received': wh['signals_received'],
                'created_at': wh['created_at'],
                'url': f'/api/webhook/{wh["webhook_id"]}'
            }
            for wh in self.webhook_configs.values()
            if wh['user_id'] == user_id
        ]
    
    def toggle_webhook(self, user_id: str, webhook_id: str, enabled: bool) -> Dict[str, Any]:
        """Enable or disable a webhook"""
        if webhook_id not in self.webhook_configs:
            return {'success': False, 'error': 'Webhook not found'}
        
        webhook = self.webhook_configs[webhook_id]
        
        if webhook['user_id'] != user_id:
            return {'success': False, 'error': 'Unauthorized'}
        
        webhook['enabled'] = enabled
        self._save_webhook_configs()
        
        status = 'enabled' if enabled else 'disabled'
        log_event("WEBHOOK", f"Webhook {webhook_id} {status}")
        
        return {'success': True, 'message': f'Webhook {status}'}
    
    def delete_webhook(self, user_id: str, webhook_id: str) -> Dict[str, Any]:
        """Delete a webhook"""
        if webhook_id not in self.webhook_configs:
            return {'success': False, 'error': 'Webhook not found'}
        
        webhook = self.webhook_configs[webhook_id]
        
        if webhook['user_id'] != user_id:
            return {'success': False, 'error': 'Unauthorized'}
        
        del self.webhook_configs[webhook_id]
        if webhook_id in self.webhook_secrets:
            del self.webhook_secrets[webhook_id]
        
        self._save_webhook_configs()
        self._save_webhook_secrets()
        
        log_event("WEBHOOK", f"Deleted webhook {webhook_id}")
        
        return {'success': True, 'message': 'Webhook deleted'}


# Global instance
webhook_handler = WebhookHandler()
