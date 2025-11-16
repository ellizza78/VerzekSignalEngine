"""
Signal Dispatcher
Sends generated signals to backend API and Telegram
"""
import requests
import logging
from typing import Dict, Optional
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class SignalDispatcher:
    """Dispatches signals to backend API and tracks metrics"""
    
    def __init__(self):
        self.backend_url = os.getenv('BACKEND_API_URL', 'https://api.verzekinnovative.com')
        self.api_key = os.getenv('BACKEND_API_KEY', '')
        self.signals_sent = 0
        self.signals_failed = 0
        
    async def dispatch(self, signal_data: Dict) -> bool:
        """
        Send signal to backend API
        
        Args:
            signal_data: Signal dictionary from Signal.to_dict()
            
        Returns:
            True if successfully sent, False otherwise
        """
        try:
            # Add dispatcher metadata
            payload = {
                **signal_data,
                'source': 'VerzekSignalEngine',
                'dispatcher_timestamp': datetime.now().isoformat()
            }
            
            # Send to backend API
            success = await self._send_to_backend(payload)
            
            if success:
                self.signals_sent += 1
                logger.info(f"✅ Signal dispatched: {signal_data['symbol']} {signal_data['direction']}")
                
                # Log to file for backup
                self._log_signal_to_file(signal_data)
            else:
                self.signals_failed += 1
                logger.error(f"❌ Failed to dispatch signal: {signal_data['symbol']}")
            
            return success
            
        except Exception as e:
            self.signals_failed += 1
            logger.error(f"❌ Dispatcher error: {e}")
            return False
    
    async def _send_to_backend(self, payload: Dict) -> bool:
        """Send signal to VerzekAutoTrader backend"""
        try:
            url = f"{self.backend_url}/api/signals"
            
            headers = {
                'Content-Type': 'application/json',
                'X-API-Key': self.api_key
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.debug(f"Backend responded: {response.json()}")
                return True
            else:
                logger.warning(f"Backend returned {response.status_code}: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error("Backend API timeout")
            return False
        except Exception as e:
            logger.error(f"Backend API error: {e}")
            return False
    
    def _log_signal_to_file(self, signal_data: Dict):
        """Save signal to local file for backup"""
        try:
            log_dir = './logs/signals'
            os.makedirs(log_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d')
            log_file = f"{log_dir}/signals_{timestamp}.log"
            
            with open(log_file, 'a') as f:
                f.write(f"{datetime.now().isoformat()} | {signal_data}\n")
                
        except Exception as e:
            logger.error(f"Failed to log signal to file: {e}")
    
    def get_stats(self) -> Dict:
        """Get dispatcher statistics"""
        return {
            'signals_sent': self.signals_sent,
            'signals_failed': self.signals_failed,
            'success_rate': (self.signals_sent / (self.signals_sent + self.signals_failed) * 100) if (self.signals_sent + self.signals_failed) > 0 else 0
        }


# Singleton instance
_dispatcher_instance = None

def get_dispatcher() -> SignalDispatcher:
    """Get or create dispatcher instance"""
    global _dispatcher_instance
    if _dispatcher_instance is None:
        _dispatcher_instance = SignalDispatcher()
    return _dispatcher_instance
