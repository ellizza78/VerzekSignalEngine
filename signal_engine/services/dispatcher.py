"""
Signal Dispatcher
Sends generated signals to backend API and Telegram
Master Fusion Engine v2.0 - SignalCandidate Support
"""
import requests
import logging
from typing import Dict, Optional
from datetime import datetime
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from core.models import SignalCandidate

load_dotenv()

logger = logging.getLogger(__name__)


class SignalDispatcher:
    """Dispatches signals to backend API and tracks metrics"""
    
    def __init__(self):
        self.backend_url = os.getenv('BACKEND_API_URL', 'https://api.verzekinnovative.com')
        self.internal_token = os.getenv('HOUSE_ENGINE_TOKEN', '')
        self.signals_sent = 0
        self.signals_failed = 0
        
    async def dispatch_candidate(self, candidate: SignalCandidate) -> bool:
        """
        Send SignalCandidate to backend API (Fusion Engine v2.0)
        
        Args:
            candidate: SignalCandidate object from fusion engine
            
        Returns:
            True if successfully sent, False otherwise
        """
        try:
            # Build backend payload (SignalCandidate already has calculated prices)
            backend_payload = {
                'source': candidate.bot_source,
                'symbol': candidate.symbol,
                'side': candidate.side,
                'entry': float(candidate.entry),
                'stop_loss': float(candidate.stop_loss),
                'take_profits': [float(tp) for tp in candidate.take_profits],
                'timeframe': candidate.timeframe,
                'confidence': int(candidate.confidence),
                'version': 'SE.v2.0-FUSION',
                'metadata': {
                    'signal_id': candidate.signal_id,
                    'bot_source': candidate.bot_source,
                    'timestamp': candidate.created_at.isoformat(),
                    'fusion_approved': True
                }
            }
            
            # Send to backend
            success = await self._send_candidate_to_backend(backend_payload)
            
            if success:
                self.signals_sent += 1
                logger.info(f"✅ Signal dispatched: {candidate.symbol} {candidate.side} (ID: {candidate.signal_id[:8]})")
                
                # Log to file for backup
                self._log_signal_to_file(backend_payload)
            else:
                self.signals_failed += 1
                logger.error(f"❌ Failed to dispatch signal: {candidate.symbol}")
            
            return success
            
        except Exception as e:
            self.signals_failed += 1
            logger.error(f"❌ Dispatcher error: {e}")
            return False
    
    async def dispatch(self, signal_data: Dict) -> bool:
        """
        Send signal to backend API (Legacy format)
        
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
    
    async def _send_candidate_to_backend(self, payload: Dict) -> bool:
        """
        Send SignalCandidate to VerzekAutoTrader backend (Fusion Engine v2.0)
        Retries up to 3 times on failure
        """
        max_retries = 3
        
        for attempt in range(1, max_retries + 1):
            try:
                url = f"{self.backend_url}/api/house-signals/ingest"
                
                headers = {
                    'Content-Type': 'application/json',
                    'X-INTERNAL-TOKEN': self.internal_token
                }
                
                response = requests.post(
                    url,
                    json=payload,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Backend accepted signal (ID: {result.get('signal_id', 'N/A')})")
                    return True
                else:
                    logger.warning(f"Backend returned {response.status_code}: {response.text}")
                    if attempt < max_retries:
                        logger.info(f"Retrying... (attempt {attempt + 1}/{max_retries})")
                        continue
                    return False
                    
            except requests.exceptions.Timeout:
                logger.error(f"Backend API timeout (attempt {attempt}/{max_retries})")
                if attempt < max_retries:
                    continue
                return False
            except Exception as e:
                logger.error(f"Backend API error (attempt {attempt}/{max_retries}): {e}")
                if attempt < max_retries:
                    continue
                return False
        
        return False
    
    async def _send_to_backend(self, payload: Dict) -> bool:
        """
        Send signal to VerzekAutoTrader backend house signals endpoint
        Retries up to 3 times on failure
        """
        max_retries = 3
        
        for attempt in range(1, max_retries + 1):
            try:
                url = f"{self.backend_url}/api/house-signals/ingest"
                
                headers = {
                    'Content-Type': 'application/json',
                    'X-INTERNAL-TOKEN': self.internal_token
                }
                
                # Map signal_data to backend expected format
                backend_payload = {
                    'source': payload.get('strategy', 'UNKNOWN').upper().split()[0],
                    'symbol': payload['symbol'].replace('/', ''),
                    'side': payload['direction'],
                    'entry': float(payload['entry_price']),
                    'stop_loss': float(payload['sl_price']),
                    'take_profits': [float(payload['tp_price'])],
                    'timeframe': payload.get('timeframe', 'M5').upper(),
                    'confidence': int(payload.get('confidence', 75)),
                    'version': payload.get('version', 'SE.v1.0'),
                    'metadata': {
                        'strategy': payload.get('strategy', ''),
                        'timestamp': payload.get('dispatcher_timestamp', '')
                    }
                }
                
                response = requests.post(
                    url,
                    json=backend_payload,
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Backend accepted signal (ID: {result.get('signal_id', 'N/A')})")
                    return True
                else:
                    logger.warning(f"Backend returned {response.status_code}: {response.text}")
                    if attempt < max_retries:
                        logger.info(f"Retrying... (attempt {attempt + 1}/{max_retries})")
                        continue
                    return False
                    
            except requests.exceptions.Timeout:
                logger.error(f"Backend API timeout (attempt {attempt}/{max_retries})")
                if attempt < max_retries:
                    continue
                return False
            except Exception as e:
                logger.error(f"Backend API error (attempt {attempt}/{max_retries}): {e}")
                if attempt < max_retries:
                    continue
                return False
        
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
